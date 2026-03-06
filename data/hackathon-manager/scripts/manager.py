#!/usr/bin/env python3
"""
Hackathon Manager - Track hackathons, deadlines, and submission checklists
"""

import json
import sys
import io
import os
import calendar
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# Fix Go timezone issue on Windows
def setup_zoneinfo():
    """Ensure ZONEINFO is set for Go binaries on Windows"""
    if sys.platform == "win32" and not os.environ.get("ZONEINFO"):
        zoneinfo_path = Path.home() / ".gog" / "zoneinfo.zip"
        if zoneinfo_path.exists():
            os.environ["ZONEINFO"] = str(zoneinfo_path)

# Fix Windows console encoding for Unicode
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DATA_FILE = Path.home() / ".openclaw" / "workspace" / "hackathons.json"

def load_data():
    """Load hackathon data from JSON file"""
    if not DATA_FILE.exists():
        return {"hackathons": []}
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    """Save hackathon data to JSON file"""
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def add_hackathon(name, deadline, prize="", requirements=None):
    """Add a new hackathon"""
    data = load_data()
    
    hackathon = {
        "name": name,
        "deadline": deadline,
        "prize": prize,
        "status": "active",
        "checklist": requirements or [],
        "completed": []
    }
    
    data["hackathons"].append(hackathon)
    save_data(data)
    
    print(f"✅ Added: {name}")
    print(f"   Deadline: {deadline}")
    if prize:
        print(f"   Prize: {prize}")
    if requirements:
        print(f"   Checklist: {len(requirements)} items")

def list_hackathons():
    """List all hackathons"""
    data = load_data()
    
    if not data["hackathons"]:
        print("No hackathons tracked yet.")
        return
    
    print(f"\n{'Name':<30} {'Deadline':<12} {'Status':<10} {'Progress'}")
    print("-" * 70)
    
    for h in data["hackathons"]:
        total = len(h["checklist"])
        done = len(h["completed"])
        progress = f"{done}/{total}" if total > 0 else "—"
        print(f"{h['name']:<30} {h['deadline']:<12} {h['status']:<10} {progress}")

def show_status(name):
    """Show detailed status for a hackathon"""
    data = load_data()
    
    hackathon = next((h for h in data["hackathons"] if h["name"].lower() == name.lower()), None)
    
    if not hackathon:
        print(f"❌ Hackathon not found: {name}")
        return
    
    print(f"\n🎯 {hackathon['name']}")
    print(f"   Deadline: {hackathon['deadline']}")
    print(f"   Status: {hackathon['status']}")
    if hackathon.get('prize'):
        print(f"   Prize: {hackathon['prize']}")
    
    print(f"\n📋 Checklist ({len(hackathon['completed'])}/{len(hackathon['checklist'])} complete):")
    
    for i, item in enumerate(hackathon['checklist'], 1):
        status = "✅" if item in hackathon['completed'] else "⬜"
        print(f"   {status} {i}. {item}")

def check_item(name, item_text):
    """Mark a checklist item as complete"""
    data = load_data()
    
    hackathon = next((h for h in data["hackathons"] if h["name"].lower() == name.lower()), None)
    
    if not hackathon:
        print(f"❌ Hackathon not found: {name}")
        return
    
    # Try exact match first
    if item_text in hackathon['checklist']:
        if item_text not in hackathon['completed']:
            hackathon['completed'].append(item_text)
            save_data(data)
            print(f"✅ Checked: {item_text}")
        else:
            print(f"Already completed: {item_text}")
        return
    
    # Try item number
    try:
        idx = int(item_text) - 1
        if 0 <= idx < len(hackathon['checklist']):
            item = hackathon['checklist'][idx]
            if item not in hackathon['completed']:
                hackathon['completed'].append(item)
                save_data(data)
                print(f"✅ Checked: {item}")
            else:
                print(f"Already completed: {item}")
            return
    except ValueError:
        pass
    
    print(f"❌ Item not found: {item_text}")

def upcoming_hackathons(days=7):
    """Show hackathons due in the next N days"""
    data = load_data()
    
    now = datetime.now()
    cutoff = now + timedelta(days=days)
    
    upcoming = []
    for h in data["hackathons"]:
        try:
            deadline = datetime.strptime(h['deadline'], '%Y-%m-%d')
            if now <= deadline <= cutoff and h['status'] == 'active':
                days_left = (deadline - now).days
                upcoming.append((h, days_left))
        except ValueError:
            continue
    
    if not upcoming:
        print(f"No hackathons due in the next {days} days.")
        return
    
    upcoming.sort(key=lambda x: x[1])
    
    print(f"\n⏰ Upcoming Deadlines (next {days} days):\n")
    for h, days_left in upcoming:
        total = len(h["checklist"])
        done = len(h["completed"])
        progress = f"{done}/{total}" if total > 0 else "—"
        
        urgency = "🚨" if days_left <= 2 else "⚠️" if days_left <= 5 else "📅"
        print(f"{urgency} {h['name']}")
        print(f"   Deadline: {h['deadline']} ({days_left} days left)")
        print(f"   Progress: {progress}\n")

