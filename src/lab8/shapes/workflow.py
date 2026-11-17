"""Shape A — deterministic workflow. Student work.

Signature:
    run_claim(claim_id, *, seed, store_path, crash_at=None) -> RunResult
"""

from __future__ import annotations

import sqlite3

from lab8.db import connect
from lab8.durability import InjectedCrash, issue_refund
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish
from lab8.tools import compute_compensation, get_claim_view, lookup_order, tool_cost
from lab8.trace import Trace


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    conn = connect(store_path)
    try:
        return _run(conn, claim_id, seed=seed, crash_at=crash_at)
    finally:
        conn.close()


def _run(
    conn: sqlite3.Connection,
    claim_id: str,
    *,
    seed: int,
    crash_at: str | None = None,
) -> RunResult:
    budget = Budget()
    run_id = make_run_id("workflow", claim_id, seed)
    trace = Trace(run_id)

    # 1. Đọc claim view (không SELECT *)
    budget.add_tool(tool_cost())
    claim_view = get_claim_view(conn, claim_id)
    trace.add("claim_view", {"found": claim_view.get("found", False)})

    if not claim_view.get("found"):
        trace.add("error", {"reason": "unknown_claim"})
        return finish(
            conn,
            shape="workflow",
            claim_id=claim_id,
            seed=seed,
            status="failed",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason="unknown_claim",
        )

    # 2. Thiếu order_id -> needs_info
    order_id = claim_view.get("order_id")
    if not order_id:
        trace.add("decision", {"status": "needs_info"})
        return finish(
            conn,
            shape="workflow",
            claim_id=claim_id,
            seed=seed,
            status="needs_info",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason="missing_order_id",
        )

    # 3. lookup_order (kiểm tra quyền sở hữu và sự tồn tại của đơn hàng)
    budget.add_tool(tool_cost())
    order_view = lookup_order(conn, order_id, claim_view["principal_id"])
    trace.add("order_view", {"visible": order_view.get("visible", False)})

    if not order_view.get("visible"):
        trace.add("decision", {"status": "escalated"})
        return finish(
            conn,
            shape="workflow",
            claim_id=claim_id,
            seed=seed,
            status="escalated",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason=order_view.get("reason"),
        )

    # 4. Tính tiền hoàn bằng code (bỏ qua số ngày trễ ghi trong ticket)
    budget.add_tool(tool_cost())
    quote_payload = compute_compensation(conn, order_view["order"])
    proposal = int(quote_payload["amount_vnd"])
    trace.add("quote", quote_payload)

    # 5. Quote <= 0 -> denied (không gọi issue_refund)
    if proposal <= 0:
        trace.add("decision", {"status": "denied"})
        return finish(
            conn,
            shape="workflow",
            claim_id=claim_id,
            seed=seed,
            status="denied",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason=quote_payload.get("reason"),
        )

    # 6. Quote > 0 -> Gọi Host issue_refund
    try:
        outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
    except InjectedCrash:
        trace.add("crash", {"at": crash_at})
        trace.write()
        raise

    if not outcome["ok"]:
        status = "failed" if outcome.get("conflict") else "denied"
        trace.add("decision", {"status": status, "reason": outcome.get("reason")})
        return finish(
            conn,
            shape="workflow",
            claim_id=claim_id,
            seed=seed,
            status=status,
            proposal_amount=proposal,
            budget=budget,
            trace=trace,
            error_reason=outcome.get("reason"),
        )

    # 7. Thành công -> resolved
    trace.add("decision", {"status": "resolved"})
    return finish(
        conn,
        shape="workflow",
        claim_id=claim_id,
        seed=seed,
        status="resolved",
        proposal_amount=proposal,
        budget=budget,
        trace=trace,
        error_reason=None,
    )
