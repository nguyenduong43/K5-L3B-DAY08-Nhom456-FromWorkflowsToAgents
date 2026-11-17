# Báo cáo cá nhân — MSSV_HoTen

Đổi tên file theo quy tắc `MSSV_HoTen.md`.

Ví dụ: `2A202603877_NguyenNgocVinh.md`.

## 1. Thông tin thành viên

- Họ tên: Nguyễn Ngọc Vinh
- MSSV: 2A202603877
- Email: 26ai.vinhnn2@vinuni.edu.vn
- GitHub: https://github.com/cuakicuc4444

## 2. Phần việc phụ trách

Phụ trách Shape B — Single Agent trong `src/lab8/shapes/single.py`: xây dựng vòng ReAct tối đa 8 bước, chỉ sử dụng read tools; phần tính quote do code thực hiện và thao tác ghi refund đi qua host.

## 3. Đóng góp cụ thể

- Thay stub của `single.run_claim` bằng luồng ReAct có giới hạn 8 bước.
- Xử lý các nhánh claim không tồn tại, thiếu `order_id`, đơn không hiển thị và quote bằng 0.
- Gửi quote đầy đủ đến `durability.issue_refund`; không để model gọi công cụ ghi hoặc tự quyết định số tiền.
- Ghi trace theo run, chỉ đưa vào trace các dữ kiện cần thiết, không ghi ticket thô.
- Thêm `src/tests/test_single.py` với hai test: giới hạn ReAct và xử lý claim thiếu `order_id`.
- Commit chính: chưa có; bổ sung hash sau khi commit.
- Phần CP3 truyền `crash_at` chưa nằm trong phần bàn giao này; theo phân công, TV4 tiếp tục xử lý.

## 4. Bằng chứng

- Chạy `python -m pytest -q tests\test_single.py`: **2 passed in 0.37s**.
- Hai test đã thêm:
  - `test_single_caps_react_at_eight_steps`
  - `test_single_requests_information_when_order_id_is_missing`
- Trong log chạy student matrix, không thấy lỗi ở các ca public thông thường của shape `single`. T12 của `single` còn fail vì chưa nối `crash_at` vào host; đây là phần CP3 được giao cho TV4.
- Các lỗi workflow/orchestrator trong cùng log do hai shape đó vẫn còn stub, không thuộc phần việc của mình.

## 5. Công cụ AI đã dùng

Đã dùng trợ lý AI trong VS Code để hiểu yêu cầu của Shape B, triển khai `single.run_claim`, bổ sung test và đọc log kiểm thử. Tự kiểm tra bằng cách chạy hai test của bản thân; kết quả là 2 test pass. Pylance cũng không báo lỗi cú pháp hoặc diagnostic trên hai file đã sửa.

## 6. Tự đánh giá

Đã hoàn thành phần Shape B và hai test riêng theo phân công CP2. Kết quả kiểm thử mục tiêu đạt yêu cầu. Phần crash-resume T12 cần được hoàn tất ở CP3 khi TV4 truyền `crash_at` vào `durability.issue_refund` và kiểm tra lại crash suite.