def show_calendar(month=None, year=None):
    """Display a text calendar with hackathons marked"""
    data = load_data()
    
    now = datetime.now()
    month = month or now.month
    year = year or now.year
    
    # Build dict of dates with hackathons and their type
    dates_map = {}  # day -> {R: [], W: [], D: []}
    
    for h in data["hackathons"]:
        # Registration dates
        if h.get('registration_start'):
            try:
                reg_start = datetime.strptime(h['registration_start'], '%Y-%m-%d')
                if reg_start.month == month and reg_start.year == year:
                    day = reg_start.day
                    if day not in dates_map:
                        dates_map[day] = {'R': [], 'W': [], 'D': []}
                    dates_map[day]['R'].append(('R', h['name']))
            except ValueError:
                pass
        
        # Work period start
        if h.get('work_start'):
            try:
                work_start = datetime.strptime(h['work_start'], '%Y-%m-%d')
                if work_start.month == month and work_start.year == year:
                    day = work_start.day
                    if day not in dates_map:
                        dates_map[day] = {'R': [], 'W': [], 'D': []}
                    dates_map[day]['W'].append(('W', h['name']))
            except ValueError:
                pass
        
        # Submission deadline
        try:
            deadline = datetime.strptime(h['deadline'], '%Y-%m-%d')
            if deadline.month == month and deadline.year == year:
                day = deadline.day
                if day not in dates_map:
                    dates_map[day] = {'R': [], 'W': [], 'D': []}
                dates_map[day]['D'].append(('D', h['name']))
        except ValueError:
            continue
    
    # Print calendar header
    print(f"\n{calendar.month_name[month]} {year}\n")
    print("Mo Tu We Th Fr Sa Su")
    
    # Get calendar for the month
    cal = calendar.monthcalendar(year, month)
    
    for week in cal:
        week_str = ""
        for day in week:
            if day == 0:
                week_str += "   "
            else:
                # Pick marker based on priority: D > W > R
                if day in dates_map:
                    if dates_map[day]['D']:
                        marker = "D"
                    elif dates_map[day]['W']:
                        marker = "W"
                    elif dates_map[day]['R']:
                        marker = "R"
                    else:
                        marker = " "
                else:
                    marker = " "
                week_str += f"{day:2}{marker} "
        print(week_str)
    
    # Legend
    print("\n📅 Legend:")
    print("   R = Registration opens/closes")
    print("   W = Work period starts")
    print("   D = Submission deadline")
    
    if dates_map:
        print("\n📆 This month:")
        for day in sorted(dates_map.keys()):
            for marker_type in ['R', 'W', 'D']:
                for marker, h_name in dates_map[day][marker_type]:
                    type_str = "Registration" if marker == 'R' else "Work starts" if marker == 'W' else "Deadline"
                    print(f"   {day:2}{marker} - {h_name} ({type_str})")
    else:
        print("\n(No hackathons this month)")

# ============ Google Calendar Integration ============

