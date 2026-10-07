"""Load the lab's STORAGE_CREDENTIALS JSON into masked GitHub env vars."""
import json
import os
from pathlib import Path

credentials = json.loads(os.environ["STORAGE_CREDENTIALS"])
mapping = {
    "aws_access_key_id": "AWS_ACCESS_KEY_ID",
    "aws_secret_access_key": "AWS_SECRET_ACCESS_KEY",
    "aws_session_token": "AWS_SESSION_TOKEN",
    "region": "AWS_DEFAULT_REGION",
}
for required in ("aws_access_key_id", "aws_secret_access_key"):
    if not credentials.get(required):
        raise SystemExit(f"STORAGE_CREDENTIALS is missing {required}")

lines = []
for key, environment_name in mapping.items():
    value = credentials.get(key)
    if value:
        if not isinstance(value, str) or "\n" in value or "\r" in value:
            raise SystemExit(f"Invalid value for {key}")
        if key != "region":
            print(f"::add-mask::{value}")
        lines.append(f"{environment_name}={value}\n")
with Path(os.environ["GITHUB_ENV"]).open("a", encoding="utf-8") as destination:
    destination.writelines(lines)
print("AWS credentials configured.")
