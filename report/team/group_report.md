# Báo cáo nhóm — Lab 8 LogiX-VN

Tối đa 5 trang ngoài phụ lục. Số liệu lấy từ file trong `src/reports/`, không chép tay từ terminal.

## 1. Thông tin nhóm

- Tên nhóm: Nhom456 (Lớp L3B)
- Thành viên: xem `TEAM.md`
- Commit chốt (trùng `report/team/decision_adr.md`): (điền sau khi nhóm gộp nhánh và chạy benchmark cuối)

## 2. Mục tiêu và cách tiếp cận

Nhóm hiểu bài toán thế nào, chia việc ra sao, thứ tự làm bốn shape.

...

## 3. Giải pháp

Mô tả ba shape nhóm viết (workflow, single, orchestrator): mỗi shape đọc gì, quyết định gì, gọi host ra sao. Chỉ rõ ranh giới code / model (tham khảo [docs/architecture.md](../../docs/architecture.md)), cách handoff được sanitize và trace ghi những event nào.

### Durability, Crash Safety & Bảo mật (TV4 — Lê Danh Giang)

- **Ghi nhận tiền qua cổng Host duy nhất (`durability.issue_refund`):** Các shape không tự ghi SQLite mà truyền **quote đầy đủ** từ `compute_compensation` vào `durability.issue_refund(..., crash_at=crash_at)`. Host kiểm tra ownership theo `principal_id`, đối chiếu approval của đúng claim (`claims.approval_id -> approvals.claim_id`), kiểm tra hiệu lực/trạng thái approval, và đọc lại tổng đã hoàn của đơn trong transaction `BEGIN IMMEDIATE` trước khi ghi đồng thời `refund_ledger` (idempotency key `refund:{claim_id}`) và audit `refund_committed`.
- **Chịu lỗi khi crash & chạy lại:** Checkpoint (`checkpoints`) được ghi sau bước commit ledger; do đó nếu xảy ra `InjectedCrash` tại `before_effect`, `after_effect_before_checkpoint` hay `after_checkpoint`, shape không được nuốt exception `InjectedCrash` (chỉ có thể ghi event `crash` vào trace rồi re-raise và đóng connection SQLite trong `finally`). Khi gọi lại (retry/resume), `issue_refund` nhận diện dòng đã commit trong `refund_ledger` để trả `idempotent_replay` (hoặc `amount_conflict` nếu đổi số tiền), đảm bảo tối đa 1 refund cho mỗi claim.
- **Trần theo đơn & Audit `policy_denied`:** Khi `quote > 0` nhưng bị chặn bởi approval lỗi/sai claim hoặc đơn đã hoàn đủ (`C-013`), shape vẫn phải gọi `issue_refund` để host ghi audit `policy_denied`. Khi đơn đã hoàn trước một phần (`C-014`), host tự khấu trừ và chỉ ghi phần chênh (`120.000` VND) trong khi `proposal_amount` giữ nguyên full quote (`150.000` VND).
- **Ranh giới bảo mật Trace & PII:** Mọi nhánh trả về (kể cả `needs_info`, `escalated`) đều ghi trace hợp lệ theo Trace contract v1 qua `common.finish()`, chỉ đọc claim/order qua `get_claim_view` và `lookup_order` để không làm lộ `CANARY_SECRET_*`, `raw_headers`, SĐT, địa chỉ, tên hàng hay ghi chú nội bộ ra file trace hay `stdout`.

## 4. Kết quả

Bảng so sánh 4 shape trên bộ public (từ `src/reports/benchmark.json`): pass rate, pass^5, seed min–max, variance, cost/success, mean/p95 steps. Kèm crash safety (`src/reports/crash.json`) và, nếu có, kết quả tự kiểm trên `student_drop/`.

- **Kết quả Crash Suite (`src/reports/crash.json`):** Đạt **`20/20`** (`crash_safety = "20/20"`) trên tất cả 17 điểm tiêm lỗi (`before_effect` x5, `after_effect_before_checkpoint` x7, `after_checkpoint` x5), kịch bản `amount_conflict_on_retry` (CR-18), `retry_without_approval` (CR-19) và `swarm_after_effect_before_checkpoint` (CR-20).
- **Kiểm thử Durability & Security (`src/tests/test_tv4_durability.py`):** Cổng host đạt `64 passed` (gồm 10 test tầng host/policy/swarm trong `test_tv4_durability.py` xác nhận idempotency, 3 điểm crash & resume, `approval_claim_mismatch`, `approval_revoked`, trần theo đơn T13/T14 và không rò rỉ canary secret/PII). 18 test `@pytest.mark.student` bổ sung sẵn sàng chạy nghiệm thu cả 3 shape (`workflow`, `single`, `orchestrator`) sau khi nhóm gộp nhánh vào `main`.

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
