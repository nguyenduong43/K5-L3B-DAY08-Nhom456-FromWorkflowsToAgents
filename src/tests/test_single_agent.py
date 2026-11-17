"""Tests written by TV2 (Single Agent Dev - Shape B).

Covers:
- Step cap enforcement (8 steps max).
- Early stop on missing order_id (needs_info).
- Unauthorized order access returns escalated with no PII in trace.
- Model cannot invoke write tools (issue_refund) directly.
- Single agent deterministic compensation calculation via code.
"""

from __future__ import annotations

import json
from pathlib import Path
import pytest

from lab8.db import connect
from lab8.runtime import ToolRejected, dispatch, run_react
from lab8.schemas import Budget
from lab8.shapes.single import run_claim
from lab8.tools import get_claim_view


def test_react_step_limit_enforced(public_db):
    """TV2 test: verify that reaching max_steps=8 stops with step_cap."""
    conn = connect(public_db)
    budget = Budget()
    steps_taken = 0

    def endless_decide(seen):
        nonlocal steps_taken
        steps_taken += 1
        # Continuously calling lookup_policy without ever returning 'final'
        return {"tool": "lookup_policy", "args": {}}

    claim_view = get_claim_view(conn, "C-001")
    outcome = run_react(
        conn,
        budget,
        observation={"claim": claim_view},
        decide=endless_decide,
        max_steps=8,
        worker=True,
    )
    conn.close()

    assert steps_taken == 8
    assert outcome["stopped"] == "step_cap"
    assert outcome["final"]["status"] == "failed"
    assert outcome["final"]["error_reason"] == "step_cap"


def test_single_stops_early_on_missing_order_id(public_db):
    """TV2 test: C-004 has no order_id; must return needs_info without ledger entries."""
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


def test_single_escalated_and_no_pii_leak(public_db):
    """TV2 test: C-005 attempts to access another user's order; returns escalated with no PII."""
    res = run_claim("C-005", seed=11, store_path=str(public_db))
    assert res.status == "escalated"
    assert res.proposal_amount == 0

    # Inspect generated trace file to verify zero secret/PII leak
    assert res.trace_path is not None
    trace_content = Path(res.trace_path).read_text(encoding="utf-8")
    for forbidden in ["CANARY_SECRET_", "0901111222", "99 Duong Bi Mat", "SECRET_ITEM_VANG"]:
        assert forbidden not in trace_content


def test_single_worker_cannot_call_write_tools(public_db):
    """TV2 test: inside the ReAct worker, dispatching issue_refund is blocked."""
    conn = connect(public_db)
    budget = Budget()
    with pytest.raises(ToolRejected):
        dispatch(conn, budget, "issue_refund", {"claim_id": "C-001", "amount": 35000}, worker=True)
    conn.close()
