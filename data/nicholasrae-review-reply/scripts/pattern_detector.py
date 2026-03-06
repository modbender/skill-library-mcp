#!/usr/bin/env python3
"""
ReviewReply — pattern_detector.py
Surfaces repeat-complaint patterns from recent reviews.
If the same complaint theme appears 3+ times in 7 days → immediate Telegram alert.

Usage:
    python3 scripts/pattern_detector.py             # Run detection (called by monitor.py)
    python3 scripts/pattern_detector.py --report    # Print pattern report, no Telegram
    python3 scripts/pattern_detector.py --days 14   # Custom lookback window
    python3 scripts/pattern_detector.py --dry-run   # Detect but don't send Telegram
"""

import os
import sys
import json
import argparse
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from pathlib import Path
from collections import defaultdict

# ─── Config ───────────────────────────────────────────────────────────────────

SKILL_DIR = Path(__file__).parent.parent
DATA_DIR = SKILL_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

REVIEWS_FILE = DATA_DIR / "reviews.json"
METRICS_FILE = DATA_DIR / "metrics.json"

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

CLAUDE_MODEL = "claude-haiku-4-5"  # Fast + cheap for classification

# Pattern detection thresholds
PATTERN_THRESHOLD = 3          # Minimum occurrences to trigger alert
PATTERN_WINDOW_DAYS = 7        # Rolling window in days
ALERT_COOLDOWN_HOURS = 24      # Don't re-alert same pattern within this window


# ─── Data Helpers ─────────────────────────────────────────────────────────────

def load_reviews() -> list:
    if REVIEWS_FILE.exists():
        try:
            return json.loads(REVIEWS_FILE.read_text())
        except json.JSONDecodeError:
            return []
    return []


def load_metrics() -> dict:
    if METRICS_FILE.exists():
        try:
            return json.loads(METRICS_FILE.read_text())
        except json.JSONDecodeError:
            pass
    return {"apps": {}, "pattern_alerts": [], "last_run": None}


def save_metrics(metrics: dict):
    METRICS_FILE.write_text(json.dumps(metrics, indent=2, ensure_ascii=False))


def get_recent_reviews(reviews: list, days: int) -> list:
    """Filter reviews to those created within the last N days."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    recent = []
    for r in reviews:
        created = r.get("created_date", "")
        if not created:
            continue
        try:
            dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
            if dt >= cutoff:
                recent.append(r)
        except ValueError:
            pass
    return recent


# ─── Claude: Complaint Clustering ─────────────────────────────────────────────

def cluster_complaints_with_claude(reviews: list, app_name: str) -> list[dict]:
    """
    Use Claude to identify and cluster complaint themes across reviews.
    Returns list of pattern dicts: {theme, count, reviews, severity}
    """
    if not ANTHROPIC_API_KEY:
        # Fallback: simple keyword clustering
        return keyword_cluster_fallback(reviews)

    if not reviews:
        return []

    # Build review list for Claude
    review_texts = []
    for i, r in enumerate(reviews):
        text = f"{i+1}. [{r['rating']}★] {r.get('title', '')} — {r.get('body', '')}".strip()
        review_texts.append(text[:300])  # Truncate very long reviews

    reviews_block = "\n".join(review_texts)

    system_prompt = """You are a product analyst. Your job is to identify recurring complaint themes in App Store reviews.
Group complaints by theme. Focus on actionable, specific issues (not vague sentiment).
Output ONLY valid JSON — no commentary, no markdown, just raw JSON."""

    user_prompt = f"""App: {app_name}
Reviews from last 7 days:

{reviews_block}

Identify all distinct complaint themes that appear more than once. For each theme:
- Summarize the complaint in ≤10 words
- List which review numbers mention it
- Rate severity: high (app broken/unusable), medium (major friction), low (minor annoyance)

Return JSON array:
[
  {{
    "theme": "Short description of complaint",
    "review_indices": [1, 3, 5],
    "severity": "high|medium|low",
    "category": "crash|performance|ui|missing_feature|content|billing|other"
  }}
]

