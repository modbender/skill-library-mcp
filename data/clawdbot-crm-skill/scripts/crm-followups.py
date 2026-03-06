#!/usr/bin/python3
"""
CRM Follow-ups Tool - Check due follow-ups and dormant contacts
Usage:
    python crm-followups.py                    # Show all due today
    python crm-followups.py --days 7           # Due in next 7 days
    python crm-followups.py --dormant 90       # Not contacted in 90 days
    python crm-followups.py --summary          # Quick summary for heartbeat
"""

import argparse
from datetime import datetime, timedelta
from pathlib import Path
import yaml

CONTACTS_DIR = Path(__file__).parent.parent
PEOPLE_DIR = CONTACTS_DIR / "people"


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


def parse_date(d) -> datetime | None:
    """Parse a date from various formats."""
    if d is None:
        return None
    if isinstance(d, datetime):
        return d
    if hasattr(d, 'year'):  # date object
        return datetime.combine(d, datetime.min.time())
    if isinstance(d, str):
        try:
            return datetime.strptime(d, "%Y-%m-%d")
        except ValueError:
            return None
    return None


def load_people() -> list[tuple[Path, dict]]:
    """Load all people contacts."""
    if not PEOPLE_DIR.exists():
        return []
    
    contacts = []
    for filepath in PEOPLE_DIR.glob("*.md"):
        fm = parse_frontmatter(filepath)
        if fm and fm.get("type") == "person":
            contacts.append((filepath, fm))
    return contacts


def get_due_followups(days_ahead: int = 0) -> list[tuple[str, str, datetime]]:
    """Get contacts with follow-ups due within N days."""
    people = load_people()
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    cutoff = today + timedelta(days=days_ahead)
    
    due = []
    for filepath, fm in people:
        if fm.get("status") == "archived":
            continue
        
        follow_up = parse_date(fm.get("follow_up"))
        if follow_up and follow_up <= cutoff:
            name = fm.get("name", filepath.stem)
            due.append((filepath.stem, name, follow_up))
    
    return sorted(due, key=lambda x: x[2])


def get_dormant_contacts(days: int = 90) -> list[tuple[str, str, datetime, int]]:
    """Get contacts not contacted in N days."""
    people = load_people()
    cutoff = datetime.now() - timedelta(days=days)
    
    dormant = []
    for filepath, fm in people:
        if fm.get("status") in ("archived", "dormant"):
            continue
        
        last_contact = parse_date(fm.get("last_contact"))
        if last_contact and last_contact < cutoff:
            name = fm.get("name", filepath.stem)
            days_ago = (datetime.now() - last_contact).days
            dormant.append((filepath.stem, name, last_contact, days_ago))
    
    return sorted(dormant, key=lambda x: x[3], reverse=True)


def get_upcoming_birthdays(days_ahead: int = 30) -> list[tuple[str, str, str]]:
    """Get contacts with birthdays in the next N days."""
    # Future enhancement - need birthday field
    return []


def format_summary() -> str:
    """Generate a summary for heartbeat check."""
    lines = []
    
    # Due today
    due_today = get_due_followups(0)
    if due_today:
        lines.append(f"⚠️ **{len(due_today)} follow-up(s) due today:**")
        for slug, name, date in due_today[:5]:  # Limit to 5
            lines.append(f"  • {name}")
        if len(due_today) > 5:
            lines.append(f"  ...and {len(due_today) - 5} more")
        lines.append("")
    
    # Due this week
    due_week = get_due_followups(7)
    due_week = [(s, n, d) for s, n, d in due_week if d.date() > datetime.now().date()]
    if due_week:
        lines.append(f"📅 **{len(due_week)} follow-up(s) due this week**")
        lines.append("")
    
    # Dormant (90+ days)
    dormant = get_dormant_contacts(90)
    if dormant:
        lines.append(f"😴 **{len(dormant)} contact(s) going dormant** (90+ days no contact)")
        for slug, name, last, days in dormant[:3]:
            lines.append(f"  • {name} ({days} days)")
        lines.append("")
    
    if not lines:
        return "✅ No urgent follow-ups or dormant contacts."
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Check CRM follow-ups")
    parser.add_argument("--days", "-d", type=int, default=0,
                        help="Show follow-ups due within N days (default: today)")
    parser.add_argument("--dormant", type=int, nargs="?", const=90,
                        help="Show contacts not contacted in N days (default: 90)")
    parser.add_argument("--summary", "-s", action="store_true",
                        help="Show summary for heartbeat")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    if args.summary:
        print(format_summary())
        return
    
    # Follow-ups
    due = get_due_followups(args.days)
    
    if args.json:
        import json
        output = {
            "due_followups": [
                {"slug": s, "name": n, "date": d.strftime("%Y-%m-%d")}
                for s, n, d in due
            ]
        }
        if args.dormant:
            dormant = get_dormant_contacts(args.dormant)
            output["dormant"] = [
                {"slug": s, "name": n, "last_contact": d.strftime("%Y-%m-%d"), "days_ago": days}
                for s, n, d, days in dormant
            ]
        print(json.dumps(output, indent=2))
        return
    
    # Text output
    if due:
        period = "today" if args.days == 0 else f"in the next {args.days} days"
        print(f"📅 Follow-ups due {period}:\n")
        for slug, name, date in due:
            days_until = (date.date() - datetime.now().date()).days
            if days_until < 0:
                status = f"⚠️ OVERDUE by {-days_until} days"
            elif days_until == 0:
                status = "📍 TODAY"
            else:
                status = f"in {days_until} days"
            print(f"  • {name} — {date.strftime('%Y-%m-%d')} ({status})")
    else:
        period = "today" if args.days == 0 else f"in the next {args.days} days"
        print(f"✅ No follow-ups due {period}.")
    
    # Dormant contacts
    if args.dormant:
        print()
        dormant = get_dormant_contacts(args.dormant)
        if dormant:
            print(f"😴 Contacts not reached in {args.dormant}+ days:\n")
            for slug, name, last, days in dormant:
                print(f"  • {name} — last contact {last.strftime('%Y-%m-%d')} ({days} days ago)")
        else:
            print(f"✅ No dormant contacts (all contacted within {args.dormant} days).")


if __name__ == "__main__":
    main()
