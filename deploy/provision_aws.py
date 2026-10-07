"""Create the lab's private S3 bucket, scoped roles and one Ubuntu EC2 instance.

Run from the repository root after AWS CLI console login and gh auth login.
The SSH key stays in ignored .secrets/. No AWS access key is created.
"""
import argparse
import ipaddress
import json
from pathlib import Path
import subprocess
import sys
from urllib.request import urlopen

AWS = r"C:\Program Files\Amazon\AWSCLIV2\aws.exe"
GH = r"C:\Program Files\GitHub CLI\gh.exe"
ROOT = Path(__file__).resolve().parents[1]
REPO = "khangduong2k4het-netizen/K4-L3L4-Track2-Day21-DuongDatKhang-2A202602624-CI-CD-for-AI-Systems"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default="income-lab")
    parser.add_argument("--region", default="ap-southeast-1")
    args = parser.parse_args()
    private = ROOT / ".secrets"
    private.mkdir(exist_ok=True)

    def aws(*command, optional=False):
        result = subprocess.run(
            [AWS, *command, "--profile", args.profile, "--region", args.region,
             "--output", "json", "--no-cli-pager"],
            capture_output=True, text=True, encoding="utf-8",
        )
        if result.returncode:
            if optional and any(code in result.stderr for code in (
                "NoSuchEntity", "NoSuchBucket", "404", "InvalidKeyPair.NotFound",
            )):
                return None
            raise RuntimeError(result.stderr.strip())
        return json.loads(result.stdout) if result.stdout.strip() else {}

    def document(name, value):
        path = private / name
        path.write_text(json.dumps(value), encoding="utf-8")
        return "file://" + str(path)

    account = aws("sts", "get-caller-identity")["Account"]
    bucket = f"income-lab-{account}-{args.region}"
    tags = [{"Key": "Project", "Value": "income-lab-day21"}]
    if aws("s3api", "head-bucket", "--bucket", bucket, optional=True) is None:
        command = ["s3api", "create-bucket", "--bucket", bucket]
        if args.region != "us-east-1":
            command += ["--create-bucket-configuration", f"LocationConstraint={args.region}"]
        aws(*command)
    aws("s3api", "put-public-access-block", "--bucket", bucket,
        "--public-access-block-configuration", "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true")
    aws("s3api", "put-bucket-tagging", "--bucket", bucket,
        "--tagging", document("bucket-tags.json", {"TagSet": tags}))
    print(f"Private S3 bucket ready: {bucket}", flush=True)

    provider = f"arn:aws:iam::{account}:oidc-provider/token.actions.githubusercontent.com"
    if aws("iam", "get-open-id-connect-provider", "--open-id-connect-provider-arn", provider, optional=True) is None:
        aws("iam", "create-open-id-connect-provider", "--url", "https://token.actions.githubusercontent.com",
            "--client-id-list", "sts.amazonaws.com")
    info = json.loads(subprocess.check_output([GH, "api", f"repos/{REPO}"], text=True, encoding="utf-8"))
    owner, repo_name = REPO.split("/")
    subjects = [
        f"repo:{REPO}:ref:refs/heads/main",
        f"repo:{owner}@{info['owner']['id']}/{repo_name}@{info['id']}:ref:refs/heads/main",
    ]
    ci_trust = {"Version": "2012-10-17", "Statement": [{
        "Effect": "Allow", "Principal": {"Federated": provider},
        "Action": "sts:AssumeRoleWithWebIdentity", "Condition": {"StringEquals": {
            "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
            "token.actions.githubusercontent.com:sub": subjects,
        }},
    }]}
    ec2_trust = {"Version": "2012-10-17", "Statement": [{
        "Effect": "Allow", "Principal": {"Service": "ec2.amazonaws.com"}, "Action": "sts:AssumeRole",
    }]}
    for name, trust in [("income-lab-github", ci_trust), ("income-lab-ec2-reader", ec2_trust)]:
        existing = aws("iam", "get-role", "--role-name", name, optional=True)
        if existing is None:
            aws("iam", "create-role", "--role-name", name,
                "--assume-role-policy-document", document(name + "-trust.json", trust))
        else:
            aws("iam", "update-assume-role-policy", "--role-name", name,
                "--policy-document", document(name + "-trust.json", trust))
    ci_policy = {"Version": "2012-10-17", "Statement": [
        {"Effect": "Allow", "Action": ["s3:ListBucket", "s3:GetBucketLocation"], "Resource": f"arn:aws:s3:::{bucket}"},
        {"Effect": "Allow", "Action": ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"],
         "Resource": [f"arn:aws:s3:::{bucket}/dvc/*", f"arn:aws:s3:::{bucket}/artifacts/current/*", f"arn:aws:s3:::{bucket}/deployments/*"]},
    ]}
    ec2_policy = {"Version": "2012-10-17", "Statement": [{
        "Effect": "Allow", "Action": "s3:GetObject", "Resource": [f"arn:aws:s3:::{bucket}/artifacts/current/model.joblib", f"arn:aws:s3:::{bucket}/deployments/*"],
    }]}
    for role, policy in [("income-lab-github", ci_policy), ("income-lab-ec2-reader", ec2_policy)]:
        aws("iam", "put-role-policy", "--role-name", role, "--policy-name", "income-lab-s3",
            "--policy-document", document(role + "-policy.json", policy))
    profile_name = "income-lab-ec2-reader"
    instance_profile = aws("iam", "get-instance-profile", "--instance-profile-name", profile_name, optional=True)
    if instance_profile is None:
        aws("iam", "create-instance-profile", "--instance-profile-name", profile_name)
        aws("iam", "add-role-to-instance-profile", "--instance-profile-name", profile_name, "--role-name", profile_name)
    elif not instance_profile["InstanceProfile"]["Roles"]:
        aws("iam", "add-role-to-instance-profile", "--instance-profile-name", profile_name, "--role-name", profile_name)
    print("Scoped GitHub OIDC and EC2 instance roles ready.", flush=True)

    vpcs = aws("ec2", "describe-vpcs", "--filters", "Name=is-default,Values=true")["Vpcs"]
    if not vpcs:
        raise RuntimeError("No default VPC; select an existing public VPC before launching")
    vpc = vpcs[0]["VpcId"]
    groups = aws("ec2", "describe-security-groups", "--filters", f"Name=vpc-id,Values={vpc}",
                 "Name=group-name,Values=income-lab-api")["SecurityGroups"]
    group = groups[0]["GroupId"] if groups else aws(
        "ec2", "create-security-group", "--group-name", "income-lab-api", "--description", "Day21 lab SSH and API", "--vpc-id", vpc,
    )["GroupId"]
    public_ip = str(ipaddress.IPv4Address(urlopen("https://checkip.amazonaws.com", timeout=15).read().decode().strip()))
    existing_ports = {p.get("FromPort") for p in aws("ec2", "describe-security-groups", "--group-ids", group)["SecurityGroups"][0]["IpPermissions"]}
    for port, cidr in [(22, public_ip + "/32"), (8080, "0.0.0.0/0")]:
        if port not in existing_ports:
            aws("ec2", "authorize-security-group-ingress", "--group-id", group,
                "--protocol", "tcp", "--port", str(port), "--cidr", cidr)
    aws("ec2", "create-tags", "--resources", group, "--tags", "Key=Project,Value=income-lab-day21")
    key = private / "income-lab.pem"
    if not key.exists():
        subprocess.run(["ssh-keygen", "-t", "rsa", "-b", "3072", "-f", str(key), "-N", "", "-C", "income-lab-day21"], check=True, capture_output=True)
    if aws("ec2", "describe-key-pairs", "--key-names", "income-lab-day21", optional=True) is None:
        aws("ec2", "import-key-pair", "--key-name", "income-lab-day21", "--public-key-material", "fileb://" + str(key) + ".pub")
    existing = aws("ec2", "describe-instances", "--filters", "Name=tag:Project,Values=income-lab-day21",
                   "Name=instance-state-name,Values=pending,running,stopping,stopped")["Reservations"]
    if existing:
        instance = existing[0]["Instances"][0]
    else:
        subnets = aws("ec2", "describe-subnets", "--filters", f"Name=vpc-id,Values={vpc}", "Name=default-for-az,Values=true")["Subnets"]
        if not subnets:
            raise RuntimeError("No default public subnet found")
        ami = aws("ssm", "get-parameter", "--name", "/aws/service/canonical/ubuntu/server/22.04/stable/current/amd64/hvm/ebs-gp2/ami-id")["Parameter"]["Value"]
        instance = aws("ec2", "run-instances", "--image-id", ami, "--instance-type", "t3.small", "--count", "1",
            "--key-name", "income-lab-day21", "--iam-instance-profile", f"Name={profile_name}",
            "--network-interfaces", json.dumps([{"DeviceIndex": 0, "SubnetId": subnets[0]["SubnetId"], "Groups": [group], "AssociatePublicIpAddress": True}]),
            "--block-device-mappings", json.dumps([{"DeviceName": "/dev/sda1", "Ebs": {"VolumeSize": 20, "VolumeType": "gp3", "Encrypted": True, "DeleteOnTermination": True}}]),
            "--metadata-options", "HttpTokens=required,HttpEndpoint=enabled", "--credit-specification", "CpuCredits=standard",
            "--tag-specifications", json.dumps([
                {"ResourceType": "instance", "Tags": tags + [{"Key": "Name", "Value": "income-lab-api"}]},
                {"ResourceType": "volume", "Tags": tags},
            ]), "--client-token", "income-lab-day21-api-v1",
        )["Instances"][0]
    ci_policy["Statement"] += [
        {"Effect": "Allow", "Action": "ssm:SendCommand", "Resource": [
            f"arn:aws:ec2:{args.region}:{account}:instance/{instance['InstanceId']}",
            f"arn:aws:ssm:{args.region}::document/AWS-RunShellScript",
        ]},
        {"Effect": "Allow", "Action": "ssm:GetCommandInvocation", "Resource": "*"},
    ]
    aws("iam", "put-role-policy", "--role-name", "income-lab-github", "--policy-name", "income-lab-s3",
        "--policy-document", document("income-lab-github-policy.json", ci_policy))
    aws("iam", "attach-role-policy", "--role-name", "income-lab-ec2-reader",
        "--policy-arn", "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore")
    metadata = {"account": account, "region": args.region, "bucket": bucket,
                "instance_id": instance["InstanceId"], "security_group": group,
                "ssh_cidr": public_ip + "/32",
                "ci_role_arn": f"arn:aws:iam::{account}:role/income-lab-github", "ssh_user": "ubuntu"}
    output = ROOT / "outputs/deployment.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(json.dumps(metadata, indent=2), flush=True)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
