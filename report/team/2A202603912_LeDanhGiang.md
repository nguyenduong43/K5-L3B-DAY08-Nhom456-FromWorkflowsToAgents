# Báo cáo cá nhân — 2A202603912_LeDanhGiang

## 1. Thông tin thành viên

- Họ tên: Lê Danh Giang
- MSSV: 2A202603912
- Email: 26ai.giangld@vinuni.edu.vn
- GitHub: https://github.com/giangj

## 2. Phần việc phụ trách

- **Vai trò:** Thành viên 4 (TV4) — Durability, Crash Safety & Bảo mật (CP3, CP4).
- **Phạm vi công việc:**
  - Thiết lập và kiểm định cơ chế idempotency (`refund:{claim_id}`), xử lý lỗi khi crash giữa transaction và checkpoint (`crash_at` + không nuốt `InjectedCrash`).
  - Nghiệm thu bộ kiểm thử 20 điểm crash (`src/reports/crash.json` đạt `20/20`).
  - Kiểm tra cổng duyệt (`approval_claim_mismatch`, `approval_revoked`, `approval_expired`, `missing_approval`), trần hoàn tiền theo đơn (T13, T14), và bảo mật trace (`CANARY_SECRET_*`, PII).
  - Viết bộ kiểm thử `src/tests/test_tv4_durability.py`.
  - Đóng góp phần Durability, Crash Safety & Bảo mật trong `report/team/group_report.md` và cập nhật `TEAM.md`.

## 3. Đóng góp cụ thể

- **Nhánh làm việc:** `LeDanhGiang-03912` (tách từ `main`).
- **Commit kỹ thuật chính:** `4a5f381` (`test(durability): add TV4 durability/security suite and 20/20 crash report`).
- **File test đã thêm:** `src/tests/test_tv4_durability.py` gồm 10 test kiểm định trực tiếp tầng host/durability/policy/swarm (chạy mặc định trong `pytest -q`) và 18 test `@pytest.mark.student` phủ cả 3 shape (`workflow`, `single`, `orchestrator`) cho T11, 3 điểm crash T12, `approval_claim_mismatch` và trần theo đơn T13/T14:
  - `test_idempotency_same_claim`: gọi lại cùng `claim_id` vẫn chỉ có 1 dòng `refund_ledger`, 1 audit `refund_committed`, có checkpoint và trả `idempotent_replay`.
  - `test_idempotency_amount_conflict_preserves_committed_row`: gọi lại với số tiền khác trả `conflict=True` (`amount_conflict`), ghi audit xung đột và giữ nguyên số tiền cũ.
  - `test_all_crash_points_recover_without_duplicate_refund`: kiểm tra cả 3 điểm crash (`before_effect`, `after_effect_before_checkpoint`, `after_checkpoint`), đảm bảo `InjectedCrash` được ném đúng lúc và resume cho ra đúng 1 refund + 1 audit + checkpoint.
  - `test_approval_mismatch_revoked_expired_and_missing_record_policy_denied`: kiểm tra `approval_claim_mismatch`, `approval_revoked`, `approval_expired` (`C-007`), `missing_approval` đều bị chặn và ghi audit `policy_denied`.
  - `test_order_cap_blocks_t13_and_pays_difference_on_t14`: kiểm tra quy tắc truyền full quote để host trừ phần đã hoàn của đơn (T13 trả `order_already_refunded` + `policy_denied`; T14 chỉ trả phần chênh 120.000 VND).
  - `test_swarm_crash_resume_and_trace_leak_safety`: kiểm tra crash/resume trên `swarm_reference` ở cả 3 điểm crash, đồng thời quét `artifact_blob` không lộ `CANARY_SECRET_`, header, SĐT, địa chỉ hay ghi chú nội bộ.
  - Nhóm test `@pytest.mark.student`: `test_shapes_t11_idempotency_single_refund`, `test_shapes_t12_crash_points_propagate_and_resume_safely`, `test_shapes_reject_approval_claim_mismatch_and_audit_policy_denied`, `test_shapes_respect_order_cap_t13_and_t14` (sẵn sàng chạy kiểm chứng ngay khi nhóm gộp 3 shape vào `main`).
