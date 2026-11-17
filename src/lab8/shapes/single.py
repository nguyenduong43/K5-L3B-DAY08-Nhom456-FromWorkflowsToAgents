"""Shape B — one ReAct agent. Student work.

Use `lab8.runtime.run_react` with max_steps=8. `decide` may pick a read tool.
It must not call `issue_refund`. After the loop, the host validates the quote
and is the only writer.

A decide() that trusts ticket text over the order row will fail hidden claims
where the customer overstates the delay or cites a superseded clause.

Per-order cap: an order may already have been refunded by an earlier claim.
The read tool `lookup_refund_history` shows how much. The host still enforces
the cap, so pass the full quote to `durability.issue_refund`, not a net amount.

Caps: stop at 8 steps. Count model calls in the Budget so cost stays comparable.

Trace contract v1 (docs/contracts.md): return a trace_path to a JSON file written in this run,
{"run_id": <same run_id>, "events": [...]}, on every return path including early
ones. `lab8.trace.Trace` does this; your own tracer is fine if it matches.
"""

from __future__ import annotations

import sqlite3
from typing import Any

from lab8.db import connect
from lab8.durability import issue_refund
from lab8.mock_llm import complete
from lab8.runtime import run_react
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish, safe_dump
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
    crash_at: str | None,
) -> RunResult:
    budget = Budget()
    run_id = make_run_id("single", claim_id, seed)
    trace = Trace(run_id)
    trace.add("shape", {"name": "single", "max_steps": 8})
    decision_count = 0

    def decide(seen: dict[str, Any]) -> dict[str, Any]:
        nonlocal decision_count
        decision_count += 1
        last_tool = seen.get("last_tool")
        stage = "start" if last_tool is None else f"after_{last_tool}"

        # MockLLM supplies seeded text; the adapter routes only from read-tool results.
        complete(
            budget,
            seed=seed,
            purpose="single_decide",
            prompt=f"stage={stage}; claim_id={claim_id}",
        )
        trace.add("agent_step", {"step": decision_count, "stage": stage})

        if last_tool is None:
            trace.add("tool_call", {"tool": "get_claim_view"})
            return {"tool": "get_claim_view", "args": {"claim_id": claim_id}}

        result = seen["last_result"]
        if last_tool == "get_claim_view":
            trace.add(
                "tool_result",
                {
                    "tool": last_tool,
                    "found": bool(result.get("found")),
                    "claim_id": claim_id,
                    "order_id": result.get("order_id"),
                },
            )
            if not result.get("found"):
                return {"final": {"status": "failed", "error_reason": "unknown_claim"}}
            if not result.get("order_id"):
                return {
                    "final": {
                        "status": "needs_info",
                        "error_reason": "missing_order_id",
                    }
                }
            trace.add("tool_call", {"tool": "lookup_order"})
            return {
                "tool": "lookup_order",
                "args": {
                    "order_id": result["order_id"],
                    "principal_id": result["principal_id"],
                },
            }

        if last_tool == "lookup_order":
            visible = bool(result.get("visible"))
            trace.add(
                "tool_result",
                {
                    "tool": last_tool,
                    "visible": visible,
                    "reason": result.get("reason"),
                },
            )
            if not visible:
                return {
                    "final": {
                        "status": "escalated",
                        "error_reason": result.get("reason"),
                    }
                }
            trace.add("tool_call", {"tool": "compute_compensation"})
            return {
                "tool": "compute_compensation",
                "args": {"order": result["order"]},
            }

        if last_tool == "compute_compensation":
            quote_payload = result
            trace.add("quote", safe_dump(quote_payload))
            return {
                "final": {
                    "status": "quoted",
                    "proposal_amount": int(quote_payload["amount_vnd"]),
                    "quote": quote_payload,
                }
            }

        return {
            "final": {
                "status": "failed",
                "error_reason": "unexpected_tool_result",
            }
        }

    react_result = run_react(
        conn,
        budget,
        observation={"claim_id": claim_id},
        decide=decide,
        max_steps=8,
    )
    final = react_result["final"]

    if final.get("status") != "quoted":
        status = final.get("status", "failed")
        reason = final.get("error_reason")
        trace.add("decision", {"status": status, "reason": reason})
        return finish(
            conn,
            shape="single",
            claim_id=claim_id,
            seed=seed,
            status=status,
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason=reason,
        )

    proposal = int(final["proposal_amount"])
    if proposal <= 0:
        reason = final["quote"].get("reason")
        trace.add("decision", {"status": "denied", "reason": reason})
        return finish(
            conn,
            shape="single",
            claim_id=claim_id,
            seed=seed,
            status="denied",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason=reason,
        )

    # TODO CP3 (student): pass crash_at=crash_at and let InjectedCrash propagate.
    del crash_at
    outcome = issue_refund(conn, claim_id, proposal)
    if not outcome["ok"]:
        status = "failed" if outcome["conflict"] else "denied"
        trace.add("decision", {"status": status, "reason": outcome["reason"]})
        return finish(
            conn,
            shape="single",
            claim_id=claim_id,
            seed=seed,
            status=status,
            proposal_amount=proposal,
            budget=budget,
            trace=trace,
            error_reason=outcome["reason"],
        )

    trace.add("decision", {"status": "resolved"})
    return finish(
        conn,
        shape="single",
        claim_id=claim_id,
        seed=seed,
        status="resolved",
        proposal_amount=proposal,
        budget=budget,
        trace=trace,
        error_reason=None,
    )
