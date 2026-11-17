# Team

## Thông tin nhóm

- Tên nhóm: Nhom456
- Lớp: L3B
- Repo nhóm: `K5-L3B-DAY08-Nhom456-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt:
Repo:https://github.com/nguyenduong43/K5-L3B-DAY08-Nhom456-FromWorkflowsToAgents.git
Nhánh nộp:NguyenTungDuong
Commit chốt:feat(workflow): implement Shape A deterministic workflow and unit tests

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Nguyễn Tùng Dương | 2A202603850 | nguyenduong342003@gmail.com | nguyenduong43 | Leader / integration / workflow |
|   2 | Nguyễn Ngọc Vinh | 2A202603877 | 26ai.vinhnn2@vinuni.edu.vn| https://github.com/cuakicuc4444 | Phụ trách Shape B — Single Agent trong `src/lab8/shapes/single.py`: xây dựng vòng ReAct tối đa 8 bước, chỉ sử dụng read tools; phần tính quote do code thực hiện và thao tác ghi refund đi qua host. |
|   3 | Nguyễn Lâm Tùng | 2A202603854 | nlamtung.work@gmail.com | nlamtung | orchestrator / handoff |
|   4 |        |      |       |        |         |
|   5 |        |      |       |        |         |

Gợi ý chia vai:

- Nhóm 5 người: TV1 (Leader/Workflow), TV2 (Single ReAct), TV3 (Orchestrator/Handoff), TV4 (Durability/Crash/Security), TV5 (Benchmark/ADR).

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Nguyễn Tùng Dương | Leader / integration / workflow | feat(workflow) | src/tests/test_workflow.py::test_workflow_delay_refund_ok |
| Nguyễn Ngọc Vinh | Thành viên 2 / single agent | Chưa commit — điền hash sau khi commit | `src/tests/test_single.py::test_single_caps_react_at_eight_steps`; `src/tests/test_single.py::test_single_requests_information_when_order_id_is_missing` |
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
## 2A202603850_NguyenTungDuong

### Phần việc phụ trách

- Leader nhóm: Quản lý repo, phân công vai trò, thiết lập môi trường và điều phối tiến độ.
- Triển khai Shape A (Workflow): Cài đặt luồng deterministic workflow trong `src/lab8/shapes/workflow.py`.
- Viết test kiểm thử cho Shape A trong `src/tests/test_workflow.py`.
- Đồng tác giả báo cáo nhóm `report/team/group_report.md`.

### Đóng góp cụ thể

- Triển khai hoàn chỉnh Shape A pass 62/62 test student của đề bài.
- Đảm bảo ranh giới an toàn: Tiền do code tính bằng `compute_compensation`, model không can thiệp ghi ledger.
- Xử lý trần theo đơn bằng cách truyền quote đầy đủ vào `durability.issue_refund`, hỗ trợ `crash_at` an toàn cho khôi phục sau crash.
- Viết unit tests kiểm thử các nhánh rẽ nghiệp vụ: `test_workflow_delay_refund_ok` và `test_workflow_missing_order_needs_info`.

### Bằng chứng

- File mã nguồn: `src/lab8/shapes/workflow.py`
- File unit test: `src/tests/test_workflow.py`
- Báo cáo cá nhân chi tiết: `report/team/2A202603850_NguyenTungDuong.md`
- Kết quả test: `pytest -q -m student -o addopts= -k workflow` -> 62 passed in 0.32s
