#!/usr/bin/env python3
"""
SeaLegs SpotCast API — Complete Workflow Example

Demonstrates all 9 SpotCast API endpoints in a single end-to-end workflow:

  1. Check account balance
  2. Create a SpotCast
  3. Poll until processing completes
  4. Retrieve the full SpotCast
  5. Refresh with updated weather data
  6. Poll until refresh completes
  7. List forecast history
  8. Get a specific forecast
  9. List all SpotCasts

Requirements:
  pip install requests

Usage:
  # Option 1: Set env vars directly
  export SEALEGS_API_KEY=sk_live_your_key_here
  python examples/spotcast_workflow.py

  # Option 2: Create examples/.env file (gitignored)
  echo "SEALEGS_API_KEY=sk_live_your_key_here" > examples/.env
  python examples/spotcast_workflow.py

Cost: ~2 credits (1-day create + 1-day refresh)
"""

import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

# Load .env file from the examples directory if it exists
_env_file = Path(__file__).parent / ".env"
if _env_file.exists():
    with open(_env_file) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _key, _, _value = _line.partition("=")
                os.environ.setdefault(_key.strip(), _value.strip())

BASE_URL = os.environ.get("SEALEGS_API_BASE_URL", "https://api.sealegs.ai/v3").rstrip("/")
API_KEY = os.environ.get("SEALEGS_API_KEY")

POLL_INTERVAL = 10  # seconds
MAX_POLL_TIME = 300  # 5 minutes


def get_headers():
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }


def poll_until_completed(spotcast_id):
    """Poll the status endpoint until processing completes."""
    url = f"{BASE_URL}/spotcast/{spotcast_id}/status"
    start = time.time()

    while time.time() - start < MAX_POLL_TIME:
        resp = requests.get(url, headers=get_headers())
        resp.raise_for_status()
        data = resp.json()

        status = data["status"]
        if status == "completed":
            print(f"  Completed in {time.time() - start:.0f}s")
            return data
        if status == "failed":
            print(f"  FAILED: {data}")
            sys.exit(1)

        # Show progress if available
        progress = data.get("progress", {})
        stage = progress.get("stage", status)
        pct = progress.get("percentage", "")
        pct_str = f" ({pct}%)" if pct != "" else ""
        print(f"  {stage}{pct_str}")

        time.sleep(POLL_INTERVAL)

    print("  Timed out waiting for completion")
    sys.exit(1)


def main():
    if not API_KEY:
        print("Error: Set SEALEGS_API_KEY environment variable")
        sys.exit(1)

    print(f"Using API at {BASE_URL}\n")

    # ── 1. Check account balance ──────────────────────────────────────────
    print("1. Checking account balance...")
    resp = requests.get(f"{BASE_URL}/account/balance", headers=get_headers())
    resp.raise_for_status()
    balance = resp.json()
    print(f"   Credits: {balance['credit_balance']} available")
    print(f"   Purchased: {balance['total_credits_purchased']}, Used: {balance['total_credits_used']}")

    if balance["credit_balance"] < 2:
        print(f"\n   Need at least 2 credits. Purchase at: {balance['purchase_url']}")
        sys.exit(1)

    # ── 2. Create a SpotCast ──────────────────────────────────────────────
    print("\n2. Creating SpotCast for Miami...")
    tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).strftime("%Y-%m-%dT00:00:00Z")

    resp = requests.post(
        f"{BASE_URL}/spotcast",
        headers=get_headers(),
        json={
            "latitude": 25.7617,
            "longitude": -80.1918,
            "start_date": tomorrow,
            "num_days": 1,
            "trip_duration_hours": 8,
            "vessel_info": {"type": "sailboat", "length_ft": 35},
            "preferences": {
                "language": "en",
                "distance_units": "nm",
                "speed_units": "kts",
            },
            "metadata": {"location_name": "Miami Marina"},
        },
    )
    resp.raise_for_status()
    create = resp.json()

    spotcast_id = create["id"]
    forecast_id = create["forecast_id"]
    print(f"   SpotCast: {spotcast_id}")
    print(f"   Forecast: {forecast_id}")
    print(f"   Credits charged: {create['credits_charged']}, remaining: {create['credits_remaining']}")
    print(f"   Estimated time: ~{create['estimated_completion_seconds']}s")

    # ── 3. Poll until completed ───────────────────────────────────────────
    print("\n3. Waiting for processing...")
    poll_until_completed(spotcast_id)

    # ── 4. Get the full SpotCast ──────────────────────────────────────────
    print("\n4. Retrieving SpotCast details...")
    resp = requests.get(f"{BASE_URL}/spotcast/{spotcast_id}", headers=get_headers())
    resp.raise_for_status()
    sc = resp.json()

    coords = sc["coordinates"]
    fp = sc["forecast_period"]
    print(f"   Location: {coords['latitude']}, {coords['longitude']}")
    print(f"   Period: {fp['start_date'][:10]} to {fp['end_date'][:10]} ({fp['num_days']} days)")
    print(f"   Trip duration: {sc['trip_duration_hours']}h")

    ai = sc["latest_forecast"]["ai_analysis"]
    print(f"\n   Summary: {ai['summary'][:120]}...")
    for day in ai["daily_classifications"]:
        print(f"   [{day['classification']}] {day['date']}: {day['summary'][:100]}...")

    # ── 5. Refresh the SpotCast ───────────────────────────────────────────
    print("\n5. Refreshing with latest weather data...")
    resp = requests.post(
        f"{BASE_URL}/spotcast/{spotcast_id}/refresh", headers=get_headers()
    )
    resp.raise_for_status()
    refresh = resp.json()
    refresh_forecast_id = refresh["forecast_id"]
    print(f"   New forecast: {refresh_forecast_id}")

    # ── 6. Poll refresh until completed ───────────────────────────────────
    print("\n6. Waiting for refresh...")
    poll_until_completed(spotcast_id)

    # ── 7. List forecast history ──────────────────────────────────────────
    print("\n7. Listing forecast history...")
    resp = requests.get(
        f"{BASE_URL}/spotcast/{spotcast_id}/forecasts",
        headers=get_headers(),
        params={"limit": 5},
    )
    resp.raise_for_status()
    fc_list = resp.json()
    print(f"   {len(fc_list['data'])} forecasts found:")
    for entry in fc_list["data"]:
        print(f"   - {entry['forecast_id']} ({entry['status']}, {entry['created_at'][:19]})")

    # ── 8. Get a specific forecast ────────────────────────────────────────
    print(f"\n8. Getting original forecast {forecast_id}...")
    resp = requests.get(
        f"{BASE_URL}/spotcast/{spotcast_id}/forecast/{forecast_id}",
        headers=get_headers(),
    )
    resp.raise_for_status()
    fc = resp.json()
    print(f"   Status: {fc['status']}")
    print(f"   Classification: {fc['ai_analysis']['daily_classifications'][0]['classification']}")

    # ── 9. List all SpotCasts ─────────────────────────────────────────────
    print("\n9. Listing all SpotCasts...")
    resp = requests.get(
        f"{BASE_URL}/spotcasts", headers=get_headers(), params={"limit": 5}
    )
    resp.raise_for_status()
    sc_list = resp.json()
    print(f"   {len(sc_list['data'])} SpotCasts (has_more={sc_list['has_more']}):")
    for item in sc_list["data"]:
        coords = item["coordinates"]
        status = item["latest_forecast"]["status"]
        print(f"   - {item['id']}: ({coords['latitude']}, {coords['longitude']}) [{status}]")

    print("\nDone! All 9 endpoints exercised successfully.")


if __name__ == "__main__":
    main()
