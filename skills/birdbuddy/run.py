#!/usr/bin/env python3
"""Bird Buddy skill for OpenClaw - query your smart bird feeder."""

import asyncio
import json
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta, timezone
from birdbuddy.client import BirdBuddy

# Load .env from same directory as this script
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

BB_EMAIL = os.environ.get("BIRDBUDDY_EMAIL")
BB_PASSWORD = os.environ.get("BIRDBUDDY_PASSWORD")

def bail(msg):
    print(json.dumps({"error": msg}))
    sys.exit(1)

if not BB_EMAIL or not BB_PASSWORD:
    bail("BIRDBUDDY_EMAIL and BIRDBUDDY_PASSWORD environment variables required")

bb = BirdBuddy(BB_EMAIL, BB_PASSWORD)

async def cmd_status():
    await bb.refresh()
    result = []
    for fid, feeder in bb.feeders.items():
        result.append({
            "id": fid,
            "name": feeder.name,
            "state": str(feeder.state),
            "battery": {
                "percentage": feeder.battery.percentage if feeder.battery else None,
                "charging": feeder.battery.is_charging if feeder.battery else None,
                "state": str(feeder.battery.state) if feeder.battery else None,
            },
            "food": feeder.food.value if feeder.food else None,
            "signal": {
                "state": str(feeder.signal.state) if feeder.signal else None,
                "rssi": feeder.signal.rssi if feeder.signal else None,
            },
            "temperature": feeder.temperature if feeder.temperature else None,
        })
    print(json.dumps(result, indent=2))

async def cmd_feed(hours=24):
    since = datetime.now(timezone.utc) - timedelta(hours=int(hours))
    feed = await bb.refresh_feed(since=since)
    postcards = []
    for item in feed:
        if item.get("__typename") == "FeedItemNewPostcard":
            postcards.append({
                "id": item.get("id"),
                "timestamp": item.get("createdAt"),
                "thumbnail": item.get("thumbnail", {}).get("contentUrl") if item.get("thumbnail") else None,
            })
    print(json.dumps(postcards, indent=2))

async def cmd_sighting(postcard_id):
    sighting = await bb.sighting_from_postcard(postcard_id)
    report = sighting.report
    birds = []
    for s in report.sightings:
        bird = {"type": type(s).__name__}
        if hasattr(s, "species") and s.species:
            bird["species"] = s.species.name
        if hasattr(s, "suggestions") and s.suggestions:
            bird["suggestions"] = [sg.species.name for sg in s.suggestions if hasattr(sg, "species")]
        birds.append(bird)
    medias = [{"type": m["__typename"], "url": m.get("contentUrl"), "thumbnail": m.get("thumbnailUrl")}
              for m in sighting.medias]
    print(json.dumps({"birds": birds, "media": medias}, indent=2))

async def cmd_recent(hours=24, limit=5):
    since = datetime.now(timezone.utc) - timedelta(hours=int(hours))
    feed = await bb.refresh_feed(since=since)
    count = 0
    results = []
    for item in feed:
        if item.get("__typename") == "FeedItemNewPostcard" and count < int(limit):
            try:
                sighting = await bb.sighting_from_postcard(item.get("id"))
                birds = []
                for s in sighting.report.sightings:
                    if hasattr(s, "species") and s.species:
                        birds.append(s.species.name)
                    elif hasattr(s, "suggestions") and s.suggestions:
                        birds.append(f"possibly {s.suggestions[0].species.name}")
                results.append({
                    "postcard_id": item.get("id"),
                    "timestamp": item.get("createdAt"),
                    "birds": birds,
                    "thumbnail": item.get("thumbnail", {}).get("contentUrl") if item.get("thumbnail") else None,
                    "media_count": len(sighting.medias),
                })
                count += 1
            except Exception as e:
                results.append({"postcard_id": item.get("id"), "error": str(e)})
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        bail("Usage: run.py <status|feed|sighting|recent> [args...]")

    cmd = sys.argv[1]
    if cmd == "status":
        asyncio.run(cmd_status())
    elif cmd == "feed":
        hours = sys.argv[2] if len(sys.argv) > 2 else 24
        asyncio.run(cmd_feed(hours))
    elif cmd == "sighting":
        if len(sys.argv) < 3:
            bail("Usage: run.py sighting <postcard_id>")
        asyncio.run(cmd_sighting(sys.argv[2]))
    elif cmd == "recent":
        hours = sys.argv[2] if len(sys.argv) > 2 else 24
        limit = sys.argv[3] if len(sys.argv) > 3 else 5
        asyncio.run(cmd_recent(hours, limit))
    else:
        bail(f"Unknown command: {cmd}")