If no recurring themes, return [].
"""

    payload = {
        "model": CLAUDE_MODEL,
        "max_tokens": 1024,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_prompt}],
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=data,
        headers={
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
            raw = result["content"][0]["text"].strip()

            # Strip markdown code fences if present
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            raw = raw.strip()

            clusters = json.loads(raw)

            # Hydrate with actual review data
            patterns = []
            for cluster in clusters:
                indices = [i - 1 for i in cluster.get("review_indices", []) if 1 <= i <= len(reviews)]
                matched_reviews = [reviews[i] for i in indices]

                if len(matched_reviews) < 2:
                    continue

                avg_rating = sum(r["rating"] for r in matched_reviews) / len(matched_reviews)
                patterns.append({
                    "theme": cluster["theme"],
                    "count": len(matched_reviews),
                    "severity": cluster.get("severity", "medium"),
                    "category": cluster.get("category", "other"),
                    "avg_rating": round(avg_rating, 1),
                    "reviews": matched_reviews,
                })

            return patterns

    except (urllib.error.HTTPError, json.JSONDecodeError, KeyError) as e:
        print(f"  ⚠️  Claude clustering failed: {e} — falling back to keyword method")
        return keyword_cluster_fallback(reviews)


def keyword_cluster_fallback(reviews: list) -> list[dict]:
    """
    Simple keyword-based fallback clustering when Claude is unavailable.
    Groups reviews by common words in titles/bodies.
    """
    COMPLAINT_KEYWORDS = {
        "crash": ["crash", "crashes", "crashed", "force close", "closes itself"],
        "freeze": ["freeze", "frozen", "freezing", "hang", "hangs", "stuck"],
        "slow": ["slow", "sluggish", "laggy", "lag", "loading", "loads", "takes forever"],
        "login": ["login", "log in", "sign in", "signin", "password", "account"],
        "subscription": ["subscription", "billing", "charge", "charged", "refund", "purchase"],
        "sync": ["sync", "syncing", "not syncing", "data lost", "lost data"],
        "notification": ["notification", "notifications", "alerts", "push"],
        "ui_bug": ["button", "tap", "doesn't work", "not working", "broken", "bug"],
    }

    clusters = defaultdict(list)

    for review in reviews:
        text = f"{review.get('title', '')} {review.get('body', '')}".lower()
        for theme, keywords in COMPLAINT_KEYWORDS.items():
            if any(kw in text for kw in keywords):
                clusters[theme].append(review)

    patterns = []
    for theme, matched in clusters.items():
        if len(matched) >= 2:
            avg_rating = sum(r["rating"] for r in matched) / len(matched)
            patterns.append({
                "theme": theme.replace("_", " ").title(),
                "count": len(matched),
                "severity": "high" if avg_rating < 2 else "medium",
                "category": theme,
                "avg_rating": round(avg_rating, 1),
                "reviews": matched,
            })

    return patterns


# ─── Alert Deduplication ──────────────────────────────────────────────────────

def already_alerted(metrics: dict, app_id: str, theme: str, cooldown_hours: int) -> bool:
    """Check if we already sent an alert for this pattern recently."""
    alerts = metrics.get("pattern_alerts", [])
    cutoff = datetime.now(timezone.utc) - timedelta(hours=cooldown_hours)

    for alert in alerts:
        if alert.get("app_id") != app_id:
            continue
        if alert.get("theme", "").lower() != theme.lower():
            continue
        try:
            sent_at = datetime.fromisoformat(alert["sent_at"].replace("Z", "+00:00"))
            if sent_at >= cutoff:
                return True
        except (ValueError, KeyError):
            pass
    return False


def record_alert(metrics: dict, app_id: str, app_name: str, theme: str, count: int):
    """Record that we sent an alert."""
    if "pattern_alerts" not in metrics:
        metrics["pattern_alerts"] = []

    metrics["pattern_alerts"].append({
        "app_id": app_id,
        "app_name": app_name,
        "theme": theme,
        "count": count,
        "sent_at": datetime.now(timezone.utc).isoformat(),
    })

    # Keep only last 200 alerts
    metrics["pattern_alerts"] = metrics["pattern_alerts"][-200:]


# ─── Telegram Alerts ──────────────────────────────────────────────────────────

def send_telegram_alert(pattern: dict, app: dict):
    """Send an immediate Telegram alert for a detected pattern."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print(f"  ⚠️  Telegram not configured — printing alert instead:")
        print(format_pattern_alert(pattern, app))
        return

    text = format_pattern_alert(pattern, app)
    send_telegram_message(text)


