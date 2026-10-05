# Day 19 — Bài thu hoạch & Phân tích Hybrid Search

## 1. So sánh hiệu năng các chế độ tìm kiếm (Mode Comparison)

- **Keyword (BM25)**: Thắng ở câu hỏi *Exact Match* (tên riêng, mã ID, thuật ngữ cố định) nhờ cơ chế tính tần suất từ khóa chính xác (TF-IDF/IDF), nhưng thất bại ở các câu hỏi diễn đạt lại (Paraphrase).
- **Semantic (Vector)**: Thắng ở câu hỏi *Paraphrase* nhờ tìm kiếm trên không gian nhúng ngữ nghĩa (Dense Vector Embeddings), nhưng dễ bỏ sót các thuật ngữ hiếm hoặc từ khóa chính xác.
- **Hybrid Search (RRF k=60)**: Đạt hiệu năng tổng thể cao nhất (**Precision@10 = 78.6%**, vượt Keyword +0.8pp và Vector +5.4pp), áp đảo ở nhóm *Mixed Queries* (100.0%) nhờ dung hòa ưu điểm của cả lexcial và semantic.

## 2. Khi nào KHÔNG nên sử dụng Hybrid Search?

1. **Ràng buộc độ trễ cực nghiêm ngặt (Sub-millisecond latency)**: Hybrid tốn thêm chi phí tính toán đồng thời cả 2 đường search + giải thuật xếp hạng RRF.
2. **Tra cứu mã cố định (Exact ID / SKU Lookups)**: Các hệ thống tra cứu mã số tài khoản, SKU sản phẩm chỉ cần B-Tree hoặc Inverted Index thuần túy.

---

## 3. Khai báo phạm vi sử dụng AI (AI Usage)

- **Công cụ:** Antigravity AI
- **Phạm vi hỗ trợ:** Khởi tạo môi trường venv, chạy benchmark tự động, kiểm thử pytest và tổng hợp thư mục submission.
