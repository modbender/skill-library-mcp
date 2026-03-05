#!/usr/bin/env python3
"""CircleCI CLI — CircleCI CI/CD — manage pipelines, workflows, jobs, and insights via REST API

Zero dependencies beyond Python stdlib.
Built by M. Abidi | agxntsix.ai
"""

import argparse, json, os, sys, urllib.request, urllib.error, urllib.parse

API_BASE = "https://circleci.com/api/v2"

def get_env(name):
    val = os.environ.get(name, "")
    if not val:
        env_path = os.path.join(os.environ.get("WORKSPACE", os.path.expanduser("~/.openclaw/workspace")), ".env")
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith(name + "="):
                        val = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break
    if not val:
        print(f"Error: {name} not set", file=sys.stderr)
        sys.exit(1)
    return val


def get_headers():
    token = get_env("CIRCLECI_TOKEN")
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json", "Accept": "application/json"}



def get_api_base():
    base = API_BASE
    pass
    return base

def req(method, path, data=None, params=None):
    headers = get_headers()
    if path.startswith("http"):
        url = path
    else:
        url = get_api_base() + path
    if params:
        qs = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
        if qs:
            url = f"{url}?{qs}" if "?" not in url else f"{url}&{qs}"
    body = json.dumps(data).encode() if data else None
    r = urllib.request.Request(url, data=body, method=method)
    for k, v in headers.items():
        r.add_header(k, v)
    try:
        resp = urllib.request.urlopen(r, timeout=30)
        raw = resp.read().decode()
        return json.loads(raw) if raw.strip() else {"ok": True}
    except urllib.error.HTTPError as e:
        err_body = e.read().decode()
        print(json.dumps({"error": True, "code": e.code, "message": err_body}), file=sys.stderr)
        sys.exit(1)


def try_json(val):
    if val is None:
        return None
    try:
        return json.loads(val)
    except (json.JSONDecodeError, ValueError):
        return val


def out(data, human=False):
    if human and isinstance(data, dict):
        for k, v in data.items():
            print(f"  {k}: {v}")
    elif human and isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                for k, v in item.items():
                    print(f"  {k}: {v}")
                print()
            else:
                print(item)
    else:
        print(json.dumps(data, indent=2, default=str))


def cmd_me(args):
    """Get current user."""
    path = "/me"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_pipelines(args):
    """List pipelines."""
    path = f"/project/{args.slug}/pipeline"
    params = {}
    if getattr(args, "branch", None): params["branch"] = args.branch
    data = req("GET", path, params=params)
    out(data, getattr(args, "human", False))

def cmd_pipeline_get(args):
    """Get pipeline."""
    path = f"/pipeline/{args.id}"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_pipeline_trigger(args):
    """Trigger pipeline."""
    path = f"/project/{args.slug}/pipeline"
    body = {}
    if getattr(args, "branch", None): body["branch"] = try_json(args.branch)
    if getattr(args, "parameters", None): body["parameters"] = try_json(args.parameters)
    data = req("POST", path, data=body)
    out(data, getattr(args, "human", False))

def cmd_pipeline_config(args):
    """Get pipeline config."""
    path = f"/pipeline/{args.id}/config"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_workflows(args):
    """List workflows."""
    path = f"/pipeline/{args.id}/workflow"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_workflow_get(args):
    """Get workflow."""
    path = f"/workflow/{args.id}"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_workflow_cancel(args):
    """Cancel workflow."""
    path = f"/workflow/{args.id}/cancel"
    data = req("POST", path)
    out(data, getattr(args, "human", False))

def cmd_workflow_rerun(args):
    """Rerun workflow."""
    path = f"/workflow/{args.id}/rerun"
    data = req("POST", path)
    out(data, getattr(args, "human", False))

def cmd_jobs(args):
    """List workflow jobs."""
    path = f"/workflow/{args.id}/job"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_job_get(args):
    """Get job details."""
    path = f"/project/{args.slug}/job/{args.job_number}"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_job_cancel(args):
    """Cancel job."""
    path = f"/project/{args.slug}/job/{args.job_number}/cancel"
    data = req("POST", path)
    out(data, getattr(args, "human", False))

def cmd_job_artifacts(args):
    """List job artifacts."""
    path = f"/project/{args.slug}/{args.job_number}/artifacts"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_insights_workflows(args):
    """Workflow insights."""
    path = f"/insights/{args.slug}/workflows"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_contexts(args):
    """List contexts."""
    path = "/context"
    params = {}
    if getattr(args, "owner_id", None): params["owner_id"] = args.owner_id
    data = req("GET", path, params=params)
    out(data, getattr(args, "human", False))

