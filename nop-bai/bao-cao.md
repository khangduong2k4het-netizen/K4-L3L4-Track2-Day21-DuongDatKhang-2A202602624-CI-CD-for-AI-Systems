# Báo cáo Day 21 — CI/CD cho AI Systems

Dương Đạt Khang · MSSV 2A202602624 · K4 · Kiểm tra 07/10/2026

Repository: [GitHub public](https://github.com/khangduong2k4het-netizen/K4-L3L4-Track2-Day21-DuongDatKhang-2A202602624-CI-CD-for-AI-Systems).

## 1. Bộ siêu tham số đã chọn và lý do

| n_estimators | learning_rate | max_depth | F1 | Accuracy |
|---|---|---|---|---|
| 100 | 0.1 | 3 | 0.7109 | 0.8780 |
| 50 | 0.05 | 2 | 0.6051 | 0.8460 |
| 200 | 0.1 | 5 | 0.7149 | 0.8740 |

Ba thí nghiệm MLflow dùng 22.361 mẫu huấn luyện, cùng 500 mẫu holdout và random_state=42. Chọn 200 cây, learning_rate=0.1, max_depth=5 trong params.yaml vì F1 cao nhất, vượt ngưỡng 0.65. Cấu hình 100 cây có accuracy cao hơn nhưng F1 thấp hơn. Cấu hình 50 cây vừa nông vừa có learning rate nhỏ, chưa đủ vòng boosting để sửa sai. Giảm learning rate thường cần tăng số cây; tăng độ sâu giúp học tương tác nhưng tăng chi phí và nguy cơ quá khớp. Vì ba tham số thay đổi đồng thời, chưa thể quy toàn bộ cải thiện cho riêng độ sâu.

## 2. Vì sao Quality Gate dùng F1 thay vì Accuracy

Lớp thu nhập cao chiếm 24,8% holdout. Luôn dự đoán thu nhập thấp vẫn đạt accuracy 75,2%, nhưng F1 lớp dương bằng 0. F1 kết hợp precision và recall, giúp đánh giá cả dự đoán nhầm và bỏ sót lớp thiểu số. Mã gọi f1_score(y_eval, preds), chỉ đánh giá target=1. Macro trung bình hai lớp, weighted trung bình theo số mẫu; cả hai không phải F1 riêng lớp dương. Gate kiểm tra F1 hữu hạn từ 0.65; chỉ sau khi qua Gate, Release mới ghi model hiện hành lên S3. Run thử mô hình yếu đạt F1 0.6051: Gate thất bại và Release tự động bị bỏ qua, chứng minh ngưỡng hoạt động thật.

## 3. Khó khăn và cách giải quyết

- Phụ thuộc: Python 3.13 không có wheel phù hợp với scikit-learn 1.4.2; tạo virtualenv Python 3.11.9 riêng. MLflow 2.13 lỗi với SQLAlchemy 2.1; giới hạn SQLAlchemy trong nhánh 2.0.
- Kết nối: SSH từ máy cá nhân bị timeout; chuyển sang SSM với quyền giới hạn đúng EC2, GitHub xác thực OIDC và API dùng instance role. Không đưa private key lên GitHub.
- Tự động hóa: commit ban đầu chưa tạo run dù workflow active; bật lại Actions ở cấp repository, sau đó xác nhận event=push bằng API và run thực tế.

## 4. So sánh Bước 2 và Bước 3

| Bước | Mẫu train | F1 | Accuracy |
|---|---|---|---|
| [2](https://github.com/khangduong2k4het-netizen/K4-L3L4-Track2-Day21-DuongDatKhang-2A202602624-CI-CD-for-AI-Systems/actions/runs/37604919875) | 22.361 | 0.7149 | 0.8740 |
| [3](https://github.com/khangduong2k4het-netizen/K4-L3L4-Track2-Day21-DuongDatKhang-2A202602624-CI-CD-for-AI-Systems/actions/runs/37607774898) | 44.722 | 0.7354 | 0.8820 |

Giữ nguyên tham số và holdout, Bước 3 thay đổi F1 +0.0205, accuracy +0.0080; thêm dữ liệu không bảo đảm mọi chỉ số cùng tăng. Commit 9443ae8d chỉ cập nhật con trỏ DVC, tự kích hoạt đủ bốn jobs xanh và triển khai lên EC2 qua SSM. Số liệu lấy từ report artifact của từng run; bằng chứng và hạn chế ảnh được ghi trong checklist nộp bài.
