# Nộp bài Day 21 — Dương Đạt Khang

MSSV **2A202602624**, khóa **K4**. Repository: [GitHub public](https://github.com/khangduong2k4het-netizen/K4-L3L4-Track2-Day21-DuongDatKhang-2A202602624-CI-CD-for-AI-Systems).

## Checklist

- [x] Code train, serving, tests và workflow đã hoàn thiện, không còn TODO.
- [x] MLflow có 3 cấu hình khác nhau, đủ F1 lớp dương và accuracy.
- [x] DVC push thành công lên S3 private; dữ liệu xuất hiện trên S3 Console.
- [x] Bước 2: Unit Test, Train, Quality Gate, Release đều xanh.
- [x] Run mô hình yếu chứng minh F1 dưới 0.65 chặn Release.
- [x] EC2 trả GET /healthz và POST /score đúng qua IP công khai.
- [x] Bước 3: commit chỉ thay DVC pointer, event push, bốn jobs xanh.
- [x] Báo cáo đủ 4 mục, 517 từ theo cách đếm tách khoảng trắng, không còn chú thích HTML.
- [x] Các ảnh bằng chứng hiện có đều dưới 1 MB.
- [x] Thư mục `nop-bai/` và mã nguồn đã đẩy lên repository public.
- [ ] Chụp bổ sung thanh địa chỉ thật và cửa sổ terminal theo quy ước ảnh.
- [ ] Nộp URL repository vào đúng bài Day 21 trên VLearn.

## Kết quả thực tế

| Bằng chứng | F1 / Accuracy hoặc kết quả | Liên kết |
|---|---|---|
| MLflow cục bộ | 3 runs: 0.7109/0.8780; 0.6051/0.8460; 0.7149/0.8740 | [Ảnh 01](anh-chup-man-hinh/01-mlflow-ui.png) |
| Bước 2 | 0.7149 / 0.8740, bốn jobs xanh | [Run Bước 2](https://github.com/khangduong2k4het-netizen/K4-L3L4-Track2-Day21-DuongDatKhang-2A202602624-CI-CD-for-AI-Systems/actions/runs/37604919875), [ảnh 02](anh-chup-man-hinh/02-actions-buoc-2.png) |
| Bước 3 | 0.7354 / 0.8820, bốn jobs xanh; event `push` | [Run Bước 3](https://github.com/khangduong2k4het-netizen/K4-L3L4-Track2-Day21-DuongDatKhang-2A202602624-CI-CD-for-AI-Systems/actions/runs/37607774898), [ảnh 03](anh-chup-man-hinh/03-actions-buoc-3.png) |
| Gate chặn | F1 0.6051, Quality Gate failure, Release skipped | [Run thử Gate](https://github.com/khangduong2k4het-netizen/K4-L3L4-Track2-Day21-DuongDatKhang-2A202602624-CI-CD-for-AI-Systems/actions/runs/37605388654), [ảnh 07](anh-chup-man-hinh/07-quality-gate-chan.png) |
| API EC2 | healthz `ok`, score trả prediction/label hợp lệ | [Kết quả curl gốc](api-test.txt), [ảnh 04](anh-chup-man-hinh/04-curl-api.png) |
| S3 Console | DVC cache và `artifacts/current/model.joblib` | [Ảnh 05a](anh-chup-man-hinh/05a-storage-dvc.png), [ảnh 05b](anh-chup-man-hinh/05b-storage-model.png) |

Chi tiết run IDs, commit SHA, toàn bộ số liệu và MLflow run IDs trong
[ket-qua-thuc-nghiem.json](ket-qua-thuc-nghiem.json). Bước 3 thêm batch2 đúng một lần,
tăng train từ 22.361 lên 44.722 mẫu, giữ nguyên holdout 500 mẫu và cấu hình 200/0.1/5.
Commit dữ liệu: [9443ae8d](https://github.com/khangduong2k4het-netizen/K4-L3L4-Track2-Day21-DuongDatKhang-2A202602624-CI-CD-for-AI-Systems/commit/9443ae8dbf89a9b95e8fbb4e08e2d0fb594b8773).

## Triển khai AWS

- Region: `ap-southeast-1`; EC2 `t3.small`: `i-0a9249b9b954a67f6`.
- API đã kiểm tra trước khi dừng: `http://18.142.137.123:8080`; hiện tạm ngừng phục vụ.
- Bucket private: `income-lab-406382424864-ap-southeast-1`.
- Pipeline dùng GitHub OIDC, triển khai SSM; API tải model bằng instance role.
- Model chỉ được xuất bản sau Quality Gate. Không thực hiện bonus.

## Giới hạn ảnh và việc còn lại

Ảnh 01/02/03/05/07 chụp trang web thật bằng Playwright nhưng không chứa thanh địa chỉ
trình duyệt. Công cụ chụp cửa sổ Windows không kết nối được native pipe (OS error 2),
nên chưa đáp ứng quy ước chụp cả URL. Ảnh 04 là bản hiển thị transcript của lệnh curl
chạy thật, **không phải ảnh cửa sổ terminal**; file api-test.txt giữ lệnh, phản hồi và exit code.
Cần chụp bổ sung hai chi tiết này nếu người chấm yêu cầu đúng hình thức trong
[quy định ảnh](anh-chup-man-hinh/README.md). Không ghép thanh địa chỉ hoặc giả giao diện terminal.

EC2 đã được tạm dừng (stopped) sau khi kiểm tra xong để tiết kiệm AWS credit (chi tiết trong [ec2-status.json](ec2-status.json)).
Có thể start lại khi cần kiểm tra API thực tế và dọn tài nguyên sau khi chấm bài.
