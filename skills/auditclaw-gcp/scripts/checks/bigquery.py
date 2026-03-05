"""GCP BigQuery checks: no public dataset access (allUsers/allAuthenticatedUsers)."""

from google.cloud import bigquery


def run_bigquery_checks(project_id):
    """Run BigQuery public access checks and return findings.

    Args:
        project_id: GCP project ID.

    Returns:
        Standard result dict with check, provider, status, total, passed, failed, findings.
    """
    findings = []
    public_entities = {"allUsers", "allAuthenticatedUsers"}

    try:
        bq_client = bigquery.Client(project=project_id)
        datasets = list(bq_client.list_datasets())
    except Exception as e:
        return {
            "check": "bigquery",
            "provider": "gcp",
            "status": "fail",
            "total": 1,
            "passed": 0,
            "failed": 1,
            "findings": [{
                "resource": "bigquery/api",
                "status": "fail",
                "detail": f"Could not list datasets: {e}",
            }],
        }

    if not datasets:
        return {
            "check": "bigquery",
            "provider": "gcp",
            "status": "pass",
            "total": 0,
            "passed": 0,
            "failed": 0,
            "findings": [],
        }

    for dataset_ref in datasets:
        try:
            ds = bq_client.get_dataset(dataset_ref.reference)
        except Exception as e:
            findings.append({
                "resource": f"bigquery/{dataset_ref.dataset_id}/access",
                "status": "fail",
                "detail": f"Could not read dataset {dataset_ref.dataset_id}: {e}",
            })
            continue

        has_public = False
        for entry in (ds.access_entries or []):
            entity_id = getattr(entry, "entity_id", None)
            if entity_id in public_entities:
                has_public = True
                break

        ds_id = dataset_ref.dataset_id
        if has_public:
            findings.append({
                "resource": f"bigquery/{ds_id}/public-access",
                "status": "fail",
                "detail": f"Dataset '{ds_id}' has public access (allUsers or allAuthenticatedUsers)",
            })
        else:
            findings.append({
                "resource": f"bigquery/{ds_id}/public-access",
                "status": "pass",
                "detail": f"Dataset '{ds_id}' has no public access entries",
            })

    passed = sum(1 for f in findings if f["status"] == "pass")
    return {
        "check": "bigquery",
        "provider": "gcp",
        "status": "pass" if passed == len(findings) else "fail",
        "total": len(findings),
        "passed": passed,
        "failed": len(findings) - passed,
        "findings": findings,
    }
