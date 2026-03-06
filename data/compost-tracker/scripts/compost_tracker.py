#!/usr/bin/env python3
"""
Compost Tracker - Track compost piles and monitor decomposition progress
Part of IOU's gardening skills suite
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

DB_FILE = os.path.join(os.path.dirname(__file__), "compost_tracker_db.json")


def is_safe_path(path: str) -> bool:
    """Validate path is safe for write operations"""
    # Convert to absolute path
    path = os.path.abspath(path)

    # Get workspace directory
    workspace = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

    # Allowed paths: workspace, home directory, /tmp
    allowed = [
        workspace,
        os.path.expanduser("~"),
        "/tmp"
    ]

    # Check if path is within allowed directories
    for allowed_dir in allowed:
        if path.startswith(allowed_dir + os.sep) or path == allowed_dir:
            # Block sensitive dotfiles
            relative = os.path.relpath(path, allowed_dir)
            if relative.startswith("."):
                return False
            # Block system directories within allowed paths
            blocked = ["bin", "sbin", "etc", "lib", "usr", "var", "sys", "proc", "dev"]
            for part in relative.split(os.sep):
                if part in blocked:
                    return False
            return True

    return False


def load_db():
    """Load compost database"""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    return {"compost_piles": [], "next_id": 1}


def save_db(data):
    """Save compost database"""
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def add_pile(name, size=None, location=None, materials=None, notes=None):
    """Add a new compost pile"""
    db = load_db()

    pile = {
        "id": db["next_id"],
        "name": name,
        "created": datetime.now().isoformat(),
        "size": size or "Medium",
        "location": location or "Backyard",
        "materials": materials or [],
        "notes": notes or "",
        "status": "Active",
        "readings": [],
        "turns": []
    }

    db["compost_piles"].append(pile)
    db["next_id"] += 1
    save_db(db)

    print(f"✓ Compost pile added: {name}")
    print(f"  Size: {pile['size']}, Location: {pile['location']}")


def list_piles():
    """List all compost piles"""
    db = load_db()

    if not db["compost_piles"]:
        print("No compost piles tracked yet.")
        return

    print(f"\n🗑️  Compost Piles ({len(db['compost_piles'])} total):\n")

    for pile in sorted(db["compost_piles"], key=lambda x: x["created"], reverse=True):
        status_icon = "✅" if pile["status"] == "Ready" else "🔄"
        print(f"{status_icon} {pile['name']} ({pile['size']})")
        print(f"   Location: {pile['location']}")
        print(f"   Status: {pile['status']}")
        print(f"   Readings: {len(pile['readings'])}, Turns: {len(pile['turns'])}")
        if pile["notes"]:
            print(f"   Notes: {pile['notes']}")
        print()


def show_pile(name):
    """Show details for a compost pile"""
    db = load_db()

    pile = None
    for p in db["compost_piles"]:
        if p["name"].lower() == name.lower():
            pile = p
            break

    if not pile:
        print(f"Compost pile '{name}' not found.")
        return

    created = datetime.fromisoformat(pile["created"]).strftime("%Y-%m-%d")

    print(f"\n{'='*60}")
    print(f"🗑️  {pile['name']}")
    print(f"{'='*60}")
    print(f"Created: {created}")
    print(f"Size: {pile['size']}")
    print(f"Location: {pile['location']}")
    print(f"Status: {pile['status']}")
    print(f"\nMaterials: {', '.join(pile['materials']) if pile['materials'] else 'None specified'}")

    if pile["notes"]:
        print(f"\nNotes: {pile['notes']}")

    if pile["readings"]:
        print(f"\n📊 Temperature Readings ({len(pile['readings'])}):\n")
        for reading in pile["readings"][-5:]:  # Show last 5
            date = datetime.fromisoformat(reading["date"]).strftime("%Y-%m-%d %H:%M")
            temp = reading["temperature"]
            notes = f" - {reading['notes']}" if reading["notes"] else ""
            print(f"  {date}: {temp}°C{notes}")

    if pile["turns"]:
        print(f"\n🔄 Turn History ({len(pile['turns'])}):\n")
        for turn in pile["turns"][-5:]:  # Show last 5
            date = datetime.fromisoformat(turn["date"]).strftime("%Y-%m-%d")
            notes = f" - {turn['notes']}" if turn["notes"] else ""
            print(f"  {date}: Turned pile{notes}")

    print(f"\n{'='*60}\n")


def add_reading(name, temperature, notes=None):
    """Add a temperature reading to a pile"""
    db = load_db()

    pile = None
    for p in db["compost_piles"]:
        if p["name"].lower() == name.lower():
            pile = p
            break

    if not pile:
        print(f"Compost pile '{name}' not found.")
        return

    reading = {
        "date": datetime.now().isoformat(),
        "temperature": temperature,
        "notes": notes or ""
    }

    pile["readings"].append(reading)
    save_db(db)

    print(f"✓ Temperature reading added to {name}: {temperature}°C")


def turn_pile(name, notes=None):
    """Record a turn event for a pile"""
    db = load_db()

    pile = None
    for p in db["compost_piles"]:
        if p["name"].lower() == name.lower():
            pile = p
            break

    if not pile:
        print(f"Compost pile '{name}' not found.")
        return

    turn = {
        "date": datetime.now().isoformat(),
        "notes": notes or "Regular turn"
    }

    pile["turns"].append(turn)
    save_db(db)

    print(f"✓ Turn recorded for {name}")


def harvest_pile(name):
    """Mark a compost pile as harvested/ready"""
    db = load_db()

    pile = None
    for p in db["compost_piles"]:
        if p["name"].lower() == name.lower():
            pile = p
            break

    if not pile:
        print(f"Compost pile '{name}' not found.")
        return

    pile["status"] = "Ready"
    pile["readings"].append({
        "date": datetime.now().isoformat(),
        "temperature": "Harvest",
        "notes": "Compost ready for use"
    })

    save_db(db)

    print(f"✓ {name} marked as ready to harvest!")


def search(query):
    """Search across compost piles"""
    db = load_db()
    query = query.lower()

    results = []
    for pile in db["compost_piles"]:
        # Search name, location, materials, notes, status
        if (query in pile["name"].lower() or
            query in pile["location"].lower() or
            query in pile["status"].lower() or
            any(query in material.lower() for material in pile["materials"]) or
            (pile["notes"] and query in pile["notes"].lower())):
            results.append(pile)

    if not results:
        print(f"No compost piles matching '{query}' found.")
        return

    print(f"\n🔍 Search results for '{query}':\n")

    for pile in results:
        print(f"• {pile['name']} ({pile['status']})")
        print(f"  Location: {pile['location']}, Size: {pile['size']}")


def export(path):
    """Export compost data to markdown"""
    if not is_safe_path(path):
        print(f"❌ Export path not allowed: {path}")
        print("Allowed paths: workspace, home directory, /tmp")
        return

    db = load_db()

    md_content = "# Compost Tracker Data\n\n"
    md_content += f"*Exported: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n"

    if not db["compost_piles"]:
        md_content += "No compost piles tracked.\n"
    else:
        for pile in sorted(db["compost_piles"], key=lambda x: x["created"]):
            created = datetime.fromisoformat(pile["created"]).strftime("%Y-%m-%d")
            md_content += f"## {pile['name']}\n\n"
            md_content += f"- **Created:** {created}\n"
            md_content += f"- **Size:** {pile['size']}\n"
            md_content += f"- **Location:** {pile['location']}\n"
            md_content += f"- **Status:** {pile['status']}\n"
            md_content += f"- **Materials:** {', '.join(pile['materials']) if pile['materials'] else 'None'}\n"
            if pile["notes"]:
                md_content += f"- **Notes:** {pile['notes']}\n"

            if pile["readings"]:
                md_content += "\n### Temperature Readings\n\n"
                for reading in pile["readings"]:
                    date = datetime.fromisoformat(reading["date"]).strftime("%Y-%m-%d %H:%M")
                    notes = f" ({reading['notes']})" if reading["notes"] else ""
                    md_content += f"- {date}: {reading['temperature']}°C{notes}\n"

            if pile["turns"]:
                md_content += "\n### Turn History\n\n"
                for turn in pile["turns"]:
                    date = datetime.fromisoformat(turn["date"]).strftime("%Y-%m-%d")
                    notes = f" - {turn['notes']}" if turn["notes"] else ""
                    md_content += f"- {date}: Turned{notes}\n"

            md_content += "\n---\n\n"

    # Ensure directory exists
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

    with open(path, 'w') as f:
        f.write(md_content)

    print(f"✓ Compost data exported to: {path}")


def main():
    if len(sys.argv) < 2:
        print("Compost Tracker - Track compost piles and decomposition")
        print("\nCommands:")
        print("  add <name> [--size <size>] [--location <location>] [--materials <m1,m2,...>] [--notes <notes>]")
        print("  list                    List all compost piles")
        print("  show <name>             Show compost pile details")
        print("  temp <name> <temp>      Add temperature reading")
        print("  turn <name> [--notes <notes>]  Record a turn")
        print("  harvest <name>          Mark pile as ready")
        print("  search <query>          Search compost piles")
        print("  export <path>           Export to markdown")
        print("\nExamples:")
        print("  compost_tracker.py add \"Kitchen Pile\" --size \"Large\" --location \"Garden Corner\" --materials \"kitchen scraps,leaves\"")
        print("  compost_tracker.py temp \"Kitchen Pile\" 55")
        print("  compost_tracker.py turn \"Kitchen Pile\" --notes \"Aerated with pitchfork\"")
        print("  compost_tracker.py export ~/compost-data.md")
        return

    command = sys.argv[1]

    if command == "add" and len(sys.argv) >= 3:
        name = sys.argv[2]
        size = None
        location = None
        materials = None
        notes = None

        # Parse arguments
        i = 3
        while i < len(sys.argv):
            if sys.argv[i] == "--size" and i + 1 < len(sys.argv):
                size = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--location" and i + 1 < len(sys.argv):
                location = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--materials" and i + 1 < len(sys.argv):
                materials = [m.strip() for m in sys.argv[i + 1].split(",")]
                i += 2
            elif sys.argv[i] == "--notes" and i + 1 < len(sys.argv):
                notes = sys.argv[i + 1]
                i += 2
            else:
                i += 1

        add_pile(name, size, location, materials, notes)

    elif command == "list":
        list_piles()

    elif command == "show" and len(sys.argv) >= 3:
        show_pile(sys.argv[2])

    elif command == "temp" and len(sys.argv) >= 4:
        try:
            temp = float(sys.argv[3])
            notes = None
            if len(sys.argv) > 4:
                notes = " ".join(sys.argv[4:])
            add_reading(sys.argv[2], temp, notes)
        except ValueError:
            print("Error: Temperature must be a number")

    elif command == "turn" and len(sys.argv) >= 3:
        notes = None
        if "--notes" in sys.argv:
            idx = sys.argv.index("--notes")
            notes = " ".join(sys.argv[idx + 1:]) if idx + 1 < len(sys.argv) else None
        turn_pile(sys.argv[2], notes)

    elif command == "harvest" and len(sys.argv) >= 3:
        harvest_pile(sys.argv[2])

    elif command == "search" and len(sys.argv) >= 3:
        search(sys.argv[2])

    elif command == "export" and len(sys.argv) >= 3:
        export(sys.argv[2])

    else:
        print("Unknown command. Run without arguments for help.")


if __name__ == "__main__":
    main()
