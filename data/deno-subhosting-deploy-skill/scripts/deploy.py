#!/usr/bin/env python3
"""
Standalone Deno Deploy script.
Reads credentials from ~/.config/deno-deploy/{access_token,org_id}.

Usage:
  python deploy.py --name <project-name> --code <path-to-code-file>
  python deploy.py --name <project-name> --code-string '<inline code>'
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error

API = "https://api.deno.com/v1"
CONFIG_DIR = os.path.expanduser("~/.config/deno-deploy")


def get_credentials():
    token_path = os.path.join(CONFIG_DIR, "access_token")
    org_id_path = os.path.join(CONFIG_DIR, "org_id")
    if not os.path.exists(token_path) or not os.path.exists(org_id_path):
        print("ERROR: Deno Deploy credentials not found.")
        print()
        print("1. Create a Deno Subhosting org at: https://dash.deno.com/subhosting/new_auto")
        print("2. Copy the org ID and access token from the org dashboard")
        print("3. Save them:")
        print(f"   mkdir -p {CONFIG_DIR}")
        print(f'   echo "your_token_here" > {token_path}')
        print(f'   echo "your_org_id_here" > {org_id_path}')
        sys.exit(1)
    token = open(token_path).read().strip()
    org_id = open(org_id_path).read().strip()
    return token, org_id


def api_request(method, path, token, body=None):
    url = f"{API}{path}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"ERROR: HTTP {e.code} from Deno API")
        print(error_body)
        sys.exit(1)


def deploy(project_name, code, entry_point="main.ts", env_vars=None, description=None):
    token, org_id = get_credentials()

    # Step 1: Create project
    print(f"Creating project '{project_name}'...")
    body = {"name": project_name}
    if description:
        body["description"] = description
    project = api_request("POST", f"/organizations/{org_id}/projects", token, body)
    project_id = project["id"]
    project_name_actual = project["name"]
    print(f"  Project created: {project_name_actual} (id: {project_id})")

    # Step 2: Create deployment
    print("Deploying code...")
    deployment_body = {
        "entryPointUrl": entry_point,
        "assets": {
            entry_point: {
                "kind": "file",
                "content": code,
                "encoding": "utf-8",
            }
        },
        "envVars": env_vars or {},
    }
    if description:
        deployment_body["description"] = description
    deployment = api_request("POST", f"/projects/{project_id}/deployments", token, deployment_body)

    deployment_id = deployment.get("id", "")
    status = deployment.get("status", "unknown")
    domains = deployment.get("domains", [])
    url = f"https://{project_name_actual}.deno.dev"

    print(f"\n--- Deployment Response ---")
    print(json.dumps(deployment, indent=2))
    print(f"---")

    if status == "failed":
        print(f"\n❌ Deployment failed!")
        print(f"   Status: {status}")
        print(f"   Check the response above for error details.")
        sys.exit(1)

    print(f"\n✅ Deployed successfully!")
    print(f"   URL: {url}")
    print(f"   Deployment ID: {deployment_id}")
    print(f"   Status: {status}")
    if domains:
        print(f"   Domains: {', '.join(domains)}")
    print(f"\n⚠️  IMPORTANT: Verify the deployment by visiting the URL above.")
    print(f"   If the page shows an error, check the deployment logs at:")
    print(f"   https://dash.deno.com/projects/{project_name_actual}/deployments/{deployment_id}")
    return {"url": url, "deployment_id": deployment_id, "status": status, "project_id": project_id, "project_name": project_name_actual}


def main():
    parser = argparse.ArgumentParser(description="Deploy code to Deno Deploy")
    parser.add_argument("--name", required=True, help="Project name (kebab-case)")
    parser.add_argument("--code", help="Path to TypeScript/JS file to deploy")
    parser.add_argument("--code-string", help="Inline code string to deploy")
    parser.add_argument("--entry-point", default="main.ts", help="Entry point filename (default: main.ts)")
    parser.add_argument("--description", help="Project description")
    args = parser.parse_args()

    if args.code:
        with open(args.code) as f:
            code = f.read()
    elif args.code_string:
        code = args.code_string
    else:
        print("ERROR: Provide either --code <file> or --code-string '<code>'")
        sys.exit(1)

    deploy(args.name, code, args.entry_point, description=args.description)


if __name__ == "__main__":
    main()