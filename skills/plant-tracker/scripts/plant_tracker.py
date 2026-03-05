#!/usr/bin/env python3
"""
Plant tracker - stores and manages plant information and care schedules.
Usage: python3 plant_tracker.py add "<name>" --species "<species>" --location "<location>"
       python3 plant_tracker.py list
       python3 plant_tracker.py show "<name>"
       python3 plant_tracker.py care "<name>" --action "<action>" [notes]
       python3 plant_tracker.py search "<query>"
       python3 plant_tracker.py export <output_file>
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime

DB_PATH = Path.home() / ".openclaw" / "workspace" / "plants_db.json"

VALID_ACTIONS = [
    "water", "fertilize", "prune", "harvest", "repot",
    "plant", "pesticide", "inspect", "note"
]

def load_db():
    """Load plant database from JSON file."""
    if not DB_PATH.exists():
        return {"plants": {}}
    try:
        with open(DB_PATH, 'r') as f:
            return json.load(f)
    except:
        return {"plants": {}}

def save_db(db):
    """Save plant database to JSON file."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(DB_PATH, 'w') as f:
        json.dump(db, f, indent=2)

def add_plant(name, species=None, location=None, planted=None, notes=None):
    """Add a plant to the database."""
    db = load_db()
    plants = db["plants"]

    if name in plants:
        print(f"❌ Plant '{name}' already exists. Use 'show' to view details.")
        return False

    plants[name] = {
        "species": species,
        "location": location,
        "planted": planted,
        "notes": notes,
        "created": datetime.now().isoformat(),
        "care_history": []
    }

    save_db(db)
    print(f"✓ Added plant: {name}")
    if species:
        print(f"  Species: {species}")
    if location:
        print(f"  Location: {location}")
    if planted:
        print(f"  Planted: {planted}")
    return True

def list_plants():
    """List all plants."""
    db = load_db()
    plants = db["plants"]

    if not plants:
        print("🌱 No plants in your collection yet.")
        print("   Use 'add' to start tracking your plants.")
        return

    print("\n🌿 Your Plants:")
    print("-" * 70)
    for name, data in sorted(plants.items()):
        species = f" ({data['species']})" if data.get('species') else ""
        location = f" | 📍 {data['location']}" if data.get('location') else ""
        care_count = len(data.get('care_history', []))
        last_care = ""
        if care_count > 0:
            last_care = f" | Last: {data['care_history'][-1]['action']}"
        print(f"  • {name}{species}{location}{last_care}")
    print()

def show_plant(name):
    """Show detailed information for a plant."""
    db = load_db()
    plants = db["plants"]

    if name not in plants:
        print(f"❌ Plant '{name}' not found.")
        print("   Use 'list' to see all plants.")
        return False

    data = plants[name]
    print(f"\n🌿 {name}")
    print("=" * 70)

    if data.get('species'):
        print(f"Species:     {data['species']}")
    if data.get('location'):
        print(f"Location:    {data['location']}")
    if data.get('planted'):
        print(f"Planted:     {data['planted']}")
    print(f"Added:       {data['created'][:10]}")

    if data.get('notes'):
        print(f"\nNotes: {data['notes']}")

    care_history = data.get('care_history', [])
    if care_history:
        print(f"\n📝 Care History ({len(care_history)} entries):")
        print("-" * 70)
        # Show last 10 entries in reverse order
        recent = list(reversed(care_history))[-10:]
        for entry in recent:
            ts = entry["timestamp"][:19].replace("T", " ")
            action = entry["action"]
            notes = f" - {entry['notes']}" if entry.get('notes') else ""
            print(f"  {ts} | {action.upper()}{notes}")
        if len(care_history) > 10:
            print(f"  ... and {len(care_history) - 10} more entries")
    else:
        print(f"\n📝 No care history yet.")

    print()
    return True

def record_care(name, action, notes=None):
    """Record care action for a plant."""
    db = load_db()
    plants = db["plants"]

    if name not in plants:
        print(f"❌ Plant '{name}' not found.")
        print("   Use 'list' to see all plants.")
        return False

    if action not in VALID_ACTIONS:
        print(f"❌ Invalid action: {action}")
        print(f"   Valid actions: {', '.join(VALID_ACTIONS)}")
        return False

    entry = {
        "action": action,
        "timestamp": datetime.now().isoformat(),
        "notes": notes
    }

    plants[name]["care_history"].append(entry)
    save_db(db)
    print(f"✓ Recorded {action} for {name}")
    if notes:
        print(f"  Note: {notes}")
    return True

def search(query):
    """Search plants by name, species, location, or care notes."""
    db = load_db()
    plants = db["plants"]

    if not plants:
        print("🌱 No plants to search.")
        return

    query_lower = query.lower()
    results = []

    for name, data in plants.items():
        matches = []

        # Search plant name
        if query_lower in name.lower():
            matches.append("name")

        # Search species
        if data.get('species') and query_lower in data['species'].lower():
            matches.append("species")

        # Search location
        if data.get('location') and query_lower in data['location'].lower():
            matches.append("location")

        # Search care history
        for entry in data.get('care_history', []):
            if query_lower in entry.get('action', '').lower():
                matches.append("care")
            if entry.get('notes') and query_lower in entry['notes'].lower():
                matches.append("care")

        if matches:
            results.append({
                "name": name,
                "data": data,
                "matches": set(matches)
            })

    if not results:
        print(f"🔍 No results for '{query}'")
        return

    print(f"\n🔍 Search results for '{query}':")
    print("-" * 70)
    for r in results:
        matches_str = ", ".join(sorted(r["matches"]))
        print(f"\n  🌿 {r['name']} (matched: {matches_str})")
        if r['data'].get('species'):
            print(f"     Species: {r['data']['species']}")
        if r['data'].get('location'):
            print(f"     Location: {r['data']['location']}")
    print()

