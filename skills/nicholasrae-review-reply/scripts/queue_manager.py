#!/usr/bin/env python3
"""
ReviewReply — queue_manager.py
Manages the reply approval queue and sends daily 8am Telegram digest.
Handles approve/edit/reject actions and posts approved replies to App Store Connect.

Usage:
    python3 scripts/queue_manager.py --send-digest        # Send 8am Telegram digest
    python3 scripts/queue_manager.py --approve <id>       # Approve pending reply
    python3 scripts/queue_manager.py --edit <id> "text"   # Edit then approve reply
    python3 scripts/queue_manager.py --reject <id>        # Reject (no reply sent)
    python3 scripts/queue_manager.py --skip <id>          # Skip (never reply)
    python3 scripts/queue_manager.py --status             # Show queue status
    python3 scripts/queue_manager.py --post <id>          # Manually post a reply
    python3 scripts/queue_manager.py --metrics            # Show metrics summary
"""

import os
import sys
import json
import time
import argparse
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ─── JWT (same as monitor.py) ─────────────────────────────────────────────────
try:
    import jwt
    HAS_JWT = True
except ImportError:
    HAS_JWT = False

# ─── Config ───────────────────────────────────────────────────────────────────

SKILL_DIR = Path(__file__).parent.parent
DATA_DIR = SKILL_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

QUEUE_FILE = DATA_DIR / "queue.json"
REVIEWS_FILE = DATA_DIR / "reviews.json"
METRICS_FILE = DATA_DIR / "metrics.json"

# App Store Connect
ASC_BASE_URL = "https://api.appstoreconnect.apple.com/v1"
ASC_KEY_ID = os.environ.get("APP_STORE_KEY_ID", "")
ASC_ISSUER_ID = os.environ.get("APP_STORE_ISSUER_ID", "")
ASC_PRIVATE_KEY_PATH = os.environ.get("APP_STORE_PRIVATE_KEY_PATH", "")

# Telegram
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# Queue display
MAX_DIGEST_ITEMS = 10   # Max items per daily digest message
PREVIEW_CHARS = 120     # Review text preview length


# ─── Data Helpers ─────────────────────────────────────────────────────────────

def load_queue() -> list:
    if QUEUE_FILE.exists():
        try:
            return json.loads(QUEUE_FILE.read_text())
        except json.JSONDecodeError:
            return []
    return []


def save_queue(queue: list):
    QUEUE_FILE.write_text(json.dumps(queue, indent=2, ensure_ascii=False))


def load_reviews() -> list:
    if REVIEWS_FILE.exists():
        try:
            return json.loads(REVIEWS_FILE.read_text())
        except json.JSONDecodeError:
            return []
    return []


def save_reviews(reviews: list):
    reviews.sort(key=lambda r: r.get("created_date", ""), reverse=True)
    REVIEWS_FILE.write_text(json.dumps(reviews, indent=2, ensure_ascii=False))


def load_metrics() -> dict:
    if METRICS_FILE.exists():
        try:
            return json.loads(METRICS_FILE.read_text())
        except json.JSONDecodeError:
            pass
    return {"apps": {}, "pattern_alerts": [], "last_run": None}


def save_metrics(metrics: dict):
    METRICS_FILE.write_text(json.dumps(metrics, indent=2, ensure_ascii=False))


def find_queue_item(queue: list, item_id: str) -> tuple[int, dict | None]:
    """Find a queue item by sequential number (1-based) or review_id."""
    # Try as a 1-based index first
    try:
        idx = int(item_id) - 1
        pending = [i for i, q in enumerate(queue) if q["status"] == "pending"]
        if 0 <= idx < len(pending):
            real_idx = pending[idx]
            return real_idx, queue[real_idx]
    except ValueError:
        pass

    # Try as review_id or partial match
    for i, item in enumerate(queue):
        if item["review_id"] == item_id or item["review_id"].startswith(item_id):
            return i, item

    return -1, None


# ─── JWT Auth (duplicate from monitor.py for standalone use) ──────────────────

