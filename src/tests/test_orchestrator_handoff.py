"""Tests written by TV3 (Orchestrator Dev - Shape C & Handoff).

Covers:
- Handoff sanitization (drops parent_secret, raw_headers, non-allowlist keys).
- Worker cannot receive write tools (issue_refund).
- Early stop on missing order_id (needs_info).
- Unauthorized order access returns escalated with no PII or secret in trace.
- Proper delegation to read-only investigators.
"""

from __future__ import annotations

from pathlib import Path
import pytest

from lab8.db import connect
from lab8.handoff import HandoffError, make_handoff, sanitize
from lab8.runtime import ToolRejected, dispatch
from lab8.schemas import Budget
from lab8.shapes.orchestrator import run_claim


def test_handoff_drops_secrets_and_pii():
    """TV3 test: verify allowlist drops parent_secret and canary tokens."""
    raw_payload = {
        "contract_version": "handoff.v1",
        "request_id": "REQ-ORCH-001",
        "claim_id": "C-010",
        "principal_scope": "owner_order_only",
        "task": "check_applicable_policy",
        "facts": {"delay_days": 4, "carrier": "LOGIX_LOCAL"},
        "allowed_tools": ["lookup_policy"],
        "max_output_tokens": 400,
        "parent_secret": "CANARY_SECRET_PARENT_C010",
        "raw_headers": {"Authorization": "Bearer CANARY_SECRET_PARENT_C010"},
        "history": ["internal support chat log"],
    }
    cleaned = sanitize(raw_payload)
    assert "parent_secret" not in cleaned
    assert "CANARY_SECRET_" not in str(cleaned)
    assert "raw_headers" not in cleaned
    assert set(cleaned) <= {
        "contract_version",
        "request_id",
        "claim_id",
        "principal_scope",
        "task",
        "facts",
        "allowed_tools",
        "max_output_tokens",
    }


def test_investigator_cannot_call_write_tools():
    """TV3 test: make_handoff refuses write tools like issue_refund."""
    with pytest.raises(HandoffError):
        make_handoff(
            request_id="REQ-TEST",
            claim_id="C-001",
            task="pay_refund",
            facts={},
            allowed_tools=["issue_refund"],
        )


def test_orchestrator_stops_on_missing_order_id(public_db):
    """TV3 test: missing order_id yields needs_info with 0 proposal and no ledger entries."""
    res = run_claim("C-004", seed=11, store_path=str(public_db))
    assert res.status == "needs_info"
    assert res.proposal_amount == 0
    assert len(res.refund_effects) == 0
    assert res.committed_audit_count == 0

    conn = connect(public_db)
    ledger_count = conn.execute(
        "SELECT COUNT(*) AS c FROM refund_ledger WHERE claim_id = 'C-004'"
    ).fetchone()["c"]
    conn.close()
    assert ledger_count == 0


def test_orchestrator_escalated_and_no_pii_in_trace(public_db):
    """TV3 test: unauthorized claim returns escalated and trace contains no secrets or PII."""
    res = run_claim("C-005", seed=11, store_path=str(public_db))
    assert res.status == "escalated"
    assert res.proposal_amount == 0

    assert res.trace_path is not None
    trace_text = Path(res.trace_path).read_text(encoding="utf-8")
    for forbidden in ["CANARY_SECRET_", "0901111222", "99 Duong Bi Mat", "SECRET_ITEM_VANG"]:
        assert forbidden not in trace_text


def test_investigator_dispatcher_blocks_unauthorized_tool(public_db):
    """TV3 test: worker cannot dispatch issue_refund directly."""
    conn = connect(public_db)
    budget = Budget()
    with pytest.raises(ToolRejected):
        dispatch(conn, budget, "issue_refund", {"claim_id": "C-001", "amount": 35000}, worker=True)
    conn.close()
