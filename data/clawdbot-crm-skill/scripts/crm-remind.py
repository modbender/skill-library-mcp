#!/usr/bin/python3
"""
CRM Remind Tool - Create cron reminders for follow-ups
Usage:
    python crm-remind.py alice-chen                    # Remind on follow_up date
    python crm-remind.py alice-chen --in 3d            # Remind in 3 days
    python crm-remind.py alice-chen --at 2026-02-15    # Remind on specific date
    python crm-remind.py --list                        # List pending reminders
"""

import argparse
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
import yaml

CONTACTS_DIR = Path(__file__).parent.parent
PEOPLE_DIR = CONTACTS_DIR / "people"
REMINDERS_FILE = CONTACTS_DIR / ".reminders.json"


def parse_frontmatter(filepath: Path) -> dict | None:
    """Extract YAML frontmatter from a markdown file."""
    try:
        content = filepath.read_text()
        if not content.startswith("---"):
            return None
        end = content.find("---", 3)
        if end == -1:
            return None
        yaml_content = content[3:end].strip()
        return yaml.safe_load(yaml_content)
    except Exception:
        return None


def find_contact(slug: str) -> tuple[Path, dict] | None:
    """Find a contact by slug."""
    for subdir in ["people", "companies", "events"]:
        dir_path = CONTACTS_DIR / subdir
        if not dir_path.exists():
            continue
        
        filepath = dir_path / f"{slug}.md"
        if filepath.exists():
            fm = parse_frontmatter(filepath)
            if fm:
                return filepath, fm
        
        # Partial match
        for fp in dir_path.glob("*.md"):
            if slug in fp.stem:
                fm = parse_frontmatter(fp)
                if fm:
                    return fp, fm
    return None


def parse_duration(duration: str) -> timedelta:
    """Parse duration like '3d', '1w', '2h'."""
    match = re.match(r"(\d+)([dhwm])", duration.lower())
    if not match:
        raise ValueError(f"Invalid duration: {duration}")
    
    num = int(match.group(1))
    unit = match.group(2)
    
    if unit == "h":
        return timedelta(hours=num)
    elif unit == "d":
        return timedelta(days=num)
    elif unit == "w":
        return timedelta(weeks=num)
    elif unit == "m":
        return timedelta(days=num * 30)
    else:
        raise ValueError(f"Unknown unit: {unit}")


def load_reminders() -> list[dict]:
    """Load reminders from file."""
    if not REMINDERS_FILE.exists():
        return []
    try:
        return json.loads(REMINDERS_FILE.read_text())
    except Exception:
        return []


def save_reminders(reminders: list[dict]):
    """Save reminders to file with secure permissions."""
    import os
    REMINDERS_FILE.write_text(json.dumps(reminders, indent=2))
    os.chmod(REMINDERS_FILE, 0o600)  # Owner read/write only


def add_reminder(slug: str, name: str, remind_at: datetime, message: str = None):
    """Add a reminder."""
    reminders = load_reminders()
    
    reminder = {
        "slug": slug,
        "name": name,
        "remind_at": remind_at.isoformat(),
        "message": message or f"Follow up with {name}",
        "created_at": datetime.now().isoformat()
    }
    
    reminders.append(reminder)
    save_reminders(reminders)
    return reminder


def get_due_reminders() -> list[dict]:
    """Get reminders that are due now."""
    reminders = load_reminders()
    now = datetime.now()
    
    due = []
    remaining = []
    
    for r in reminders:
        remind_at = datetime.fromisoformat(r["remind_at"])
        if remind_at <= now:
            due.append(r)
        else:
            remaining.append(r)
    
    # Save remaining
    save_reminders(remaining)
    
    return due


def main():
    parser = argparse.ArgumentParser(description="CRM reminder management")
    parser.add_argument("contact", nargs="?", help="Contact slug")
    parser.add_argument("--in", dest="in_duration", help="Remind in duration (e.g., 3d, 1w)")
    parser.add_argument("--at", dest="at_date", help="Remind at date (YYYY-MM-DD)")
    parser.add_argument("--message", "-m", help="Custom reminder message")
    parser.add_argument("--list", "-l", action="store_true", help="List pending reminders")
    parser.add_argument("--check", action="store_true", help="Check and return due reminders")
    parser.add_argument("--clear", action="store_true", help="Clear all reminders")
    
    args = parser.parse_args()
    
    if args.clear:
        save_reminders([])
        print("All reminders cleared.")
        return
    
    if args.check:
        due = get_due_reminders()
        if due:
            print(f"🔔 {len(due)} reminder(s) due:")
            for r in due:
                print(f"  • {r['name']}: {r['message']}")
        else:
            print("No reminders due.")
        return
    
    if args.list:
        reminders = load_reminders()
        if not reminders:
            print("No pending reminders.")
            return
        
        print(f"📅 {len(reminders)} pending reminder(s):\n")
        for r in sorted(reminders, key=lambda x: x["remind_at"]):
            remind_at = datetime.fromisoformat(r["remind_at"])
            delta = remind_at - datetime.now()
            if delta.days > 0:
                when = f"in {delta.days} days"
            elif delta.seconds > 3600:
                when = f"in {delta.seconds // 3600} hours"
            else:
                when = "soon"
            print(f"  • {r['name']} — {remind_at.strftime('%Y-%m-%d %H:%M')} ({when})")
            print(f"    {r['message']}")
        return
    
    if not args.contact:
        parser.print_help()
        return
    
    # Find the contact
    result = find_contact(args.contact)
    if not result:
        print(f"Contact not found: {args.contact}")
        return
    
    filepath, fm = result
    name = fm.get("name", filepath.stem)
    slug = filepath.stem
    
    # Determine remind time
    if args.in_duration:
        remind_at = datetime.now() + parse_duration(args.in_duration)
    elif args.at_date:
        remind_at = datetime.strptime(args.at_date, "%Y-%m-%d")
        # Set to 9am
        remind_at = remind_at.replace(hour=9, minute=0)
    else:
        # Use follow_up date from contact
        follow_up = fm.get("follow_up")
        if not follow_up:
            print(f"No follow_up date set for {name}. Use --in or --at to specify.")
            return
        
        if isinstance(follow_up, str):
            remind_at = datetime.strptime(follow_up, "%Y-%m-%d")
        else:
            remind_at = datetime.combine(follow_up, datetime.min.time())
        remind_at = remind_at.replace(hour=9, minute=0)
    
    # Add the reminder
    reminder = add_reminder(slug, name, remind_at, args.message)
    print(f"✓ Reminder set: {name}")
    print(f"  When: {remind_at.strftime('%Y-%m-%d %H:%M')}")
    print(f"  Message: {reminder['message']}")


if __name__ == "__main__":
    main()