def generate_jwt_token() -> str:
    if not HAS_JWT:
        raise RuntimeError("PyJWT is required: pip3 install PyJWT cryptography")
    if not all([ASC_KEY_ID, ASC_ISSUER_ID, ASC_PRIVATE_KEY_PATH]):
        raise RuntimeError("Missing App Store Connect credentials")

    key_path = Path(ASC_PRIVATE_KEY_PATH).expanduser()
    private_key = key_path.read_text()

    now = int(time.time())
    payload = {
        "iss": ASC_ISSUER_ID,
        "iat": now,
        "exp": now + 1200,
        "aud": "appstoreconnect-v1",
    }
    headers = {"alg": "ES256", "kid": ASC_KEY_ID, "typ": "JWT"}

    return jwt.encode(payload, private_key, algorithm="ES256", headers=headers)


# ─── App Store Connect: Post Reply ────────────────────────────────────────────

def post_reply_to_app_store(review_id: str, reply_text: str) -> bool:
    """Post an approved reply to App Store Connect."""
    try:
        token = generate_jwt_token()
    except RuntimeError as e:
        print(f"  ❌ Auth failed: {e}")
        return False

    # Check if a response already exists, delete it if so
    url = f"{ASC_BASE_URL}/customerReviews/{review_id}/response"
    check_req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(check_req, timeout=15) as resp:
            existing = json.loads(resp.read())
            if existing.get("data"):
                # Delete existing response first
                existing_id = existing["data"]["id"]
                del_req = urllib.request.Request(
                    f"{ASC_BASE_URL}/customerReviewResponses/{existing_id}",
                    headers={"Authorization": f"Bearer {token}"},
                    method="DELETE",
                )
                urllib.request.urlopen(del_req, timeout=15)
    except urllib.error.HTTPError as e:
        if e.code != 404:
            print(f"  ⚠️  Could not check existing response: {e.code}")

    # Post new response
    payload = {
        "data": {
            "type": "customerReviewResponses",
            "attributes": {"responseBody": reply_text},
            "relationships": {
                "review": {
                    "data": {"type": "customerReviews", "id": review_id}
                }
            },
        }
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{ASC_BASE_URL}/customerReviewResponses",
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
            if result.get("data"):
                return True
            print(f"  ⚠️  Unexpected API response: {result}")
            return False
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"  ❌  App Store API error {e.code}: {body[:300]}")
        return False


# ─── Update Review Status ─────────────────────────────────────────────────────

def update_review_status(review_id: str, status: str, replied_at: str = None):
    """Update reply_status in reviews.json."""
    reviews = load_reviews()
    for r in reviews:
        if r["id"] == review_id:
            r["reply_status"] = status
            if replied_at:
                r["replied_at"] = replied_at
            break
    save_reviews(reviews)


# ─── Queue Actions ────────────────────────────────────────────────────────────

def action_approve(item_id: str) -> bool:
    """Approve a pending reply and post it to App Store."""
    queue = load_queue()
    idx, item = find_queue_item(queue, item_id)

    if not item:
        print(f"❌ Item #{item_id} not found in queue")
        return False

    if item["status"] != "pending":
        print(f"❌ Item #{item_id} is not pending (status: {item['status']})")
        return False

    reply_text = item.get("approved_reply") or item.get("draft_reply")
    if not reply_text:
        print(f"❌ No reply text for item #{item_id}")
        return False

    print(f"📤 Posting reply to App Store Connect…")
    print(f"   Review: {item['rating']}★ — {item['review_title'][:60]}")
    print(f"   Reply:  {reply_text[:100]}…")

    success = post_reply_to_app_store(item["review_id"], reply_text)

    if success:
        now = datetime.now(timezone.utc).isoformat()
        queue[idx]["status"] = "posted"
        queue[idx]["approved_reply"] = reply_text
        queue[idx]["posted_at"] = now
        save_queue(queue)
        update_review_status(item["review_id"], "posted", replied_at=now)
        print(f"✅ Reply posted successfully!")
        return True
    else:
        # Mark approved but not posted (can retry)
        queue[idx]["status"] = "approved"
        queue[idx]["approved_reply"] = reply_text
        save_queue(queue)
        update_review_status(item["review_id"], "approved")
        print(f"⚠️  Marked as approved but post failed — retry with --post {item_id}")
        return False


