#!/usr/bin/env python3
"""
update_checklist.py — Mark a species as found in the checklist via the API.

Usage:
  python update_checklist.py \
    --species "California Quail" \
    --region "Northern California" \
    --api-url "https://your-api.up.railway.app" \
    --workspace "./birdfolio"

Output (JSON to stdout):
  {"status": "ok", "tier": "common", "dateFound": "2026-02-18"}
  {"status": "not_on_checklist"} — if species isn't in the checklist (bonus find)
"""
import argparse
import json
import os
import sys
import urllib.request
import urllib.error


def slugify(name):
    return name.lower().replace(" ", "-").replace("'", "").replace(".", "")


def read_config(workspace):
    config_path = os.path.join(workspace, "config.json")
    if os.path.exists(config_path):
        with open(config_path) as f:
            return json.load(f)
    return {}


def api_patch(base_url, path):
    req = urllib.request.Request(f"{base_url}{path}", method="PATCH")
    req.add_header("Content-Length", "0")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read()), None
    except urllib.error.HTTPError as e:
        return None, e.code


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--species", required=True)
    parser.add_argument("--region", required=True)
    parser.add_argument("--api-url", required=True)
    parser.add_argument("--workspace", default="./birdfolio")
    args = parser.parse_args()

    workspace = os.path.abspath(args.workspace)
    config = read_config(workspace)
    api_url = args.api_url or config.get("apiUrl", "")
    telegram_id = config.get("telegramId")

    if not telegram_id:
        print(json.dumps({"status": "error", "message": "No telegramId in config.json."}))
        sys.exit(1)

    slug = slugify(args.species)
    result, err_code = api_patch(api_url, f"/users/{telegram_id}/checklist/{slug}")

    if err_code == 404:
        # Species not on checklist — it's a bonus find, that's fine
        print(json.dumps({"status": "not_on_checklist"}))
        return

    if result is None:
        print(json.dumps({"status": "error", "message": f"API error {err_code}"}))
        sys.exit(1)

    print(json.dumps({
        "status": "ok",
        "tier": result.get("rarity_tier"),
        "dateFound": result.get("date_found"),
    }))


if __name__ == "__main__":
    main()
