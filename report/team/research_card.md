# Research card

File này nằm cố định ở `report/team/research_card.md`; `python -m lab8.check_submission` đọc cột "Nhóm điền" bằng máy.

Phần này nối tiếp phần mini research ở buổi lý thuyết (slide 62–63). Chọn **một** câu R1–R4, điền 6 dòng, rồi biến nó thành **một ablation** chạy được trong lab: giữ nguyên model (MockLLM), tool, seed, corpus và giá, chỉ thay đổi một biến.

| Câu | Nguồn (thư viện tham khảo, slide 68–69) | Câu hỏi gợi ý cho lab |
| --- | --- | --- |
| R1 · Scaling | Google Research 2026, *Towards a Science of Scaling Agent Systems* | Task claims chủ yếu tuần tự hay song song được? Dự đoán thêm investigator sẽ làm pass rate và cost/success thay đổi thế nào. |
| R2 · Failure taxonomy | MAST, NeurIPS 2025, *Why Do Multi-Agent LLM Systems Fail?* | Các trial fail của swarm (seed 55) thuộc nhóm nào: lỗi giao việc, lệch mục tiêu, hay lỗi kiểm chứng? |
| R3 · Architecture choices | AgentArch, AACL 2026 | Nếu đổi topology mà giữ nguyên mọi thứ khác, biến nào phải cố định để kết luận còn đúng? |
| R4 · Evaluation confounders | EMNLP 2026, *Rethinking Evaluation of MAS Efficiency* | Làm sao chứng minh chênh lệch giữa A/B/C/D là do topology, không phải do prompt, tool hay seed? |

## Phiếu của nhóm

Điền vào cột cuối. Không xóa hai cột đầu.

| Field | Hướng dẫn | Nhóm điền |
| --- | --- | --- |
| CÂU | R1 / R2 / R3 / R4 | R2 |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | NeurIPS 2025, *Why Do Multi-Agent LLM Systems Fail?* (MAST taxonomy), URL: https://arxiv.org/abs/2503.13657, empirical failure taxonomy on Multi-Agent Systems. |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Các hệ thống Multi-Agent LLM thường gặp lỗi do thiếu cơ chế kiểm chứng độc lập (verification failure) và nhầm lẫn ngữ cảnh khi trao đổi dữ liệu không tin cậy (context misalignment). |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Môi trường Multi-Agent có tool use; giới hạn ở việc phân biệt giữa user ticket input (untrusted) và system database ground truth. |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Khi chuyển từ Workflow (Shape A) sang Swarm (Shape D), variance tăng từ 0 lên > 0 và pass^5 giảm từ 1.0 xuống < 1.0 do Swarm gặp lỗi verification ở seed nhạy cảm (seed 55 ở test T02). |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Giữ cố định: MockLLM, database tools, seeds (11,22,33,44,55), public claims corpus, bảng giá pricing.yaml, host evaluator. Biến duy nhất thay đổi: Kiến trúc xử lý (Topology: Workflow vs Swarm). |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Lỗi mismatch trạng thái giải quyết do agent tin ticket thay vì DB; đo bằng Pass rate, Pass^5, Seed variance, và Cost per success. |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn): python -m lab8.benchmark --shapes swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark_swarm_preview.json
- Run id / file report: reports/benchmark_swarm_preview.json
- Kết quả so với hypothesis (đúng / sai / không kết luận được), kèm số liệu: Đúng. Swarm thể hiện rõ lỗi verification ở seed 55 trên test T02: pass rate đạt 0.986, pass^5 đạt 0.929, variance 0.000816 (dao động từ min 0.929 đến max 1.000), cost per success 49.57 VND. Swarm bị lỗi 1 trial do nhầm trạng thái claim giữa ticket và database.
- Giới hạn: MockLLM không phải model sản xuất, latency là `unavailable`.

Muốn đi xa hơn một ablation để lấy điểm cộng thì xem [docs/bonus_topics.md](../../docs/bonus_topics.md).
