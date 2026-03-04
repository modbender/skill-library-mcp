"""EKS/ECS compliance checks: cluster encryption, logging."""


def run_eks_ecs_checks(session, region="us-east-1"):
    """Run all container service checks and return findings."""
    findings = []
    findings.extend(_check_eks(session, region))
    findings.extend(_check_ecs(session, region))

    passed = sum(1 for f in findings if f["status"] == "pass")
    return {
        "check": "eks_ecs",
        "provider": "aws",
        "status": "pass" if not findings or passed == len(findings) else "fail",
        "total": len(findings),
        "passed": passed,
        "failed": len(findings) - passed,
        "findings": findings,
    }


def _check_eks(session, region):
    """Check EKS cluster security settings."""
    eks = session.client("eks", region_name=region)
    findings = []

    try:
        clusters = eks.list_clusters()["clusters"]
    except Exception:
        return []

    for cluster_name in clusters:
        try:
            cluster = eks.describe_cluster(name=cluster_name)["cluster"]

            # Encryption
            enc_config = cluster.get("encryptionConfig", [])
            has_encryption = len(enc_config) > 0
            findings.append({
                "resource": f"eks/{cluster_name}/encryption",
                "status": "pass" if has_encryption else "fail",
                "detail": f"Secrets encryption: {'enabled' if has_encryption else 'not enabled'}",
            })

            # Logging
            logging_config = cluster.get("logging", {}).get("clusterLogging", [])
            enabled_types = []
            for lc in logging_config:
                if lc.get("enabled"):
                    enabled_types.extend(lc.get("types", []))
            findings.append({
                "resource": f"eks/{cluster_name}/logging",
                "status": "pass" if enabled_types else "fail",
                "detail": f"Logging types: {', '.join(enabled_types)}" if enabled_types else "No logging enabled",
            })

            # Public endpoint
            vpc_config = cluster.get("resourcesVpcConfig", {})
            public_access = vpc_config.get("endpointPublicAccess", True)
            findings.append({
                "resource": f"eks/{cluster_name}/public-endpoint",
                "status": "fail" if public_access else "pass",
                "detail": f"Public endpoint: {'enabled' if public_access else 'disabled'}",
            })
        except Exception:
            continue

    return findings


def _check_ecs(session, region):
    """Check ECS cluster settings."""
    ecs = session.client("ecs", region_name=region)
    findings = []

    try:
        cluster_arns = ecs.list_clusters()["clusterArns"]
        if not cluster_arns:
            return []

        clusters = ecs.describe_clusters(
            clusters=cluster_arns,
            include=["SETTINGS"],
        )["clusters"]

        for cluster in clusters:
            name = cluster["clusterName"]
            settings = {s["name"]: s["value"] for s in cluster.get("settings", [])}
            container_insights = settings.get("containerInsights") == "enabled"
            findings.append({
                "resource": f"ecs/{name}/container-insights",
                "status": "pass" if container_insights else "fail",
                "detail": f"Container Insights: {'enabled' if container_insights else 'disabled'}",
            })
    except Exception:
        pass  # ECS may not be available or access denied

    return findings