def format_pattern_alert(pattern: dict, app: dict) -> str:
    """Format a pattern alert message for Telegram."""
    severity_emoji = {"high": "🚨", "medium": "⚠️", "low": "📋"}.get(pattern["severity"], "⚠️")
    category_emoji = {
        "crash": "💥",
        "performance": "🐌",
        "freeze": "🧊",
        "slow": "🐌",
        "login": "🔐",
        "subscription": "💳",
        "sync": "🔄",
        "notification": "🔔",
        "ui_bug": "🐛",
        "other": "📌",
    }.get(pattern["category"], "📌")

    reviews = pattern["reviews"][:3]  # Show up to 3 examples
    examples = []
    for r in reviews:
        date = r.get("created_date", "")[:10]
        title = r.get("title", r.get("body", "No text"))[:60]
        examples.append(f'• "{title}" — {r["rating"]}★ ({date})')

    examples_text = "\n".join(examples)

    lines = [
        f"{severity_emoji} *Pattern Alert — {app['name']}*",
        "",
        f"{category_emoji} Complaint: _{pattern['theme']}_",
        f"Count: *{pattern['count']} reviews* in the last 7 days",
        f"Rating avg: {pattern['avg_rating']}★",
        "",
        "Recent examples:",
        examples_text,
        "",
        f"👉 Severity: *{pattern['severity'].upper()}*",
    ]

    return "\n".join(lines)


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
                print(f"  ⚠️  Telegram API error: {result}")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"  ❌  Telegram error {e.code}: {body[:200]}")
    except Exception as e:
        print(f"  ❌  Telegram error: {e}")


# ─── Main Detection ───────────────────────────────────────────────────────────

def run_detection(days: int = PATTERN_WINDOW_DAYS, dry_run: bool = False, report_only: bool = False):
    """Main detection loop across all apps."""
    all_reviews = load_reviews()
    if not all_reviews:
        print("No reviews found in data/reviews.json")
        return 0

    metrics = load_metrics()
    recent_reviews = get_recent_reviews(all_reviews, days)

    if not recent_reviews:
        print(f"No reviews in the last {days} days")
        return 0

    # Group by app
    apps_map = defaultdict(lambda: {"name": "", "reviews": []})
    for r in recent_reviews:
        app_id = r.get("app_id", "unknown")
        apps_map[app_id]["name"] = r.get("app_name", "Unknown App")
        apps_map[app_id]["reviews"].append(r)

    total_alerts = 0
    total_patterns = 0

    for app_id, app_data in apps_map.items():
        app = {"id": app_id, "name": app_data["name"]}
        app_reviews = app_data["reviews"]

        print(f"\n🔍 {app['name']}: analyzing {len(app_reviews)} review(s) from last {days} days…")

        patterns = cluster_complaints_with_claude(app_reviews, app["name"])

        if not patterns:
            print(f"   ✅ No recurring patterns detected")
            continue

        for pattern in patterns:
            total_patterns += 1
            count = pattern["count"]
            theme = pattern["theme"]

            print(f"   📊 Pattern: \"{theme}\" — {count}x (avg {pattern['avg_rating']}★, {pattern['severity']} severity)")

            if count < PATTERN_THRESHOLD:
                print(f"      ↳ Below threshold ({PATTERN_THRESHOLD}+) — not alerting")
                continue

            if already_alerted(metrics, app_id, theme, ALERT_COOLDOWN_HOURS):
                print(f"      ↳ Already alerted in last {ALERT_COOLDOWN_HOURS}h — skipping")
                continue

            # Send alert
            if report_only:
                print(f"\n{'='*60}")
                print(format_pattern_alert(pattern, app))
                print('='*60)
            elif dry_run:
                print(f"      ↳ [dry-run] Would send Telegram alert")
                print(f"\n{format_pattern_alert(pattern, app)}\n")
            else:
                print(f"      ↳ 🚨 Sending Telegram alert!")
                send_telegram_alert(pattern, app)
                record_alert(metrics, app_id, app["name"], theme, count)
                total_alerts += 1

    if not dry_run and not report_only:
        save_metrics(metrics)

    print(f"\n{'─'*60}")
    print(f"Pattern detection complete: {total_patterns} pattern(s) found, {total_alerts} alert(s) sent")
    return total_alerts


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="ReviewReply — pattern detector")
    parser.add_argument("--report", action="store_true", help="Print report only, no Telegram")
    parser.add_argument("--dry-run", action="store_true", help="Detect but don't send Telegram")
    parser.add_argument("--days", type=int, default=PATTERN_WINDOW_DAYS,
                        help=f"Lookback window in days (default: {PATTERN_WINDOW_DAYS})")
    args = parser.parse_args()

    run_detection(days=args.days, dry_run=args.dry_run, report_only=args.report)


if __name__ == "__main__":
    main()
