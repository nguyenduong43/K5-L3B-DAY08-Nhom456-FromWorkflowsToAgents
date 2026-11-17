"""Unit test kiểm thử Shape A (Workflow)."""

from __future__ import annotations

import pytest
from lab8.shapes.workflow import run_claim
from tests.conftest import CLAIMS, WORLD
from lab8.db import init_store


def _make_store(tmp_path, name: str):
    path = tmp_path / name
    init_store(path, WORLD, CLAIMS).close()
    return path


def test_workflow_delay_refund_ok(tmp_path):
    """C-001: Đơn giao trễ 4 ngày -> Hoàn đúng 35,000 VND."""
    store = _make_store(tmp_path, "workflow-c001.sqlite")
    result = run_claim("C-001", seed=11, store_path=str(store))
    assert result.status == "resolved"
    assert result.proposal_amount == 35000
    assert len(result.refund_effects) == 1
    assert result.refund_effects[0]["amount_vnd"] == 35000


def test_workflow_missing_order_needs_info(tmp_path):
    """C-004: Thiếu order_id -> Trả về needs_info, không ghi ledger."""
    store = _make_store(tmp_path, "workflow-c004.sqlite")
    result = run_claim("C-004", seed=11, store_path=str(store))
    assert result.status == "needs_info"
    assert result.proposal_amount == 0
    assert len(result.refund_effects) == 0
