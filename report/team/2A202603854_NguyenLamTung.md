# Báo cáo cá nhân — 2A202603854_NguyenLamTung

## 1. Thông tin thành viên

- Họ tên: Nguyễn Lâm Tùng
- MSSV: 2A202603854
- Email: nlamtung.work@gmail.com
- GitHub: nlamtung

## 2. Phần việc phụ trách

- **Shape phụ trách:** Shape C — Orchestrator & Investigator (`src/lab8/shapes/orchestrator.py`).
- **Nhiệm vụ kiểm thử:** Xây dựng bộ test độc lập `src/tests/test_orchestrator_handoff.py` kiểm tra cơ chế Handoff sanitization, drop secrets/headers, chặn write tools đối với worker, và dừng sớm.
- **Ranh giới bảo mật:** Đảm bảo kiến trúc Orchestrator tuân thủ nghiêm ngặt ranh giới bảo mật Handoff (chỉ truyền các field allowlist qua `make_handoff`, không đưa `parent_secret` hay PII vào investigator hoặc trace).

## 3. Đóng góp cụ thể

1. **Cài đặt Shape C (`src/lab8/shapes/orchestrator.py`):**
   - Thiết kế mô hình điều phối 2 tầng: Orchestrator đóng vai trò trung tâm tiếp nhận yêu cầu, phân tích ticket và đóng gói thông tin sang Investigator chỉ đọc.
   - Sử dụng `lab8.handoff.make_handoff` để khởi tạo gói bàn giao dữ liệu với allowlist chặt chẽ: loại bỏ triệt để `parent_secret`, `raw_headers` và thông tin ngữ cảnh thô từ `claims`.
   - Cấp phát quyền tối thiểu cho Investigator qua danh sách `allowed_tools=["lookup_order", "lookup_policy", "compute_compensation"]`. Toàn bộ đều là read tools; Investigator không có quyền ghi hay truy cập sổ cái ledger.
   - Ủy quyền thực thi cho Investigator thông qua `lab8.runtime.run_readonly_investigators` với phạm vi principal được cô lập (`owner_order_only`).
   - Orchestrator tiếp nhận kết quả định giá từ investigator (`investigated["tools"]["compute_compensation"]`), kiểm tra tính hợp lệ và gọi Host qua `durability.issue_refund(conn, claim_id, proposal, crash_at=crash_at)`.
   - Xử lý dừng sớm: nếu claim thiếu `order_id` trả ngay `status="needs_info"` (proposal = 0); nếu đơn không thuộc sở hữu của khách trả `status="escalated"` và bảo vệ toàn bộ PII (SĐT, địa chỉ, tên hàng) khỏi trace.
   - Chuyển tiếp an toàn tham số `crash_at` vào `durability.issue_refund` và re-raise exception `InjectedCrash` để phục vụ bộ kiểm thử crash safety.
   - Tuân thủ quy tắc trần theo đơn (Order-level cap) và đảm bảo ghi nhận đầy đủ audit log `policy_denied` của Host khi quote > 0 bị từ chối.

2. **Xây dựng bộ Unit Test (`src/tests/test_orchestrator_handoff.py`):**
   - `test_handoff_drops_secrets_and_pii`: Kiểm tra `sanitize` loại bỏ hoàn toàn `parent_secret`, `raw_headers` và chỉ giữ lại các trường hợp lệ trong hợp đồng `handoff.v1`.
   - `test_investigator_cannot_call_write_tools`: Kiểm tra `make_handoff` ném `HandoffError` khi cố tình cấp write tool (`issue_refund`) cho worker.
   - `test_orchestrator_stops_on_missing_order_id`: Kiểm tra claim thiếu `order_id` (C-004) dừng sớm với `needs_info`, không ghi ledger.
   - `test_orchestrator_escalated_and_no_pii_in_trace`: Kiểm tra claim truy cập đơn trái phép (C-005) trả `escalated` và trace không rò rỉ secret hoặc PII.
   - `test_investigator_dispatcher_blocks_unauthorized_tool`: Kiểm tra dispatch chặn lệnh gọi write tools khi `worker=True`.

## 4. Bằng chứng

- **Test passed:**
  - `src/tests/test_orchestrator_handoff.py`: 5/5 passed.
  - Ma trận test student (`python -m pytest -q -m student -o addopts= -k orchestrator`): 62/62 passed (100%).
  - Cổng Host (`python -m pytest -q`): 59 passed, 0 failed.
- **Check submission:**
  - `python -m lab8.check_submission` xác nhận:
    ```text
    == shapes ==
    [ OK ] shape orchestrator: format đúng, 12/12 claim public pass ở seed 11
    ```
- **Commit hash & test reference:**
  - Ghi nhận tại `TEAM.md`: `src/tests/test_orchestrator_handoff.py::test_handoff_drops_secrets_and_pii`.

## 5. Công cụ AI đã dùng

- **Công cụ:** Antigravity Assistant (Google DeepMind).
- **Mục đích sử dụng:**
  - Hỗ trợ phân tích kiến trúc Orchestrator-Investigator và các yêu cầu về hợp đồng Handoff v1 trong [contracts.md](../../docs/contracts.md).
  - Hỗ trợ xây dựng các test case kiểm tra việc bảo mật Handoff và cô lập quyền của Investigator.
- **Cách tự kiểm tra kết quả:**
  - Chạy toàn bộ các bộ test tự động qua `pytest` (host test, unit test, student matrix cho orchestrator).
  - Kiểm tra nội dung file trace trong `src/traces/` để đảm bảo event `handoff` đã được sanitize và không lộ token canary hay PII.
  - Chạy script kiểm tra nộp bài `python -m lab8.check_submission`.

## 6. Tự đánh giá

- **Mức độ hoàn thành:** 100% nhiệm vụ được giao cho Shape C (Orchestrator Dev & Handoff).
- **Tuân thủ quy tắc:** Đảm bảo tuyệt đối 3 tiêu chí Must-Pass (không bypass approval, không lộ secret/PII qua handoff/trace, an toàn khi crash).
- **Chất lượng code:** Kiến trúc phân tầng rõ ràng, đảm bảo nguyên tắc bảo mật *least privilege*, code sạch và format chuẩn.