def cmd_envvars(args):
    """List project env vars."""
    path = f"/project/{args.slug}/envvar"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_envvar_set(args):
    """Set env var."""
    path = f"/project/{args.slug}/envvar"
    body = {}
    if getattr(args, "name", None): body["name"] = try_json(args.name)
    if getattr(args, "value", None): body["value"] = try_json(args.value)
    data = req("POST", path, data=body)
    out(data, getattr(args, "human", False))



def main():
    parser = argparse.ArgumentParser(description="CircleCI CLI")
    parser.add_argument("--human", action="store_true", help="Human-readable output")
    sub = parser.add_subparsers(dest="command")

    me_p = sub.add_parser("me", help="Get current user")
    me_p.set_defaults(func=cmd_me)

    pipelines_p = sub.add_parser("pipelines", help="List pipelines")
    pipelines_p.add_argument("slug", help="Project slug (gh/org/repo)")
    pipelines_p.add_argument("--branch", help="Branch", default=None)
    pipelines_p.set_defaults(func=cmd_pipelines)

    pipeline_get_p = sub.add_parser("pipeline-get", help="Get pipeline")
    pipeline_get_p.add_argument("id", help="Pipeline ID")
    pipeline_get_p.set_defaults(func=cmd_pipeline_get)

    pipeline_trigger_p = sub.add_parser("pipeline-trigger", help="Trigger pipeline")
    pipeline_trigger_p.add_argument("slug", help="Project slug")
    pipeline_trigger_p.add_argument("--branch", help="Branch", default=None)
    pipeline_trigger_p.add_argument("--parameters", help="JSON params", default=None)
    pipeline_trigger_p.set_defaults(func=cmd_pipeline_trigger)

    pipeline_config_p = sub.add_parser("pipeline-config", help="Get pipeline config")
    pipeline_config_p.add_argument("id", help="Pipeline ID")
    pipeline_config_p.set_defaults(func=cmd_pipeline_config)

    workflows_p = sub.add_parser("workflows", help="List workflows")
    workflows_p.add_argument("id", help="Pipeline ID")
    workflows_p.set_defaults(func=cmd_workflows)

    workflow_get_p = sub.add_parser("workflow-get", help="Get workflow")
    workflow_get_p.add_argument("id", help="Workflow ID")
    workflow_get_p.set_defaults(func=cmd_workflow_get)

    workflow_cancel_p = sub.add_parser("workflow-cancel", help="Cancel workflow")
    workflow_cancel_p.add_argument("id", help="Workflow ID")
    workflow_cancel_p.set_defaults(func=cmd_workflow_cancel)

    workflow_rerun_p = sub.add_parser("workflow-rerun", help="Rerun workflow")
    workflow_rerun_p.add_argument("id", help="Workflow ID")
    workflow_rerun_p.set_defaults(func=cmd_workflow_rerun)

    jobs_p = sub.add_parser("jobs", help="List workflow jobs")
    jobs_p.add_argument("id", help="Workflow ID")
    jobs_p.set_defaults(func=cmd_jobs)

    job_get_p = sub.add_parser("job-get", help="Get job details")
    job_get_p.add_argument("slug", help="Project slug")
    job_get_p.add_argument("job_number", help="Job number")
    job_get_p.set_defaults(func=cmd_job_get)

    job_cancel_p = sub.add_parser("job-cancel", help="Cancel job")
    job_cancel_p.add_argument("slug", help="Slug")
    job_cancel_p.add_argument("job_number", help="Job number")
    job_cancel_p.set_defaults(func=cmd_job_cancel)

    job_artifacts_p = sub.add_parser("job-artifacts", help="List job artifacts")
    job_artifacts_p.add_argument("slug", help="Slug")
    job_artifacts_p.add_argument("job_number", help="Job number")
    job_artifacts_p.set_defaults(func=cmd_job_artifacts)

    insights_workflows_p = sub.add_parser("insights-workflows", help="Workflow insights")
    insights_workflows_p.add_argument("slug", help="Project slug")
    insights_workflows_p.set_defaults(func=cmd_insights_workflows)

    contexts_p = sub.add_parser("contexts", help="List contexts")
    contexts_p.add_argument("--owner_id", help="Owner ID", default=None)
    contexts_p.set_defaults(func=cmd_contexts)

    envvars_p = sub.add_parser("envvars", help="List project env vars")
    envvars_p.add_argument("slug", help="Project slug")
    envvars_p.set_defaults(func=cmd_envvars)

    envvar_set_p = sub.add_parser("envvar-set", help="Set env var")
    envvar_set_p.add_argument("slug", help="Slug")
    envvar_set_p.add_argument("--name", help="Name", default=None)
    envvar_set_p.add_argument("--value", help="Value", default=None)
    envvar_set_p.set_defaults(func=cmd_envvar_set)


    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
