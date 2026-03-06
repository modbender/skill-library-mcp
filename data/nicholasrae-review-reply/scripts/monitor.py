#!/usr/bin/env python3
"""
ReviewReply — monitor.py
Polls App Store Connect API for new reviews across all monitored apps.
Stores new reviews in data/reviews.json and triggers drafting + pattern detection.

Usage:
    python3 scripts/monitor.py                    # Normal run
    python3 scripts/monitor.py --dry-run          # Fetch but don't save
    python3 scripts/monitor.py --app 6758923557   # Single app only
    python3 scripts/monitor.py --since 2026-02-01 # Override lookback date
"""

import os
import sys
import json
import time
import argparse
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ─── App Store Connect JWT ────────────────────────────────────────────────────
try:
    import jwt  # PyJWT
    HAS_JWT = True
except ImportError:
    HAS_JWT = False

import urllib.request
import urllib.error

# ─── Config ───────────────────────────────────────────────────────────────────

# Directory layout
SKILL_DIR = Path(__file__).parent.parent
DATA_DIR = SKILL_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

REVIEWS_FILE = DATA_DIR / "reviews.json"
METRICS_FILE = DATA_DIR / "metrics.json"

# Monitored apps — add new apps here
APPS = [
    {"name": "FeedFare",         "id": "6758923557"},
    {"name": "Inflection Point", "id": "6759310530"},
    # {"name": "PetFace",          "id": "TBD"},   # Uncomment when live
]

# How far back to look for reviews on first run (days)
DEFAULT_LOOKBACK_DAYS = 30

# App Store Connect API
ASC_BASE_URL = "https://api.appstoreconnect.apple.com/v1"
ASC_KEY_ID = os.environ.get("APP_STORE_KEY_ID", "")
ASC_ISSUER_ID = os.environ.get("APP_STORE_ISSUER_ID", "")
ASC_PRIVATE_KEY_PATH = os.environ.get("APP_STORE_PRIVATE_KEY_PATH", "")

# Rating threshold for drafting replies (1–3 inclusive)
REPLY_DRAFT_THRESHOLD = 3


# ─── JWT Auth ─────────────────────────────────────────────────────────────────

def generate_jwt_token() -> str:
    """Generate a signed JWT for App Store Connect API auth."""
    if not HAS_JWT:
        raise RuntimeError(
            "PyJWT is required: pip3 install PyJWT cryptography"
        )
    if not all([ASC_KEY_ID, ASC_ISSUER_ID, ASC_PRIVATE_KEY_PATH]):
        raise RuntimeError(
            "Missing App Store Connect credentials.\n"
            "Set APP_STORE_KEY_ID, APP_STORE_ISSUER_ID, and APP_STORE_PRIVATE_KEY_PATH.\n"
            "See references/app-store-connect-api.md for setup."
        )

    key_path = Path(ASC_PRIVATE_KEY_PATH).expanduser()
    if not key_path.exists():
        raise FileNotFoundError(f"Private key not found: {key_path}")

    private_key = key_path.read_text()

    now = int(time.time())
    payload = {
        "iss": ASC_ISSUER_ID,
        "iat": now,
        "exp": now + 1200,  # 20 minutes max
        "aud": "appstoreconnect-v1",
    }
    headers = {
        "alg": "ES256",
        "kid": ASC_KEY_ID,
        "typ": "JWT",
    }

    token = jwt.encode(payload, private_key, algorithm="ES256", headers=headers)
    return token


# ─── API Helpers ──────────────────────────────────────────────────────────────

def api_get(path: str, token: str, params: dict = None) -> dict:
    """Make an authenticated GET request to App Store Connect."""
    url = f"{ASC_BASE_URL}{path}"
    if params:
        query = "&".join(f"{k}={v}" for k, v in params.items())
        url = f"{url}?{query}"

    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"API error {e.code} for {url}: {body}")


def api_post(path: str, token: str, body: dict) -> dict:
    """Make an authenticated POST request to App Store Connect."""
    url = f"{ASC_BASE_URL}{path}"
    data = json.dumps(body).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"API error {e.code} for {url}: {body}")


