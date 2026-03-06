#!/usr/bin/env python3
"""
Seasonal planting guide - provides zone-specific planting schedules.
Usage: python3 seasonal_planting.py now --zone <zone>
       python3 seasonal_planting.py month --month <month> --zone <zone>
       python3 seasonal_planting.py year --zone <zone>
       python3 seasonal_planting.py search <query>
       python3 seasonal_planting.py show <plant>
       python3 seasonal_planting.py add <plant> --planting <months> --zone <zones>
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime
from calendar import month_name

DB_PATH = Path.home() / ".openclaw" / "workspace" / "planting_calendar.json"

# Built-in planting database
DEFAULT_PLANTS = {
    "tomato": {
        "category": "warm-season",
        "planting": ["april", "may", "june"],
        "zones": ["5a", "5b", "6a", "6b", "7a", "7b", "8a", "8b", "9a"],
        "notes": "Start indoors 6-8 weeks before last frost"
    },
    "pepper": {
        "category": "warm-season",
        "planting": ["april", "may", "june"],
        "zones": ["5a", "5b", "6a", "6b", "7a", "7b", "8a", "8b"],
        "notes": "Heat-loving, start indoors"
    },
    "lettuce": {
        "category": "cool-season",
        "planting": ["march", "april", "may", "august", "september"],
        "zones": ["3a", "3b", "4a", "4b", "5a", "5b", "6a", "6b", "7a", "7b", "8a"],
        "notes": "Succession plant every 2 weeks"
    },
    "spinach": {
        "category": "cool-season",
        "planting": ["march", "april", "september", "october"],
        "zones": ["3a", "3b", "4a", "4b", "5a", "5b", "6a", "6b", "7a", "7b"],
        "notes": "Bolts in hot weather, shade in summer"
    },
    "kale": {
        "category": "cool-season",
        "planting": ["march", "april", "may", "august", "september"],
        "zones": ["3a", "3b", "4a", "4b", "5a", "5b", "6a", "6b", "7a", "7b", "8a"],
        "notes": "Cold-hardy, sweeter after frost"
    },
    "carrots": {
        "category": "root-vegetable",
        "planting": ["april", "may", "june", "july"],
        "zones": ["3a", "3b", "4a", "4b", "5a", "5b", "6a", "6b", "7a", "7b", "8a"],
        "notes": "Direct sow, thin seedlings"
    },
    "beans": {
        "category": "warm-season",
        "planting": ["may", "june", "july"],
        "zones": ["5a", "5b", "6a", "6b", "7a", "7b", "8a", "8b", "9a"],
        "notes": "Bush beans faster, pole beans produce longer"
    },
    "corn": {
        "category": "warm-season",
        "planting": ["may", "june"],
        "zones": ["5a", "5b", "6a", "6b", "7a", "7b", "8a", "8b", "9a"],
        "notes": "Plant in blocks for pollination"
    },
    "squash": {
        "category": "warm-season",
        "planting": ["may", "june"],
        "zones": ["5a", "5b", "6a", "6b", "7a", "7b", "8a", "8b", "9a"],
        "notes": "Zucchini, summer squash, winter squash varieties"
    },
    "cucumber": {
        "category": "warm-season",
        "planting": ["may", "june", "july"],
        "zones": ["5a", "5b", "6a", "6b", "7a", "7b", "8a", "8b", "9a"],
        "notes": "Provide trellis for vining varieties"
    },
    "peas": {
        "category": "cool-season",
        "planting": ["march", "april"],
        "zones": ["3a", "3b", "4a", "4b", "5a", "5b", "6a", "6b", "7a", "7b"],
        "notes": "Cool weather crop, stop in hot weather"
    },
    "radishes": {
        "category": "root-vegetable",
        "planting": ["april", "may", "september", "october"],
        "zones": ["3a", "3b", "4a", "4b", "5a", "5b", "6a", "6b", "7a", "7b", "8a"],
        "notes": "Fast-growing, harvest in 30 days"
    },
    "broccoli": {
        "category": "cool-season",
        "planting": ["march", "april", "august"],
        "zones": ["3a", "3b", "4a", "4b", "5a", "5b", "6a", "6b", "7a", "7b", "8a"],
        "notes": "Transplant seedlings, harvest main head then side shoots"
    },
    "cauliflower": {
        "category": "cool-season",
        "planting": ["april", "may"],
        "zones": ["4a", "4b", "5a", "5b", "6a", "6b", "7a", "7b"],
        "notes": "Blanch heads by tying leaves"
    },
    "eggplant": {
        "category": "warm-season",
        "planting": ["may", "june"],
        "zones": ["5a", "5b", "6a", "6b", "7a", "7b", "8a", "8b", "9a"],
        "notes": "Start indoors, heat-loving"
    },
    "basil": {
        "category": "herb",
        "planting": ["april", "may", "june"],
        "zones": ["5a", "5b", "6a", "6b", "7a", "7b", "8a", "8b", "9a"],
        "notes": "Annual herb, pinch flowers to encourage leaves"
    },
    "rosemary": {
        "category": "herb",
        "planting": ["april", "may"],
        "zones": ["7a", "7b", "8a", "8b", "9a", "10a", "10b"],
        "notes": "Perennial, drought-tolerant"
    },
    "thyme": {
        "category": "herb",
        "planting": ["april", "may"],
        "zones": ["4a", "4b", "5a", "5b", "6a", "6b", "7a", "7b", "8a", "8b"],
        "notes": "Perennial, drought-tolerant"
    },
    "parsley": {
        "category": "herb",
        "planting": ["april", "may"],
        "zones": ["4a", "4b", "5a", "5b", "6a", "6b", "7a", "7b", "8a", "8b"],
        "notes": "Biennial, harvest year 1, seed year 2"
    },
    "cilantro": {
        "category": "herb",
        "planting": ["april", "may", "september"],
        "zones": ["4a", "4b", "5a", "5b", "6a", "6b", "7a", "7b", "8a", "8b"],
        "notes": "Annual, bolts quickly in heat"
    },
    "chives": {
        "category": "herb",
        "planting": ["april", "may"],
        "zones": ["3a", "3b", "4a", "4b", "5a", "5b", "6a", "6b", "7a", "7b", "8a", "8b"],
        "notes": "Perennial, garlic-flavored"
    },
    "oregano": {
        "category": "herb",
        "planting": ["april", "may"],
        "zones": ["5a", "5b", "6a", "6b", "7a", "7b", "8a", "8b", "9a"],
        "notes": "Perennial, drought-tolerant"
    },
    "sage": {
        "category": "herb",
        "planting": ["april", "may"],
        "zones": ["5a", "5b", "6a", "6b", "7a", "7b", "8a", "8b"],
        "notes": "Perennial, woody shrub"
    },
    "dill": {
        "category": "herb",
        "planting": ["april", "may", "june"],
        "zones": ["4a", "4b", "5a", "5b", "6a", "6b", "7a", "7b", "8a", "8b"],
        "notes": "Annual, attracts beneficial insects"
    },
    "beets": {
        "category": "root-vegetable",
        "planting": ["april", "may", "june", "july"],
        "zones": ["3a", "3b", "4a", "4b", "5a", "5b", "6a", "6b", "7a", "7b", "8a"],
        "notes": "Both roots and greens edible"
    },
    "onions": {
        "category": "root-vegetable",
        "planting": ["april", "may"],
        "zones": ["3a", "3b", "4a", "4b", "5a", "5b", "6a", "6b", "7a", "7b", "8a"],
        "notes": "Sets or seeds, long-season crop"
    },
    "garlic": {
        "category": "root-vegetable",
        "planting": ["october", "november"],
        "zones": ["3a", "3b", "4a", "4b", "5a", "5b", "6a", "6b", "7a", "7b"],
        "notes": "Plant in fall, harvest next summer"
    },
    "turnips": {
        "category": "root-vegetable",
        "planting": ["april", "may", "august", "september"],
        "zones": ["3a", "3b", "4a", "4b", "5a", "5b", "6a", "6b", "7a", "7b", "8a"],
        "notes": "Fast-growing, both roots and greens"
    },
    "potatoes": {
        "category": "root-vegetable",
        "planting": ["april", "may"],
        "zones": ["3a", "3b", "4a", "4b", "5a", "5b", "6a", "6b", "7a", "7b", "8a"],
        "notes": "Plant seed pieces, hill up soil"
    },
    "pumpkins": {
        "category": "warm-season",
        "planting": ["may", "june"],
        "zones": ["4a", "4b", "5a", "5b", "6a", "6b", "7a", "7b", "8a", "8b"],
        "notes": "Long season (100+ days), needs space"
    },
    "melons": {
        "category": "warm-season",
        "planting": ["may", "june"],
        "zones": ["5a", "5b", "6a", "6b", "7a", "7b", "8a", "8b", "9a"],
        "notes": "Watermelon, cantaloupe, honeydew"
    },
    "zucchini": {
        "category": "warm-season",
        "planting": ["may", "june", "july"],
        "zones": ["5a", "5b", "6a", "6b", "7a", "7b", "8a", "8b", "9a"],
        "notes": "Prolific, harvest when small"
    },
    "brussels-sprouts": {
        "category": "cool-season",
        "planting": ["may", "june"],
        "zones": ["4a", "4b", "5a", "5b", "6a", "6b", "7a", "7b"],
        "notes": "Long season, sweeter after frost"
    },
    "arugula": {
        "category": "cool-season",
        "planting": ["march", "april", "may", "september", "october"],
        "zones": ["3a", "3b", "4a", "4b", "5a", "5b", "6a", "6b", "7a", "7b", "8a"],
        "notes": "Spicy greens, bolts in heat"
    },
    "collards": {
        "category": "cool-season",
        "planting": ["march", "april", "may", "august"],
        "zones": ["5a", "5b", "6a", "6b", "7a", "7b", "8a", "8b"],
        "notes": "Heat-tolerant greens"
    },
    "swiss-chard": {
        "category": "cool-season",
        "planting": ["april", "may", "june", "july"],
        "zones": ["3a", "3b", "4a", "4b", "5a", "5b", "6a", "6b", "7a", "7b", "8a"],
        "notes": "Colorful stems, long harvest season"
    },
    "okra": {
        "category": "warm-season",
        "planting": ["may", "june"],
        "zones": ["6a", "6b", "7a", "7b", "8a", "8b", "9a"],
        "notes": "Heat-loving, harvest frequently"
    }
}

def load_db():
    """Load planting calendar database."""
    db = {"plants": DEFAULT_PLANTS.copy(), "custom": {}}
    if DB_PATH.exists():
        try:
            with open(DB_PATH, 'r') as f:
                custom_data = json.load(f)
                db["custom"] = custom_data.get("custom", {})
        except:
            pass
    return db

def save_db(db):
    """Save planting calendar database."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(DB_PATH, 'w') as f:
        json.dump(db, f, indent=2)

