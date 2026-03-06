#!/usr/bin/env python3
"""
XQueue Post Engine — checks the queue and posts to X.
Run via cron every 15 minutes.

Reads credentials from environment variables (X_CONSUMER_KEY, X_CONSUMER_SECRET, X_ACCESS_TOKEN,
X_ACCESS_TOKEN_SECRET). Optional macOS Keychain fallback if XQUEUE_KEYCHAIN_ACCOUNT is set.
Fallback: env vars X_CONSUMER_KEY, X_CONSUMER_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET
"""

import base64
import hashlib
import hmac
import json
import os
import re
import secrets
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
MAX_TWEET_LENGTH = 280
SUPPORTED_MEDIA = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_IMAGE_BYTES = 5 * 1024 * 1024  # 5MB
MAX_GIF_BYTES = 15 * 1024 * 1024  # 15MB


def load_config(queue_dir: Path) -> dict:
    config_path = queue_dir / "config.json"
    if not config_path.exists():
        print(f"ERROR: No config.json in {queue_dir}", file=sys.stderr)
        sys.exit(1)
    return json.loads(config_path.read_text())


def log_action(config: dict, queue_dir: Path, message: str):
    log_path = Path(config.get("logFile", "xqueue/posted.log"))
    # Security: reject absolute paths to prevent arbitrary file writes
    if log_path.is_absolute():
        log_path = Path("xqueue/posted.log")
    log_path = queue_dir.parent / log_path
    # Ensure log stays within the queue parent directory
    try:
        log_path.resolve().relative_to(queue_dir.parent.resolve())
    except ValueError:
        log_path = queue_dir.parent / "xqueue" / "posted.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(log_path, "a") as f:
        f.write(f"[{ts}] {message}\n")


# ---------------------------------------------------------------------------
# OAuth 1.0a
# ---------------------------------------------------------------------------

