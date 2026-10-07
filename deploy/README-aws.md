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
3. Mở API cổng 8080 để kiểm tra bài. SSH cổng 22 chỉ cho IP máy quản trị.
   Pipeline triển khai qua Systems Manager (SSM), không dùng SSH key.
4. Gắn IAM instance role cho EC2 có quyền `s3:GetObject` trên
   `arn:aws:s3:::BUCKET/artifacts/current/model.joblib` và bundle trong `deployments/`.
   API tự dùng instance role; gắn `AmazonSSMManagedInstanceCore` để SSM agent hoạt động.
5. Cấp IAM role cho GitHub OIDC quyền `s3:ListBucket` trên bucket và
   `s3:GetObject`, `s3:PutObject`, `s3:DeleteObject` trong prefix `dvc/`,
   cùng quyền ghi model trong `artifacts/current/` và bundle trong `deployments/`.
   Trust policy chỉ cho repo này, nhánh `main`. Role được `ssm:SendCommand` với
   document `AWS-RunShellScript` trên đúng EC2 lab và đọc trạng thái lệnh.

Không dùng root access key. Bucket, instance và secrets chưa được tạo chỉ bởi
việc có các file hướng dẫn này; phải thực hiện trên tài khoản AWS đã đăng nhập.

Script tạo tài nguyên có thể chạy lại, giữ SSH key trong `.secrets/` (đã ignore):

```powershell
.\.venv311\Scripts\python.exe deploy/provision_aws.py --profile income-lab --region ap-southeast-1
```

Kiểm tra `aws freetier get-account-plan-state` trước khi chạy. Gói PAID vẫn dùng
credit còn lại, nhưng sẽ tính phí khi credit hết hoặc hết hạn. EC2, EBS và Public
IPv4 tiếp tục tiêu hao credit khi giữ máy hoạt động. Stop EC2 khi không cần API;
EBS vẫn còn phí lưu trữ. Terminate EC2 sau khi chấm bài nếu không cần giữ VM.
Không tạo Elastic IP, NAT Gateway hay load balancer cho lab này.

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

## GitHub Secrets và variables cho SSM

Trong repository Settings → Secrets and variables → Actions, cấu hình:

| Secret | Giá trị |
|---|---|
| `AWS_ROLE_ARN` | ARN của IAM role `income-lab-github` dùng GitHub OIDC |
| `ARTIFACT_BUCKET` | Tên bucket S3, không có `s3://` |
| `SERVER_HOST` | Public IPv4 hoặc DNS của EC2 |

Đặt Actions **variables** `AWS_REGION` và `EC2_INSTANCE_ID`. GitHub lấy credentials tạm
thời qua OIDC cho từng job; không lưu AWS access key hoặc root credentials trong
GitHub. Mỗi job Train/Release có quyền `id-token: write`.

## Pipeline và kiểm tra

`Unit Test → Train → Quality Gate → Release` có đúng bốn jobs. Train lưu model
ứng viên và report thành GitHub artifacts. Quality Gate chặn F1 dưới 0.65,
NaN, infinity và giá trị không hợp lệ. Release mới upload model được duyệt
vào `artifacts/current/model.joblib`, upload bundle code lên S3, gọi SSM để tải
bundle trên EC2 và restart service.
Nó thử lại health check rồi kiểm tra cả `/score`.

Để chứng minh gate chặn mô hình yếu, chạy workflow thủ công với
`training_preset=weak-model-demo` khi vẫn dùng batch 1. Train chạy thật bộ
50/0.05/2; nếu F1 dưới 0.65, Quality Gate thất bại và Release tự động bị bỏ qua.
Lựa chọn này chỉ sửa params trong runner, không đổi `params.yaml` trên nhánh main.

Ảnh nộp bài phải chụp kết quả thật: bốn jobs xanh, curl gọi tới IP EC2,
và S3 Console thấy `dvc/` cùng model hiện hành. Không dùng ảnh kiểm thử cục bộ
thay cho bằng chứng triển khai cloud.