def get_current_month():
    """Get current month name."""
    return datetime.now().strftime("%B").lower()

def get_plant(zone, custom_plants=None):
    """Get plants for a specific month and zone."""
    if custom_plants is None:
        custom_plants = {}
    
    month = get_current_month()
    return get_plants_for_month(month, zone, custom_plants)

def get_plants_for_month(month, zone, custom_plants=None):
    """Get plants that can be planted in a specific month for a zone."""
    if custom_plants is None:
        custom_plants = {}
    
    month = month.lower()
    zone = zone.lower()
    results = []
    
    # Check default plants
    for name, data in DEFAULT_PLANTS.items():
        if month in data["planting"]:
            if zone in [z.lower() for z in data["zones"]]:
                results.append({
                    "name": name,
                    "category": data["category"],
                    "source": "default",
                    "notes": data.get("notes", "")
                })
    
    # Check custom plants
    for name, data in custom_plants.items():
        if month in data.get("planting", []):
            if zone in [z.lower() for z in data.get("zones", [])]:
                results.append({
                    "name": name,
                    "category": data.get("category", "custom"),
                    "source": "custom",
                    "notes": data.get("notes", "")
                })
    
    return results

def get_year_calendar(zone, custom_plants=None):
    """Get full year planting calendar for a zone."""
    if custom_plants is None:
        custom_plants = {}
    
    calendar = {}
    months = list(month_name)[1:]  # January to December
    
    for month in months:
        plants = get_plants_for_month(month.lower(), zone.lower(), custom_plants)
        calendar[month] = plants
    
    return calendar