def get_credential(service: str, env_var: str) -> str:
    """Get credential from env var first, fall back to macOS Keychain if XQUEUE_KEYCHAIN_ACCOUNT is set."""
    val = os.environ.get(env_var, "")
    if val:
        return val
    # Optional macOS Keychain fallback — only if user explicitly configures it
    account = os.environ.get("XQUEUE_KEYCHAIN_ACCOUNT", "")
    if account:
        import subprocess
        try:
            result = subprocess.run(
                ["security", "find-generic-password", "-a", account, "-s", service, "-w"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except Exception:
            pass
    return ""


def oauth_request(method: str, url: str, body: dict = None, params: dict = None) -> dict:
    consumer_key = get_credential("x-consumer-key", "X_CONSUMER_KEY")
    consumer_secret = get_credential("x-consumer-secret", "X_CONSUMER_SECRET")
    access_token = get_credential("x-access-token", "X_ACCESS_TOKEN")
    access_secret = get_credential("x-access-token-secret", "X_ACCESS_TOKEN_SECRET")

    oauth_params = {
        "oauth_consumer_key": consumer_key,
        "oauth_nonce": secrets.token_hex(16),
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": str(int(time.time())),
        "oauth_token": access_token,
        "oauth_version": "1.0",
    }

    # For signature, include query params but NOT JSON body
    all_params = {**oauth_params}
    if params:
        all_params.update(params)

    param_str = "&".join(
        f"{urllib.parse.quote(k, '')}={urllib.parse.quote(str(v), '')}"
        for k, v in sorted(all_params.items())
    )
    base_url = url.split("?")[0]
    base = f"{method}&{urllib.parse.quote(base_url, '')}&{urllib.parse.quote(param_str, '')}"
    key = f"{urllib.parse.quote(consumer_secret, '')}&{urllib.parse.quote(access_secret, '')}"
    sig = base64.b64encode(
        hmac.new(key.encode(), base.encode(), hashlib.sha1).digest()
    ).decode()
    oauth_params["oauth_signature"] = sig

    auth_header = "OAuth " + ", ".join(
        f'{urllib.parse.quote(k, "")}="{urllib.parse.quote(v, "")}"'
        for k, v in sorted(oauth_params.items())
    )

    req_url = url
    if params:
        req_url += "?" + urllib.parse.urlencode(params)

    headers = {"Authorization": auth_header}
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(req_url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        return {"error": e.code, "body": error_body}


def upload_media(file_path: Path) -> str:
    """Upload media to X and return media_id string. Uses v1.1 chunked upload."""
    consumer_key = get_credential("x-consumer-key", "X_CONSUMER_KEY")
    consumer_secret = get_credential("x-consumer-secret", "X_CONSUMER_SECRET")
    access_token = get_credential("x-access-token", "X_ACCESS_TOKEN")
    access_secret = get_credential("x-access-token-secret", "X_ACCESS_TOKEN_SECRET")

    media_data = file_path.read_bytes()
    media_b64 = base64.b64encode(media_data).decode()

    suffix = file_path.suffix.lower()
    media_type = {
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".png": "image/png", ".gif": "image/gif", ".webp": "image/webp",
    }.get(suffix, "image/jpeg")

    # Use v1.1 media upload with multipart
    url = "https://upload.twitter.com/1.1/media/upload.json"

    # Build multipart form data
    boundary = secrets.token_hex(16)
    body_parts = []
    body_parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"media_data\"\r\n\r\n{media_b64}\r\n")
    body_parts.append(f"--{boundary}--\r\n")
    body_bytes = "".join(body_parts).encode()

    oauth_params = {
        "oauth_consumer_key": consumer_key,
        "oauth_nonce": secrets.token_hex(16),
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": str(int(time.time())),
        "oauth_token": access_token,
        "oauth_version": "1.0",
    }

    param_str = "&".join(
        f"{urllib.parse.quote(k, '')}={urllib.parse.quote(str(v), '')}"
        for k, v in sorted(oauth_params.items())
    )
    base = f"POST&{urllib.parse.quote(url, '')}&{urllib.parse.quote(param_str, '')}"
    key = f"{urllib.parse.quote(consumer_secret, '')}&{urllib.parse.quote(access_secret, '')}"
    sig = base64.b64encode(
        hmac.new(key.encode(), base.encode(), hashlib.sha1).digest()
    ).decode()
    oauth_params["oauth_signature"] = sig

    auth_header = "OAuth " + ", ".join(
        f'{urllib.parse.quote(k, "")}="{urllib.parse.quote(v, "")}"'
        for k, v in sorted(oauth_params.items())
    )

    req = urllib.request.Request(
        url, data=body_bytes,
        headers={
            "Authorization": auth_header,
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
            return str(result["media_id_string"])
    except urllib.error.HTTPError as e:
        print(f"Media upload failed: {e.code} {e.read().decode()}", file=sys.stderr)
        return None


# ---------------------------------------------------------------------------
# Posting logic
# ---------------------------------------------------------------------------

def parse_tweet_file(file_path: Path, separator: str) -> list[dict]:
    """Parse a tweet file into a list of {text, community} dicts."""
    content = file_path.read_text().strip()
    if not content:
        return []

    # Split into individual tweets (for threads)
    parts = [p.strip() for p in content.split(separator)]
    parts = [p for p in parts if p]

    tweets = []
    for part in parts:
        community = None
        text = part

        # Check for community tag
        match = re.match(r"^Post to ([^:]+):\s*(.+)$", part, re.DOTALL)
        if match:
            community = match.group(1).strip()
            text = match.group(2).strip()

        tweets.append({"text": text, "community": community})
    return tweets


def find_media(time_dir: Path) -> list[Path]:
    """Find media files in the time directory."""
    media = []
    for f in sorted(time_dir.iterdir()):
        if f.suffix.lower() in SUPPORTED_MEDIA:
            size = f.stat().st_size
            max_size = MAX_GIF_BYTES if f.suffix.lower() == ".gif" else MAX_IMAGE_BYTES
            if size <= max_size:
                media.append(f)
            else:
                print(f"WARN: {f.name} too large ({size} bytes), skipping", file=sys.stderr)
    return media[:4]  # X max 4 media per tweet


def post_tweets(tweets: list[dict], media_files: list[Path], communities: dict,
                dry_run: bool) -> list[dict]:
    """Post tweets (potentially as a thread). Returns list of results."""
    results = []
    reply_to = None

    # Upload media (attach to first tweet only for threads)
    media_ids = []
    if media_files:
        for mf in media_files:
            if dry_run:
                media_ids.append("DRY_RUN_MEDIA")
            else:
                mid = upload_media(mf)
                if mid:
                    media_ids.append(mid)

    for i, tweet in enumerate(tweets):
        text = tweet["text"]

        # Validate length
        if len(text) > MAX_TWEET_LENGTH:
            results.append({"error": f"Tweet {i+1} is {len(text)} chars (max {MAX_TWEET_LENGTH})", "text": text[:50]})
            continue

        # Build request body
        body = {"text": text}

        # Reply chain for threads
        if reply_to:
            body["reply"] = {"in_reply_to_tweet_id": reply_to}

        # Media (first tweet of thread gets the media)
        if i == 0 and media_ids and media_ids[0] != "DRY_RUN_MEDIA":
            body["media"] = {"media_ids": media_ids}

        # Community posting — X API v2 supports community_id in the tweet body
        community_name = tweet.get("community")
        if community_name and community_name in communities:
            cid = communities[community_name]
            if cid:
                body["community_id"] = cid

        if dry_run:
            results.append({"dry_run": True, "text": text[:50], "reply_to": reply_to})
            reply_to = f"DRY_RUN_{i}"
        else:
            result = oauth_request("POST", "https://api.x.com/2/tweets", body)
            if "data" in result:
                tweet_id = result["data"]["id"]
                reply_to = tweet_id
                results.append({"id": tweet_id, "text": text[:50]})
            else:
                results.append({"error": result, "text": text[:50]})
                break  # Stop thread on error

        # Small delay between thread tweets
        if len(tweets) > 1 and i < len(tweets) - 1:
            time.sleep(2)

    return results


# ---------------------------------------------------------------------------
# Main scheduler
# ---------------------------------------------------------------------------

def normalize_time(folder_name: str) -> tuple:
    """Parse time folder name like '9am', '12pm', '5pm' into (hour, minute)."""
    match = re.match(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)", folder_name.lower())
    if not match:
        return None
    hour = int(match.group(1))
    minute = int(match.group(2) or 0)
    ampm = match.group(3)
    if ampm == "pm" and hour != 12:
        hour += 12
    elif ampm == "am" and hour == 12:
        hour = 0
    return (hour, minute)


def should_post_now(time_folder: str, now: datetime) -> bool:
    """Check if current time is within the 15-min window for this time slot."""
    parsed = normalize_time(time_folder)
    if parsed is None:
        return False
    hour, minute = parsed
    slot_minutes = hour * 60 + minute
    now_minutes = now.hour * 60 + now.minute
    # Post if we're 0-14 minutes past the slot time
    return 0 <= (now_minutes - slot_minutes) < 15


def run(queue_dir: Path):
    """Main run: check current day/time, post matching content."""
    config = load_config(queue_dir)
    dry_run = config.get("dryRun", False)
    delete_after = config.get("deleteAfterPost", True)
    separator = config.get("separator", "---")
    communities = config.get("communities", {})

    # Get current day/time in configured timezone
    tz_name = config.get("timezone", "UTC")
    os.environ["TZ"] = tz_name
    try:
        time.tzset()
    except AttributeError:
        pass  # Windows doesn't have tzset
    now = datetime.now()
    day_name = now.strftime("%A")  # "Monday", "Tuesday", etc.

    day_dir = queue_dir / day_name
    if not day_dir.exists():
        return  # No folder for today

    posted_count = 0
    for time_dir in sorted(day_dir.iterdir()):
        if not time_dir.is_dir():
            continue
        if not should_post_now(time_dir.name, now):
            continue

        # Find tweet files
        tweet_files = sorted([
            f for f in time_dir.iterdir()
            if f.suffix.lower() in (".md", ".txt") and f.is_file()
        ])

        if not tweet_files:
            continue

        media_files = find_media(time_dir)

        for tweet_file in tweet_files:
            tweets = parse_tweet_file(tweet_file, separator)
            if not tweets:
                continue

            prefix = "[DRY RUN] " if dry_run else ""
            print(f"{prefix}Posting from {day_name}/{time_dir.name}/{tweet_file.name}")

            results = post_tweets(tweets, media_files, communities, dry_run)

            for r in results:
                if "error" in r:
                    log_action(config, queue_dir, f"ERROR {tweet_file.name}: {r['error']}")
                    print(f"  ERROR: {r['error']}", file=sys.stderr)
                else:
                    action = "WOULD POST" if dry_run else "POSTED"
                    log_action(config, queue_dir, f"{action} {tweet_file.name}: {r.get('text', '')}")
                    print(f"  {action}: {r.get('text', '')}")

            # Clean up
            if delete_after and not dry_run and not any("error" in r for r in results):
                tweet_file.unlink()
                for mf in media_files:
                    mf.unlink()
                posted_count += 1

    if posted_count:
        print(f"Done. Posted {posted_count} item(s).")


def main():
    # Find queue dir: check argument, then workspace default
    if len(sys.argv) > 1:
        queue_dir = Path(sys.argv[1])
    else:
        # Default: look for xqueue in workspace
        workspace = Path.home() / ".openclaw" / "workspace"
        queue_dir = workspace / "xqueue"

    if not queue_dir.exists():
        print(f"Queue directory not found: {queue_dir}")
        print("Run xqueue-setup.py first.")
        sys.exit(1)

    run(queue_dir)


if __name__ == "__main__":
    main()
