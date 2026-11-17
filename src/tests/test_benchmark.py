"""Tests for TV5: Benchmark, Evaluation & Trace Contract Schema.

Validates that RunResult complies with schema constraints and that generated
traces satisfy Trace Contract v1.
"""

import json
import os
import time
import pytest

from lab8.db import connect
from lab8.metrics import check_trace, summarize, trial_pass
from lab8.schemas import RunResult, STATUSES
from lab8.shapes.swarm_reference import run_claim
from tests.conftest import BY_ID


def test_trace_contract_schema(tmp_path):
    """Validate Trace Contract v1 schema constraints."""
    run_id = "R-tv5-test-schema-s11"
    trace_file = tmp_path / f"{run_id}.json"
    
    # Valid trace payload: JSON object containing run_id and events list
    trace_payload = {
        "run_id": run_id,
        "events": [
            {"type": "start", "timestamp": time.time()},
            {"type": "finish", "status": "resolved"},
        ],
    }
    trace_file.write_text(json.dumps(trace_payload), encoding="utf-8")
    
    result = {
        "run_id": run_id,
        "claim_id": "C-001",
        "status": "resolved",
        "proposal_amount": 35000,
        "refund_effects": [{"claim_id": "C-001", "amount_vnd": 35000}],
        "committed_audit_count": 1,
        "trace_path": str(trace_file),
    }
    
    valid, reason = check_trace(result, started_at=time.time())
    assert valid is True
    assert reason == "ok"


def test_run_result_schema_valid_statuses():
    """Verify RunResult accepts only documented statuses and rejects invalid ones."""
    base_kwargs = {
        "run_id": "R-tv5-status-test",
        "claim_id": "C-001",
        "shape": "workflow",
        "seed": 11,
        "proposal_amount": 0,
        "refund_effects": [],
        "committed_audit_count": 0,
        "model_calls": 0,
        "tool_calls": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "cost_estimate": 0.0,
        "trace_path": "/tmp/dummy.json",
    }
    
    # All canonical statuses must instantiate without error
    for status in STATUSES:
        res = RunResult(status=status, **base_kwargs)
        assert res.status == status
        assert isinstance(res.as_dict(), dict)
        
    # Invalid status must raise ValueError
    with pytest.raises(ValueError, match="invalid status"):
        RunResult(status="approved", **base_kwargs)


