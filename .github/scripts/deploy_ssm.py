"""Deploy the approved serving code through SSM using the job's OIDC role."""
import json
import os
from pathlib import Path
import re
import tarfile
import time

import boto3

bucket = os.environ["ARTIFACT_BUCKET"]
instance = os.environ["EC2_INSTANCE_ID"]
revision = os.environ["GITHUB_SHA"]
if not re.fullmatch(r"[a-z0-9][a-z0-9.-]+", bucket):
    raise SystemExit("Invalid bucket")
if not re.fullmatch(r"i-[0-9a-f]+", instance) or not re.fullmatch(r"[0-9a-f]{40}", revision):
    raise SystemExit("Invalid instance or revision")
archive = Path("outputs/serving.tar.gz")
archive.parent.mkdir(exist_ok=True)
with tarfile.open(archive, "w:gz") as bundle:
    for name in ["src/serve.py", "requirements-serve.txt"]:
        bundle.add(name, arcname=name)
key = f"deployments/{revision}/serving.tar.gz"
boto3.client("s3").upload_file(str(archive), bucket, key)
download = f"import boto3; boto3.client('s3').download_file({bucket!r}, {key!r}, '/tmp/income-serving.tar.gz')"
commands = [
    "set -eu",
    "cd /home/ubuntu/income-api",
    ".venv/bin/python -c " + json.dumps(download),
    "tar --no-same-owner -xzf /tmp/income-serving.tar.gz",
    "chown ubuntu:ubuntu src/serve.py requirements-serve.txt",
    "sudo -u ubuntu .venv/bin/python -m pip install -r requirements-serve.txt",
    "systemctl restart income-api",
    """ready=0
for attempt in $(seq 1 24); do
  if curl --fail --silent --show-error --max-time 5 http://127.0.0.1:8080/healthz | .venv/bin/python -c 'import json,sys; assert json.load(sys.stdin).get("status") == "ok"'; then
    ready=1
    break
  fi
  sleep 5
done
if [ "$ready" != 1 ]; then
  journalctl -u income-api -n 40 --no-pager
  exit 1
fi""",
    """curl --fail --silent --show-error --max-time 10 http://127.0.0.1:8080/score -H 'Content-Type: application/json' -d '{"features":[60,2,5,2,4,0,1,0,0,45]}' | .venv/bin/python -c 'import json,sys; d=json.load(sys.stdin); assert d["prediction"] in (0,1); assert d["label"] == ("thu_nhap_cao" if d["prediction"] else "thu_nhap_thap"); print(d)'""",
    "echo 'Health check and prediction passed.'",
]
ssm = boto3.client("ssm")
command = ssm.send_command(
    InstanceIds=[instance], DocumentName="AWS-RunShellScript",
    Parameters={"commands": commands, "executionTimeout": ["600"]},
    Comment=f"Income API release {revision[:12]}", TimeoutSeconds=600,
)["Command"]["CommandId"]
print(f"SSM deployment command: {command}", flush=True)
for _ in range(200):
    time.sleep(3)
    try:
        result = ssm.get_command_invocation(CommandId=command, InstanceId=instance)
    except ssm.exceptions.InvocationDoesNotExist:
        continue
    if result["Status"] in ("Pending", "InProgress", "Delayed"):
        continue
    print(result.get("StandardOutputContent", ""))
    print(result.get("StandardErrorContent", ""))
    if result["Status"] != "Success":
        raise SystemExit(f"SSM deployment failed: {result['Status']}")
    break
else:
    raise SystemExit("Timed out waiting for SSM deployment")
