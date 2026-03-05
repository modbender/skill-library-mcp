#!/usr/bin/env python3
"""
Recruiter CLI: publish, update, delete job postings and list matched candidates.
"""
import sys
import json
from base import AuthenticatedClient, DEFAULT_API


JOB_FIELDS = ("title", "companyName", "requirement", "salary", "location", "jobType", "education", "experience")


def publish_job(api_url, data):
    """Publish a new job posting."""
    client = AuthenticatedClient(api_url, "RECRUITER")

    payload = {k: data[k] for k in JOB_FIELDS}
    payload["status"] = data.get("status", "ACTIVE")

    result = client.post("/jobs", payload)
    result["token"] = client.token_manager.get_token()
    return result


def update_job(api_url, data):
    """Update an existing job posting (partial update supported)."""
    client = AuthenticatedClient(api_url, "RECRUITER")

    job_id = data.get("jobId")
    if not job_id:
        return {"success": False, "error": "jobId is required for update"}

    payload = {k: data[k] for k in (*JOB_FIELDS, "status") if k in data}
    if not payload:
        return {"success": False, "error": "No fields to update"}

    result = client.put(f"/jobs/{job_id}", payload)
    result["token"] = client.token_manager.get_token()
    return result


def delete_job(api_url, data):
    """Soft-delete a job posting by setting status to INACTIVE."""
    client = AuthenticatedClient(api_url, "RECRUITER")

    job_id = data.get("jobId")
    if not job_id:
        return {"success": False, "error": "jobId is required for delete"}

    result = client.put(f"/jobs/{job_id}", {"status": "INACTIVE"})
    result["token"] = client.token_manager.get_token()
    return result


def list_matches(api_url, data):
    """List matched candidates for a specific job posting."""
    client = AuthenticatedClient(api_url, "RECRUITER")

    job_id = data.get("jobId")
    if not job_id:
        return {"success": False, "error": "jobId is required for listing matches"}

    result = client.get(f"/matches/job/{job_id}")
    result["token"] = client.token_manager.get_token()
    return result


# Action handlers
ACTIONS = {
    "publish": publish_job,
    "update": update_job,
    "delete": delete_job,
    "matches": list_matches,
}


if __name__ == "__main__":
    try:
        # Parse input
        data = None
        if len(sys.argv) > 1:
            data = json.loads(sys.argv[1])
        elif not sys.stdin.isatty():
            input_data = sys.stdin.read()
            if input_data.strip():
                data = json.loads(input_data)

        if not data:
            print(json.dumps({
                "success": False,
                "error": "Usage: publish_job.py <json> (or pipe json to stdin)"
            }))
            sys.exit(1)

        # Extract parameters
        api_url = data.pop("apiUrl", DEFAULT_API)
        action = data.pop("action", "publish")

        # Execute action
        fn = ACTIONS.get(action)
        if not fn:
            print(json.dumps({
                "success": False,
                "error": f"Unknown action: {action}. Use: {', '.join(ACTIONS)}"
            }))
            sys.exit(1)

        result = fn(api_url, data)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))
        sys.exit(1)
