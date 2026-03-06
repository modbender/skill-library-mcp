#!/usr/bin/env python3
"""
CapRover Deploy Script
======================
Deploy apps to CapRover via GitHub workflow_dispatch or CapRover webhook.

Usage:
    deploy.py --app <name> [--branch <branch>] [--strategy github|webhook|cli]
    deploy.py --list
    deploy.py --status <app>

Examples:
    python3 deploy.py --app laringoscopio
    python3 deploy.py --app laringoscopio --branch feat/new-ui
    python3 deploy.py --app polymarket-insider --strategy webhook
    python3 deploy.py --list
    python3 deploy.py --status laringoscopio
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "config.json"


def load_config():
    if not CONFIG_PATH.exists():
        print(f"❌ Config not found: {CONFIG_PATH}")
        print("   Create it from config.example.json and fill in your credentials.")
        sys.exit(1)
    with open(CONFIG_PATH) as f:
        return json.load(f)


def find_app(config, name):
    """Find app config by name (case-insensitive, fuzzy)."""
    apps = config.get("apps", {})
    name_lower = name.lower().replace("-", "").replace("_", "")

    # Exact match first
    if name in apps:
        return name, apps[name]

    # Fuzzy match
    for key, val in apps.items():
        if key.lower().replace("-", "").replace("_", "") == name_lower:
            return key, val

    # Partial match
    for key, val in apps.items():
        if name_lower in key.lower().replace("-", "").replace("_", ""):
            return key, val

    print(f"❌ App '{name}' not found in config.")
    print(f"   Available apps: {', '.join(apps.keys())}")
    sys.exit(1)


def http_post(url, data=None, headers=None):
    """Simple HTTP POST wrapper."""
    body = json.dumps(data).encode() if data else b""
    req = urllib.request.Request(url, data=body, method="POST")
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as resp:
            status = resp.status
            body = resp.read().decode()
            return status, body
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def http_get(url, headers=None):
    """Simple HTTP GET wrapper."""
    req = urllib.request.Request(url)
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, {}


def strategy_github(config, app_config, branch):
    """Trigger GitHub Actions workflow_dispatch."""
    gh = config.get("github", {})
    token = gh.get("token", "")
    repo = app_config.get("github_repo", "")
    workflow = app_config.get("github_workflow", "deploy.yml")

    if not token:
        print("❌ github.token not configured in config.json")
        return False
    if not repo:
        print("❌ github_repo not configured for this app")
        return False

    ref = branch or app_config.get("default_branch", "main")
    url = f"https://api.github.com/repos/{repo}/actions/workflows/{workflow}/dispatches"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    payload = {"ref": ref}

    print(f"🚀 Triggering GitHub workflow dispatch...")
    print(f"   Repo: {repo}")
    print(f"   Workflow: {workflow}")
    print(f"   Branch/ref: {ref}")

    status, body = http_post(url, payload, headers)

    if status == 204:
        print("✅ Workflow triggered successfully!")
        print(f"   Check progress: https://github.com/{repo}/actions")
        return True
    elif status == 404:
        print(f"❌ Workflow not found: {workflow}")
        print(f"   Make sure the workflow file exists and has 'workflow_dispatch' trigger.")
        print(f"   Check: https://github.com/{repo}/actions")
        return False
    else:
        print(f"❌ GitHub API error {status}: {body}")
        return False


def strategy_webhook(config, app_config):
    """POST to CapRover webhook URL."""
    webhook_url = app_config.get("caprover_webhook_url", "")

    if not webhook_url or "OPTIONAL" in webhook_url or "WEBHOOK_TOKEN" in webhook_url:
        print("❌ caprover_webhook_url not configured for this app")
        print("   Find it in: CapRover Dashboard → App → Deployment tab → Webhook URL")
        return False

    print(f"🚀 Triggering CapRover webhook...")
    print(f"   URL: {webhook_url[:60]}...")

    status, body = http_post(webhook_url)
    if status in (200, 201, 204):
        print("✅ Webhook triggered successfully!")
        return True
    else:
        print(f"❌ Webhook error {status}: {body[:200]}")
        return False


def strategy_cli(config, app_config, branch=None):
    """Deploy via CapRover CLI using App Token."""
    import subprocess

    caprover_url = config.get("caprover", {}).get("url", "")
    app_token = app_config.get("caprover_app_token", "")
    app_name = app_config.get("caprover_app_name", "")

    if not caprover_url or "yourdomain" in caprover_url:
        print("❌ caprover.url not configured")
        return False
    if not app_token or "TOKEN" in app_token:
        print("❌ caprover_app_token not configured for this app")
        return False
    if not app_name:
        print("❌ caprover_app_name not configured for this app")
        return False

    # Check if caprover CLI is installed
    result = subprocess.run(["which", "caprover"], capture_output=True)
    if result.returncode != 0:
        print("❌ caprover CLI not installed. Run: npm install -g caprover")
        return False

    print(f"🚀 Deploying via CapRover CLI...")
    cmd = [
        "caprover", "deploy",
        "--caproverUrl", caprover_url,
        "--appToken", app_token,
        "--appName", app_name,
    ]
    if branch:
        cmd += ["--branch", branch]

    print(f"   App: {app_name}")
    result = subprocess.run(cmd, capture_output=False)
    if result.returncode == 0:
        print("✅ Deployed successfully!")
        return True
    else:
        print("❌ Deploy failed. Check output above.")
        return False


def cmd_list(config):
    """List configured apps."""
    apps = config.get("apps", {})
    if not apps:
        print("No apps configured in config.json")
        return

    print("Configured apps:")
    for name, app in apps.items():
        repo = app.get("github_repo", "—")
        workflow = app.get("github_workflow", "—")
        caprover = app.get("caprover_app_name", "—")
        has_token = "✅" if app.get("caprover_app_token", "").startswith("eyJ") or \
                            (app.get("caprover_app_token") and "TOKEN" not in app.get("caprover_app_token", "")) else "❌"
        has_webhook = "✅" if app.get("caprover_webhook_url") and "WEBHOOK_TOKEN" not in app.get("caprover_webhook_url", "") else "❌"
        print(f"\n  {name}")
        print(f"    GitHub:    {repo} → {workflow}")
        print(f"    CapRover:  {caprover}  token={has_token}  webhook={has_webhook}")


def cmd_status(config, app_name):
    """Check latest deploy status for an app."""
    _, app_config = find_app(config, app_name)
    gh = config.get("github", {})
    token = gh.get("token", "")
    repo = app_config.get("github_repo", "")
    workflow = app_config.get("github_workflow", "deploy.yml")

    if not token or not repo:
        print("❌ GitHub token and repo required to check status")
        return

    url = f"https://api.github.com/repos/{repo}/actions/workflows/{workflow}/runs?per_page=3"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }
    status, data = http_get(url, headers)
    if status != 200:
        print(f"❌ GitHub API error {status}")
        return

    runs = data.get("workflow_runs", [])
    if not runs:
        print("No recent runs found.")
        return

    print(f"Recent deploys for {app_name}:")
    for run in runs[:3]:
        status_icon = {"completed": "✅", "in_progress": "🔄", "queued": "⏳"}.get(run.get("status", ""), "❓")
        conclusion = run.get("conclusion", "—") or "—"
        if conclusion == "failure":
            status_icon = "❌"
        elif conclusion == "success":
            status_icon = "✅"
        created = run.get("created_at", "")[:19]
        branch = run.get("head_branch", "—")
        run_id = run.get("id")
        print(f"  {status_icon} #{run_id} {conclusion} | branch={branch} | {created}")
    print(f"\n  Full history: https://github.com/{repo}/actions")


def main():
    parser = argparse.ArgumentParser(description="CapRover deploy helper")
    parser.add_argument("--app", "-a", help="App name to deploy")
    parser.add_argument("--branch", "-b", help="Branch to deploy (default: app's default_branch)")
    parser.add_argument("--strategy", "-s", choices=["github", "webhook", "cli", "auto"],
                        default="auto", help="Deploy strategy")
    parser.add_argument("--list", "-l", action="store_true", help="List configured apps")
    parser.add_argument("--status", help="Check deploy status for an app")
    args = parser.parse_args()

    config = load_config()

    if args.list:
        cmd_list(config)
        return

    if args.status:
        cmd_status(config, args.status)
        return

    if not args.app:
        parser.print_help()
        sys.exit(1)

    app_key, app_config = find_app(config, args.app)
    print(f"📦 App: {app_key}")

    strategy = args.strategy
    branch = args.branch

    if strategy == "auto":
        # Auto: try GitHub first, then webhook, then CLI
        gh_token = config.get("github", {}).get("token", "")
        gh_repo = app_config.get("github_repo", "")
        gh_workflow = app_config.get("github_workflow", "")
        webhook = app_config.get("caprover_webhook_url", "")
        app_token = app_config.get("caprover_app_token", "")

        if gh_token and gh_repo and gh_workflow:
            strategy = "github"
        elif webhook and "WEBHOOK_TOKEN" not in webhook:
            strategy = "webhook"
        elif app_token and "TOKEN" not in app_token:
            strategy = "cli"
        else:
            print("❌ No valid deploy strategy found. Check config.json.")
            print("   You need at least one of:")
            print("   - github.token + github_repo + github_workflow")
            print("   - caprover_webhook_url")
            print("   - caprover_app_token")
            sys.exit(1)

    print(f"🎯 Strategy: {strategy}")

    if strategy == "github":
        success = strategy_github(config, app_config, branch)
    elif strategy == "webhook":
        success = strategy_webhook(config, app_config)
    elif strategy == "cli":
        success = strategy_cli(config, app_config, branch)
    else:
        print(f"❌ Unknown strategy: {strategy}")
        success = False

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
