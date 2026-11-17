# Báo cáo cá nhân — 2A202603850_NguyenTungDuong

## 1. Thông tin thành viên

- Họ tên: Nguyễn Tùng Dương
- MSSV: 2A202603850
- Email: nguyenduong342003@gmail.com
- GitHub: nguyenduong43
- Nhóm: Nhom456 (Lớp L3B)
- Vai trò: Leader / Integration / Shape A (Workflow)

## 2. Phần việc phụ trách

- **Leader nhóm Nhom456:** Khởi tạo repository, phân công vai trò nhiệm vụ cho 5 thành viên, thiết lập kế hoạch triển khai qua 5 Checkpoints và điều phối tiến độ.
- **Phụ trách Shape A (`src/lab8/shapes/workflow.py`):** Triển khai toàn bộ logic deterministic workflow tuần tự, an toàn, tuân thủ đúng luật nghiệp vụ LogiX-VN và Trace contract v1.
- **Tác giả Unit Test:** Viết bộ kiểm thử nghiệp vụ cho Workflow trong `src/tests/test_workflow.py`.
- **Báo cáo nhóm (`group_report.md`):** Đồng tác giả, phụ trách mục Tổng quan nhóm, Mục tiêu và Giải pháp Shape A.

## 3. Đóng góp cụ thể

- Cài đặt hàm `run_claim` trong `src/lab8/shapes/workflow.py`:
  - Đọc claim an toàn qua `get_claim_view` (lọc qua allowlist, không dùng `SELECT *`).
  - Kiểm tra `order_id`: Trả về `needs_info` nếu thiếu, không ghi ledger.
  - Kiểm tra quyền sở hữu và sự tồn tại của đơn hàng bằng `lookup_order`: Trả về `escalated` nếu không tìm thấy hoặc sai chủ đơn (không để lộ SĐT, địa chỉ, ghi chú nội bộ).
  - Tính tiền bồi thường bằng code với `compute_compensation` từ dữ liệu database, bỏ qua số ngày trễ ghi trong ticket khách hàng.
  - Xử lý Quote $\le 0$: Trả về `denied` mà không gọi Host `issue_refund`.
  - Xử lý Quote $> 0$: Gọi Host `durability.issue_refund` với **quote đầy đủ**, Host tự động khấu trừ phần đã hoàn trước đó (vượt qua test trần theo đơn T13, T14).
  - Hỗ trợ Crash Durability: Truyền tham số `crash_at` vào Host và không bắt lỗi `InjectedCrash` để đảm bảo kiểm thử crash phục hồi an toàn (vượt qua test T12).
  - Đóng gói kết quả bằng `lab8.shapes.common.finish()` để ghi trace chuẩn và lấy snapshot ledger tự động.
- Viết 2 unit tests trong `src/tests/test_workflow.py`:
  - `test_workflow_delay_refund_ok`: Đơn giao trễ 4 ngày (`C-001`) được hoàn đúng 35.000 VND.
  - `test_workflow_missing_order_needs_info`: Đơn thiếu `order_id` (`C-004`) trả về `needs_info`, không ghi ledger.

## 4. Bằng chứng

- File code chính: [src/lab8/shapes/workflow.py](file:///Users/minhanmacs/Documents/K5-L3B-DAY08-Nhom456-FromWorkflowsToAgents/src/lab8/shapes/workflow.py)
- File test cá nhân: [src/tests/test_workflow.py](file:///Users/minhanmacs/Documents/K5-L3B-DAY08-Nhom456-FromWorkflowsToAgents/src/tests/test_workflow.py)
- Kết quả kiểm thử thực nghiệm trên máy:
  - Test cá nhân: `tests/test_workflow.py` $\rightarrow$ **`2 passed in 0.02s`**
  - Toàn bộ 62 test student của Shape Workflow: `pytest -q -m student -o addopts= -k workflow` $\rightarrow$ **`62 passed in 0.32s`**
  - Cổng kiểm soát Host: `pytest -q` $\rightarrow$ **`56 passed in 0.29s`** (Xanh 100%)

## 5. Công cụ AI đã dùng

- **Công cụ:** Antigravity AI Assistant.
- **Mục đích sử dụng:**
  - Hỗ trợ phân tích tài liệu đặc tả nghiệp vụ ([docs/business_rules.md](file:///Users/minhanmacs/Documents/K5-L3B-DAY08-Nhom456-FromWorkflowsToAgents/docs/business_rules.md)) và Trace contract v1.
  - Xây dựng bản kế hoạch phân công công việc chi tiết cho 5 thành viên ([KE_HOACH_THUC_HIEN.md](file:///Users/minhanmacs/Documents/K5-L3B-DAY08-Nhom456-FromWorkflowsToAgents/KE_HOACH_THUC_HIEN.md)).
  - Gợi ý cấu trúc mã nguồn tối ưu cho Shape A theo đúng ranh giới Code/Model.
- **Cách tự kiểm tra kết quả:**
  - Tự rà soát logic code để đảm bảo tuyệt đối không để LLM quyết định số tiền hoàn hay gọi trực tiếp database.
  - Chạy thực tế toàn bộ test suite cục bộ trên máy qua lệnh `pytest` và kiểm tra tính hợp lệ bằng `check_submission`.

## 6. Tự đánh giá

- Hoàn thành đầy đủ và vượt tiến độ các mốc Checkpoint 1 & 2.
- Code sạch, chuẩn contract, pass 100% các bài test liên quan đến Shape Workflow.
- Đóng góp tích cực vào việc điều phối và định hướng cho cả nhóm.
- Mức độ hoàn thành: **Xuất sắc (10/10)**.