def action_edit(item_id: str, new_text: str) -> bool:
    """Edit a reply text and mark as approved."""
    queue = load_queue()
    idx, item = find_queue_item(queue, item_id)

    if not item:
        print(f"❌ Item #{item_id} not found in queue")
        return False

    print(f"✏️  Updating reply for {item['rating']}★ review…")
    print(f"   Old: {(item.get('draft_reply') or '')[:100]}")
    print(f"   New: {new_text[:100]}")

    queue[idx]["approved_reply"] = new_text
    queue[idx]["edited_at"] = datetime.now(timezone.utc).isoformat()
    queue[idx]["status"] = "pending"  # Still needs posting
    save_queue(queue)

    # Now approve it
    return action_approve(item_id)


def action_reject(item_id: str) -> bool:
    """Reject a reply — no response will be sent."""
    queue = load_queue()
    idx, item = find_queue_item(queue, item_id)

    if not item:
        print(f"❌ Item #{item_id} not found in queue")
        return False

    queue[idx]["status"] = "rejected"
    save_queue(queue)
    update_review_status(item["review_id"], "rejected")
    print(f"❌ Reply #{item_id} rejected — no response will be sent")
    return True


def action_skip(item_id: str) -> bool:
    """Skip a review — will never receive a reply."""
    queue = load_queue()
    idx, item = find_queue_item(queue, item_id)

    if not item:
        print(f"❌ Item #{item_id} not found in queue")
        return False

    queue[idx]["status"] = "skipped"
    save_queue(queue)
    update_review_status(item["review_id"], "skipped")
    print(f"⏭  Review #{item_id} skipped")
    return True


def action_post(item_id: str) -> bool:
    """Manually retry posting an approved reply."""
    queue = load_queue()
    idx, item = find_queue_item(queue, item_id)

    if not item:
        print(f"❌ Item #{item_id} not found in queue")
        return False

    reply_text = item.get("approved_reply") or item.get("draft_reply")
    if not reply_text:
        print(f"❌ No approved reply for item #{item_id}")
        return False

    success = post_reply_to_app_store(item["review_id"], reply_text)
    if success:
        now = datetime.now(timezone.utc).isoformat()
        queue[idx]["status"] = "posted"
        queue[idx]["posted_at"] = now
        save_queue(queue)
        update_review_status(item["review_id"], "posted", replied_at=now)
        print(f"✅ Reply posted!")
    return success


# ─── Daily Digest ─────────────────────────────────────────────────────────────

def format_star_bar(rating: int) -> str:
    return "★" * rating + "☆" * (5 - rating)


def format_digest_item(idx: int, item: dict) -> str:
    """Format a single queue item for the Telegram digest."""
    num_emoji = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    num = num_emoji[idx] if idx < len(num_emoji) else f"{idx+1}."

    created = item.get("created_date", "")[:10]
    rating = item.get("rating", "?")
    app = item.get("app_name", "Unknown")
    reviewer = item.get("reviewer", "Anonymous")
    title = item.get("review_title", "")
    body = item.get("review_body", "")
    review_text = title if title else body
    if len(review_text) > PREVIEW_CHARS:
        review_text = review_text[:PREVIEW_CHARS] + "…"

    draft = item.get("draft_reply", "")
    if len(draft) > PREVIEW_CHARS:
        draft_preview = draft[:PREVIEW_CHARS] + "…"
    else:
        draft_preview = draft

    lines = [
        f"{'─'*20}",
        f"{num} *{app}* — {format_star_bar(rating)} by {reviewer} ({created})",
        f'   _{review_text}_',
        f"",
        f"   📝 *Draft:*",
        f'   "{draft_preview}"',
        f"",
        f"   ✅ `/approve_{idx+1}`  ✏️ `/edit_{idx+1}`  ❌ `/reject_{idx+1}`",
    ]
    return "\n".join(lines)


