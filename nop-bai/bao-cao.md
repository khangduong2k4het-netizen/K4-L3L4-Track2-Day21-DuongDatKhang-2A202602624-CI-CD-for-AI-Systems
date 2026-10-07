# Báo Cáo Lab Day 21 - CI/CD cho AI Systems

| | |
|---|---|
| Họ và tên | Dương Đạt Khang |
| MSSV | 2A202602624 |
| Lớp / Khóa | K4 |
| Repo GitHub | https://github.com/khangduong2k4het-netizen/K4-L3L4-Track2-Day21-DuongDatKhang-2A202602624-CI-CD-for-AI-Systems |
| Ngày nộp | Chưa nộp; kiểm tra ngày 07/10/2026 |

## 1. Bộ Siêu Tham Số Đã Chọn và Lý Do

| Lần chạy | n_estimators | learning_rate | max_depth | f1_score | accuracy |
|---|---|---|---|---|---|
| 1 | 100 | 0.1 | 3 | 0.7109 | 0.8780 |
| 2 | 50 | 0.05 | 2 | 0.6051 | 0.8460 |
| 3 | 200 | 0.1 | 5 | 0.7149 | 0.8740 |

**Bộ siêu tham số đã chọn:** `n_estimators=200`, `learning_rate=0.1`, `max_depth=5`.

**Lý do:** Lần 3 đạt F1 cao nhất (0.7149), vượt ngưỡng 0.65. Lần 1 có accuracy cao hơn nhưng F1 thấp hơn, nên chọn theo accuracy sẽ bỏ qua cấu hình tốt nhất cho lớp thu nhập cao. Lần 2 giảm cả số cây, learning rate và độ sâu, chỉ đạt F1 0.6051. Learning rate nhỏ thường cần nhiều cây hơn để bù lại, nhưng lần này chỉ dùng 50 cây. Các tham số thay đổi đồng thời nên chưa tách riêng ảnh hưởng từng tham số. Ba lần dùng cùng 22.361 mẫu huấn luyện, 500 mẫu holdout, random_state=42. Model và report của lần 3 đã được lưu.

## 2. Vì Sao Ngưỡng Chất Lượng Đặt Trên F1 Chứ Không Phải Accuracy

Adult có khoảng 24,8% mẫu thu nhập cao. Mô hình luôn dự đoán thu nhập thấp đạt accuracy 75,2% nhưng F1 lớp dương bằng 0. Accuracy tổng thể dễ che lấp việc bỏ sót lớp thiểu số. F1 kết hợp precision và recall của lớp dương, phản ánh cả dự đoán nhầm lẫn bỏ sót. Quality Gate dùng F1 từ 0.65; accuracy chỉ tham khảo. Mã gọi `f1_score(y_eval, preds)`, mặc định đánh giá target=1. Macro lấy trung bình hai lớp, còn weighted lấy trung bình theo số mẫu mỗi lớp. Cả hai không phải F1 riêng lớp dương nên không phù hợp với ngưỡng lab.

## 3. Khó Khăn Gặp Phải và Cách Giải Quyết

| Khó khăn | Nguyên nhân | Cách giải quyết |
|---|---|---|
| Cài dependency thất bại. | Python 3.13 thiếu wheel scikit-learn 1.4.2. | Dùng `.venv311` với Python 3.11.9. |
| MLflow không mở SQLite. | SQLAlchemy 2.1 bỏ class MLflow 2.13 cần. | Giới hạn SQLAlchemy về 2.0; tests đã qua. |
| Chưa triển khai AWS/Actions. | Chưa đăng nhập AWS/GitHub. | Đã cài CLI, chuẩn bị pipeline; còn chờ đăng nhập. |

## 4. So Sánh Bước 2 và Bước 3

| | f1_score | accuracy |
|---|---|---|
| Bước 2 (chỉ `train_batch1`) | Chưa có kết quả CI | Chưa có kết quả CI |
| Bước 3 (thêm `train_batch2`) | Chưa chạy | Chưa chạy |

**Nhận xét:** Kết quả cục bộ 0.7149/0.8740 thuộc Bước 1, không thay cho kết quả Actions của Bước 2. Chưa thể kết luận tăng/giảm vì chưa chạy Bước 3; bảng sẽ được cập nhật từ artifacts thật của hai lần chạy.
