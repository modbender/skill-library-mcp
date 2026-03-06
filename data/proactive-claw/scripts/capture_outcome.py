#!/usr/bin/env python3
"""
capture_outcome.py — Save post-event outcome and sync to notes destination.

Usage:
  python3 capture_outcome.py \
    --event-title "Investor Demo" \
    --event-datetime "2025-03-15T14:00:00" \
    --recurring-id "" \
    --notes "Demo went well. Investors liked the product. Need to send deck." \
    --action-items "Send deck to investors|Schedule follow-up call|Update pricing page" \
    --sentiment "positive" \
    --follow-up-needed "true"
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# Python version guard
if sys.version_info < (3, 8):
    print(json.dumps({
        "error": "python_version_too_old",
        "detail": f"Python 3.8+ required. You have {sys.version}.",
        "fix": "Install Python 3.8+: https://www.python.org/downloads/"
    }))
    sys.exit(1)

SKILL_DIR = Path.home() / ".openclaw/workspace/skills/proactive-claw"
CONFIG_FILE = SKILL_DIR / "config.json"
OUTCOMES_DIR = SKILL_DIR / "outcomes"


def load_config():
    with open(CONFIG_FILE) as f:
        return json.load(f)


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:40]


def save_local(outcome, notes_path):
    OUTCOMES_DIR.mkdir(parents=True, exist_ok=True)
    date_str = outcome["event_datetime"][:10]
    slug = slugify(outcome["event_title"])
    filename = OUTCOMES_DIR / f"{date_str}_{slug}.json"
    with open(filename, "w") as f:
        json.dump(outcome, f, indent=2)
    return str(filename)


def _applescript_escape(s: str) -> str:
    """Escape a string for safe embedding in an AppleScript quoted string."""
    return s.replace("\\", "\\\\").replace('"', '\\"')


def save_apple_notes(outcome):
    import tempfile
    title = f"🦞 {outcome['event_title']} — {outcome['event_datetime'][:10]}"
    items = "\n".join(f"• {item}" for item in outcome.get("action_items", []))
    body = (
        f"Event: {outcome['event_title']}\n"
        f"Date: {outcome['event_datetime'][:10]}\n"
        f"Sentiment: {outcome.get('sentiment', 'neutral')}\n\n"
        f"Notes:\n{outcome.get('outcome_notes', '')}\n\n"
        f"Action Items:\n{items if items else 'None'}\n\n"
        f"Follow-up needed: {outcome.get('follow_up_needed', False)}\n"
        f"Tags: {', '.join(outcome.get('tags', []))}\n"
    )
    # Write body to a temp file to avoid any injection via string interpolation
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as tf:
        tf.write(body)
        tmp_path = tf.name

    safe_title = _applescript_escape(title)
    safe_path = _applescript_escape(tmp_path)
    script = f'''
set noteBody to (read POSIX file "{safe_path}" as «class utf8»)
tell application "Notes"
    make new note at folder "Notes" with properties {{name:"{safe_title}", body:noteBody}}
end tell
'''
    try:
        subprocess.run(["osascript", "-e", script], check=True, capture_output=True)
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--event-title", required=True)
    parser.add_argument("--event-datetime", required=True)
    parser.add_argument("--recurring-id", default="")
    parser.add_argument("--notes", default="")
    parser.add_argument("--action-items", default="",
                        help="Pipe-separated list OR use --action-items-json for items containing pipes")
    parser.add_argument("--action-items-json", default="",
                        help="JSON array string, e.g. '[\"item 1\", \"item 2\"]'")
    parser.add_argument("--sentiment", choices=["positive", "neutral", "negative"], default="neutral")
    parser.add_argument("--follow-up-needed", choices=["true", "false"], default="false")
    parser.add_argument("--tags", default="")
    args = parser.parse_args()

    config = load_config()

    if args.action_items_json:
        try:
            action_items = json.loads(args.action_items_json)
            if not isinstance(action_items, list):
                raise ValueError("action-items-json must be a JSON array")
        except (json.JSONDecodeError, ValueError) as e:
            print(json.dumps({"error": "invalid_action_items_json", "detail": str(e)}))
            sys.exit(1)
    else:
        action_items = [i.strip() for i in args.action_items.split("|") if i.strip()] if args.action_items else []
    tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else []

    outcome = {
        "event_title": args.event_title,
        "event_datetime": args.event_datetime,
        "recurring_id": args.recurring_id,
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "prep_done": True,
        "outcome_notes": args.notes,
        "action_items": action_items,
        "sentiment": args.sentiment,
        "follow_up_needed": args.follow_up_needed == "true",
        "tags": tags,
    }

    result = {"status": "saved", "destinations": []}

    # Always save locally
    notes_path = os.path.expanduser(config.get("notes_path", str(OUTCOMES_DIR)))
    local_path = save_local(outcome, notes_path)
    result["destinations"].append({"type": "local", "path": local_path})

    # Optional: Apple Notes
    destination = config.get("notes_destination", "local")
    if destination == "apple-notes":
        try:
            save_apple_notes(outcome)
            result["destinations"].append({"type": "apple-notes", "status": "created"})
        except Exception as e:
            result["destinations"].append({"type": "apple-notes", "status": "error", "error": str(e)})

    # Optional: Notion outcome logging.
    # NETWORK CALL: POST https://api.notion.com/v1/pages
    # Sends: NOTION_API_KEY (Bearer token) + event title, date, sentiment, notes text.
    # Gated by: notes_destination="notion" in config.json AND both env vars set.
    # NOTION_API_KEY: your Notion integration token (env var)
    # NOTION_OUTCOMES_DB_ID: the database ID where outcomes are saved (env var)
    elif destination == "notion":
        notion_key = os.environ.get("NOTION_API_KEY")
        notion_db = os.environ.get("NOTION_OUTCOMES_DB_ID")
        if notion_key and notion_db:
            try:
                import urllib.request
                payload = json.dumps({
                    "parent": {"database_id": notion_db},
                    "properties": {
                        "Name": {"title": [{"text": {"content": args.event_title}}]},
                        "Date": {"date": {"start": args.event_datetime[:10]}},
                        "Sentiment": {"select": {"name": args.sentiment}},
                        "Notes": {"rich_text": [{"text": {"content": args.notes}}]},
                    }
                }).encode()
                req = urllib.request.Request(
                    "https://api.notion.com/v1/pages",
                    data=payload,
                    headers={
                        "Authorization": f"Bearer {notion_key}",
                        "Content-Type": "application/json",
                        "Notion-Version": "2022-06-28"
                    }
                )
                urllib.request.urlopen(req)
                result["destinations"].append({"type": "notion", "status": "created"})
            except Exception as e:
                result["destinations"].append({"type": "notion", "status": "error", "error": str(e)})

    result["outcome"] = outcome
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
