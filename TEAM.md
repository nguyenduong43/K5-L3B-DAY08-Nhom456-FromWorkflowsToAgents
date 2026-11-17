# Team

## Thông tin nhóm

- Tên nhóm: Nhom456
- Lớp: L3B
- Repo nhóm: `K5-L3B-DAY08-Nhom456-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt: https://github.com/nguyenduong43/K5-L3B-DAY08-Nhom456-FromWorkflowsToAgents (nhánh cá nhân TV4: `LeDanhGiang-03912`)

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 |        |      |       |        | integration / workflow |
|   2 |        |      |       |        | single agent |
|   3 |        |      |       |        | orchestrator / handoff |
|   4 | Lê Danh Giang | 2A202603912 | 26ai.giangld@vinuni.edu.vn | https://github.com/giangj | durability / crash |
|   5 |        |      |       |        | evaluation / benchmark |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Lê Danh Giang | durability / crash | 4a5f381 | src/tests/test_tv4_durability.py::test_idempotency_same_claim; src/tests/test_tv4_durability.py::test_all_crash_points_recover_without_duplicate_refund; src/tests/test_tv4_durability.py::test_approval_mismatch_revoked_expired_and_missing_record_policy_denied; src/tests/test_tv4_durability.py::test_order_cap_blocks_t13_and_pays_difference_on_t14 |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## MSSV_HoTen

### Phần việc phụ trách

-

### Đóng góp cụ thể

-

### Bằng chứng

-

## 2A202603912_LeDanhGiang

### Phần việc phụ trách

- Thành viên 4 (TV4) — Durability, Crash Safety & Bảo mật (CP3, CP4).
- Nghiệm thu bộ crash suite `src/reports/crash.json` (`20/20`).
- Viết bộ test kiểm định idempotency, crash/resume, approval binding, trần theo đơn và bảo mật trace trong `src/tests/test_tv4_durability.py`.
- Viết mục Durability, Crash Safety & Bảo mật trong `report/team/group_report.md` và báo cáo cá nhân `report/team/2A202603912_LeDanhGiang.md`.

### Đóng góp cụ thể

- Commit kỹ thuật `4a5f381`: thêm `src/tests/test_tv4_durability.py` (10 test tầng host/durability/policy/swarm + 18 test `@pytest.mark.student` cho cả 3 shape `workflow`, `single`, `orchestrator`) và `src/reports/crash.json` (`20/20`).
- Rà soát code nhánh các thành viên trước khi merge `main`: xác nhận `workflow.py` và `orchestrator.py` đã truyền `crash_at`; ghi chú để nhóm bổ sung `crash_at` cho `single.py` trên nhánh `NguyenNgocVinh` và khôi phục `report/team/MSSV_HoTen.md` khi merge.

### Bằng chứng

- Commit hash: `4a5f381`
- File test: `src/tests/test_tv4_durability.py` (`10 passed` cổng host, `64 passed` toàn bộ `pytest -q`)
- Báo cáo crash: `src/reports/crash.json` (`crash_safety = "20/20"`)
- Báo cáo cá nhân: `report/team/2A202603912_LeDanhGiang.md`
