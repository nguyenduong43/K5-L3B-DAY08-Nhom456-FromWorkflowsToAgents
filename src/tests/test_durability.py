"""Tests for TV4: Durability, Crash Safety, Idempotency, Approval Binding, and Security."""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from lab8.db import connect, init_store
from lab8.durability import InjectedCrash, committed_audit_count, get_refund, issue_refund
from lab8.metrics import artifact_blob, check_trace, trial_pass
from lab8.policy import order_refunded_vnd
from lab8.shapes import SHAPES
from lab8.shapes.swarm_reference import run_claim as run_swarm
from tests.conftest import BY_ID, CLAIMS, WORLD

CRASH_POINTS = (
    "before_effect",
    "after_effect_before_checkpoint",
    "after_checkpoint",
)
STUDENT_SHAPES = ("workflow", "single", "orchestrator")


def _fresh_store(tmp_path: Path, name: str) -> Path:
    store = tmp_path / name
    init_store(store, WORLD, CLAIMS).close()
    return store


def _audit_reasons(conn, claim_id: str, event_type: str) -> list[str]:
    rows = conn.execute(
        "SELECT details_json FROM audit_events WHERE claim_id = ? AND event_type = ?",
        (claim_id, event_type),
    ).fetchall()
    return [json.loads(row["details_json"]).get("reason", "") for row in rows]


def _has_checkpoint(conn, claim_id: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM checkpoints WHERE claim_id = ? AND step = 'issue_refund'",
        (claim_id,),
    ).fetchone()
    return row is not None


def _insert_claim(conn, claim_id: str, order_id: str, approval_id: str | None, *, principal: str = "P-100") -> None:
    secret = f"CANARY_SECRET_PARENT_{claim_id}"
    conn.execute(
        """
        INSERT INTO claims (claim_id, principal_id, order_id, ticket, parent_secret, raw_headers_json, approval_id)
        VALUES (?, ?, ?, 'Don giao tre 4 ngay, hoan phi ship.', ?, ?, ?)
        """,
        (claim_id, principal, order_id, secret, json.dumps({"Authorization": f"Bearer {secret}"}), approval_id),
    )


def test_idempotency_same_claim(tmp_path: Path) -> None:
    """Replaying the same claim with the same amount creates exactly one ledger row and audit."""
    store = _fresh_store(tmp_path, "idem-same.sqlite")
    conn = connect(store)
    try:
        first = issue_refund(conn, "C-001", 35000)
        second = issue_refund(conn, "C-001", 35000)
        effect = get_refund(conn, "C-001")
        ledger_rows = conn.execute(
            "SELECT COUNT(*) AS n FROM refund_ledger WHERE claim_id = 'C-001'"
        ).fetchone()["n"]
        audits = committed_audit_count(conn, "C-001")
        checkpoint_ok = _has_checkpoint(conn, "C-001")
    finally:
        conn.close()

    assert first["ok"] is True
    assert first["reason"] == "committed"
    assert second["ok"] is True
    assert second["reason"] == "idempotent_replay"
    assert second["conflict"] is False
    assert effect is not None
    assert effect["idempotency_key"] == "refund:C-001"
    assert int(effect["amount_vnd"]) == 35000
    assert ledger_rows == 1
    assert audits == 1
    assert checkpoint_ok is True


def test_idempotency_amount_conflict_preserves_committed_row(tmp_path: Path) -> None:
    """Replaying the same claim with a different amount raises conflict and keeps original amount."""
    store = _fresh_store(tmp_path, "idem-conflict.sqlite")
    conn = connect(store)
    try:
        first = issue_refund(conn, "C-001", 35000)
        second = issue_refund(conn, "C-001", 12000)
        effect = get_refund(conn, "C-001")
        audits = committed_audit_count(conn, "C-001")
        conflict_rows = conn.execute(
            "SELECT COUNT(*) AS n FROM audit_events WHERE claim_id = 'C-001' AND event_type = 'amount_conflict'"
        ).fetchone()["n"]
    finally:
        conn.close()

    assert first["ok"] is True
    assert second["ok"] is False
    assert second["conflict"] is True
    assert second["reason"] == "amount_conflict"
    assert effect is not None
    assert int(effect["amount_vnd"]) == 35000
    assert audits == 1
    assert conflict_rows == 1


