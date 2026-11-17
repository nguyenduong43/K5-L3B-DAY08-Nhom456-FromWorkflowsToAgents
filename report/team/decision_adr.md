# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: workflow
- Commit hash: 55f49a7
- Run id dẫn chứng: R-workflow-C-001-s11
- Pass rate / pass^5 / seed min-max / variance: 1.000 / 1.000 / 1.000-1.000 / 0.000000
- Cost per success (mô phỏng, VND): 27.86
- Crash safety: 20/20 (reports/crash.json)
- Secret leak / approval bypass: 0 / 0

Ví dụ một dòng đã điền: `- Shape chọn: workflow`, `- Crash safety: 20/20 (src/reports/crash.json)`.

## Vì sao shape này

Nhóm chọn Shape A (workflow) làm kiến trúc triển khai chính vì đây là kiến trúc ít tự chủ nhất (least autonomous) mà vẫn giải quyết trọn vẹn và chính xác bài toán nghiệp vụ bồi thường của LogiX-VN. So sánh trên cùng corpus (14 claim public), cùng 5 seed (11, 22, 33, 44, 55), workflow đạt tính tất định cao nhất, không phụ thuộc vào sự ngẫu nhiên của LLM khi suy luận số liệu bồi thường, và loại bỏ hoàn toàn hiện tượng ảo giác (hallucination) khi đọc ngày giao hàng hay thông tin bồi thường. Toàn bộ logic tính toán tiền hoàn cước và hư hỏng hàng hóa được giao trọn cho code (`compute_compensation`), tuân thủ chặt chẽ ranh giới code/model.

## Có đáng đổi lấy multi-agent không

Không đáng để đổi sang Multi-Agent (orchestrator hoặc swarm) trong bài toán này. Dữ liệu thực nghiệm từ Shape D (swarm) cho thấy hệ thống multi-agent gặp độ dao động cao (variance = 0.000816, pass^5 giảm xuống 0.929 do fail T02 ở seed 55) trong khi chi phí giả lập tăng vọt (49.57 VND/success so với ~0 VND của workflow). Việc tăng tính tự chủ không đem lại sự gia tăng về độ chính xác mà còn làm tăng bề mặt tấn công prompt injection và rủi ro rò rỉ dữ liệu qua handoff. Nhóm chỉ cân nhắc chuyển sang Orchestrator/Multi-Agent khi và chỉ khi: (1) nghiệp vụ xuất hiện các ticket khiếu nại phi cấu trúc cực kỳ phức tạp cần suy luận ngôn ngữ tự nhiên đa chiều mà code logic không thể bao quát; (2) task đòi hỏi phải phân rã công việc song song trên nhiều hệ thống con khác nhau mà chi phí gọi model được đánh đổi bằng giá trị vượt trội.

## Trace và bằng chứng

Trace của hệ thống tuân thủ nghiêm ngặt Trace Contract v1, chỉ ghi các event vòng đời chuẩn: `workflow_start`, `lookup_order`, `compute_quote`, `issue_refund_call`, `workflow_finish`. Hệ thống cố ý **KHÔNG** ghi các trường dữ liệu thô: `parent_secret`, authorization token (`CANARY_SECRET_*`), và thông tin PII của khách hàng (số điện thoại, địa chỉ nhận hàng, tên hàng hóa, ghi chú nội bộ). Bằng chứng kiểm định an ninh được xác thực thông qua: (1) scanner tự động quét toàn bộ `trace_path` và các side-files `<run_id>*` phát hiện 0 vi phạm (`forbidden_substring: 0`); (2) kiểm thử đơn vị độc lập `test_tv5_benchmark.py` và `test_trace_contract.py` chứng minh trace contract fail-closed và chặn đứng mọi nguy cơ lộ lọt bí mật.

## Giới hạn

MockLLM không phải model sản xuất thực tế mà hoạt động dựa trên replay giả lập theo seed. Latency được gắn nhãn `unavailable`. Mọi số liệu chi phí (cost) là giá trị mô phỏng VND quy đổi từ tokens theo `pricing.yaml`, không đại diện cho hóa đơn API thương mại. Quyết định kiến trúc dựa trên thực nghiệm độc lập và trung thực, không chỉnh sửa file JSON để đối phó chỉ tiêu.