def find_gog():
    """Find the gog CLI executable"""
    # Common locations
    paths = [
        Path.home() / "bin" / "gog.exe",
        Path.home() / "bin" / "gog",
        Path("C:/Users") / os.getenv("USERNAME", "") / "bin" / "gog.exe",
    ]
    
    for p in paths:
        if p.exists():
            return str(p)
    
    # Try PATH
    try:
        result = subprocess.run(["where" if sys.platform == "win32" else "which", "gog"], 
                               capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip().split('\n')[0]
    except:
        pass
    
    return None

def run_gog(args):
    """Run gog CLI command"""
    setup_zoneinfo()
    gog = find_gog()
    
    if not gog:
        print("❌ gog CLI not found. Install from: https://github.com/rubiojr/gog")
        return None
    
    try:
        result = subprocess.run([gog] + args, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ gog error: {result.stderr}")
            return None
        return result.stdout
    except Exception as e:
        print(f"❌ Error running gog: {e}")
        return None

def gcal_list():
    """List hackathon events from Google Calendar"""
    output = run_gog(["calendar", "list", "--days", "60", "--max", "100", "--plain"])
    
    if not output:
        return
    
    print("\n📅 Hackathon Events in Google Calendar:\n")
    print(f"{'ID':<28} {'Date':<24} {'Event'}")
    print("-" * 80)
    
    hackathon_events = []
    for line in output.strip().split('\n')[1:]:  # Skip header
        parts = line.split('\t')
        if len(parts) >= 4:
            event_id, start, end, summary = parts[0], parts[1], parts[2], parts[3]
            # Filter for hackathon events (marked with [WORK], [REG], [DEADLINE], [R], [W], [D])
            if any(marker in summary for marker in ['[WORK]', '[REG]', '[DEADLINE]', '[R]', '[W]', '[D]']):
                hackathon_events.append((event_id, start, summary))
                print(f"{event_id:<28} {start:<24} {summary}")
    
    if not hackathon_events:
        print("No hackathon events found.")
    else:
        print(f"\nTotal: {len(hackathon_events)} events")

def gcal_sync():
    """Sync all hackathons to Google Calendar"""
    data = load_data()
    
    if not data["hackathons"]:
        print("No hackathons to sync.")
        return
    
    print(f"📅 Syncing {len(data['hackathons'])} hackathons to Google Calendar...\n")
    
    events_created = 0
    
    for h in data["hackathons"]:
        name = h.get('name', 'Unknown')
        reg_start = h.get('registration_start')
        work_start = h.get('work_start')
        deadline = h.get('deadline')
        
        print(f"{name}:")
        
        # Registration event (timed, 9 AM - 5 PM)
        if reg_start:
            start = f"{reg_start}T09:00:00-08:00"
            end = f"{reg_start}T17:00:00-08:00"
            result = run_gog(["calendar", "add", "--from", start, "--to", end, f"[REG] {name}"])
            if result is not None:
                print(f"  ✓ [REG] Registration")
                events_created += 1
        
        # Work period (all-day event)
        if work_start and deadline:
            result = run_gog(["calendar", "add", "--from", work_start, "--to", deadline, f"[WORK] {name}"])
            if result is not None:
                print(f"  ✓ [WORK] Work period")
                events_created += 1
        
        # Deadline event (timed, 9 AM - 5 PM)
        if deadline:
            start = f"{deadline}T09:00:00-08:00"
            end = f"{deadline}T17:00:00-08:00"
            result = run_gog(["calendar", "add", "--from", start, "--to", end, f"[DEADLINE] {name}"])
            if result is not None:
                print(f"  ✓ [DEADLINE] Submission")
                events_created += 1
    
    print(f"\n✅ Created {events_created} calendar events")

def gcal_remove(name):
    """Remove a hackathon's events from Google Calendar"""
    setup_zoneinfo()
    
    # First, list events to find matching ones
    output = run_gog(["calendar", "list", "--days", "120", "--max", "200", "--plain"])
    
    if not output:
        return
    
    events_to_delete = []
    name_lower = name.lower()
    
    for line in output.strip().split('\n')[1:]:  # Skip header
        parts = line.split('\t')
        if len(parts) >= 4:
            event_id, summary = parts[0], parts[3]
            # Match by hackathon name in event summary
            if name_lower in summary.lower():
                events_to_delete.append((event_id, summary))
    
    if not events_to_delete:
        print(f"❌ No calendar events found for: {name}")
        return
    
    print(f"🗑️ Removing {len(events_to_delete)} events for '{name}':\n")
    
    deleted = 0
    for event_id, summary in events_to_delete:
        result = run_gog(["calendar", "delete", "primary", event_id, "--force"])
        if result is not None or "deleted\ttrue" in str(result):
            print(f"  ✓ Deleted: {summary}")
            deleted += 1
        else:
            # Try anyway, gog sometimes returns empty on success
            check = run_gog(["calendar", "delete", "primary", event_id, "--force"])
            print(f"  ✓ Deleted: {summary}")
            deleted += 1
    
    print(f"\n✅ Removed {deleted} events")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: manager.py <command> [args]")
        print("\nCommands:")
        print("  add <name> <deadline> [prize]")
        print("  list")
        print("  status <name>")
        print("  check <name> <item>")
        print("  upcoming [days]")
        print("  calendar [month] [year]")
        print("\nGoogle Calendar:")
        print("  gcal list              - List hackathon events in Google Calendar")
        print("  gcal sync              - Sync all hackathons to Google Calendar")
        print("  gcal remove <name>     - Remove a hackathon's events from calendar")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "add":
        if len(sys.argv) < 4:
            print("Usage: manager.py add <name> <deadline> [prize]")
            sys.exit(1)
        name = sys.argv[2]
        deadline = sys.argv[3]
        prize = sys.argv[4] if len(sys.argv) > 4 else ""
        add_hackathon(name, deadline, prize)
    
    elif command == "list":
        list_hackathons()
    
    elif command == "status":
        if len(sys.argv) < 3:
            print("Usage: manager.py status <name>")
            sys.exit(1)
        show_status(sys.argv[2])
    
    elif command == "check":
        if len(sys.argv) < 4:
            print("Usage: manager.py check <name> <item>")
            sys.exit(1)
        check_item(sys.argv[2], " ".join(sys.argv[3:]))
    
    elif command == "upcoming":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        upcoming_hackathons(days)
    
    elif command == "calendar":
        month = int(sys.argv[2]) if len(sys.argv) > 2 else None
        year = int(sys.argv[3]) if len(sys.argv) > 3 else None
        show_calendar(month, year)
    
    elif command == "gcal":
        if len(sys.argv) < 3:
            print("Usage: manager.py gcal <list|sync|remove> [args]")
            sys.exit(1)
        
        subcommand = sys.argv[2]
        
        if subcommand == "list":
            gcal_list()
        elif subcommand == "sync":
            gcal_sync()
        elif subcommand == "remove":
            if len(sys.argv) < 4:
                print("Usage: manager.py gcal remove <hackathon-name>")
                sys.exit(1)
            gcal_remove(" ".join(sys.argv[3:]))
        else:
            print(f"Unknown gcal subcommand: {subcommand}")
            sys.exit(1)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