def search_plants(query, custom_plants=None):
    """Search for plants by name."""
    if custom_plants is None:
        custom_plants = {}
    
    query = query.lower()
    results = []
    
    # Search default plants
    for name, data in DEFAULT_PLANTS.items():
        if query in name.lower():
            results.append({
                "name": name,
                "category": data["category"],
                "planting": data["planting"],
                "zones": data["zones"],
                "source": "default",
                "notes": data.get("notes", "")
            })
    
    # Search custom plants
    for name, data in custom_plants.items():
        if query in name.lower():
            results.append({
                "name": name,
                "category": data.get("category", "custom"),
                "planting": data.get("planting", []),
                "zones": data.get("zones", []),
                "source": "custom",
                "notes": data.get("notes", "")
            })
    
    return results

def show_plant(name, custom_plants=None):
    """Show details for a specific plant."""
    if custom_plants is None:
        custom_plants = {}
    
    name_lower = name.lower()
    
    # Check default plants
    if name_lower in DEFAULT_PLANTS:
        data = DEFAULT_PLANTS[name_lower]
        return {
            "name": name,
            "category": data["category"],
            "planting": data["planting"],
            "zones": data["zones"],
            "source": "default",
            "notes": data.get("notes", "")
        }
    
    # Check custom plants
    for key, data in custom_plants.items():
        if key.lower() == name_lower:
            return {
                "name": key,
                "category": data.get("category", "custom"),
                "planting": data.get("planting", []),
                "zones": data.get("zones", []),
                "source": "custom",
                "notes": data.get("notes", "")
            }
    
    return None

