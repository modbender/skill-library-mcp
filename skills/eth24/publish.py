#!/usr/bin/env python3
"""Publish ETH24 to Typefully or format for CLI output."""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import httpx

SCRIPT_DIR = Path(__file__).parent
CONFIG = json.loads((SCRIPT_DIR / "config.json").read_text())

TYPEFULLY_BASE = "https://api.typefully.com"


def _headers():
    api_key = os.environ.get("TYPEFULLY_API_KEY")
    if not api_key:
        print("ERROR: TYPEFULLY_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


def upload_image(social_set_id, image_path):
    """Upload an image to Typefully, return its media_id."""
    headers = _headers()
    filename = Path(image_path).name

    # Request upload slot
    resp = httpx.post(
        f"{TYPEFULLY_BASE}/v2/social-sets/{social_set_id}/media/upload",
        headers=headers,
        json={"file_name": filename},
        timeout=30,
    )
    resp.raise_for_status()
    slot = resp.json()
    media_id = slot["media_id"]

    # PUT binary to presigned URL
    with open(image_path, "rb") as f:
        httpx.put(
            slot["upload_url"],
            content=f.read(),
            timeout=60,
        ).raise_for_status()

    # Wait for Typefully to process the image
    print(f"  Uploaded {filename} ({media_id}), waiting for processing...", file=sys.stderr)
    time.sleep(5)
    return media_id


def create_draft(social_set_id, posts):
    """Create a draft on Typefully and return the API response."""
    resp = httpx.post(
        f"{TYPEFULLY_BASE}/v2/social-sets/{social_set_id}/drafts",
        headers=_headers(),
        json={
            "platforms": {"x": {"enabled": True, "posts": posts}},
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def format_tweet(ranked):
    """Format ranked data as a single tweet for Typefully."""
    stories = ranked.get("stories", [])
    highlights = ranked.get("highlights", "")
    date_label = ranked.get("date_label", datetime.now().strftime("%-m/%d/%y"))
    brand = CONFIG.get("brand", {})

    lines = [f"{brand.get('name', 'ETH24')} - {date_label}"]

    if highlights:
        lines.append(f"\n{highlights}")

    for s in stories:
        tweet_url = s.get("tweet_url", "")
        if not tweet_url:
            continue
        commentary = s.get("commentary", "")
        lines.append(f"\n♦︎ {commentary}\n{tweet_url}")

    lines.append(
        f"\n{brand.get('name', 'ETH24')} by {brand.get('account', '@ethcforg')}\n"
        f"Open source: {brand.get('repo_url', 'github.com/ETHCF/eth24')}"
    )

    return "\n".join(lines)


def format_cli(ranked):
    """Format ranked data as plain text for stdout."""
    stories = ranked.get("stories", [])
    highlights = ranked.get("highlights", "")
    date_label = ranked.get("date_label", datetime.now().strftime("%-m/%d/%y"))
    brand = CONFIG.get("brand", {})

    lines = [f"{brand.get('name', 'ETH24')} - {date_label}"]

    if highlights:
        lines.append(f"\n{highlights}")

    for s in stories:
        tweet_url = s.get("tweet_url", "")
        if not tweet_url:
            continue
        commentary = s.get("commentary", "")
        lines.append(f"\n♦︎ {commentary}\n  {tweet_url}")

    return "\n".join(lines)


def main():
    today = datetime.now().strftime("%Y-%m-%d")
    out_dir = SCRIPT_DIR / "output" / today
    ranked_path = out_dir / "ranked.json"

    if ranked_path.exists():
        ranked = json.loads(ranked_path.read_text())
    else:
        ranked = json.loads(sys.stdin.read())

    social_set_id = os.environ.get("TYPEFULLY_SOCIAL_SET_ID")
    if not social_set_id:
        print("ERROR: TYPEFULLY_SOCIAL_SET_ID not set", file=sys.stderr)
        sys.exit(1)

    text = format_tweet(ranked)
    posts = [{"text": text}]

    # Save preview
    (out_dir / "thread.txt").write_text(text)
    print(f"> Tweet preview: {out_dir / 'thread.txt'}", file=sys.stderr)

    # Push to Typefully
    result = create_draft(social_set_id, posts)
    print("> Draft created on Typefully", file=sys.stderr)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
