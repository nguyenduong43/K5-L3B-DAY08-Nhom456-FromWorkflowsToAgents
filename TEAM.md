# Team

## Thông tin nhóm

- Tên nhóm:
- Lớp: L3A
- Repo nhóm: `K5-L3A-DAY08-TenNhom-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt:

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 |        |      |       |        |         |
|   2 |        |      |       |        |         |
|   3 | Nguyễn Lâm Tùng | 2A202603854 | nlamtung.work@gmail.com | nlamtung | orchestrator / handoff |
Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Nguyễn Lâm Tùng | orchestrator / handoff | 97ea1a0 | src/tests/test_orchestrator_handoff.py::test_handoff_drops_secrets_and_pii |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## 2A202603854_NguyenLamTung

### Phần việc phụ trách

- Cài đặt Shape C — Orchestrator & Investigator (`src/lab8/shapes/orchestrator.py`).
- Viết bộ kiểm thử độc lập cho Orchestrator & Handoff (`src/tests/test_orchestrator_handoff.py`).
- Đảm bảo ranh giới bảo mật Handoff Sanitization (`make_handoff`): chỉ chuyển field allowlist, không lộ parent secret hay PII.

### Đóng góp cụ thể

- Cài đặt mô hình điều phối 2 tầng (Orchestrator + Read-only Investigator): Orchestrator nhận claim, đóng gói handoff và ủy quyền tra cứu cho Investigator qua `run_readonly_investigators`.
- Đảm bảo an toàn Handoff qua `lab8.handoff.make_handoff`: loại bỏ hoàn toàn `parent_secret`, `raw_headers` và chỉ cấp các read tools (`lookup_order`, `lookup_policy`, `compute_compensation`).
- Đảm bảo tiền bồi thường tính bằng hàm chuẩn `compute_compensation`, Orchestrator gọi Host `durability.issue_refund` để ghi ledger. Investigator không có quyền ghi.
- Xử lý dừng sớm (`needs_info`, `escalated`) và bảo vệ dữ liệu PII/secret trong trace.
- Chuyển tiếp an toàn `crash_at` vào `durability.issue_refund`, không nuốt exception `InjectedCrash`.
- Viết 5 unit tests độc lập kiểm tra sanitization, chặn write tools, dừng sớm, chống leak PII và ủy quyền an toàn.

### Bằng chứng

- File test: `src/tests/test_orchestrator_handoff.py::test_handoff_drops_secrets_and_pii` (5/5 passed).
- Ma trận test student: 62/62 tests của `orchestrator` passed 100%.
- Kiểm tra submission: `[ OK ] shape orchestrator: format đúng, 12/12 claim public pass ở seed 11`.
