#!/usr/bin/env python3
"""
init_birdfolio.py — Initialize Birdfolio for a user via the API.

Creates the user record and local workspace folders.
Checklist is populated separately by the agent after You.com search.

Usage:
  python init_birdfolio.py \
    --telegram-id YOUR_TELEGRAM_ID \
    --region "Northern California" \
    --api-url "https://your-api.up.railway.app" \
    [--workspace "./birdfolio"]

Output (JSON to stdout):
  {"status": "ok", "workspace": "...", "files_created": [...], "next": "..."}
"""
import argparse
import json
import os
import sys
import urllib.request
import urllib.error


def api_post(base_url, path, payload):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{base_url}{path}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--telegram-id", required=True, type=int)
    parser.add_argument("--region", required=True)
    parser.add_argument("--api-url", required=True, help="Birdfolio API base URL")
    parser.add_argument("--workspace", default="./birdfolio")
    args = parser.parse_args()

    workspace = os.path.abspath(args.workspace)

    # Create local folder structure for cards and birds
    folders = [
        workspace,
        os.path.join(workspace, "cards"),
        os.path.join(workspace, "birds"),
    ]
    for folder in folders:
        os.makedirs(folder, exist_ok=True)

    # Save config locally for quick access
    config = {
        "telegramId": args.telegram_id,
        "homeRegion": args.region,
        "apiUrl": args.api_url,
    }
    config_path = os.path.join(workspace, "config.json")
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

    # Register user via API
    try:
        api_post(args.api_url, "/users", {
            "telegram_id": args.telegram_id,
            "region": args.region,
        })
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(json.dumps({"status": "error", "message": f"API error {e.code}: {body}"}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))
        sys.exit(1)

    print(json.dumps({
        "status": "ok",
        "workspace": workspace,
        "files_created": ["config.json", "cards/", "birds/"],
        "next": "Populate checklist.json with You.com search results, then write to workspace.",
    }))


if __name__ == "__main__":
    main()
