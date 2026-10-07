#!/usr/bin/env bash
# Run once on an Ubuntu EC2 instance after copying src/ and requirements-serve.txt.
set -euo pipefail
bucket="${1:?Usage: bash deploy/setup-ec2.sh BUCKET REGION}"
region="${2:?Usage: bash deploy/setup-ec2.sh BUCKET REGION}"
[[ "$bucket" =~ ^[a-z0-9][a-z0-9.-]+$ ]] || { echo 'Invalid S3 bucket name'; exit 1; }
[[ "$region" =~ ^[a-z]{2}-[a-z]+-[0-9]+$ ]] || { echo 'Invalid AWS region'; exit 1; }
app_root="$HOME/income-api"
test -f "$app_root/src/serve.py"
test -f "$app_root/requirements-serve.txt"
sudo apt-get update
sudo apt-get install -y python3-venv python3-pip curl
python3 -m venv "$app_root/.venv"
"$app_root/.venv/bin/python" -m pip install -r "$app_root/requirements-serve.txt"
mkdir -p "$app_root/models"
sudo tee /etc/systemd/system/income-api.service >/dev/null <<EOF
[Unit]
Description=Adult Income Inference API (S3)
Wants=network-online.target
After=network-online.target

[Service]
User=$(id -un)
WorkingDirectory=$app_root
Environment="ARTIFACT_BUCKET=$bucket"
Environment="AWS_DEFAULT_REGION=$region"
Environment="MODEL_PATH=$app_root/models/model.joblib"
ExecStart=$app_root/.venv/bin/python $app_root/src/serve.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload
sudo systemctl enable income-api
echo 'Service configured. Release will start it after publishing an approved model.'
