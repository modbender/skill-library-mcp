#!/usr/bin/env python3
"""
log_sighting.py — Log a bird sighting via the Birdfolio API.

Usage:
  python log_sighting.py \
    --species "Great Blue Heron" \
    --scientific-name "Ardea herodias" \
    --rarity "rare" \
    --region "Northern California" \
    --date "2026-02-18" \
    --notes "" \
    --api-url "https://your-api.up.railway.app" \
    --workspace "./birdfolio"

Output (JSON to stdout):
  {"status": "ok", "sighting": {...}, "isLifer": true, "totalSightings": 3, "totalSpecies": 2}
"""
import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import date


def read_config(workspace):
    config_path = os.path.join(workspace, "config.json")
    if os.path.exists(config_path):
        with open(config_path) as f:
            return json.load(f)
    return {}


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


def api_get(base_url, path):
    req = urllib.request.Request(f"{base_url}{path}")
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--species", required=True)
    parser.add_argument("--scientific-name", required=True)
    parser.add_argument("--rarity", required=True,
                        choices=["common", "rare", "superRare", "bonus"])
    parser.add_argument("--region", required=True)
    parser.add_argument("--date", default=str(date.today()))
    parser.add_argument("--notes", default="")
    parser.add_argument("--card-png-url", default="")
    parser.add_argument("--api-url", required=True)
    parser.add_argument("--workspace", default="./birdfolio")
    args = parser.parse_args()

    workspace = os.path.abspath(args.workspace)
    config = read_config(workspace)
    api_url = args.api_url or config.get("apiUrl", "")
    telegram_id = config.get("telegramId")

    if not telegram_id:
        print(json.dumps({"status": "error", "message": "No telegramId in config.json. Run init_birdfolio.py first."}))
        sys.exit(1)

    try:
        sighting = api_post(api_url, f"/users/{telegram_id}/sightings", {
            "common_name": args.species,
            "scientific_name": args.scientific_name,
            "rarity": args.rarity,
            "region": args.region,
            "date_spotted": args.date,
            "notes": args.notes,
            "card_png_url": args.card_png_url,
        })

        stats = api_get(api_url, f"/users/{telegram_id}/stats")

    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(json.dumps({"status": "error", "message": f"API error {e.code}: {body}"}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))
        sys.exit(1)

    print(json.dumps({
        "status": "ok",
        "sighting": sighting,
        "isLifer": sighting.get("is_lifer", False),
        "totalSightings": stats.get("total_sightings", 0),
        "totalSpecies": stats.get("total_species", 0),
    }))


if __name__ == "__main__":
    main()
