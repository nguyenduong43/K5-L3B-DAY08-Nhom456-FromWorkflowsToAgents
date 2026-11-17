# Báo cáo nhóm — Lab 8 LogiX-VN

Tối đa 5 trang ngoài phụ lục. Số liệu lấy từ file trong `src/reports/`, không chép tay từ terminal.

## 1. Thông tin nhóm

- Tên nhóm:
- Thành viên: xem `TEAM.md`
- Commit chốt (trùng `report/team/decision_adr.md`):

## 2. Mục tiêu và cách tiếp cận

Nhóm hiểu bài toán thế nào, chia việc ra sao, thứ tự làm bốn shape.

...

## 3. Giải pháp

Mô tả ba shape nhóm viết (workflow, single, orchestrator): mỗi shape đọc gì, quyết định gì, gọi host ra sao. Chỉ rõ ranh giới code / model (tham khảo [docs/architecture.md](../../docs/architecture.md)), cách handoff được sanitize và trace ghi những event nào.

...

## 4. Kết quả

### Bảng so sánh 4 kiến trúc trên bộ Public (14 claims x 5 seeds = 70 trials/shape)
Dữ liệu trích xuất tự động từ `src/reports/benchmark.json`:

| Kiến trúc (Shape) | Pass rate | Pass^5 | Seed min–max | Variance | Chi phí / Success (VND) | Mean steps | p95 steps |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **A: Workflow** | **1.000** | **1.000** | 1.000 – 1.000 | **0.000000** | **27.86** | 3.79 | 4.0 |
| **B: Single ReAct** | **1.000** | **1.000** | 1.000 – 1.000 | **0.000000** | 30.39 | 11.36 | 12.0 |
| **C: Orchestrator** | **1.000** | **1.000** | 1.000 – 1.000 | **0.000000** | 47.85 | 2.86 | 3.0 |
| **D: Swarm Reference** | 0.986 | 0.929 | 0.929 – 1.000 | 0.000816 | 49.57 | 2.80 | 3.0 |

* **Độ an toàn khi Crash (`src/reports/crash.json`)**: Đạt tuyệt đối **20/20** (`crash_safety: "20/20"`).
* **Bảo mật & Phê duyệt**: `secret_leak_count = 0`, `approval_bypass_count = 0` trên toàn bộ các trials.
* **Nhận xét kết quả**: Shape A (Workflow) vượt trội ở cả chi phí rẻ nhất (27.86 VND), độ ổn định tuyệt đối (Variance = 0, Pass^5 = 1.000) và tính tất định. Swarm (Shape D) thất bại ở seed 55 trên test T02 do nhầm lẫn giữa dữ liệu ticket người dùng và cơ sở dữ liệu.

Quyết định kiến trúc và lý do: xem `report/team/decision_adr.md`. Phiếu nghiên cứu và ablation: xem `report/team/research_card.md`.

## 5. Khó khăn và cách xử lý

Lỗi gặp phải (kèm lệnh, output hoặc ảnh chụp) và cách nhóm xử lý.

...

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong `TEAM.md` (bảng đóng góp) và báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện

MockLLM không phải model sản xuất; latency là `unavailable`. Nêu thêm giới hạn của nhóm và điều kiện làm kết luận thay đổi.

...

## 8. Tài liệu tham khảo

...