- **Rà soát code các nhánh thành viên trước khi gộp `main`:**
  - Xác nhận nhánh `origin/NguyenTungDuong` (`workflow.py`) và `origin/TungNL` (`orchestrator.py`) đã truyền `crash_at` và re-raise `InjectedCrash` đúng quy định.
  - Phát hiện nhánh `origin/NguyenNgocVinh` (`single.py`) vẫn còn `# TODO CP3 (student)` / `del crash_at` chưa truyền `crash_at` vào `issue_refund` (cần bổ sung khi gộp nhánh để T12 không fail `"crash did not fire"`) và đã xóa nhầm file mẫu `report/team/MSSV_HoTen.md`.

## 4. Bằng chứng

- **Commit hash:** `4a5f381` (trên nhánh `LeDanhGiang-03912`).
- **File báo cáo crash sinh bằng công cụ:** `src/reports/crash.json` (`"count": 20, "passed": 20, "crash_safety": "20/20"`).
- **Lệnh kiểm chứng đã chạy trong `src/`:**
  - `python -m lab8.smoke` → `lab8.smoke pass` (`Python 3.11.9 | Windows AMD64 | manifest 1.1 | MockLLM seeded | swarm C-001 refund 35000 | trace clean`).
  - `python -m lab8.demo.buggy_workflow` → `unsafe refund rows: 2 (the host ledger must stay at 1)`.
  - `python -m pytest -q` → `64 passed, 266 deselected in 14.10s`.
  - `python -m pytest -v tests/test_tv4_durability.py` → `10 passed, 18 deselected in 1.31s`.
  - `python -m lab8.crash_test --count 20 --out reports/crash.json` → `crash_safety 20/20`.

## 5. Công cụ AI đã dùng

- **Công cụ sử dụng:** Trợ lý lập trình AI (Antigravity / Gemini) để hỗ trợ đọc hiểu toàn bộ codebase (`durability.py`, `policy.py`, `metrics.py`, `crash_test.py`, `check_submission.py`), thiết kế bộ test `src/tests/test_tv4_durability.py`, rà soát sự khác biệt giữa các nhánh thành viên và trình bày báo cáo.
- **Cách tự kiểm tra kết quả:**
  - Đọc đối chiếu trực tiếp mã nguồn `src/lab8/durability.py`, `src/lab8/policy.py`, `src/lab8/tools.py`, `src/lab8/metrics.py` và các luật trong `docs/business_rules.md`, `docs/contracts.md`.
  - Tự thiết lập môi trường `.venv` (Python 3.11.9) và chạy toàn bộ lệnh kiểm thử (`lab8.smoke`, `lab8.demo.buggy_workflow`, `pytest -q`, `pytest -v tests/test_tv4_durability.py`, `lab8.crash_test`, `lab8.check_submission`), kiểm tra trực tiếp nội dung `src/reports/crash.json` và không chỉnh sửa tay các file thước đo hay JSON báo cáo.

## 6. Tự đánh giá

- Hoàn thành đầy đủ các hạng mục độc lập của TV4 trên nhánh `LeDanhGiang-03912`: cổng host xanh (`64 passed`), suite crash đạt `20/20` (`src/reports/crash.json`), có bộ test riêng cho idempotency, 3 điểm crash, approval mismatch, order cap và trace leak safety.
- Phần test `@pytest.mark.student` trên 3 shape đã được chuẩn bị sẵn trong `src/tests/test_tv4_durability.py`; bước tiếp theo khi cả nhóm gộp code từ các nhánh vào `main` là rà lại nhánh `single.py` (gắn `crash_at`) và chạy `python -m pytest -q -m student -o addopts=` cùng `python -m lab8.check_submission` để đạt `0 FAIL` trên toàn repo nhóm.
