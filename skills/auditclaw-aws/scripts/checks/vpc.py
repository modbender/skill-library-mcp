"""VPC compliance checks: flow logs, security groups, NACLs."""


def run_vpc_checks(session, region="us-east-1"):
    """Run all VPC checks and return findings."""
    findings = []
    findings.extend(_check_flow_logs(session, region))
    findings.extend(_check_security_groups(session, region))

    passed = sum(1 for f in findings if f["status"] == "pass")
    return {
        "check": "vpc",
        "provider": "aws",
        "status": "pass" if passed == len(findings) else "fail",
        "total": len(findings),
        "passed": passed,
        "failed": len(findings) - passed,
        "findings": findings,
    }


def _check_flow_logs(session, region):
    """Check that all VPCs have flow logs enabled."""
    ec2 = session.client("ec2", region_name=region)
    vpcs = ec2.describe_vpcs()["Vpcs"]
    flow_logs = ec2.describe_flow_logs()["FlowLogs"]
    vpc_ids_with_logs = {fl["ResourceId"] for fl in flow_logs if fl.get("ResourceId")}

    findings = []
    for vpc in vpcs:
        vpc_id = vpc["VpcId"]
        has_logs = vpc_id in vpc_ids_with_logs
        findings.append({
            "resource": f"vpc/{vpc_id}/flow-logs",
            "status": "pass" if has_logs else "fail",
            "detail": f"Flow logs {'enabled' if has_logs else 'not enabled'}",
        })
    return findings


def _check_security_groups(session, region):
    """Check for overly permissive security group rules."""
    ec2 = session.client("ec2", region_name=region)
    sgs = ec2.describe_security_groups()["SecurityGroups"]

    findings = []
    for sg in sgs:
        sg_id = sg["GroupId"]
        sg_name = sg.get("GroupName", sg_id)

        # Check inbound rules for 0.0.0.0/0
        has_open_inbound = False
        for rule in sg.get("IpPermissions", []):
            for ip_range in rule.get("IpRanges", []):
                if ip_range.get("CidrIp") == "0.0.0.0/0":
                    port = rule.get("FromPort", "all")
                    if port not in (80, 443):  # HTTP/HTTPS are acceptable
                        has_open_inbound = True

        findings.append({
            "resource": f"sg/{sg_name}/{sg_id}",
            "status": "fail" if has_open_inbound else "pass",
            "detail": "Open inbound rules on non-HTTP ports" if has_open_inbound
                      else "No overly permissive inbound rules",
        })
    return findings
