# Báo cáo cá nhân — 2A202603912_LeDanhGiang

## 1. Thông tin thành viên

- Họ tên: Lê Danh Giang
- MSSV: 2A202603912
- Email: 26ai.giangld@vinuni.edu.vn
- GitHub: https://github.com/giangj

## 2. Phần việc phụ trách

- **Vai trò:** Thành viên 4 (TV4) — Durability, Crash Safety & Bảo mật (CP3, CP4).
- **Phạm vi công việc:**
  - Rà soát và hoàn thiện tích hợp `crash_at` / `InjectedCrash` (CP3) trên 3 shape (`workflow.py`, `single.py`, `orchestrator.py`).
  - Thiết lập và kiểm định cơ chế idempotency (`refund:{claim_id}`), xử lý lỗi khi crash giữa transaction và checkpoint.
  - Nghiệm thu bộ kiểm thử 20 điểm crash (`src/reports/crash.json` đạt `20/20`).
  - Kiểm tra cổng duyệt (`approval_claim_mismatch`, `approval_revoked`, `approval_expired`, `missing_approval`), trần hoàn tiền theo đơn (T13, T14), và bảo mật trace (`CANARY_SECRET_*`, PII).
  - Viết bộ kiểm thử `src/tests/test_tv4_durability.py`.
  - Đóng góp phần Durability, Crash Safety & Bảo mật trong `report/team/group_report.md` và cập nhật `TEAM.md`.

## 3. Đóng góp cụ thể

- **Nhánh làm việc:** `LeDanhGiang-03912` (đã cập nhật và đồng bộ với `origin/main` qua merge commit `b3977b1`).
- **Các commit kỹ thuật chính:**
  - `4a5f381` — `test(durability): add TV4 durability/security suite and 20/20 crash report`:
    - Thêm `src/reports/crash.json` đạt `20/20`.
    - Thêm `src/tests/test_tv4_durability.py` gồm 10 test tầng host/durability/policy/swarm (`pytest -q`) và 18 test `@pytest.mark.student` phủ cả 3 shape (`workflow`, `single`, `orchestrator`) cho T11, 3 điểm crash T12 (`before_effect`, `after_effect_before_checkpoint`, `after_checkpoint`), `approval_claim_mismatch` và trần theo đơn T13/T14.
  - `638b24c` — `fix(single): wire crash_at and propagate InjectedCrash for CP3`:
    - Khi rà soát `origin/main`, phát hiện `src/lab8/shapes/single.py` vẫn còn `# TODO CP3 (student)` / `del crash_at` khiến T12 và 3 điểm crash trên `single` bị fail (`DID NOT RAISE InjectedCrash` — 4 failed trên tổng 266 test).
    - Đã sửa `src/lab8/shapes/single.py` để truyền `crash_at=crash_at` vào `issue_refund`, ghi event `crash` vào trace khi gặp `InjectedCrash` và `raise` lại đúng chuẩn như `workflow.py` và `orchestrator.py`.
- **Kiểm tra bảo mật & nghiệp vụ trên cả 3 shape:**
  - Xác nhận cả `workflow`, `single`, `orchestrator` đều tính tiền bằng code (`compute_compensation`), truyền full quote vào `durability.issue_refund`, để host ghi audit `policy_denied` khi approval lỗi/sai claim hoặc đơn đã hoàn đủ, và không làm lộ `CANARY_SECRET_*`, `raw_headers` hay PII (SĐT, địa chỉ, tên hàng, ghi chú nội bộ) trong trace.

## 4. Bằng chứng

- **Commit kỹ thuật:** `4a5f381`, `638b24c` (trên nhánh `LeDanhGiang-03912`).
- **File báo cáo crash sinh bằng công cụ:** `src/reports/crash.json` (`"count": 20, "passed": 20, "crash_safety": "20/20"`).
- **Kết quả chạy kiểm thử trong `src/`:**
  - `python -m lab8.smoke` → `lab8.smoke pass` (`Python 3.11.9 | Windows AMD64 | manifest 1.1 | MockLLM seeded | swarm C-001 refund 35000 | trace clean`).
  - `python -m pytest -q` → **`73 passed, 266 deselected`** (xanh 100% cổng host + unit test của TV1, TV2, TV3, TV4).
  - `python -m pytest -q -m student -o addopts=` → **`266 passed, 73 deselected`** (xanh 100% ma trận T01–T14 trên cả 4 shape + toàn bộ 18 test shape của TV4 cho `workflow`, `single`, `orchestrator`).
  - `python -m lab8.crash_test --count 20 --out reports/crash.json` → **`crash_safety 20/20`**.
  - `python -m lab8.check_submission` → cả 3 shape (`workflow`, `single`, `orchestrator`) đều `[ OK ]` (12/12 claim public ở seed 11), `[ OK ] reports/crash.json: 20/20`, `[ OK ] TEAM.md: bảng đóng góp có 4 thành viên` (chỉ còn 9 FAIL thuộc phần CP5 của TV5 chưa chạy benchmark/ADR).

## 5. Công cụ AI đã dùng

- **Công cụ sử dụng:** Trợ lý lập trình AI (Antigravity / Gemini) để hỗ trợ đọc hiểu toàn bộ codebase (`durability.py`, `policy.py`, `metrics.py`, `crash_test.py`, `check_submission.py`), rà soát mã nguồn các shape trên `main`, thiết kế bộ test `src/tests/test_tv4_durability.py`, sửa `TODO CP3` trong `single.py` và tổng hợp báo cáo.
- **Cách tự kiểm tra kết quả:**
  - Chạy thực nghiệm kiểm chứng trước và sau khi sửa `single.py`: trước khi sửa ghi nhận đúng 4 test T12/crash fail ở `single`; sau khi sửa chạy lại toàn bộ `pytest -q`, `pytest -q -m student -o addopts=`, `lab8.crash_test` và `lab8.check_submission` đều đạt xanh.
  - Đối chiếu trực tiếp `src/reports/crash.json` và giữ nguyên toàn bộ các file thước đo (`durability.py`, `policy.py`, `metrics.py`, `config/*.yaml`, `data/*`).

## 6. Tự đánh giá

- Hoàn thành trọn vẹn 100% nhiệm vụ CP3 và CP4 của TV4 trên nhánh `LeDanhGiang-03912` đồng bộ với `origin/main`:
  - Khắc phục triệt để lỗ hổng `crash_at` ở `single.py`.
  - Xác nhận cả 3 shape nhóm viết pass 100% các bài test idempotency (T11), 3 điểm crash & resume (T12), `approval_claim_mismatch`, trần hoàn tiền theo đơn (T13, T14) và bảo mật trace.
  - Sẵn sàng cho TV1 merge vào `main` và TV5 chạy benchmark chốt (CP5).
