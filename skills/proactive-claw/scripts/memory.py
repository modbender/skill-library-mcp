#!/usr/bin/env python3
"""
memory.py — SQLite-backed memory layer for proactive-claw.

Replaces flat outcomes/ JSON files with a queryable store.
Supports semantic search via lightweight TF-IDF (no external model needed).
Falls back to flat JSON import on first run.

Usage:
  python3 memory.py --import-outcomes        # migrate existing JSON outcomes
  python3 memory.py --save <outcome_json>    # save a new outcome
  python3 memory.py --search "underprepared" # semantic search
  python3 memory.py --patterns <recurring_id>
  python3 memory.py --summary [--days 90]    # quarterly/period summary
  python3 memory.py --open-actions           # list unresolved action items
"""

import argparse
import json
import math
import re
import sqlite3
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

if sys.version_info < (3, 8):
    print(json.dumps({"error": "python_version_too_old", "detail": f"Python 3.8+ required. You have {sys.version}."}))
    sys.exit(1)

SKILL_DIR = Path.home() / ".openclaw/workspace/skills/proactive-claw"
DB_FILE = SKILL_DIR / "memory.db"
OUTCOMES_DIR = SKILL_DIR / "outcomes"


# ─── Schema ───────────────────────────────────────────────────────────────────

SCHEMA = """
CREATE TABLE IF NOT EXISTS outcomes (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    event_title     TEXT NOT NULL,
    event_datetime  TEXT NOT NULL,
    recurring_id    TEXT DEFAULT '',
    event_type      TEXT DEFAULT 'one_off_standard',
    captured_at     TEXT NOT NULL,
    prep_done       INTEGER DEFAULT 0,
    outcome_notes   TEXT DEFAULT '',
    sentiment       TEXT DEFAULT 'neutral',
    follow_up_needed INTEGER DEFAULT 0,
    tags            TEXT DEFAULT '[]',
    search_text     TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS action_items (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    outcome_id  INTEGER NOT NULL REFERENCES outcomes(id),
    text        TEXT NOT NULL,
    resolved    INTEGER DEFAULT 0,
    resolved_at TEXT DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS user_rules (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_text   TEXT NOT NULL,
    rule_json   TEXT NOT NULL,
    created_at  TEXT NOT NULL,
    active      INTEGER DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_recurring ON outcomes(recurring_id);
CREATE INDEX IF NOT EXISTS idx_datetime  ON outcomes(event_datetime);
CREATE INDEX IF NOT EXISTS idx_sentiment ON outcomes(sentiment);
"""


def get_db() -> sqlite3.Connection:
    SKILL_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_FILE))
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    conn.commit()
    return conn


# ─── TF-IDF Search ────────────────────────────────────────────────────────────

def tokenise(text: str) -> list:
    return re.findall(r"[a-z]{3,}", text.lower())


def build_tfidf(docs: list) -> tuple:
    """Return (tf_list, idf_dict) for a list of token lists."""
    N = len(docs)
    idf = {}
    df = Counter()
    for tokens in docs:
        for t in set(tokens):
            df[t] += 1
    for t, count in df.items():
        idf[t] = math.log((N + 1) / (count + 1)) + 1
    tf_list = []
    for tokens in docs:
        c = Counter(tokens)
        total = max(len(tokens), 1)
        tf_list.append({t: v / total for t, v in c.items()})
    return tf_list, idf