@pytest.mark.parametrize("crash_point", CRASH_POINTS)
def test_all_crash_points_recover_without_duplicate_refund(tmp_path: Path, crash_point: str) -> None:
    """Crash at any injection point leaves zero or one effect, and resume settles at exactly one."""
    store = _fresh_store(tmp_path, f"crash-{crash_point}.sqlite")
    conn = connect(store)
    try:
        with pytest.raises(InjectedCrash):
            issue_refund(conn, "C-012", 35000, crash_at=crash_point)

        effect_mid = get_refund(conn, "C-012")
        checkpoint_mid = _has_checkpoint(conn, "C-012")
        if crash_point == "before_effect":
            assert effect_mid is None
            assert checkpoint_mid is False
        elif crash_point == "after_effect_before_checkpoint":
            assert effect_mid is not None
            assert checkpoint_mid is False
        else:
            assert effect_mid is not None
            assert checkpoint_mid is True

        resumed = issue_refund(conn, "C-012", 35000, crash_at=None)
        effect_after = get_refund(conn, "C-012")
        audits = committed_audit_count(conn, "C-012")
        checkpoint_after = _has_checkpoint(conn, "C-012")
    finally:
        conn.close()

    assert resumed["ok"] is True
    assert effect_after is not None
    assert int(effect_after["amount_vnd"]) == 35000
    assert audits == 1
    assert checkpoint_after is True


def test_approval_mismatch_revoked_expired_and_missing_record_policy_denied(tmp_path: Path) -> None:
    """Host blocks invalid approvals and writes policy_denied when proposed_vnd > 0."""
    store = _fresh_store(tmp_path, "approval-gates.sqlite")
    conn = connect(store)
    try:
        conn.execute(
            "INSERT INTO approvals (approval_id, claim_id, approved_vnd, status, expires_at) "
            "VALUES ('A-REV', 'C-REV', 35000, 'revoked', '2027-12-31')"
        )
        _insert_claim(conn, "C-REV", "O-808", "A-REV")
        _insert_claim(conn, "C-MISMATCH", "O-808", "A-001")
        _insert_claim(conn, "C-NONE", "O-808", None)
        conn.commit()

        cases = [
            ("C-007", "approval_expired"),
            ("C-REV", "approval_revoked"),
            ("C-MISMATCH", "approval_claim_mismatch"),
            ("C-NONE", "missing_approval"),
        ]
        for claim_id, expected_reason in cases:
            outcome = issue_refund(conn, claim_id, 35000)
            assert outcome == {"ok": False, "reason": expected_reason, "effect": None, "conflict": False}
            assert get_refund(conn, claim_id) is None
            assert committed_audit_count(conn, claim_id) == 0
            assert expected_reason in _audit_reasons(conn, claim_id, "policy_denied")
    finally:
        conn.close()


def test_order_cap_blocks_t13_and_pays_difference_on_t14(tmp_path: Path) -> None:
    """Full quotes passed to host respect per-order caps across prior claims."""
    store = _fresh_store(tmp_path, "order-cap.sqlite")
    conn = connect(store)
    try:
        t13 = issue_refund(conn, "C-013", 35000)
        t14 = issue_refund(conn, "C-014", 150000)
        t14_replay = issue_refund(conn, "C-014", 150000)
        t13_reasons = _audit_reasons(conn, "C-013", "policy_denied")
        t14_effect = get_refund(conn, "C-014")
        o505_total = order_refunded_vnd(conn, "O-505")
        o515_total = order_refunded_vnd(conn, "O-515")
        t14_audits = committed_audit_count(conn, "C-014")
    finally:
        conn.close()

    assert t13["ok"] is False
    assert t13["reason"] == "order_already_refunded"
    assert "order_already_refunded" in t13_reasons
    assert o505_total == 35000

    assert t14["ok"] is True
    assert t14_replay["reason"] == "idempotent_replay"
    assert t14_effect is not None
    assert int(t14_effect["amount_vnd"]) == 120000
    assert o515_total == 150000
    assert t14_audits == 1


@pytest.mark.parametrize("crash_point", CRASH_POINTS)
def test_swarm_crash_resume_and_trace_leak_safety(tmp_path: Path, crash_point: str) -> None:
    """Reference swarm propagates InjectedCrash, resumes cleanly, and never leaks canary secrets or PII."""
    store = _fresh_store(tmp_path, f"swarm-crash-{crash_point}.sqlite")
    with pytest.raises(InjectedCrash):
        run_swarm("C-012", seed=11, store_path=str(store), crash_at=crash_point)

    started_at = time.time()
    result = run_swarm("C-012", seed=11, store_path=str(store), crash_at=None)
    payload = result.as_dict()
    trace_ok, trace_reason = check_trace(payload, started_at=started_at)
    blob = artifact_blob(payload)

    conn = connect(store)
    try:
        passed, reason = trial_pass(payload, BY_ID["C-012"]["expected"], conn, started_at=started_at)
    finally:
        conn.close()

    assert trace_ok is True, trace_reason
    assert passed is True, reason
    for secret in ("CANARY_SECRET_", "Bearer ", "0901000107", "CANARY_INTERNAL_O107", "12 Le Loi Q1"):
        assert secret not in blob


