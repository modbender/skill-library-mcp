"""EC2 compliance checks: IMDSv2, EBS encryption, public IPs."""


def run_ec2_checks(session, region="us-east-1"):
    """Run all EC2 checks and return findings."""
    findings = []
    findings.extend(_check_imdsv2(session, region))
    findings.extend(_check_ebs_encryption(session, region))
    findings.extend(_check_public_ips(session, region))

    passed = sum(1 for f in findings if f["status"] == "pass")
    return {
        "check": "ec2",
        "provider": "aws",
        "status": "pass" if not findings or passed == len(findings) else "fail",
        "total": len(findings),
        "passed": passed,
        "failed": len(findings) - passed,
        "findings": findings,
    }


def _check_imdsv2(session, region):
    """Check that all EC2 instances require IMDSv2."""
    ec2 = session.client("ec2", region_name=region)
    instances = ec2.describe_instances()
    findings = []
    for reservation in instances["Reservations"]:
        for inst in reservation["Instances"]:
            inst_id = inst["InstanceId"]
            metadata_options = inst.get("MetadataOptions", {})
            http_tokens = metadata_options.get("HttpTokens", "optional")
            required = http_tokens == "required"
            findings.append({
                "resource": f"ec2/{inst_id}/imdsv2",
                "status": "pass" if required else "fail",
                "detail": f"IMDSv2: {'required' if required else 'optional (insecure)'}",
            })
    return findings


def _check_ebs_encryption(session, region):
    """Check that all EBS volumes are encrypted."""
    ec2 = session.client("ec2", region_name=region)
    volumes = ec2.describe_volumes()["Volumes"]
    findings = []
    for vol in volumes:
        vol_id = vol["VolumeId"]
        encrypted = vol.get("Encrypted", False)
        findings.append({
            "resource": f"ebs/{vol_id}",
            "status": "pass" if encrypted else "fail",
            "detail": f"Encryption: {'enabled' if encrypted else 'disabled'}",
        })
    return findings


def _check_public_ips(session, region):
    """Check for EC2 instances with public IP addresses."""
    ec2 = session.client("ec2", region_name=region)
    instances = ec2.describe_instances()
    findings = []
    for reservation in instances["Reservations"]:
        for inst in reservation["Instances"]:
            inst_id = inst["InstanceId"]
            public_ip = inst.get("PublicIpAddress")
            findings.append({
                "resource": f"ec2/{inst_id}/public-ip",
                "status": "fail" if public_ip else "pass",
                "detail": f"Public IP: {public_ip}" if public_ip else "No public IP",
            })
    return findings