# ─── Data Helpers ─────────────────────────────────────────────────────────────

def load_reviews() -> list:
    """Load existing reviews from disk."""
    if REVIEWS_FILE.exists():
        try:
            return json.loads(REVIEWS_FILE.read_text())
        except json.JSONDecodeError:
            print("⚠️  reviews.json corrupted — starting fresh")
            return []
    return []


def save_reviews(reviews: list):
    """Save reviews to disk (sorted newest first)."""
    reviews.sort(key=lambda r: r.get("created_date", ""), reverse=True)
    REVIEWS_FILE.write_text(json.dumps(reviews, indent=2, ensure_ascii=False))


def load_metrics() -> dict:
    """Load or initialize metrics."""
    if METRICS_FILE.exists():
        try:
            return json.loads(METRICS_FILE.read_text())
        except json.JSONDecodeError:
            pass
    return {
        "apps": {},
        "pattern_alerts": [],
        "last_run": None,
    }


def save_metrics(metrics: dict):
    METRICS_FILE.write_text(json.dumps(metrics, indent=2, ensure_ascii=False))


def get_seen_ids(reviews: list) -> set:
    """Return set of review IDs already stored."""
    return {r["id"] for r in reviews}


# ─── Review Fetching ──────────────────────────────────────────────────────────

def fetch_reviews_for_app(app: dict, token: str, since: datetime = None) -> list:
    """
    Fetch all customer reviews for an app from App Store Connect.
    Returns list of normalized review dicts.
    """
    app_id = app["id"]
    app_name = app["name"]

    if app_id == "TBD":
        print(f"  ⏭  {app_name}: no app ID yet — skipping")
        return []

    print(f"  📡  Fetching reviews for {app_name} (ID: {app_id})...")

    all_reviews = []
    next_cursor = None
    page = 1

    while True:
        params = {
            "limit": 200,
            "sort": "-createdDate",
            "fields[customerReviews]":
                "rating,title,body,reviewerNickname,territory,createdDate",
        }
        if next_cursor:
            params["cursor"] = next_cursor

        try:
            data = api_get(f"/apps/{app_id}/customerReviews", token, params)
        except RuntimeError as e:
            print(f"  ❌  {app_name}: API error: {e}")
            return []

        reviews_raw = data.get("data", [])
        if not reviews_raw:
            break

        for item in reviews_raw:
            attrs = item.get("attributes", {})
            created = attrs.get("createdDate", "")

            # Stop if we're past the lookback window
            if since and created:
                try:
                    review_dt = datetime.fromisoformat(
                        created.replace("Z", "+00:00")
                    )
                    if review_dt < since:
                        return all_reviews
                except ValueError:
                    pass

            review = {
                "id": item["id"],
                "app_id": app_id,
                "app_name": app_name,
                "rating": attrs.get("rating", 0),
                "title": attrs.get("title", ""),
                "body": attrs.get("body", ""),
                "reviewer": attrs.get("reviewerNickname", "Anonymous"),
                "territory": attrs.get("territory", ""),
                "created_date": created,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "reply_status": "new",
                "draft_reply": None,
                "approved_reply": None,
                "replied_at": None,
            }
            all_reviews.append(review)

        # Pagination
        links = data.get("links", {})
        next_url = links.get("next")
        if not next_url:
            break

        # Extract cursor from next URL
        if "cursor=" in next_url:
            next_cursor = next_url.split("cursor=")[1].split("&")[0]
        else:
            break

        page += 1
        if page > 50:  # Safety cap: max 10,000 reviews
            print(f"  ⚠️  Capped at 50 pages for {app_name}")
            break

    print(f"  ✅  {app_name}: fetched {len(all_reviews)} reviews")
    return all_reviews


# ─── Metrics Update ───────────────────────────────────────────────────────────

