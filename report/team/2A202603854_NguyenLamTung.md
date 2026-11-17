# Báo cáo cá nhân — 2A202603854_NguyenLamTung

## 1. Thông tin thành viên

- Họ tên: Nguyễn Lâm Tùng
- MSSV: 2A202603854
- Email: nlamtung.work@gmail.com
- GitHub: nlamtung

## 2. Phần việc phụ trách

- **Shape phụ trách:** Shape B — Single ReAct Agent (`src/lab8/shapes/single.py`).
- **Nhiệm vụ kiểm thử:** Xây dựng bộ test độc lập `src/tests/test_single_agent.py` kiểm tra giới hạn bước, ranh giới an toàn, dừng sớm và chặn write tools.
- **Ranh giới bảo mật:** Đảm bảo kiến trúc Single Agent tuân thủ ranh giới Code / Model (Code tính tiền qua `compute_compensation`, Host ghi ledger qua `durability.issue_refund`, Model chỉ gọi Read Tools).

## 3. Đóng góp cụ thể

1. **Cài đặt Shape B (`src/lab8/shapes/single.py`):**
   - Sử dụng `lab8.runtime.run_react` với tham số `max_steps=8` và cờ `worker=True` để ngăn chặn Model gọi các write tools.
   - Thiết kế hàm `decide(seen)` tương tác với `MockLLM` để quyết định công cụ đọc: bước 1 gọi `lookup_order`, bước 2 gọi `compute_compensation`.
   - Tiền hoàn cước được tính toán xác định bằng hàm nghiệp vụ `compute_compensation`, tuyệt đối không để Model tự biên tự diễn hay ghi số tiền.
   - Xử lý dừng sớm: nếu thiếu `order_id` trả ngay `status="needs_info"` (proposal = 0); nếu đơn không thuộc sở hữu của principal trả `status="escalated"` và loại trừ toàn bộ PII (SĐT, địa chỉ, tên hàng) khỏi trace.
   - Tuân thủ quy tắc trần theo đơn (Order-level cap): truyền quote đầy đủ vào `durability.issue_refund` để Host tự tính và khấu trừ phần đã hoàn; ghi nhận đầy đủ audit event `policy_denied` của Host khi quote > 0 bị từ chối.
   - Chuyển tiếp an toàn tham số `crash_at` vào `durability.issue_refund` và re-raise exception `InjectedCrash` (không dùng `try...except` để nuốt lỗi).

2. **Xây dựng bộ Unit Test (`src/tests/test_single_agent.py`):**
   - `test_react_step_limit_enforced`: Kiểm tra vòng lặp ReAct dừng đúng khi chạm trần 8 bước (`step_cap`).
   - `test_single_stops_early_on_missing_order_id`: Kiểm tra claim thiếu `order_id` (C-004) dừng sớm với `needs_info`, không ghi ledger.
   - `test_single_escalated_and_no_pii_leak`: Kiểm tra claim truy cập đơn trái phép (C-005) trả `escalated` và trace không rò rỉ secret hoặc PII.
   - `test_single_worker_cannot_call_write_tools`: Kiểm tra dispatch chặn lệnh gọi write tools (`issue_refund`) khi `worker=True`.

## 4. Bằng chứng

- **Test passed:**
  - `src/tests/test_single_agent.py`: 4/4 passed.
  - Ma trận student (`python -m pytest -q -m student -o addopts= -k single`): 62/62 passed (100%).
  - Cổng Host (`python -m pytest -q`): 58 passed, 0 failed.
- **Check submission:**
  - `python -m lab8.check_submission` xác nhận:
    ```text
    == shapes ==
    [ OK ] shape single: format đúng, 12/12 claim public pass ở seed 11
    ```
- **Commit hash & test reference:**
  - Ghi nhận tại `TEAM.md`: `src/tests/test_single_agent.py::test_react_step_limit_enforced`.

## 5. Công cụ AI đã dùng

- **Công cụ:** Antigravity Assistant (Google DeepMind).
- **Mục đích sử dụng:**
  - Hỗ trợ phân tích, tổng hợp yêu cầu kỹ thuật từ các tài liệu gốc (`README.md`, `RUBRIC.md`, `RULES.md`, `contracts.md`, `business_rules.md`).
  - Gợi ý cấu trúc điều phối vòng lặp ReAct trong `decide(seen)` và xây dựng các trường hợp biên cho bộ unit test.
- **Cách tự kiểm tra kết quả:**
  - Chạy toàn bộ các bộ test tự động qua `pytest` (host test, unit test, student matrix).
  - Soát xét thủ công file JSON trace sinh ra tại `src/traces/` để xác nhận không chứa chuỗi `CANARY_SECRET_*`, số điện thoại hay địa chỉ khách hàng.
  - Chạy script kiểm tra nộp bài `python -m lab8.check_submission`.

## 6. Tự đánh giá

- **Mức độ hoàn thành:** 100% nhiệm vụ được giao cho Shape B (Single Agent).
- **Tuân thủ quy tắc:** Đảm bảo tuyệt đối 3 tiêu chí Must-Pass (không bypass approval, không lộ secret, an toàn khi crash).
- **Chất lượng code:** Mã nguồn rõ ràng, có type hint, docstring đầy đủ, format chuẩn theo hợp đồng đề bài.