def build_digest_message(pending_items: list, metrics: dict) -> str:
    """Build the full 8am digest message."""
    count = len(pending_items)
    date_str = datetime.now().strftime("%a %b %-d")

    if count == 0:
        return (
            f"📱 *ReviewReply — {date_str}*\n\n"
            f"✅ Queue is clear — no pending replies!\n\n"
            f"{format_metrics_line(metrics)}"
        )

    header = f"📱 *ReviewReply Morning Queue — {count} Pending* ({date_str})\n"

    items_text = []
    for i, item in enumerate(pending_items[:MAX_DIGEST_ITEMS]):
        items_text.append(format_digest_item(i, item))

    overflow = ""
    if count > MAX_DIGEST_ITEMS:
        overflow = f"\n_…and {count - MAX_DIGEST_ITEMS} more. Run `python3 scripts/queue_manager.py --status` to see all._\n"

    metrics_line = format_metrics_line(metrics)

    return "\n".join([header, *items_text, overflow, "", metrics_line])


def format_metrics_line(metrics: dict) -> str:
    """One-line metrics summary for the digest footer."""
    parts = []
    for app_id, app_data in metrics.get("apps", {}).items():
        name = app_data.get("name", app_id)
        avg = app_data.get("avg_rating", 0)
        trend = {"up": "📈", "down": "📉", "stable": "➡️"}.get(app_data.get("rating_trend", "stable"), "")
        rr = app_data.get("response_rate", 0)
        parts.append(f"{name}: {avg}★ {trend} · {rr}% replied")

    if parts:
        return "📊 " + " | ".join(parts)
    return "📊 No metrics yet"


def send_daily_digest(dry_run: bool = False):
    """Send the daily 8am Telegram digest."""
    queue = load_queue()
    metrics = load_metrics()

    pending = [q for q in queue if q["status"] == "pending"]
    message = build_digest_message(pending, metrics)

    if dry_run:
        print("=" * 60)
        print("DIGEST PREVIEW:")
        print("=" * 60)
        print(message)
        print("=" * 60)
        return

    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️  Telegram not configured")
        print("   Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID")
        print("\nDigest that would be sent:")
        print(message)
        return

    print(f"📤 Sending daily digest ({len(pending)} pending items)…")
    send_telegram_message(message)
    print("✅ Digest sent!")