def update_metrics(metrics: dict, app: dict, new_reviews: list, all_app_reviews: list):
    """Update per-app metrics after a monitor run."""
    app_id = app["id"]
    app_name = app["name"]

    if app_id not in metrics["apps"]:
        metrics["apps"][app_id] = {
            "name": app_name,
            "total_reviews": 0,
            "avg_rating": 0.0,
            "rating_trend": "stable",
            "response_rate": 0.0,
            "avg_response_time_hrs": None,
            "pending_count": 0,
            "posted_count": 0,
            "rejected_count": 0,
        }

    app_metrics = metrics["apps"][app_id]
    app_metrics["name"] = app_name
    app_metrics["total_reviews"] = len(all_app_reviews)
    app_metrics["new_this_run"] = len(new_reviews)

    if all_app_reviews:
        ratings = [r["rating"] for r in all_app_reviews]
        app_metrics["avg_rating"] = round(sum(ratings) / len(ratings), 2)

        # 7-day rating vs prior 7-day
        now = datetime.now(timezone.utc)
        week_ago = now - timedelta(days=7)
        two_weeks_ago = now - timedelta(days=14)

        def in_window(r, start, end):
            try:
                dt = datetime.fromisoformat(r["created_date"].replace("Z", "+00:00"))
                return start <= dt < end
            except ValueError:
                return False

        recent = [r["rating"] for r in all_app_reviews if in_window(r, week_ago, now)]
        prior = [r["rating"] for r in all_app_reviews if in_window(r, two_weeks_ago, week_ago)]

        if recent and prior:
            recent_avg = sum(recent) / len(recent)
            prior_avg = sum(prior) / len(prior)
            diff = recent_avg - prior_avg
            if diff > 0.2:
                app_metrics["rating_trend"] = "up"
            elif diff < -0.2:
                app_metrics["rating_trend"] = "down"
            else:
                app_metrics["rating_trend"] = "stable"

    # Response rate
    need_reply = [r for r in all_app_reviews if r["rating"] <= REPLY_DRAFT_THRESHOLD]
    replied = [r for r in need_reply if r["reply_status"] in ("posted", "approved")]
    if need_reply:
        app_metrics["response_rate"] = round(len(replied) / len(need_reply) * 100, 1)

    # Response time
    response_times = []
    for r in all_app_reviews:
        if r.get("replied_at") and r.get("created_date"):
            try:
                created = datetime.fromisoformat(r["created_date"].replace("Z", "+00:00"))
                replied_at = datetime.fromisoformat(r["replied_at"].replace("Z", "+00:00"))
                hrs = (replied_at - created).total_seconds() / 3600
                response_times.append(hrs)
            except ValueError:
                pass
    if response_times:
        app_metrics["avg_response_time_hrs"] = round(
            sum(response_times) / len(response_times), 1
        )


# ─── Trigger Downstream Scripts ───────────────────────────────────────────────

