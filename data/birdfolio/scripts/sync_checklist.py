#!/usr/bin/env python3
"""
sync_checklist.py — Push local checklist.json to the API (bulk import).

Usage:
  python sync_checklist.py [--workspace <path>] [--api-url <url>]

Reads birdfolio/config.json for telegramId and apiUrl if not passed.
"""
import sys, os, json, argparse, urllib.request, urllib.error

def load_config(workspace):
    cfg_path = os.path.join(workspace, "config.json")
    if os.path.exists(cfg_path):
        with open(cfg_path) as f:
            return json.load(f)
    return {}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=None)
    parser.add_argument("--api-url", default=None)
    parser.add_argument("--telegram-id", type=int, default=None)
    args = parser.parse_args()

    # Resolve workspace
    workspace = args.workspace
    if not workspace:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        workspace = os.path.abspath(os.path.join(script_dir, "..", "..", "..", "birdfolio"))

    cfg = load_config(workspace)
    api_url = (args.api_url or cfg.get("apiUrl", "")).rstrip("/")
    telegram_id = args.telegram_id or cfg.get("telegramId")

    if not api_url:
        print(json.dumps({"status": "error", "message": "No api_url. Pass --api-url or run init_birdfolio.py first."}))
        sys.exit(1)
    if not telegram_id:
        print(json.dumps({"status": "error", "message": "No telegram_id. Pass --telegram-id or run init_birdfolio.py first."}))
        sys.exit(1)

    # Load local checklist.json
    checklist_path = os.path.join(workspace, "checklist.json")
    if not os.path.exists(checklist_path):
        print(json.dumps({"status": "error", "message": f"checklist.json not found at {checklist_path}"}))
        sys.exit(1)

    with open(checklist_path) as f:
        local = json.load(f)

    # Flatten to items list
    items = []
    tier_map = {"common": "common", "rare": "rare", "superRare": "superRare"}

    for region, tiers in local.items():
        for tier_key, tier_label in tier_map.items():
            for bird in tiers.get(tier_key, []):
                items.append({
                    "species": bird["species"],
                    "slug": bird["slug"],
                    "rarity_tier": tier_label,
                    "region": region,
                    "found": bird.get("found", False),
                    "date_found": bird.get("dateFound"),
                })

    # POST to bulk import endpoint
    payload = json.dumps({"items": items}).encode()
    req = urllib.request.Request(
        f"{api_url}/users/{telegram_id}/checklist/bulk",
        data=payload,
        method="POST",
        headers={"Content-Type": "application/json"},
    )

    try:
        res = urllib.request.urlopen(req, timeout=15)
        result = json.loads(res.read().decode())
        print(json.dumps({"status": "ok", "imported": result.get("imported", len(items)), "region": list(local.keys())[0]}))
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(json.dumps({"status": "error", "code": e.code, "message": body}))
        sys.exit(1)

if __name__ == "__main__":
    main()
