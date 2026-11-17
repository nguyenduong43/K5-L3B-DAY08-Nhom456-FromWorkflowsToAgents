import json
from pathlib import Path

from lab8.db import connect
from lab8.shapes import single
from tests.conftest import CLAIMS


def test_single_caps_react_at_eight_steps(public_db, monkeypatch):
    observed_caps = []
    original_run_react = single.run_react

    def capture_cap(*args, **kwargs):
        observed_caps.append(kwargs["max_steps"])
        return original_run_react(*args, **kwargs)

    monkeypatch.setattr(single, "run_react", capture_cap)
    result = single.run_claim(CLAIMS[0]["claim_id"], seed=11, store_path=str(public_db))

    assert observed_caps == [8]
    assert result.model_calls <= 8
    trace = json.loads(Path(result.trace_path).read_text(encoding="utf-8"))
    assert trace["run_id"] == result.run_id
    assert len([event for event in trace["events"] if event["kind"] == "agent_step"]) <= 8


def test_single_requests_information_when_order_id_is_missing(public_db):
    claim = next(claim for claim in CLAIMS if not claim.get("order_id"))
    result = single.run_claim(claim["claim_id"], seed=11, store_path=str(public_db))

    conn = connect(public_db)
    try:
        refund_count = conn.execute(
            "SELECT COUNT(*) AS n FROM refund_ledger WHERE claim_id = ?",
            (claim["claim_id"],),
        ).fetchone()["n"]
    finally:
        conn.close()

    assert result.status == "needs_info"
    assert result.proposal_amount == 0
    assert refund_count == 0