def add_plant(name, planting, zones, category="custom", notes=None):
    """Add a custom plant to the calendar."""
    db = load_db()
    
    # Parse planting months
    if isinstance(planting, str):
        planting = [m.strip().lower() for m in planting.split(",")]
    
    # Parse zones
    if isinstance(zones, str):
        zones = [z.strip().lower() for z in zones.split(",")]
    
    db["custom"][name] = {
        "category": category,
        "planting": planting,
        "zones": zones,
        "notes": notes or ""
    }
    
    save_db(db)
    print(f"✓ Added plant: {name}")
    print(f"  Planting months: {', '.join(planting)}")
    print(f"  Zones: {', '.join(zones)}")
    if notes:
        print(f"  Notes: {notes}")
    return True

def export_calendar(zone, output_file, custom_plants=None):
    """Export planting calendar to markdown file."""
    calendar = get_year_calendar(zone.lower(), custom_plants)
    
    # Security: Validate output path
    output_path = Path(output_file)
    if not is_safe_path(output_path):
        print(f"❌ Security error: Cannot write to '{output_path}'")
        print("   Path must be within workspace or home directory (not system paths)")
        return False
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    md = f"# Planting Calendar - Zone {zone.upper()}\n\n"
    md += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    md += "---\n\n"
    
    for month_name_lower in [m.lower() for m in list(month_name)[1:]]:
        month_name_proper = month_name_lower.capitalize()
        plants = calendar[month_name_proper]
        
        if not plants:
            continue
        
        md += f"## {month_name_proper}\n\n"
        for p in plants:
            source_tag = f" [{p['source']}]" if p['source'] != 'default' else ""
            notes = f" - {p['notes']}" if p['notes'] else ""
            md += f"- **{p['name']}** ({p['category']}){notes}{source_tag}\n"
        md += "\n"
    
    output_path.write_text(md)
    print(f"✓ Exported planting calendar for zone {zone} to {output_path}")
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
        print("Seasonal Planting Guide - Usage:")
        print("  now --zone Z                    - What to plant this month")
        print("  month --month M --zone Z         - What to plant in specific month")
        print("  year --zone Z                   - Full year calendar")
        print("  search <query>                   - Search for plants")
        print("  show <plant>                     - Show plant details")
        print("  add <plant> --planting M --zone Z - Add custom plant")
        print("  year --zone Z --export FILE       - Export calendar to markdown")
        return

    command = sys.argv[1]
    parser = argparse.ArgumentParser()

    if command == "now":
        parser.add_argument("--zone", required=True, help="USDA hardiness zone")
        args = parser.parse_args(sys.argv[2:])
        db = load_db()
        plants = get_plant(args.zone, db["custom"])
        
        month = get_current_month().capitalize()
        print(f"\n🌱 Planting in {month} for Zone {args.zone.upper()}")
        print("-" * 70)
        
        if not plants:
            print("  No plants found for this month and zone.")
            return
        
        # Group by category
        by_category = {}
        for p in plants:
            cat = p["category"]
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(p)
        
        for cat, cat_plants in sorted(by_category.items()):
            print(f"\n  {cat.capitalize()}:")
            for p in cat_plants:
                notes = f" - {p['notes']}" if p['notes'] else ""
                print(f"    • {p['name']}{notes}")
        print()

    elif command == "month":
        parser.add_argument("--month", required=True, help="Month name")
        parser.add_argument("--zone", required=True, help="USDA hardiness zone")
        args = parser.parse_args(sys.argv[2:])
        db = load_db()
        plants = get_plants_for_month(args.month, args.zone, db["custom"])
        
        print(f"\n🌱 Planting in {args.month.capitalize()} for Zone {args.zone.upper()}")
        print("-" * 70)
        
        if not plants:
            print("  No plants found for this month and zone.")
            return
        
        for p in plants:
            notes = f" - {p['notes']}" if p['notes'] else ""
            print(f"  • {p['name']} ({p['category']}){notes}")
        print()

    elif command == "year":
        parser.add_argument("--zone", required=True, help="USDA hardiness zone")
        parser.add_argument("--export", help="Export to markdown file")
        args = parser.parse_args(sys.argv[2:])
        db = load_db()
        
        if args.export:
            export_calendar(args.zone, args.export, db["custom"])
        else:
            calendar = get_year_calendar(args.zone, db["custom"])
            
            print(f"\n📅 Full Year Calendar - Zone {args.zone.upper()}")
            print("=" * 70)
            
            months = list(month_name)[1:]
            for m in months:
                plants = calendar[m]
                if not plants:
                    continue
                print(f"\n{m}:")
                for p in plants:
                    notes = f" - {p['notes']}" if p['notes'] else ""
                    print(f"  • {p['name']} ({p['category']}){notes}")
            print()

    elif command == "search":
        if len(sys.argv) < 3:
            print("Usage: search <query>")
            return
        db = load_db()
        results = search_plants(sys.argv[2], db["custom"])
        
        if not results:
            print(f"🔍 No plants found for '{sys.argv[2]}'")
            return
        
        print(f"\n🔍 Search results for '{sys.argv[2]}':")
        print("-" * 70)
        for r in results:
            zones_str = ", ".join(r["zones"])
            months_str = ", ".join(r["planting"])
            notes = f"\n  Notes: {r['notes']}" if r['notes'] else ""
            print(f"\n  🌿 {r['name']} ({r['category']})")
            print(f"     Zones: {zones_str}")
            print(f"     Planting: {months_str}{notes}")
        print()

    elif command == "show":
        if len(sys.argv) < 3:
            print("Usage: show <plant>")
            return
        db = load_db()
        plant = show_plant(sys.argv[2], db["custom"])
        
        if not plant:
            print(f"❌ Plant '{sys.argv[2]}' not found.")
            print("   Use 'search' to find plants.")
            return
        
        zones_str = ", ".join(plant["zones"])
        months_str = ", ".join(plant["planting"])
        notes = f"\n  Notes: {plant['notes']}" if plant['notes'] else ""
        
        print(f"\n🌿 {plant['name']}")
        print("=" * 70)
        print(f"Category: {plant['category']}")
        print(f"Zones: {zones_str}")
        print(f"Planting months: {months_str}{notes}")
        print()

    elif command == "add":
        parser = argparse.ArgumentParser(description="Add custom plant")
        parser.add_argument("name", help="Plant name")
        parser.add_argument("--planting", required=True, help="Comma-separated months")
        parser.add_argument("--zone", required=True, help="Comma-separated zones")
        parser.add_argument("--category", default="custom", help="Plant category")
        parser.add_argument("--notes", help="Additional notes")
        args = parser.parse_args(sys.argv[2:])
        add_plant(args.name, args.planting, args.zone, args.category, args.notes)

    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main()
