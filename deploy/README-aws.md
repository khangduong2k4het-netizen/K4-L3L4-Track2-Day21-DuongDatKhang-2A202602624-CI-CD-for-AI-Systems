# Bước 2 trên AWS: S3, EC2 và GitHub Actions

Pipeline dùng Python 3.11. EC2 chỉ chạy API; huấn luyện chạy trên GitHub Actions.
`src/serve.py` tải model từ `s3://BUCKET/artifacts/current/model.joblib` khi
khởi động. DVC lưu dữ liệu dưới `s3://BUCKET/dvc/`.

## Đăng nhập từ Windows

AWS CLI đã được cài. Dùng profile riêng cho bài lab:

```powershell
& "C:\Program Files\Amazon\AWSCLIV2\aws.exe" login --profile income-lab --region ap-southeast-1
& "C:\Program Files\Amazon\AWSCLIV2\aws.exe" sts get-caller-identity --profile income-lab
```

Đăng nhập/MFA trong trình duyệt của bạn; không gửi mật khẩu hoặc key vào chat.
Đây là luồng [AWS CLI console login](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sign-in.html).
Region có thể thay đổi theo tài khoản. `t3.small` thuộc chương trình Free Tier
mới cho tài khoản từ 15/07/2025, trong thời hạn và credit còn lại;
kiểm tra [điều kiện AWS](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-free-tier-usage.html)
trước khi tạo instance.

## Tài nguyên cần cấu hình sau khi đăng nhập

1. Tạo S3 bucket riêng, chặn public access và giữ dữ liệu/model riêng tư.
2. Tạo EC2 Ubuntu 22.04 x86_64 loại `t3.small`, có public IPv4.
3. Cho phép SSH ở cổng 22 cho triển khai và HTTP ở cổng 8080 cho API.
4. Gắn IAM instance role cho EC2 có quyền `s3:GetObject` trên
   `arn:aws:s3:::BUCKET/artifacts/current/model.joblib`. API tự dùng instance role.
5. Cấp danh tính CI quyền `s3:ListBucket` trên bucket và
   `s3:GetObject`, `s3:PutObject`, `s3:DeleteObject` trong prefix `dvc/`,
   cùng quyền ghi model trong `artifacts/current/`.

Không dùng root access key. Bucket, instance và secrets chưa được tạo chỉ bởi
việc có các file hướng dẫn này; phải thực hiện trên tài khoản AWS đã đăng nhập.

## DVC cục bộ

Ba file `.dvc` đã được tạo. Khi biết bucket thật, cấu hình và đẩy dữ liệu:

```powershell
$env:AWS_PROFILE = "income-lab"
$env:AWS_DEFAULT_REGION = "ap-southeast-1"
$bucket = "TEN_BUCKET_THAT"
.\.venv311\Scripts\python.exe -m dvc remote add -d labstore "s3://$bucket/dvc"
.\.venv311\Scripts\python.exe -m dvc remote modify labstore region $env:AWS_DEFAULT_REGION
.\.venv311\Scripts\python.exe -m dvc push
```

DVC đọc AWS profile hoặc biến môi trường; không ghi key vào `.dvc/config`.
[Tài liệu DVC S3](https://doc.dvc.org/user-guide/data-management/remote-storage/amazon-s3).

## Cài service trên EC2

Copy `src/serve.py`, `requirements-serve.txt`, `deploy/setup-ec2.sh` lên
`~/income-api/`, giữ nguyên các thư mục con. Chạy trên EC2:

```bash
cd ~/income-api
bash deploy/setup-ec2.sh TEN_BUCKET_THAT ap-southeast-1
```

Script tạo virtualenv riêng và cài dependency phục vụ suy luận với cùng phiên
bản scikit-learn/joblib/numpy như model huấn luyện. Nó chỉ enable service;
job Release sẽ khởi động service sau khi model đủ chất lượng đã được xuất bản.

## Năm GitHub Secrets và một variable

Trong repository Settings → Secrets and variables → Actions, cấu hình:

| Secret | Giá trị |
|---|---|
| `STORAGE_CREDENTIALS` | JSON credentials của danh tính CI có quyền trên bucket |
| `ARTIFACT_BUCKET` | Tên bucket S3, không có `s3://` |
| `SERVER_HOST` | Public IPv4 hoặc DNS của EC2 |
| `SERVER_USER` | `ubuntu` cho Ubuntu AMI |
| `SERVER_SSH_KEY` | Nội dung private key SSH của EC2 |

JSON của `STORAGE_CREDENTIALS` có dạng:

```json
{
  "aws_access_key_id": "GIA_TRI_THAT",
  "aws_secret_access_key": "GIA_TRI_THAT",
  "region": "ap-southeast-1"
}
```

Với credentials tạm thời, thêm `aws_session_token`; phải cập nhật secret trước
khi credentials hết hạn. Không đưa credentials tạm thời của root vào CI.
Đặt Actions **variable** `AWS_REGION` bằng region thật; trường `region` trong
JSON cũng được hỗ trợ. Nếu cả hai đều thiếu, workflow dùng `us-east-1`.

## Pipeline và kiểm tra

`Unit Test → Train → Quality Gate → Release` có đúng bốn jobs. Train lưu model
ứng viên và report thành GitHub artifacts. Quality Gate chặn F1 dưới 0.65,
NaN, infinity và giá trị không hợp lệ. Release mới upload model được duyệt
vào `artifacts/current/model.joblib`, copy code lên EC2 và restart service.
Nó thử lại health check rồi kiểm tra cả `/score`.

Ảnh nộp bài phải chụp kết quả thật: bốn jobs xanh, curl gọi tới IP EC2,
và S3 Console thấy `dvc/` cùng model hiện hành. Không dùng ảnh kiểm thử cục bộ
thay cho bằng chứng triển khai cloud.
