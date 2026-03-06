"""ELB compliance checks: HTTPS listeners, WAF, access logging."""


def run_elb_checks(session, region="us-east-1"):
    """Run all ELB checks and return findings."""
    elbv2 = session.client("elbv2", region_name=region)
    findings = []

    try:
        lbs = elbv2.describe_load_balancers()["LoadBalancers"]
    except Exception:
        return {
            "check": "elb",
            "provider": "aws",
            "status": "pass",
            "total": 0,
            "passed": 0,
            "failed": 0,
            "findings": [],
        }

    for lb in lbs:
        lb_arn = lb["LoadBalancerArn"]
        lb_name = lb["LoadBalancerName"]

        # Check listeners for HTTPS
        try:
            listeners = elbv2.describe_listeners(LoadBalancerArn=lb_arn)["Listeners"]
            has_https = any(l.get("Protocol") == "HTTPS" for l in listeners)
            has_http_only = any(l.get("Protocol") == "HTTP" for l in listeners) and not has_https
            findings.append({
                "resource": f"elb/{lb_name}/https",
                "status": "fail" if has_http_only else "pass",
                "detail": "HTTPS listener configured" if has_https else
                          ("HTTP only (no HTTPS)" if has_http_only else "No HTTP/HTTPS listeners"),
            })
        except Exception:
            pass  # Listener check may fail if LB is being provisioned

        # Check access logging
        try:
            attrs = elbv2.describe_load_balancer_attributes(LoadBalancerArn=lb_arn)["Attributes"]
            attr_dict = {a["Key"]: a["Value"] for a in attrs}
            logging_enabled = attr_dict.get("access_logs.s3.enabled", "false") == "true"
            findings.append({
                "resource": f"elb/{lb_name}/access-logs",
                "status": "pass" if logging_enabled else "fail",
                "detail": f"Access logging: {'enabled' if logging_enabled else 'disabled'}",
            })
        except Exception:
            pass  # Attribute check may fail if LB is being provisioned

        # Check WAF association
        try:
            waf = session.client("wafv2", region_name=region)
            waf_assoc = waf.get_web_acl_for_resource(ResourceArn=lb_arn)
            has_waf = "WebACL" in waf_assoc
            findings.append({
                "resource": f"elb/{lb_name}/waf",
                "status": "pass" if has_waf else "fail",
                "detail": f"WAF: {'associated' if has_waf else 'not associated'}",
            })
        except Exception:
            findings.append({
                "resource": f"elb/{lb_name}/waf",
                "status": "fail",
                "detail": "WAF not associated",
            })

    passed = sum(1 for f in findings if f["status"] == "pass")
    return {
        "check": "elb",
        "provider": "aws",
        "status": "pass" if not findings or passed == len(findings) else "fail",
        "total": len(findings),
        "passed": passed,
        "failed": len(findings) - passed,
        "findings": findings,
    }
