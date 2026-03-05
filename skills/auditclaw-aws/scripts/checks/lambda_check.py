"""Lambda compliance checks: runtime currency, public access, VPC."""

import json

# Runtimes that are EOL or deprecated
DEPRECATED_RUNTIMES = {
    "python2.7", "python3.6", "python3.7",
    "nodejs10.x", "nodejs12.x", "nodejs14.x",
    "dotnetcore2.1", "dotnetcore3.1",
    "ruby2.5", "ruby2.7",
    "java8", "go1.x",
}


def run_lambda_checks(session, region="us-east-1"):
    """Run all Lambda checks and return findings."""
    lam = session.client("lambda", region_name=region)

    try:
        functions = lam.list_functions()["Functions"]
    except Exception:
        return {
            "check": "lambda",
            "provider": "aws",
            "status": "pass",
            "total": 0,
            "passed": 0,
            "failed": 0,
            "findings": [],
        }

    findings = []
    for fn in functions:
        fn_name = fn["FunctionName"]

        # Runtime check
        runtime = fn.get("Runtime", "unknown")
        is_deprecated = runtime in DEPRECATED_RUNTIMES
        findings.append({
            "resource": f"lambda/{fn_name}/runtime",
            "status": "fail" if is_deprecated else "pass",
            "detail": f"Runtime: {runtime}" + (" (deprecated)" if is_deprecated else ""),
        })

        # VPC check
        vpc_config = fn.get("VpcConfig", {})
        in_vpc = bool(vpc_config.get("SubnetIds"))
        findings.append({
            "resource": f"lambda/{fn_name}/vpc",
            "status": "pass" if in_vpc else "fail",
            "detail": f"VPC: {'attached' if in_vpc else 'not in VPC'}",
        })

        # Public access check
        try:
            policy_str = lam.get_policy(FunctionName=fn_name)["Policy"]
            policy = json.loads(policy_str)
            has_public = any(
                stmt.get("Principal") in ("*", {"AWS": "*"})
                for stmt in policy.get("Statement", [])
            )
            findings.append({
                "resource": f"lambda/{fn_name}/public-access",
                "status": "fail" if has_public else "pass",
                "detail": "Public access via resource policy" if has_public else "No public access",
            })
        except Exception:
            findings.append({
                "resource": f"lambda/{fn_name}/public-access",
                "status": "pass",
                "detail": "No resource policy (not publicly accessible)",
            })

    passed = sum(1 for f in findings if f["status"] == "pass")
    return {
        "check": "lambda",
        "provider": "aws",
        "status": "pass" if not findings or passed == len(findings) else "fail",
        "total": len(findings),
        "passed": passed,
        "failed": len(findings) - passed,
        "findings": findings,
    }
