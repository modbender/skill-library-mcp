#!/usr/bin/env python3
"""
adaptive_notifications.py — Self-tuning notification channel + timing intelligence.

Observes how the user responds to notifications (opened, dismissed, snoozed)
and adjusts:
  - Which channels to use per event type (openclaw, system, telegram)
  - Best time-of-day to send notifications
  - Notification frequency per event category

Usage:
  python3 adaptive_notifications.py --record-response <nudge_id> <response>
  python3 adaptive_notifications.py --get-channel "one_off_high_stakes"
  python3 adaptive_notifications.py --get-timing "Monday"
  python3 adaptive_notifications.py --analyse
  python3 adaptive_notifications.py --reset-learning
"""
from __future__ import annotations  # PEP 563 — all annotations are strings; required for Python 3.8 compat

import json
import sqlite3
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

if sys.version_info < (3, 8):
    print(json.dumps({"error": "python_version_too_old", "detail": "Python 3.8+ required."}))
    sys.exit(1)

SKILL_DIR = Path.home() / ".openclaw/workspace/skills/proactive-claw"
CONFIG_FILE = SKILL_DIR / "config.json"
sys.path.insert(0, str(SKILL_DIR / "scripts"))

DB_FILE = SKILL_DIR / "memory.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS notification_responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nudge_id TEXT DEFAULT '',
    event_type TEXT DEFAULT '',
    channel TEXT DEFAULT '',
    sent_at TEXT DEFAULT '',
    sent_hour INTEGER DEFAULT -1,
    sent_day TEXT DEFAULT '',
    response TEXT DEFAULT '',   -- 'opened', 'dismissed', 'snoozed', 'acted'
    response_delay_minutes INTEGER DEFAULT -1,
    recorded_at TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS notification_preferences (
    key TEXT PRIMARY KEY,
    value TEXT DEFAULT '',
    confidence REAL DEFAULT 0.0,
    updated_at TEXT DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_nr_event_type ON notification_responses(event_type);
CREATE INDEX IF NOT EXISTS idx_nr_channel ON notification_responses(channel);
"""

RESPONSE_SCORE = {
    "acted": 2.0,      # user acted on it immediately — best signal
    "opened": 1.0,     # user read it
    "snoozed": 0.0,    # not terrible, just bad timing
    "dismissed": -1.0, # user didn't want it
    "expired": -0.5,   # user never engaged
}

ALL_CHANNELS = ["openclaw", "system", "telegram"]
ALL_HOURS = list(range(6, 23))
MIN_SAMPLES = 5  # minimum samples before trusting a preference


def load_config() -> dict:
    try:
        with open(CONFIG_FILE) as f:
            return json.load(f)
    except Exception:
        return {}


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_FILE))
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    conn.commit()
    return conn


def record_response(conn: sqlite3.Connection, nudge_id: str, response: str,
                    event_type: str = "", channel: str = "",
                    sent_at: str = "", response_delay_minutes: int = -1) -> dict:
    """
    Record how the user responded to a notification.
    Called by daemon.py / cross_skill.py when a nudge is opened or dismissed.
    """
    if response not in RESPONSE_SCORE:
        return {"status": "error", "message": f"Unknown response: {response}. "
                f"Use: {', '.join(RESPONSE_SCORE.keys())}"}

    now = datetime.now(timezone.utc)
    sent_hour = -1
    sent_day = ""
    if sent_at:
        try:
            dt = datetime.fromisoformat(sent_at.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            sent_hour = dt.hour
            sent_day = ["Monday", "Tuesday", "Wednesday", "Thursday",
                        "Friday", "Saturday", "Sunday"][dt.weekday()]
        except Exception:
            pass

    conn.execute("""
        INSERT INTO notification_responses
            (nudge_id, event_type, channel, sent_at, sent_hour, sent_day,
             response, response_delay_minutes, recorded_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (nudge_id, event_type, channel, sent_at, sent_hour, sent_day,
          response, response_delay_minutes, now.isoformat()))
    conn.commit()

    # Trigger preference update if we have enough new data
    _update_preferences(conn)

    return {"status": "ok", "recorded": response, "nudge_id": nudge_id}


def _update_preferences(conn: sqlite3.Connection):
    """Recompute and store learned preferences from response history.
    Uses decay weighting to prioritise recent responses.
    """
    now = datetime.now(timezone.utc).isoformat()

    # Load decay utility
    try:
        from decay import decay_weight
        config = load_config()
        half_life = config.get("memory_decay_half_life_days", 90)
    except Exception:
        decay_weight = None
        half_life = 90

    # 1. Best channel per event type (with decay weighting)
    rows = conn.execute("""
        SELECT event_type, channel, response, sent_at
        FROM notification_responses
        WHERE event_type != '' AND channel != ''
    """).fetchall()

    channel_scores: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        base_score = RESPONSE_SCORE.get(row["response"], 0.0)
        if decay_weight and row["sent_at"]:
            w = decay_weight(row["sent_at"], half_life)
            base_score *= w
        channel_scores[row["event_type"]][row["channel"]].append(base_score)

    for event_type, channels in channel_scores.items():
        best_channel = None
        best_score = -99.0
        sufficient = False
        for channel, scores in channels.items():
            if len(scores) >= MIN_SAMPLES:
                sufficient = True
                avg = sum(scores) / len(scores)
                if avg > best_score:
                    best_score = avg
                    best_channel = channel
        if best_channel and sufficient:
            conf = min(1.0, sum(len(v) for v in channels.values()) / (MIN_SAMPLES * 3))
            key = f"channel_{event_type}"
            conn.execute("""
                INSERT OR REPLACE INTO notification_preferences (key, value, confidence, updated_at)
                VALUES (?, ?, ?, ?)
            """, (key, best_channel, round(conf, 2), now))

    # 2. Best hour of day (overall and per-day)
    hour_rows = conn.execute("""
        SELECT sent_hour, response, COUNT(*) as cnt
        FROM notification_responses
        WHERE sent_hour >= 0
        GROUP BY sent_hour, response
    """).fetchall()

    hour_scores: dict[int, list[float]] = defaultdict(list)
    for row in hour_rows:
        score = RESPONSE_SCORE.get(row["response"], 0.0)
        for _ in range(row["cnt"]):
            hour_scores[row["sent_hour"]].append(score)

    if hour_scores:
        best_hour = max(hour_scores, key=lambda h: (
            sum(hour_scores[h]) / len(hour_scores[h]) if hour_scores[h] else -99
        ))
        total = sum(len(v) for v in hour_scores.values())
        if total >= MIN_SAMPLES:
            conf = min(1.0, total / (MIN_SAMPLES * 5))
            conn.execute("""
                INSERT OR REPLACE INTO notification_preferences (key, value, confidence, updated_at)
                VALUES (?, ?, ?, ?)
            """, ("best_hour_overall", str(best_hour), round(conf, 2), now))

    # 3. Best hour per day-of-week
    day_hour_rows = conn.execute("""
        SELECT sent_day, sent_hour, response, COUNT(*) as cnt
        FROM notification_responses
        WHERE sent_hour >= 0 AND sent_day != ''
        GROUP BY sent_day, sent_hour, response
    """).fetchall()

    day_hour_scores: dict[str, dict[int, list[float]]] = defaultdict(lambda: defaultdict(list))
    for row in day_hour_rows:
        score = RESPONSE_SCORE.get(row["response"], 0.0)
        for _ in range(row["cnt"]):
            day_hour_scores[row["sent_day"]][row["sent_hour"]].append(score)

    for day, hours in day_hour_scores.items():
        total = sum(len(v) for v in hours.values())
        if total >= MIN_SAMPLES:
            best = max(hours, key=lambda h: sum(hours[h]) / len(hours[h]) if hours[h] else -99)
            conf = min(1.0, total / (MIN_SAMPLES * 3))
            conn.execute("""
                INSERT OR REPLACE INTO notification_preferences (key, value, confidence, updated_at)
                VALUES (?, ?, ?, ?)
            """, (f"best_hour_{day}", str(best), round(conf, 2), now))

    # 4. Per-event-type frequency (snoozed/dismissed rate → reduce frequency)
    freq_rows = conn.execute("""
        SELECT event_type, response, COUNT(*) as cnt
        FROM notification_responses
        WHERE event_type != ''
        GROUP BY event_type, response
    """).fetchall()

    event_type_totals: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for row in freq_rows:
        event_type_totals[row["event_type"]][row["response"]] = row["cnt"]

    for event_type, responses in event_type_totals.items():
        total = sum(responses.values())
        if total >= MIN_SAMPLES:
            dismiss_rate = (responses.get("dismissed", 0) + responses.get("expired", 0)) / total
            if dismiss_rate > 0.6:
                freq = "low"  # too many dismissed — reduce
            elif dismiss_rate < 0.2:
                freq = "high"
            else:
                freq = "normal"
            conn.execute("""
                INSERT OR REPLACE INTO notification_preferences (key, value, confidence, updated_at)
                VALUES (?, ?, ?, ?)
            """, (f"frequency_{event_type}", freq, round(1.0 - dismiss_rate, 2), now))

    conn.commit()


def get_channel_recommendation(conn: sqlite3.Connection, event_type: str,
                                config: dict) -> dict:
    """Return best channel for an event type, with fallback to config default."""
    pref = conn.execute(
        "SELECT value, confidence FROM notification_preferences WHERE key = ?",
        (f"channel_{event_type}",)).fetchone()

    default_channels = config.get("notification_channels", ["openclaw", "system"])

    if pref and float(pref["confidence"]) >= 0.4:
        return {
            "channel": pref["value"],
            "confidence": pref["confidence"],
            "source": "learned",
            "event_type": event_type,
        }

    # Fallback: highest-priority available channel
    for ch in ["telegram", "system", "openclaw"]:
        if ch in default_channels:
            return {
                "channel": ch,
                "confidence": 0.0,
                "source": "config_default",
                "event_type": event_type,
            }

    return {"channel": "openclaw", "confidence": 0.0, "source": "hardcoded_fallback",
            "event_type": event_type}


def get_timing_recommendation(conn: sqlite3.Connection, day: str = "") -> dict:
    """Return best hour to send notifications, optionally for a specific day."""
    if day:
        key = f"best_hour_{day}"
        pref = conn.execute(
            "SELECT value, confidence FROM notification_preferences WHERE key = ?",
            (key,)).fetchone()
        if pref and float(pref["confidence"]) >= 0.4:
            return {
                "best_hour": int(pref["value"]),
                "day": day,
                "confidence": pref["confidence"],
                "source": "learned",
            }

    # Fall back to overall best hour
    pref = conn.execute(
        "SELECT value, confidence FROM notification_preferences WHERE key = ?",
        ("best_hour_overall",)).fetchone()
    if pref and float(pref["confidence"]) >= 0.3:
        return {
            "best_hour": int(pref["value"]),
            "day": day or "any",
            "confidence": pref["confidence"],
            "source": "learned_overall",
        }

    return {
        "best_hour": 9,  # default: 9am
        "day": day or "any",
        "confidence": 0.0,
        "source": "default",
    }


def analyse(conn: sqlite3.Connection) -> dict:
    """Return a full analysis of learned notification preferences."""
    total = conn.execute("SELECT COUNT(*) FROM notification_responses").fetchone()[0]
    if total == 0:
        return {
            "status": "insufficient_data",
            "message": "No notification responses recorded yet. "
                       "Responses are recorded automatically as you interact with nudges.",
            "total_responses": 0,
        }

    # Response breakdown
    breakdown = {}
    rows = conn.execute("""
        SELECT response, COUNT(*) as cnt FROM notification_responses GROUP BY response
    """).fetchall()
    for row in rows:
        breakdown[row["response"]] = row["cnt"]

    # Learned preferences
    prefs = conn.execute("SELECT key, value, confidence FROM notification_preferences "
                         "ORDER BY confidence DESC").fetchall()
    preferences = [{"key": p["key"], "value": p["value"], "confidence": p["confidence"]}
                   for p in prefs]

    # Best + worst hours
    hour_rows = conn.execute("""
        SELECT sent_hour, AVG(
            CASE response
                WHEN 'acted' THEN 2.0 WHEN 'opened' THEN 1.0
                WHEN 'snoozed' THEN 0.0 WHEN 'dismissed' THEN -1.0
                ELSE -0.5 END) as avg_score, COUNT(*) as cnt
        FROM notification_responses WHERE sent_hour >= 0
        GROUP BY sent_hour HAVING cnt >= 2 ORDER BY avg_score DESC
    """).fetchall()

    hours_ranked = [
        {"hour": row["sent_hour"],
         "avg_score": round(row["avg_score"], 2),
         "samples": row["cnt"]}
        for row in hour_rows
    ]

    insights = []
    if hours_ranked:
        best = hours_ranked[0]
        insights.append(f"✅ Best hour to notify: {best['hour']:02d}:00 "
                        f"(score {best['avg_score']:+.1f})")
        worst = hours_ranked[-1]
        if worst["avg_score"] < -0.3:
            insights.append(f"⚠️ Avoid {worst['hour']:02d}:00 "
                            f"(score {worst['avg_score']:+.1f})")

    channel_prefs = [p for p in preferences if p["key"].startswith("channel_")]
    for cp in channel_prefs[:3]:
        et = cp["key"].replace("channel_", "")
        insights.append(f"📡 {et}: best via {cp['value']} (confidence {cp['confidence']:.0%})")

    return {
        "status": "ok",
        "total_responses": total,
        "response_breakdown": breakdown,
        "preferences": preferences,
        "hours_ranked": hours_ranked[:5],
        "insights": insights,
    }


def reset_learning(conn: sqlite3.Connection) -> dict:
    """Clear all learned preferences (keep raw response log)."""
    conn.execute("DELETE FROM notification_preferences")
    conn.commit()
    return {"status": "ok", "message": "All learned preferences cleared. "
            "Raw response log preserved for re-learning."}


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--record-response", nargs=2, metavar=("NUDGE_ID", "RESPONSE"),
                        help="Record user response to a nudge (opened/dismissed/snoozed/acted)")
    parser.add_argument("--event-type", default="",
                        help="Event type for --record-response")
    parser.add_argument("--channel", default="",
                        help="Channel used for --record-response")
    parser.add_argument("--sent-at", default="",
                        help="ISO datetime when notification was sent")
    parser.add_argument("--get-channel", metavar="EVENT_TYPE",
                        help="Get recommended channel for an event type")
    parser.add_argument("--get-timing", metavar="DAY",
                        help="Get recommended notification hour for a day (e.g. Monday)")
    parser.add_argument("--analyse", action="store_true",
                        help="Show full adaptive learning analysis")
    parser.add_argument("--reset-learning", action="store_true",
                        help="Clear learned preferences")
    args = parser.parse_args()

    conn = get_db()
    config = load_config()

    if args.record_response:
        print(json.dumps(record_response(
            conn, args.record_response[0], args.record_response[1],
            event_type=args.event_type, channel=args.channel, sent_at=args.sent_at),
            indent=2))
    elif args.get_channel:
        print(json.dumps(get_channel_recommendation(conn, args.get_channel, config), indent=2))
    elif args.get_timing:
        print(json.dumps(get_timing_recommendation(conn, args.get_timing), indent=2))
    elif args.analyse:
        print(json.dumps(analyse(conn), indent=2))
    elif args.reset_learning:
        print(json.dumps(reset_learning(conn), indent=2))
    else:
        parser.print_help()

    conn.close()


if __name__ == "__main__":
    main()