def export_plants(output_file):
    """Export all plants to a markdown file."""
    db = load_db()
    plants = db["plants"]

    if not plants:
        print("🌱 No plants to export.")
        return False

    # Security: Validate output path
    output_path = Path(output_file)
    if not is_safe_path(output_path):
        print(f"❌ Security error: Cannot write to '{output_path}'")
        print("   Path must be within workspace or home directory (not system paths)")
        return False

    # Ensure parent directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    md = f"# Plant Collection\n\n"
    md += f"**Total Plants:** {len(plants)}\n"
    md += f"**Exported:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    md += "---\n\n"

    for name, data in sorted(plants.items()):
        md += f"## {name}\n\n"
        if data.get('species'):
            md += f"**Species:** {data['species']}\n\n"
        if data.get('location'):
            md += f"**Location:** {data['location']}\n\n"
        if data.get('planted'):
            md += f"**Planted:** {data['planted']}\n\n"
        if data.get('notes'):
            md += f"**Notes:** {data['notes']}\n\n"

        care_history = data.get('care_history', [])
        if care_history:
            md += f"**Care History ({len(care_history)} entries):**\n\n"
            for entry in care_history[-20:]:  # Last 20 entries
                ts = entry["timestamp"][:19].replace("T", " ")
                action = entry["action"]
                notes = f" - {entry['notes']}" if entry.get('notes') else ""
                md += f"- {ts}: {action.upper()}{notes}\n"
            if len(care_history) > 20:
                md += f"- ... and {len(care_history) - 20} more entries\n"
            md += "\n"

        md += "---\n\n"

    output_path.write_text(md)
    print(f"✓ Exported {len(plants)} plants to {output_path}")
    return True

def is_safe_path(filepath):
    """Check if file path is within safe directories (workspace, home, or /tmp)."""
    try:
        path = Path(filepath).expanduser().resolve()
        workspace = Path.home() / ".openclaw" / "workspace"
        home = Path.home()
        tmp = Path("/tmp")

        path_str = str(path)
        workspace_str = str(workspace.resolve())
        home_str = str(home.resolve())
        tmp_str = str(tmp.resolve())

        in_workspace = path_str.startswith(workspace_str)
        in_home = path_str.startswith(home_str)
        in_tmp = path_str.startswith(tmp_str)

        # Block system paths
        system_dirs = ["/etc", "/usr", "/var", "/root", "/bin", "/sbin", "/lib", "/lib64", "/opt", "/boot", "/proc", "/sys"]
        blocked = any(path_str.startswith(d) for d in system_dirs)

        # Block sensitive dotfiles in home directory
        sensitive_patterns = [".ssh", ".bashrc", ".zshrc", ".profile", ".bash_profile", ".config/autostart"]
        for pattern in sensitive_patterns:
            if pattern in path_str:
                blocked = True
                break

        return (in_workspace or in_tmp or in_home) and not blocked
    except Exception:
        return False

def main():
    if len(sys.argv) < 2:
        print("Plant Tracker - Usage:")
        print("  add <name> [--species S] [--location L] [--planted D] [--notes N]")
        print("  list                           - List all plants")
        print("  show <name>                   - Show plant details")
        print("  care <name> --action A [notes] - Record care action")
        print("  search <query>                - Search plants")
        print("  export <output_file>           - Export plants to markdown")
        print("\nValid actions:", ", ".join(VALID_ACTIONS))
        return

    command = sys.argv[1]

    if command == "add":
        parser = argparse.ArgumentParser(description="Add a plant")
        parser.add_argument("name", help="Plant name")
        parser.add_argument("--species", help="Plant species")
        parser.add_argument("--location", help="Plant location")
        parser.add_argument("--planted", help="Date planted")
        parser.add_argument("--notes", help="Additional notes")
        args = parser.parse_args(sys.argv[2:])
        add_plant(args.name, args.species, args.location, args.planted, args.notes)

    elif command == "list":
        list_plants()

    elif command == "show":
        if len(sys.argv) < 3:
            print("Usage: show <name>")
            return
        show_plant(sys.argv[2])

    elif command == "care":
        parser = argparse.ArgumentParser(description="Record care action")
        parser.add_argument("name", help="Plant name")
        parser.add_argument("--action", required=True, help="Care action")
        parser.add_argument("notes", nargs='?', help="Care notes")
        args = parser.parse_args(sys.argv[2:])
        record_care(args.name, args.action, args.notes)

    elif command == "search":
        if len(sys.argv) < 3:
            print("Usage: search <query>")
            return
        search(sys.argv[2])

    elif command == "export":
        if len(sys.argv) < 3:
            print("Usage: export <output_file>")
            return
        export_plants(sys.argv[2])

    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main()