def send_telegram_message(text: str):
    """Send a message via Telegram Bot API."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read())
            if not result.get("ok"):
                print(f"⚠️  Telegram error: {result.get('description', result)}")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"❌ Telegram error {e.code}: {body[:200]}")


# ─── Status Report ────────────────────────────────────────────────────────────

def show_status():
    """Print a formatted queue status to stdout."""
    queue = load_queue()
    metrics = load_metrics()

    if not queue:
        print("📭 Queue is empty")
        return

    by_status = {}
    for item in queue:
        s = item["status"]
        by_status.setdefault(s, []).append(item)

    print(f"\n{'='*60}")
    print(f"ReviewReply Queue Status — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}")

    for status in ["pending", "approved", "posted", "rejected", "skipped"]:
        items = by_status.get(status, [])
        if not items:
            continue
        status_emoji = {
            "pending": "⏳",
            "approved": "✅",
            "posted": "📤",
            "rejected": "❌",
            "skipped": "⏭",
        }.get(status, "•")
        print(f"\n{status_emoji} {status.upper()} ({len(items)})")

        for i, item in enumerate(items):
            created = item.get("created_date", "")[:10]
            print(
                f"   {i+1}. [{item['rating']}★] {item['app_name']} — "
                f"\"{item.get('review_title', item.get('review_body', ''))[:50]}\" "
                f"({created})"
            )

    print(f"\n{'─'*60}")
    print(format_metrics_line(metrics))
    print()


def show_metrics():
    """Print detailed metrics report."""
    metrics = load_metrics()
    reviews = load_reviews()

    print(f"\n{'='*60}")
    print(f"ReviewReply Metrics — {datetime.now().strftime('%Y-%m-%d')}")
    print(f"{'='*60}")

    if not metrics.get("apps"):
        print("No metrics yet. Run monitor.py first.")
        return

    for app_id, app_data in metrics["apps"].items():
        name = app_data.get("name", app_id)
        trend = {"up": "📈 improving", "down": "📉 declining", "stable": "➡️ stable"}.get(
            app_data.get("rating_trend", "stable"), "unknown"
        )
        print(f"\n📱 {name}")
        print(f"   Total reviews:     {app_data.get('total_reviews', 0)}")
        print(f"   Average rating:    {app_data.get('avg_rating', 0):.1f}★  ({trend})")
        print(f"   Response rate:     {app_data.get('response_rate', 0):.1f}%")
        avg_time = app_data.get("avg_response_time_hrs")
        if avg_time:
            print(f"   Avg response time: {avg_time:.1f}h")
        print(f"   Replies posted:    {app_data.get('posted_count', 0)}")
        print(f"   Rejected:          {app_data.get('rejected_count', 0)}")

    # Pattern alerts
    alerts = metrics.get("pattern_alerts", [])
    recent_alerts = [
        a for a in alerts
        if datetime.fromisoformat(a.get("sent_at", "2000-01-01").replace("Z", "+00:00"))
        > datetime.now(timezone.utc) - timedelta(days=7)
    ]
    if recent_alerts:
        print(f"\n🚨 Pattern Alerts (last 7 days): {len(recent_alerts)}")
        for a in recent_alerts[-5:]:
            print(f"   • {a['app_name']}: \"{a['theme']}\" ({a['count']}x)")

    last_run = metrics.get("last_run", "Never")
    if last_run and last_run != "Never":
        try:
            dt = datetime.fromisoformat(last_run.replace("Z", "+00:00"))
            last_run = dt.strftime("%Y-%m-%d %H:%M UTC")
        except ValueError:
            pass
    print(f"\n⏱  Last monitor run: {last_run}")
    print()


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="ReviewReply — queue manager")
    parser.add_argument("--send-digest", action="store_true", help="Send 8am Telegram digest")
    parser.add_argument("--approve", metavar="ID", help="Approve and post reply #ID")
    parser.add_argument("--edit", nargs=2, metavar=("ID", "TEXT"), help="Edit and approve reply")
    parser.add_argument("--reject", metavar="ID", help="Reject reply #ID")
    parser.add_argument("--skip", metavar="ID", help="Skip review #ID (never reply)")
    parser.add_argument("--post", metavar="ID", help="Retry posting approved reply")
    parser.add_argument("--status", action="store_true", help="Show queue status")
    parser.add_argument("--metrics", action="store_true", help="Show metrics report")
    parser.add_argument("--dry-run", action="store_true", help="Simulate, don't post/send")
    args = parser.parse_args()

    if args.send_digest:
        send_daily_digest(dry_run=args.dry_run)

    elif args.approve:
        if args.dry_run:
            queue = load_queue()
            _, item = find_queue_item(queue, args.approve)
            if item:
                print(f"[dry-run] Would approve and post:\n{item.get('draft_reply', '')}")
        else:
            action_approve(args.approve)

    elif args.edit:
        item_id, new_text = args.edit
        if args.dry_run:
            print(f"[dry-run] Would update reply {item_id} to:\n{new_text}")
        else:
            action_edit(item_id, new_text)

    elif args.reject:
        action_reject(args.reject)

    elif args.skip:
        action_skip(args.skip)

    elif args.post:
        if args.dry_run:
            print(f"[dry-run] Would post reply {args.post}")
        else:
            action_post(args.post)

    elif args.status:
        show_status()

    elif args.metrics:
        show_metrics()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