def trigger_draft_reply(review: dict, dry_run: bool = False):
    """Spawn draft_reply.py for a single review."""
    if dry_run:
        print(f"    [dry-run] Would draft reply for review {review['id']}")
        return

    script = Path(__file__).parent / "draft_reply.py"
    review_json = json.dumps(review)
    try:
        result = subprocess.run(
            [sys.executable, str(script), "--review-json", review_json],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            print(f"    ⚠️  Draft failed for {review['id']}: {result.stderr[:200]}")
        else:
            print(f"    ✏️  Draft created for {review['rating']}★ review ({review['id'][:8]}…)")
    except subprocess.TimeoutExpired:
        print(f"    ⏱  Draft timed out for {review['id']}")
    except Exception as e:
        print(f"    ❌  Draft error: {e}")


def trigger_pattern_detector(dry_run: bool = False):
    """Spawn pattern_detector.py after reviews are saved."""
    if dry_run:
        print("    [dry-run] Would run pattern detector")
        return

    script = Path(__file__).parent / "pattern_detector.py"
    try:
        result = subprocess.run(
            [sys.executable, str(script)],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            print(f"  ⚠️  Pattern detector error: {result.stderr[:200]}")
        elif result.stdout.strip():
            print(f"  🔍  {result.stdout.strip()}")
    except Exception as e:
        print(f"  ❌  Pattern detector error: {e}")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="ReviewReply — App Store monitor")
    parser.add_argument("--dry-run", action="store_true", help="Fetch but don't save")
    parser.add_argument("--app", metavar="APP_ID", help="Monitor single app only")
    parser.add_argument("--since", metavar="DATE", help="Lookback date (YYYY-MM-DD)")
    parser.add_argument("--no-draft", action="store_true", help="Skip reply drafting")
    parser.add_argument("--no-patterns", action="store_true", help="Skip pattern detection")
    args = parser.parse_args()

    run_start = datetime.now(timezone.utc)
    print(f"\n🔍 ReviewReply Monitor — {run_start.strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)

    # Determine lookback window
    if args.since:
        try:
            since = datetime.fromisoformat(args.since).replace(tzinfo=timezone.utc)
        except ValueError:
            print(f"❌ Invalid date format: {args.since}. Use YYYY-MM-DD.")
            sys.exit(1)
    else:
        existing = load_reviews()
        if existing:
            # Look back a bit past the most recent review we have
            since = datetime.now(timezone.utc) - timedelta(hours=6)
        else:
            since = datetime.now(timezone.utc) - timedelta(days=DEFAULT_LOOKBACK_DAYS)

    print(f"📅 Looking back to: {since.strftime('%Y-%m-%d %H:%M UTC')}")

    # Generate JWT token
    print("\n🔑 Authenticating with App Store Connect...")
    try:
        token = generate_jwt_token()
        print("  ✅ JWT token generated")
    except RuntimeError as e:
        print(f"  ❌ Auth failed: {e}")
        sys.exit(1)

    # Filter apps if --app specified
    apps_to_check = APPS
    if args.app:
        apps_to_check = [a for a in APPS if a["id"] == args.app]
        if not apps_to_check:
            print(f"❌ App ID {args.app} not found in config")
            sys.exit(1)

    # Load existing data
    existing_reviews = load_reviews()
    seen_ids = get_seen_ids(existing_reviews)
    metrics = load_metrics()

    total_new = 0
    total_draft_queued = 0

    # Process each app
    print("\n📱 Checking apps...")
    for app in apps_to_check:
        raw_reviews = fetch_reviews_for_app(app, token, since=since)
        new_reviews = [r for r in raw_reviews if r["id"] not in seen_ids]

        if not new_reviews:
            print(f"  ℹ️  {app['name']}: no new reviews")
        else:
            print(f"  🆕  {app['name']}: {len(new_reviews)} new review(s)")
            total_new += len(new_reviews)

            # Draft replies for 1–3★ reviews
            if not args.no_draft:
                for review in new_reviews:
                    if review["rating"] <= REPLY_DRAFT_THRESHOLD:
                        trigger_draft_reply(review, dry_run=args.dry_run)
                        total_draft_queued += 1
                    else:
                        review["reply_status"] = "skipped"

            # Add to master list
            if not args.dry_run:
                existing_reviews.extend(new_reviews)
                seen_ids.update(r["id"] for r in new_reviews)

        # Update per-app metrics
        all_app_reviews = [r for r in existing_reviews if r["app_id"] == app["id"]]
        update_metrics(metrics, app, new_reviews, all_app_reviews)

    # Save updated data
    if not args.dry_run:
        save_reviews(existing_reviews)
        metrics["last_run"] = run_start.isoformat()
        save_metrics(metrics)
        print(f"\n💾 Saved {len(existing_reviews)} total reviews to data/reviews.json")

    # Run pattern detector
    if not args.no_patterns and total_new > 0:
        print("\n🔍 Running pattern detector...")
        trigger_pattern_detector(dry_run=args.dry_run)

    # Summary
    print("\n" + "=" * 60)
    print(f"✅ Monitor run complete")
    print(f"   New reviews found:    {total_new}")
    print(f"   Replies queued:       {total_draft_queued}")
    elapsed = (datetime.now(timezone.utc) - run_start).total_seconds()
    print(f"   Time elapsed:         {elapsed:.1f}s")
    print()


if __name__ == "__main__":
    main()
