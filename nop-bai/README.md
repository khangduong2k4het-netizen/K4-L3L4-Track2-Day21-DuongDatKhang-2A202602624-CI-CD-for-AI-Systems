# Nộp Bài - Day 21: CI/CD cho AI Systems

Thư mục này là nơi chứa **bằng chứng nộp bài**. Bạn không cần tạo thêm thư mục nào khác:
điền vào các file có sẵn và bỏ ảnh chụp màn hình vào đúng tên file đã quy định.

```
nop-bai/
├── README.md                  <- file này (checklist)
├── bao-cao.md                 <- template báo cáo, không quá 1 trang A4
└── anh-chup-man-hinh/
    ├── README.md              <- mô tả yêu cầu của từng ảnh
    ├── 01-mlflow-ui.png
    ├── 02-actions-buoc-2.png
    ├── 03-actions-buoc-3.png
    ├── 04-curl-api.png
    └── 05-cloud-storage.png
```

---

## Checklist Trước Khi Nộp

Đánh dấu `[x]` khi hoàn thành từng mục:

- [x] Repo GitHub ở chế độ **public**, truy cập được không cần đăng nhập.
- [ ] Repo GitHub chứa toàn bộ code và cấu hình đã hoàn thiện.
- [ ] Đủ 5 ảnh trong `anh-chup-man-hinh/`, đúng tên file, đúng thứ tự (xem
      [yêu cầu chi tiết](anh-chup-man-hinh/README.md)).
- [ ] `bao-cao.md` đã điền đủ 4 mục bắt buộc, có số liệu CI thật của Bước 2/3 và không vượt quá 1 trang A4.
- [ ] Đã `git push` toàn bộ thư mục `nop-bai/` lên GitHub.
- [ ] Dán URL repo GitHub vào bài nộp trên **https://vlearn.dev**.
- [ ] Mở lại URL vừa nộp ở chế độ ẩn danh để chắc chắn repo public và người chấm xem được.

## Trạng Thái Kiểm Tra Ngày 07/10/2026

**Chưa sẵn sàng nộp bài.** Repository public đã được xác nhận bằng truy cập không
đăng nhập. Báo cáo đã điền thông tin sinh viên và các phần có kết quả thực tế,
xóa comments hướng dẫn và bỏ mục bonus vì chưa thực hiện bonus nào.

| Hạng mục | Bằng chứng hiện có | Việc còn thiếu |
|---|---|---|
| MLflow tracking (12 điểm) | 3 run hoàn thành, 3 cấu hình khác nhau. | Chụp lại ảnh 01 có thanh địa chỉ URL. |
| Độ đo (8 điểm) | Cả 3 run có F1 lớp dương và accuracy. | Giữ đủ cột trong ảnh chụp lại. |
| Phân tích (4 điểm) | Mục 1/2 của báo cáo; chọn 200/0.1/5 với F1 0.7149. | Đã có nội dung phân tích. |
| DVC (12 điểm) | Đã tạo 3 con trỏ `.dvc` và cache cục bộ. | Cấu hình remote thật, `dvc push` lên S3, ảnh 05. |
| CI/CD (16 điểm) | Workflow 4 jobs đã viết và qua actionlint. | Đăng nhập GitHub/AWS, cấu hình secrets, chạy 4 jobs xanh, ảnh 02. |
| Quality Gate (4 điểm) | Tests chặn F1 thấp/không hợp lệ và chấp nhận 0.65; Release phụ thuộc Gate. | Bằng chứng Actions chặn Release khi F1 dưới 0.65. |
| Serving (12 điểm) | API S3 đã qua kiểm thử cục bộ. | Tạo/cấu hình EC2, kiểm tra API qua VM IP, ảnh 04. |
| Tự động hóa (12 điểm) | Trigger đã theo dõi `data/**.dvc`. | Sau khi Bước 2 thành công: bổ sung batch 2, DVC push, commit dữ liệu, 4 jobs xanh, ảnh 03. |

Ảnh `01-mlflow-ui.png` hiện dưới 1 MB; còn thiếu ảnh **02, 03, 04, 05**.
Không dùng kết quả cục bộ thay cho bằng chứng cloud. Mục 4 của báo cáo đang ghi
chưa có kết quả CI; cần thay bằng artifacts của hai lần chạy thật trước khi nộp.

Đây là kiểm tra độ đầy đủ bằng chứng, không phải điểm chấm chính thức.

---

## Ảnh Chụp Màn Hình Tương Ứng Với Rubric

| Ảnh | Chứng minh hạng mục nào trong rubric | Điểm |
|---|---|---|
| `01-mlflow-ui.png` | Bước 1 - MLflow tracking, Bước 1 - Độ đo | 20 |
| `02-actions-buoc-2.png` | Bước 2 - CI/CD (bốn jobs màu xanh) | 16 |
| `03-actions-buoc-3.png` | Bước 3 - Tự động hóa | 12 |
| `04-curl-api.png` | Bước 2 - Serving | 12 |
| `05-cloud-storage.png` | Bước 2 - DVC | 12 |

Phần `bao-cao.md` chứng minh hạng mục **Bước 1 - Phân tích** (4 điểm) và là nơi bạn giải
trình khi một ảnh nào đó chưa thể hiện đủ (ví dụ quality gate đã chặn đúng một lần).

---

## Quy Ước Chung

- **Định dạng ảnh**: `.png` (ưu tiên) hoặc `.jpg`. Nếu dùng `.jpg`, giữ nguyên phần tên,
  chỉ đổi đuôi — ví dụ `01-mlflow-ui.jpg`.
- **Không đổi số thứ tự đầu tên file.** Thứ tự này là thứ tự chấm bài.
- **Không che thông tin cần chấm**: tên job, trạng thái màu xanh, giá trị `f1_score`,
  đường dẫn bucket. Được phép che email cá nhân và khóa bí mật.
- **Cần chụp cả URL trên thanh địa chỉ** với các ảnh chụp từ trình duyệt (MLflow UI,
  GitHub Actions, Cloud Storage Console) để xác nhận đúng repo/project của bạn.
- **Tuyệt đối không commit khóa bí mật**: `sa-key.json`, nội dung GitHub Secrets, access
  key của cloud. Nếu ảnh lỡ chứa các thông tin này, hãy che lại trước khi commit.

---

## Ghi Chú Về Kích Thước Repo

Ảnh chụp màn hình được commit trực tiếp vào Git. Giữ mỗi ảnh dưới **1 MB** (chụp vùng cần
thiết thay vì toàn màn hình 4K, hoặc nén lại trước khi commit) để repo không phình to.

Nếu bạn dùng macOS, có thể nén nhanh bằng lệnh sẵn có:

```bash
sips -Z 1600 nop-bai/anh-chup-man-hinh/01-mlflow-ui.png
```