def cosine(vec_a: dict, vec_b: dict, idf: dict) -> float:
    keys = set(vec_a) & set(vec_b)
    if not keys:
        return 0.0
    dot = sum(vec_a[k] * vec_b[k] * idf.get(k, 1) ** 2 for k in keys)
    mag_a = math.sqrt(sum((vec_a[k] * idf.get(k, 1)) ** 2 for k in vec_a))
    mag_b = math.sqrt(sum((vec_b[k] * idf.get(k, 1)) ** 2 for k in vec_b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


# ─── CRUD ─────────────────────────────────────────────────────────────────────

def save_outcome(conn: sqlite3.Connection, outcome: dict) -> int:
    search_text = " ".join([
        outcome.get("event_title", ""),
        outcome.get("outcome_notes", ""),
        " ".join(outcome.get("action_items", [])),
        " ".join(outcome.get("tags", [])),
    ])
    cur = conn.execute("""
        INSERT INTO outcomes
          (event_title, event_datetime, recurring_id, event_type, captured_at,
           prep_done, outcome_notes, sentiment, follow_up_needed, tags, search_text)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
    """, (
        outcome.get("event_title", ""),
        outcome.get("event_datetime", ""),
        outcome.get("recurring_id", ""),
        outcome.get("event_type", "one_off_standard"),
        outcome.get("captured_at", datetime.now(timezone.utc).isoformat()),
        int(outcome.get("prep_done", False)),
        outcome.get("outcome_notes", ""),
        outcome.get("sentiment", "neutral"),
        int(outcome.get("follow_up_needed", False)),
        json.dumps(outcome.get("tags", [])),
        search_text,
    ))
    outcome_id = cur.lastrowid
    for item in outcome.get("action_items", []):
        conn.execute("INSERT INTO action_items (outcome_id, text) VALUES (?,?)", (outcome_id, item))
    conn.commit()
    return outcome_id


def get_patterns(conn: sqlite3.Connection, recurring_id: str) -> dict:
    rows = conn.execute("""
        SELECT o.*, GROUP_CONCAT(a.text, '||') as items
        FROM outcomes o
        LEFT JOIN action_items a ON a.outcome_id = o.id
        WHERE o.recurring_id = ?
        GROUP BY o.id
        ORDER BY o.event_datetime DESC
        LIMIT 10
    """, (recurring_id,)).fetchall()

    outcomes = []
    for r in rows:
        items = [i for i in (r["items"] or "").split("||") if i]
        outcomes.append({
            "event_title": r["event_title"],
            "event_datetime": r["event_datetime"],
            "sentiment": r["sentiment"],
            "prep_done": bool(r["prep_done"]),
            "follow_up_needed": bool(r["follow_up_needed"]),
            "action_items": items,
            "tags": json.loads(r["tags"] or "[]"),
        })

    if not outcomes:
        return {"recurring_id": recurring_id, "total_outcomes": 0, "outcomes": []}

    # Use decay-weighted averages if available
    try:
        from decay import weighted_average
        config_path = SKILL_DIR / "config.json"
        half_life = 90
        if config_path.exists():
            import json as _json
            half_life = _json.loads(config_path.read_text()).get("memory_decay_half_life_days", 90)
        item_pairs = [(len(o["action_items"]), o["event_datetime"]) for o in outcomes]
        prep_pairs = [(1.0 if o["prep_done"] else 0.0, o["event_datetime"]) for o in outcomes]
        avg_items = weighted_average(item_pairs, half_life)
        prep_rate = weighted_average(prep_pairs, half_life)
    except Exception:
        avg_items = sum(len(o["action_items"]) for o in outcomes) / len(outcomes)
        prep_rate = sum(1 for o in outcomes if o["prep_done"]) / len(outcomes)

    sentiments = Counter(o["sentiment"] for o in outcomes)

    return {
        "recurring_id": recurring_id,
        "total_outcomes": len(outcomes),
        "avg_action_items": round(avg_items, 1),
        "prep_rate": round(prep_rate, 2),
        "sentiment_distribution": dict(sentiments),
        "recommendation": _pattern_recommendation(avg_items, prep_rate, sentiments),
        "outcomes": outcomes,
    }


def _pattern_recommendation(avg_items: float, prep_rate: float, sentiments: Counter) -> str:
    if avg_items == 0 and sentiments.get("positive", 0) >= 3:
        return "routine_low_stakes: suppress check-ins"
    if avg_items >= 3:
        return "routine_high_stakes: always prep, reference last action items"
    if prep_rate < 0.3:
        return "low_prep_rate: user often skips prep — try shorter offset (2h)"
    if sentiments.get("negative", 0) >= 2:
        return "frequent_negative: offer more structured prep support"
    return "standard: default behaviour"


def semantic_search(conn: sqlite3.Connection, query: str, limit: int = 5) -> list:
    rows = conn.execute("SELECT id, search_text, event_title, event_datetime FROM outcomes").fetchall()
    if not rows:
        return []
    docs = [tokenise(r["search_text"]) for r in rows]
    query_tokens = tokenise(query)
    tf_list, idf = build_tfidf(docs)
    query_tf = Counter(query_tokens)
    total = max(len(query_tokens), 1)
    query_vec = {t: v / total for t, v in query_tf.items()}
    scored = []
    for i, row in enumerate(rows):
        score = cosine(query_vec, tf_list[i], idf)
        if score > 0:
            scored.append((score, row))
    scored.sort(key=lambda x: -x[0])
    return [
        {"score": round(s, 3), "event_title": r["event_title"], "event_datetime": r["event_datetime"]}
        for s, r in scored[:limit]
    ]


def get_open_actions(conn: sqlite3.Connection) -> list:
    rows = conn.execute("""
        SELECT a.id, a.text, o.event_title, o.event_datetime
        FROM action_items a
        JOIN outcomes o ON o.id = a.outcome_id
        WHERE a.resolved = 0
        ORDER BY o.event_datetime DESC
    """).fetchall()
    return [{"action_id": r["id"], "text": r["text"],
             "event": r["event_title"], "event_date": r["event_datetime"][:10]} for r in rows]


def resolve_action(conn: sqlite3.Connection, action_id: int):
    conn.execute("UPDATE action_items SET resolved=1, resolved_at=? WHERE id=?",
                 (datetime.now(timezone.utc).isoformat(), action_id))
    conn.commit()


def get_summary(conn: sqlite3.Connection, days: int = 90) -> dict:
    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    rows = conn.execute("""
        SELECT o.*, GROUP_CONCAT(a.text, '||') as items
        FROM outcomes o
        LEFT JOIN action_items a ON a.outcome_id = o.id
        WHERE o.event_datetime >= ?
        GROUP BY o.id
    """, (since,)).fetchall()

    if not rows:
        return {"period_days": days, "total_events": 0}

    by_type = Counter(r["event_type"] for r in rows)
    by_sentiment = Counter(r["sentiment"] for r in rows)
    total_items = sum(len([i for i in (r["items"] or "").split("||") if i]) for r in rows)
    prep_count = sum(1 for r in rows if r["prep_done"])
    followup_needed = sum(1 for r in rows if r["follow_up_needed"])

    # Top recurring events by frequency
    recurring = Counter(r["event_title"] for r in rows if r["recurring_id"])
    top_recurring = recurring.most_common(5)

    return {
        "period_days": days,
        "total_events": len(rows),
        "event_type_breakdown": dict(by_type),
        "sentiment_breakdown": dict(by_sentiment),
        "total_action_items_captured": total_items,
        "avg_action_items_per_event": round(total_items / len(rows), 1),
        "prep_rate": round(prep_count / len(rows), 2),
        "follow_up_needed_count": followup_needed,
        "top_recurring_events": [{"title": t, "count": c} for t, c in top_recurring],
        "insight": _summary_insight(by_type, by_sentiment, total_items, len(rows)),
    }


def _summary_insight(by_type: Counter, by_sentiment: Counter, total_items: int, total: int) -> str:
    insights = []
    if by_type.get("one_off_high_stakes", 0) / max(total, 1) > 0.3:
        insights.append("High proportion of high-stakes events — consider more prep time")
    if by_sentiment.get("negative", 0) / max(total, 1) > 0.25:
        insights.append("Frequent negative outcomes — review prep patterns")
    if total_items / max(total, 1) > 4:
        insights.append("Heavy action item load — consider a weekly review habit")
    return "; ".join(insights) if insights else "Patterns look healthy"


def import_json_outcomes(conn: sqlite3.Connection) -> int:
    """Migrate existing flat JSON outcomes into SQLite."""
    if not OUTCOMES_DIR.exists():
        return 0
    imported = 0
    for f in sorted(OUTCOMES_DIR.glob("*.json")):
        try:
            outcome = json.loads(f.read_text())
            save_outcome(conn, outcome)
            imported += 1
        except Exception:
            pass
    return imported


# ─── User Rules ───────────────────────────────────────────────────────────────

def save_rule(conn: sqlite3.Connection, rule_text: str, rule_json: dict):
    conn.execute(
        "INSERT INTO user_rules (rule_text, rule_json, created_at) VALUES (?,?,?)",
        (rule_text, json.dumps(rule_json), datetime.now(timezone.utc).isoformat())
    )
    conn.commit()


def get_active_rules(conn: sqlite3.Connection) -> list:
    rows = conn.execute("SELECT * FROM user_rules WHERE active=1").fetchall()
    return [{"id": r["id"], "rule_text": r["rule_text"],
             "rule_json": json.loads(r["rule_json"])} for r in rows]


def apply_rules(rules: list, event: dict, base_score: int) -> int:
    """Apply user rules to adjust event score. Returns adjusted score."""
    score = base_score
    title = (event.get("title") or "").lower()
    for rule in rules:
        rj = rule.get("rule_json", {})
        condition = rj.get("condition", {})
        action = rj.get("action", {})

        # Condition: title contains keyword
        kw = condition.get("title_contains", "")
        if kw and kw.lower() not in title:
            continue

        # Condition: event_type matches
        et = condition.get("event_type", "")
        if et and event.get("event_type", "") != et:
            continue

        # Condition: recurring only
        if condition.get("recurring_only") and not event.get("recurring_id"):
            continue

        # Apply action
        if "set_score" in action:
            score = action["set_score"]
        if "add_score" in action:
            score += action["add_score"]
        if "suppress" in action and action["suppress"]:
            score = 0

    return max(0, min(10, score))


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--import-outcomes", action="store_true")
    parser.add_argument("--save", metavar="JSON", help="JSON string of outcome to save")
    parser.add_argument("--search", metavar="QUERY")
    parser.add_argument("--patterns", metavar="RECURRING_ID")
    parser.add_argument("--summary", action="store_true")
    parser.add_argument("--days", type=int, default=90)
    parser.add_argument("--open-actions", action="store_true")
    parser.add_argument("--resolve-action", type=int, metavar="ACTION_ID")
    parser.add_argument("--add-rule", nargs=2, metavar=("RULE_TEXT", "RULE_JSON"))
    parser.add_argument("--list-rules", action="store_true")
    parser.add_argument("--apply-rules", metavar="EVENT_JSON")
    args = parser.parse_args()

    conn = get_db()

    if args.import_outcomes:
        n = import_json_outcomes(conn)
        print(json.dumps({"status": "imported", "count": n}))

    elif args.save:
        outcome = json.loads(args.save)
        oid = save_outcome(conn, outcome)
        print(json.dumps({"status": "saved", "outcome_id": oid}))

    elif args.search:
        results = semantic_search(conn, args.search)
        print(json.dumps({"query": args.search, "results": results}, indent=2))

    elif args.patterns:
        print(json.dumps(get_patterns(conn, args.patterns), indent=2))

    elif args.summary:
        print(json.dumps(get_summary(conn, args.days), indent=2))

    elif args.open_actions:
        print(json.dumps({"open_action_items": get_open_actions(conn)}, indent=2))

    elif args.resolve_action:
        resolve_action(conn, args.resolve_action)
        print(json.dumps({"status": "resolved", "action_id": args.resolve_action}))

    elif args.add_rule:
        rule_text, rule_json_str = args.add_rule
        rule_json = json.loads(rule_json_str)
        save_rule(conn, rule_text, rule_json)
        print(json.dumps({"status": "rule_saved", "rule_text": rule_text}))

    elif args.list_rules:
        print(json.dumps({"rules": get_active_rules(conn)}, indent=2))

    elif args.apply_rules:
        event = json.loads(args.apply_rules)
        rules = get_active_rules(conn)
        adjusted = apply_rules(rules, event, event.get("score", 5))
        print(json.dumps({"original_score": event.get("score"), "adjusted_score": adjusted, "rules_applied": len(rules)}))

    else:
        parser.print_help()

    conn.close()


if __name__ == "__main__":
    main()
