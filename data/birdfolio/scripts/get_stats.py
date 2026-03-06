#!/usr/bin/env python3
"""
get_stats.py — Fetch life list stats and checklist progress from the API.

Usage:
  python get_stats.py \
    --api-url "https://your-api.up.railway.app" \
    --workspace "./birdfolio"

Output (JSON to stdout):
  {
    "totalSightings": 5,
    "totalSpecies": 4,
    "checklistProgress": {
      "region": "Northern California",
      "common": {"found": 2, "total": 10, "species": [...]},
      "rare": {"found": 1, "total": 5, "species": [...]},
      "superRare": {"found": 0, "total": 1, "species": [...]}
    },
    "mostRecentSighting": {"commonName": "...", "date": "..."},
    "rarestBird": {"commonName": "...", "rarity": "...", "date": "..."}
  }
"""
import argparse
import json
import os
import sys
import urllib.request
import urllib.error


def read_config(workspace):
    config_path = os.path.join(workspace, "config.json")
    if os.path.exists(config_path):
        with open(config_path) as f:
            return json.load(f)
    return {}


def api_get(base_url, path):
    req = urllib.request.Request(f"{base_url}{path}")
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def main():
    parser = argparse.ArgumentParser()
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

    try:
        stats = api_get(api_url, f"/users/{telegram_id}/stats")
        checklist = api_get(api_url, f"/users/{telegram_id}/checklist")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(json.dumps({"status": "error", "message": f"API error {e.code}: {body}"}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))
        sys.exit(1)

    # Build checklist progress by tier
    tiers = {"common": [], "rare": [], "superRare": []}
    for item in checklist:
        tier = item.get("rarity_tier", "common")
        if tier in tiers:
            tiers[tier].append({
                "species": item["species"],
                "found": item["found"],
                "dateFound": item.get("date_found"),
            })

    region = config.get("homeRegion", "Unknown")
    checklist_progress = {
        "region": region,
        "common":    {"found": sum(1 for s in tiers["common"] if s["found"]),    "total": len(tiers["common"]),    "species": tiers["common"]},
        "rare":      {"found": sum(1 for s in tiers["rare"] if s["found"]),      "total": len(tiers["rare"]),      "species": tiers["rare"]},
        "superRare": {"found": sum(1 for s in tiers["superRare"] if s["found"]), "total": len(tiers["superRare"]), "species": tiers["superRare"]},
    }

    rarest = stats.get("rarest_bird")
    recent = stats.get("most_recent")

    print(json.dumps({
        "status": "ok",
        "totalSightings": stats.get("total_sightings", 0),
        "totalSpecies":   stats.get("total_species", 0),
        "checklistProgress": checklist_progress,
        "mostRecentSighting": {"commonName": recent["common_name"], "date": recent["date_spotted"]} if recent else None,
        "rarestBird": {"commonName": rarest["common_name"], "rarity": rarest["rarity"], "date": rarest["date_spotted"]} if rarest else None,
    }))


if __name__ == "__main__":
    main()