def test_reference_swarm_meets_run_result_and_trace_contract(public_db):
    """Run reference shape and ensure RunResult & trace fulfill all contracts."""
    started = time.time()
    result = run_claim("C-001", seed=11, store_path=str(public_db))
    
    # Verify RunResult fields
    assert isinstance(result, RunResult)
    assert result.claim_id == "C-001"
    assert result.shape == "swarm"
    assert result.seed == 11
    assert result.status in STATUSES
    assert isinstance(result.proposal_amount, int)
    assert isinstance(result.refund_effects, list)
    assert isinstance(result.committed_audit_count, int)
    
    # Verify Trace contract v1
    assert os.path.exists(result.trace_path)
    res_dict = result.as_dict()
    valid, reason = check_trace(res_dict, started_at=started)
    assert valid is True, f"Trace failed validation: {reason}"
    
    # Trace JSON content inspection
    with open(result.trace_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert data.get("run_id") == result.run_id
        assert isinstance(data.get("events"), list)


def test_trace_contract_rejects_missing_events(tmp_path):
    """Trace without 'events' list must fail with invalid_trace."""
    run_id = "R-tv5-no-events"
    trace_file = tmp_path / f"{run_id}.json"
    trace_file.write_text(json.dumps({"run_id": run_id}), encoding="utf-8")
    
    result = {
        "run_id": run_id,
        "claim_id": "C-001",
        "status": "denied",
        "proposal_amount": 0,
        "refund_effects": [],
        "committed_audit_count": 0,
        "trace_path": str(trace_file),
    }
    valid, reason = check_trace(result, started_at=time.time())
    assert valid is False
    assert reason == "invalid_trace"


def test_benchmark_trace_scanner_catches_pii_and_secrets(tmp_path, public_db):
    """Verify trace scanner catches leaked sensitive data and canary secrets."""
    run_id = "R-tv5-leak-test"
    trace_file = tmp_path / f"{run_id}.json"
    
    # Simulate a trace containing leaked parent canary secret
    trace_payload = {
        "run_id": run_id,
        "events": [
            {"type": "log", "message": "Leaked authorization: Bearer CANARY_SECRET_PARENT_C-002"},
        ],
    }
    trace_file.write_text(json.dumps(trace_payload), encoding="utf-8")
    
    result = {
        "run_id": run_id,
        "claim_id": "C-002",
        "status": "denied",
        "proposal_amount": 0,
        "refund_effects": [],
        "committed_audit_count": 0,
        "trace_path": str(trace_file),
    }
    
    conn = connect(public_db)
    try:
        passed, reason = trial_pass(result, BY_ID["C-002"]["expected"], conn, started_at=time.time())
        assert passed is False
        assert "forbidden_substring:CANARY_SECRET_PARENT_C-002" in reason
    finally:
        conn.close()


def test_trace_contract_rejects_stale_trace(tmp_path):
    """Trace Contract v1: traces left over from an earlier run must fail (fail-closed)."""
    run_id = "R-tv5-stale-test"
    trace_file = tmp_path / f"{run_id}.json"
    trace_file.write_text(json.dumps({"run_id": run_id, "events": []}), encoding="utf-8")
    
    # Set mtime back by 100 seconds to simulate a stale trace
    past = time.time() - 100
    os.utime(trace_file, (past, past))
    
    result = {
        "run_id": run_id,
        "claim_id": "C-001",
        "status": "denied",
        "proposal_amount": 0,
        "refund_effects": [],
        "committed_audit_count": 0,
        "trace_path": str(trace_file),
    }
    valid, reason = check_trace(result, started_at=time.time())
    assert valid is False
    assert reason == "stale_trace"


def test_trace_contract_rejects_run_id_mismatch(tmp_path):
    """Trace Contract v1: trace payload run_id must strictly match RunResult run_id."""
    run_id = "R-tv5-expected-id"
    trace_file = tmp_path / f"{run_id}.json"
    trace_file.write_text(json.dumps({"run_id": "R-tv5-different-id", "events": []}), encoding="utf-8")
    
    result = {
        "run_id": run_id,
        "claim_id": "C-001",
        "status": "denied",
        "proposal_amount": 0,
        "refund_effects": [],
        "committed_audit_count": 0,
        "trace_path": str(trace_file),
    }
    valid, reason = check_trace(result, started_at=time.time())
    assert valid is False
    assert reason == "trace_run_id_mismatch"


def test_benchmark_metrics_summarize_calculation():
    """Verify summarize() correctly computes pass rate, pass^5, variance, and cost."""
    seeds = [11, 22, 33, 44, 55]
    trials = []
    
    # Simulate claim C-001: passes on all 5 seeds
    for s in seeds:
        trials.append({
            "shape": "workflow",
            "claim_id": "C-001",
            "seed": s,
            "passed": True,
            "cost_estimate": 0.0,
            "steps": 1,
            "model_calls": 0,
            "tool_calls": 1,
            "reason": "ok",
        })
        
    # Simulate claim C-002: fails on seed 55, passes on other 4 seeds
    for s in seeds:
        passed = (s != 55)
        trials.append({
            "shape": "workflow",
            "claim_id": "C-002",
            "seed": s,
            "passed": passed,
            "cost_estimate": 10.0,
            "steps": 2,
            "model_calls": 1,
            "tool_calls": 1,
            "reason": "ok" if passed else "status_mismatch",
        })
        
    summary = summarize(trials)
    assert "workflow" in summary
    wf_metrics = summary["workflow"]
    
    # 9 passes out of 10 trials -> pass_rate = 0.9
    assert wf_metrics["trials"] == 10
    assert wf_metrics["successes"] == 9
    assert pytest.approx(wf_metrics["pass_rate"]) == 0.9
    
    # C-001 passes all 5 seeds, C-002 only 4 seeds -> 1/2 claims pass^5 -> pass_5 = 0.5
    assert pytest.approx(wf_metrics["pass_5"]) == 0.5
    
    # Seed 55 has pass rate 1/2 = 0.5; others have 2/2 = 1.0 -> variance > 0
    assert wf_metrics["seed_variance"] > 0
    assert wf_metrics["seed_min"] == 0.5
    assert wf_metrics["seed_max"] == 1.0
    
    # Cost per success: total cost = 50.0 / 9 successes
    assert pytest.approx(wf_metrics["cost_per_success_vnd"]) == (50.0 / 9)