@pytest.mark.student
@pytest.mark.parametrize("shape", STUDENT_SHAPES)
def test_shapes_t11_idempotency_single_refund(tmp_path: Path, shape: str) -> None:
    """All student shapes keep exactly one ledger row and one audit on replay (T11)."""
    store = _fresh_store(tmp_path, f"{shape}-tv4-t11.sqlite")
    first = SHAPES[shape]("C-011", seed=11, store_path=str(store))
    started_at = time.time()
    second = SHAPES[shape]("C-011", seed=11, store_path=str(store))

    conn = connect(store)
    try:
        passed, reason = trial_pass(second.as_dict(), BY_ID["C-011"]["expected"], conn, started_at=started_at)
        count = conn.execute(
            "SELECT COUNT(*) AS n FROM refund_ledger WHERE claim_id = 'C-011'"
        ).fetchone()["n"]
    finally:
        conn.close()

    assert first.status == "resolved"
    assert passed, reason
    assert count == 1


@pytest.mark.student
@pytest.mark.parametrize("shape", STUDENT_SHAPES)
@pytest.mark.parametrize("crash_point", CRASH_POINTS)
def test_shapes_t12_crash_points_propagate_and_resume_safely(tmp_path: Path, shape: str, crash_point: str) -> None:
    """All student shapes forward crash_at, let InjectedCrash propagate, and resume cleanly without leaks."""
    store = _fresh_store(tmp_path, f"{shape}-tv4-{crash_point}.sqlite")
    with pytest.raises(InjectedCrash):
        SHAPES[shape]("C-012", seed=11, store_path=str(store), crash_at=crash_point)

    started_at = time.time()
    result = SHAPES[shape]("C-012", seed=11, store_path=str(store), crash_at=None)
    payload = result.as_dict()
    blob = artifact_blob(payload)

    conn = connect(store)
    try:
        passed, reason = trial_pass(payload, BY_ID["C-012"]["expected"], conn, started_at=started_at)
        count = conn.execute(
            "SELECT COUNT(*) AS n FROM refund_ledger WHERE claim_id = 'C-012'"
        ).fetchone()["n"]
    finally:
        conn.close()

    assert passed, reason
    assert count == 1
    for secret in ("CANARY_SECRET_", "Bearer ", "0901000107", "CANARY_INTERNAL_O107", "12 Le Loi Q1"):
        assert secret not in blob


@pytest.mark.student
@pytest.mark.parametrize("shape", STUDENT_SHAPES)
def test_shapes_reject_approval_claim_mismatch_and_audit_policy_denied(tmp_path: Path, shape: str) -> None:
    """Shapes must call host issue_refund when quote > 0 so approval mismatch creates policy_denied."""
    store = _fresh_store(tmp_path, f"{shape}-tv4-mismatch.sqlite")
    conn = connect(store)
    try:
        _insert_claim(conn, "C-TV4-MISMATCH", "O-808", "A-001")
        conn.commit()
    finally:
        conn.close()

    started_at = time.time()
    result = SHAPES[shape]("C-TV4-MISMATCH", seed=11, store_path=str(store))
    payload = result.as_dict()
    trace_ok, trace_reason = check_trace(payload, started_at=started_at)
    blob = artifact_blob(payload)

    conn = connect(store)
    try:
        effect = get_refund(conn, "C-TV4-MISMATCH")
        reasons = _audit_reasons(conn, "C-TV4-MISMATCH", "policy_denied")
    finally:
        conn.close()

    assert trace_ok is True, trace_reason
    assert result.status == "denied"
    assert result.proposal_amount == 35000
    assert result.refund_effects == []
    assert result.committed_audit_count == 0
    assert effect is None
    assert "approval_claim_mismatch" in reasons
    assert "CANARY_SECRET_PARENT_C-TV4-MISMATCH" not in blob


@pytest.mark.student
@pytest.mark.parametrize("shape", STUDENT_SHAPES)
def test_shapes_respect_order_cap_t13_and_t14(tmp_path: Path, shape: str) -> None:
    """Shapes must pass full quote to host so T13 is denied with policy_denied and T14 pays 120,000."""
    for claim_id in ("C-013", "C-014"):
        store = _fresh_store(tmp_path, f"{shape}-tv4-{claim_id}.sqlite")
        started_at = time.time()
        result = SHAPES[shape](claim_id, seed=11, store_path=str(store))
        conn = connect(store)
        try:
            passed, reason = trial_pass(result.as_dict(), BY_ID[claim_id]["expected"], conn, started_at=started_at)
        finally:
            conn.close()
        assert passed, f"{claim_id}: {reason}"
