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
|   3 | Nguyễn Lâm Tùng | 2A202603854 | nlamtung.work@gmail.com | nlamtung | single agent |
Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Nguyễn Lâm Tùng | single agent | 034c6c4 | src/tests/test_single_agent.py::test_react_step_limit_enforced |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## 2A202603854_NguyenLamTung

### Phần việc phụ trách

- Cài đặt Shape B — Single ReAct Agent (`src/lab8/shapes/single.py`).
- Viết bộ kiểm thử độc lập cho Single Agent (`src/tests/test_single_agent.py`).
- Đảm bảo ranh giới bảo mật Code / Model: model chỉ gọi read tools, code tính tiền và host ghi ledger.

### Đóng góp cụ thể

- Cài đặt vòng lặp ReAct giới hạn tối đa 8 bước (`max_steps=8, worker=True`) qua `run_react`.
- Tách biệt ranh giới tính tiền bằng hàm chuẩn `compute_compensation`, model chỉ đóng vai trò think / draft.
- Xử lý các điều kiện dừng sớm (`needs_info`, `escalated`) và bảo vệ dữ liệu PII/secret trong trace.
- Chuyển tiếp an toàn `crash_at` vào `durability.issue_refund`, không nuốt exception `InjectedCrash`.
- Viết 4 test case độc lập kiểm thử giới hạn bước lặp, dừng sớm, chống leak PII và chặn lệnh ghi tiền.

### Bằng chứng

- File test: `src/tests/test_single_agent.py::test_react_step_limit_enforced` (4/4 passed).
- Ma trận test student: 62/62 tests của `single` passed 100%.
- Kiểm tra submission: `[ OK ] shape single: format đúng, 12/12 claim public pass ở seed 11`.
