#!/usr/bin/env python3
"""
nova_deploy.py — Create, build, and deploy a Nova Platform app from a Git repo.

Usage:
    python3 scripts/nova_deploy.py \
        --repo https://github.com/you/my-app \
        --name "My App" \
        --port 8000 \
        --api-key <nova-api-key> \
        [--git-ref main] \
        [--version 1.0.0] \
        [--directory /] \
        [--poll-interval 15] \
        [--timeout 900]

Nova API key:  sparsity.cloud → Account → API Keys → Create
API docs:      https://sparsity.cloud/api/docs

Workflow:
    1. POST /api/apps          — create app (with full advanced config)
    2. POST /api/apps/{sqid}/builds   — trigger build from Git
    3. Poll build until success
    4. POST /api/apps/{sqid}/deployments  — deploy the build
    5. Poll deployment until running
    6. Print the live hostname

Output:
    App hostname printed when deployment state = running, e.g.:
        https://abc123.nova.sparsity.cloud
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from typing import Any

import urllib.request
import urllib.error

NOVA_API_BASE = "https://sparsity.cloud/api"

# Default advanced config matching UI defaults
# POST /api/apps requires the 'advanced' field — this is the only config needed.

def make_advanced_config(
    port: int,
    directory: str = "/",
    enable_kms: bool = False,
    enable_s3: bool = False,
    enable_wallet: bool = False,
    enable_helios: bool = False,
    helios_chains: list | None = None,
) -> dict:
    return {
        "directory": directory,
        "app_listening_port": port,
        "egress_allow": ["**"],
        "enable_decentralized_kms": enable_kms,
        "enable_persistent_storage": enable_s3,
        "enable_s3_storage": enable_s3,
        "enable_s3_kms_encryption": enable_kms and enable_s3,
        "enable_ipfs_storage": False,
        "enable_walrus_storage": False,
        "enable_app_wallet": enable_wallet,
        "enable_helios_rpc": enable_helios,
        "helios_chains": helios_chains or [
            {"chain_id": "1", "kind": "ethereum", "network": "mainnet", "execution_rpc": "", "local_rpc_port": 18545}
        ],
    }


# ── HTTP helpers (stdlib only — no pip install needed) ────────────────────────

def _request(
    method: str,
    path: str,
    api_key: str,
    body: dict[str, Any] | None = None,
) -> dict[str, Any]:
    url = f"{NOVA_API_BASE}{path}"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body_text = e.read().decode(errors="replace")
        raise RuntimeError(f"HTTP {e.code} {e.reason} → {url}\n{body_text}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network error → {url}: {e.reason}") from e


def _post(path: str, api_key: str, body: dict[str, Any]) -> dict[str, Any]:
    return _request("POST", path, api_key, body)


def _get(path: str, api_key: str) -> dict[str, Any]:
    return _request("GET", path, api_key)


# ── Step 1: Create App ────────────────────────────────────────────────────────

def create_app(
    name: str,
    repo_url: str,
    port: int,
    directory: str,
    api_key: str,
) -> str:
    """Create the app. Returns the app sqid."""
    print(f"[1/4] Creating Nova app '{name}' from {repo_url} (port={port}) ...")
    result = _post("/apps", api_key, {
        "name": name,
        "repo_url": repo_url,
        "advanced": make_advanced_config(port, directory=directory),
    })
    sqid = result.get("sqid")
    if not sqid:
        raise RuntimeError(f"No sqid in create response: {result}")
    print(f"      App sqid: {sqid}")
    return sqid


# ── Step 2: Trigger Build ─────────────────────────────────────────────────────

def trigger_build(sqid: str, git_ref: str, version: str, api_key: str) -> int:
    """Trigger a build. Returns build id (integer)."""
    print(f"[2/4] Triggering build (git_ref={git_ref}, version={version}) ...")
    result = _post(f"/apps/{sqid}/builds", api_key, {
        "git_ref": git_ref,
        "version": version,
    })
    build_id = result.get("id")
    if not build_id:
        raise RuntimeError(f"No build id in response: {result}")
    print(f"      Build ID: {build_id}")
    return build_id


# ── Step 3: Wait for Build ────────────────────────────────────────────────────

def wait_for_build(
    build_id: int,
    api_key: str,
    poll_interval: int,
    timeout: int,
) -> None:
    """Poll build status until success or failure."""
    print(f"[3/4] Waiting for build {build_id} to complete ...")
    deadline = time.time() + timeout
    dots = 0
    while time.time() < deadline:
        try:
            data = _get(f"/builds/{build_id}/status", api_key)
        except RuntimeError as exc:
            print(f"\n      [warn] Poll error: {exc} — retrying ...")
            time.sleep(poll_interval)
            continue

        status = (data.get("status") or "unknown").lower()
        print(f"  [{('.' * dots):.<20}] build_status={status}", end="\r")
        dots += 1

        if status == "success":
            print()
            print("      Build succeeded ✓")
            return
        if status == "failed":
            print()
            err = data.get("error_message", "")
            raise RuntimeError(f"Build failed: {err}\nFull response: {data}")

        time.sleep(poll_interval)

    raise TimeoutError(f"Build {build_id} did not complete within {timeout}s.")


# ── Step 4: Create Deployment ─────────────────────────────────────────────────

def create_deployment(sqid: str, build_id: int, api_key: str) -> int:
    """Create a deployment. Returns deployment id."""
    print(f"[4/4] Deploying build {build_id} ...")
    result = _post(f"/apps/{sqid}/deployments", api_key, {"build_id": build_id})
    deploy_id = result.get("id")
    if not deploy_id:
        raise RuntimeError(f"No deployment id in response: {result}")
    print(f"      Deployment ID: {deploy_id}")
    return deploy_id


# ── Step 5: Wait for Deployment ───────────────────────────────────────────────

def wait_for_deployment(
    deploy_id: int,
    sqid: str,
    api_key: str,
    poll_interval: int,
    timeout: int,
) -> str:
    """Poll deployment status until running. Returns hostname."""
    print(f"      Waiting for deployment to reach 'running' ...")
    deadline = time.time() + timeout
    dots = 0
    while time.time() < deadline:
        try:
            data = _get(f"/deployments/{deploy_id}/status", api_key)
        except RuntimeError as exc:
            print(f"\n      [warn] Poll error: {exc} — retrying ...")
            time.sleep(poll_interval)
            continue

        state = (data.get("deployment_state") or "unknown").lower()
        msg = data.get("deployment_message", "")
        print(f"  [{('.' * dots):.<20}] state={state} {msg[:40]}", end="\r")
        dots += 1

        if state == "running":
            print()
            # Get hostname from app detail
            try:
                detail = _get(f"/apps/{sqid}/detail", api_key)
                hostname = detail.get("app", {}).get("hostname", "")
                if hostname:
                    return hostname
            except Exception:
                pass
            return ""

        if state in ("failed", "error"):
            print()
            raise RuntimeError(f"Deployment failed (state={state}): {msg}")

        time.sleep(poll_interval)

    raise TimeoutError(f"Deployment did not reach 'running' within {timeout}s.")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create, build, and deploy a Nova Platform app from Git"
    )
    parser.add_argument("--repo", required=True, help="Git repo URL, e.g. https://github.com/you/my-app")
    parser.add_argument("--name", required=True, help="App display name")
    parser.add_argument("--port", type=int, default=8000, help="App listening port (default: 8000)")
    parser.add_argument("--git-ref", default="main", help="Branch, tag, or commit SHA (default: main)")
    parser.add_argument("--version", default="1.0.0", help="Semver version for this build (default: 1.0.0)")
    parser.add_argument("--directory", default="/", help="Subdirectory in repo containing the Dockerfile (default: /)")
    parser.add_argument("--api-key", required=True, help="Nova Platform API key")
    parser.add_argument("--poll-interval", type=int, default=15, help="Poll interval in seconds (default: 15)")
    parser.add_argument("--timeout", type=int, default=900, help="Total timeout in seconds (default: 900)")
    args = parser.parse_args()

    try:
        # 1. Create app
        sqid = create_app(args.name, args.repo, args.port, args.directory, args.api_key)

        # 2. Trigger build
        build_id = trigger_build(sqid, args.git_ref, args.version, args.api_key)

        # 3. Wait for build
        wait_for_build(build_id, args.api_key, args.poll_interval, args.timeout)

        # 4. Create deployment
        deploy_id = create_deployment(sqid, build_id, args.api_key)

        # 5. Wait for running
        hostname = wait_for_deployment(
            deploy_id, sqid, args.api_key, args.poll_interval, args.timeout
        )

        app_url = f"https://{hostname}" if hostname and not hostname.startswith("http") else hostname

        print(f"""
╔══════════════════════════════════════════════════════╗
║  ✅  Nova App is LIVE                                ║
╠══════════════════════════════════════════════════════╣
║  App sqid   : {sqid:<40}║
║  Build ID   : {str(build_id):<40}║
║  Deploy ID  : {str(deploy_id):<40}║
║  URL        : {app_url:<40}║
╚══════════════════════════════════════════════════════╝

Verify:
  curl {app_url}/
  curl {app_url}/api/attestation
  curl {app_url}/api/app-wallet

Manage at: https://sparsity.cloud
""")

    except (RuntimeError, TimeoutError) as exc:
        print(f"\n[error] {exc}", file=sys.stderr)
        print("""
[manual fallback]
  1. Go to https://sparsity.cloud → Apps → Create App
  2. Fill Name, Description, Git Repo URL, and configure Advanced settings
  3. Trigger Build → wait for success
  4. Create Deployment → wait for running
""")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n[cancelled]")
        sys.exit(0)


if __name__ == "__main__":
    main()
