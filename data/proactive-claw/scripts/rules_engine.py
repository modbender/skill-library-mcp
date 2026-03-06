#!/usr/bin/env python3
"""
rules_engine.py — Natural language rule parser for proactive-claw.

Converts plain English user instructions into structured rules stored in memory.db.
Rules are applied by scan_calendar.py to adjust event scores.

Usage:
  python3 rules_engine.py --parse "Never bother me about standups unless I haven't spoken in 2 weeks"
  python3 rules_engine.py --parse "Always prep me 2 days before anything with the word board"
  python3 rules_engine.py --parse "Suppress all events on Saturdays"
  python3 rules_engine.py --list
  python3 rules_engine.py --delete <rule_id>
"""

import argparse
import json
import re
import sys
from pathlib import Path

if sys.version_info < (3, 8):
    print(json.dumps({"error": "python_version_too_old", "detail": f"Python 3.8+ required."}))
    sys.exit(1)

SKILL_DIR = Path.home() / ".openclaw/workspace/skills/proactive-claw"
sys.path.insert(0, str(SKILL_DIR / "scripts"))


# ─── Rule Patterns ────────────────────────────────────────────────────────────
# Each pattern: (regex, parser_fn) → returns rule_json dict or None

def _extract_keyword(text: str) -> str:
    """Extract quoted or last noun phrase."""
    m = re.search(r'"([^"]+)"', text)
    if m:
        return m.group(1).lower()
    m = re.search(r"word[s]?\s+(\w+)", text, re.I)
    if m:
        return m.group(1).lower()
    m = re.search(r"(?:about|for|with)\s+(\w+)", text, re.I)
    if m:
        return m.group(1).lower()
    return ""


def _extract_days(text: str) -> int:
    m = re.search(r"(\d+)\s*day", text, re.I)
    return int(m.group(1)) if m else 1


def _extract_hours(text: str) -> int:
    m = re.search(r"(\d+)\s*hour", text, re.I)
    return int(m.group(1)) if m else 1


RULE_PATTERNS = [
    # "Never bother me about standups" / "Suppress standup"
    (r"(?:never|suppress|ignore|skip|don.?t|do not)\s+(?:bother|ask|remind|notify|check).+(?:about|for)?\s+(\w+)",
     lambda m, text: {
         "condition": {"title_contains": m.group(1).lower()},
         "action": {"suppress": True},
         "description": f"Suppress all check-ins for events matching '{m.group(1)}'",
     }),

    # "Always prep me N days before anything with the word X"
    (r"always\s+prep\s+(?:me\s+)?(\d+)\s+day[s]?\s+before\s+.+?(?:word\s+)?[\"']?(\w+)[\"']?",
     lambda m, text: {
         "condition": {"title_contains": m.group(2).lower()},
         "action": {"set_score": 9, "pre_checkin_offset": f"{m.group(1)} days"},
         "description": f"Always prep {m.group(1)} days before '{m.group(2)}' events",
     }),

    # "Never bother me on Saturdays / Sundays / weekends"
    (r"(?:never|don.?t|do not)\s+(?:bother|notify|remind|ask).+(?:saturday|sunday|weekend)",
     lambda m, text: {
         "condition": {"day_of_week": ["Saturday", "Sunday"]},
         "action": {"suppress": True},
         "description": "Suppress all check-ins on weekends",
     }),

    # "Suppress all events on Saturdays"
    (r"suppress\s+.+(?:saturday|sunday|weekend)",
     lambda m, text: {
         "condition": {"day_of_week": ["Saturday", "Sunday"]},
         "action": {"suppress": True},
         "description": "Suppress all check-ins on weekends",
     }),

    # "Always remind me N hours before X"
    (r"always\s+remind\s+(?:me\s+)?(\d+)\s+hour[s]?\s+before\s+.+?(?:word\s+)?[\"']?(\w+)[\"']?",
     lambda m, text: {
         "condition": {"title_contains": m.group(2).lower()},
         "action": {"set_score": 8, "pre_checkin_offset": f"{m.group(1)} hours"},
         "description": f"Always remind {m.group(1)} hours before '{m.group(2)}' events",
     }),

    # "Boost / raise score for X"
    (r"(?:boost|raise|increase)\s+(?:score|priority)\s+for\s+.+?(?:word\s+)?[\"']?(\w+)[\"']?",
     lambda m, text: {
         "condition": {"title_contains": m.group(1).lower()},
         "action": {"add_score": 3},
         "description": f"Raise score by 3 for events matching '{m.group(1)}'",
     }),

    # "Lower / reduce score for X"
    (r"(?:lower|reduce|decrease)\s+(?:score|priority)\s+for\s+.+?(?:word\s+)?[\"']?(\w+)[\"']?",
     lambda m, text: {
         "condition": {"title_contains": m.group(1).lower()},
         "action": {"add_score": -3},
         "description": f"Lower score by 3 for events matching '{m.group(1)}'",
     }),

    # "Only check in every N occurrences for X"
    (r"(?:only|just)\s+check.?in\s+every\s+(\d+)\s+(?:time|occurrence|instance).+?(?:word\s+)?[\"']?(\w+)[\"']?",
     lambda m, text: {
         "condition": {"title_contains": m.group(2).lower(), "recurring_only": True},
         "action": {"check_in_every_n": int(m.group(1))},
         "description": f"Check in every {m.group(1)} occurrences of '{m.group(2)}'",
     }),
]


def parse_rule(text: str) -> dict:
    """Try each pattern in order. Return first match as rule_json."""
    text_lower = text.lower().strip()
    for pattern, parser in RULE_PATTERNS:
        m = re.search(pattern, text_lower)
        if m:
            try:
                rule_json = parser(m, text_lower)
                if rule_json:
                    rule_json["source_text"] = text
                    return {"parsed": True, "rule_json": rule_json,
                            "description": rule_json.get("description", text)}
            except Exception:
                continue

    # Fallback: couldn't parse
    return {
        "parsed": False,
        "rule_json": None,
        "description": None,
        "suggestion": (
            "Couldn't parse that rule automatically. Try phrasing like:\n"
            "  • 'Never bother me about standups'\n"
            "  • 'Always prep me 2 days before anything with the word board'\n"
            "  • 'Suppress all events on weekends'\n"
            "  • 'Boost score for investor'\n"
            "  • 'Only check in every 4 occurrences of standup'"
        ),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--parse", metavar="RULE_TEXT", help="Parse and save a natural language rule")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--delete", type=int, metavar="RULE_ID")
    parser.add_argument("--dry-run", action="store_true", help="Parse but don't save")
    args = parser.parse_args()

    from memory import get_db, save_rule, get_active_rules

    if args.parse:
        result = parse_rule(args.parse)
        if not result["parsed"]:
            print(json.dumps(result, indent=2))
            return

        if args.dry_run:
            print(json.dumps({"dry_run": True, "would_save": result}, indent=2))
            return

        conn = get_db()
        save_rule(conn, args.parse, result["rule_json"])
        conn.close()
        print(json.dumps({
            "status": "saved",
            "rule_text": args.parse,
            "description": result["description"],
        }, indent=2))

    elif args.list:
        conn = get_db()
        rules = get_active_rules(conn)
        conn.close()
        print(json.dumps({"rules": rules}, indent=2))

    elif args.delete:
        conn = get_db()
        conn.execute("UPDATE user_rules SET active=0 WHERE id=?", (args.delete,))
        conn.commit()
        conn.close()
        print(json.dumps({"status": "deleted", "rule_id": args.delete}))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
