#!/usr/bin/env python3
"""
Recruiter profile and jobs viewer.
View your published jobs and matched candidates.
"""
import sys
import json
from base import AuthenticatedClient, DEFAULT_API


def get_jobs(api_url):
    """Get all published jobs by this recruiter."""
    client = AuthenticatedClient(api_url, "RECRUITER")
    result = client.get("/jobs/my-jobs")
    return result


def get_job_detail(api_url, job_id):
    """Get details of a specific job."""
    client = AuthenticatedClient(api_url, "RECRUITER")
    result = client.get(f"/jobs/{job_id}")
    return result


def get_job_matches(api_url, job_id):
    """Get matched candidates for a specific job."""
    client = AuthenticatedClient(api_url, "RECRUITER")
    result = client.get(f"/matches/job/{job_id}")
    return result


def get_all_matches(api_url):
    """Get all matches across all jobs."""
    client = AuthenticatedClient(api_url, "RECRUITER")

    # First get all jobs
    jobs_result = client.get("/jobs/my-jobs")

    if not jobs_result.get("success"):
        return jobs_result

    jobs = jobs_result.get("result", [])

    # Get matches for each job
    all_matches = {}
    for job in jobs:
        job_id = job.get("id")
        try:
            matches_result = client.get(f"/matches/job/{job_id}")
            all_matches[job_id] = {
                "job": job,
                "matches": matches_result.get("result", [])
            }
        except Exception as e:
            all_matches[job_id] = {
                "job": job,
                "matches": [],
                "error": str(e)
            }

    return {
        "success": True,
        "result": all_matches
    }


def get_full_info(api_url, job_id=None):
    """Get complete information: jobs + matches."""
    client = AuthenticatedClient(api_url, "RECRUITER")

    if job_id:
        # Get specific job and its matches
        job_result = client.get(f"/jobs/{job_id}")
        matches_result = client.get(f"/matches/job/{job_id}")

        return {
            "success": True,
            "result": {
                "job": job_result.get("result"),
                "matches": matches_result.get("result")
            }
        }
    else:
        # Get all jobs and all matches
        return get_all_matches(api_url)


# Action handlers
ACTIONS = {
    "jobs": get_jobs,
    "job": get_job_detail,
    "matches": get_job_matches,
    "all-matches": get_all_matches,
    "full": get_full_info,
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
                "error": "Usage: get_profile.py <json> (or pipe json to stdin)\n"
                         "Actions: jobs, job (requires jobId), matches (requires jobId), all-matches, full"
            }))
            sys.exit(1)

        # Extract parameters
        api_url = data.pop("apiUrl", DEFAULT_API)
        action = data.pop("action", "full")
        job_id = data.get("jobId")

        # Execute action
        fn = ACTIONS.get(action)
        if not fn:
            print(json.dumps({
                "success": False,
                "error": f"Unknown action: {action}. Use: {', '.join(ACTIONS)}"
            }))
            sys.exit(1)

        # Call function with appropriate parameters
        if action in ["job", "matches"]:
            if not job_id:
                print(json.dumps({
                    "success": False,
                    "error": f"Action '{action}' requires jobId parameter"
                }))
                sys.exit(1)
            result = fn(api_url, job_id)
        elif action == "full" and job_id:
            result = fn(api_url, job_id)
        else:
            result = fn(api_url)

        print(json.dumps(result, ensure_ascii=False, indent=2))

    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))
        sys.exit(1)
