#!/usr/bin/env python3
"""
Garden layout planner - design gardens with companion planting, spacing, and sun requirements.
Usage: python3 garden_layout.py add-bed "<name>" --width <feet> --length <feet> --sun <exposure>
       python3 garden_layout.py add-plant "<bed>" "<plant>" --row <row> --col <col>
       python3 garden_layout.py companions "<plant>"
       python3 garden_layout.py spacing "<plant>"
       python3 garden_layout.py layout
       python3 garden_layout.py export <output_file>
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime

DB_PATH = Path.home() / ".openclaw" / "workspace" / "garden_layout_db.json"

# Companion planting database
COMPANION_PLANTS = {
    "tomato": {
        "good_with": ["basil", "carrots", "onions", "lettuce", "parsley", "marigolds", "asparagus"],
        "bad_with": ["potatoes", "cucumbers", "fennel"],
        "spacing": "24-36",
        "sun": "full",
        "family": "nightshade"
    },
    "pepper": {
        "good_with": ["basil", "onions", "carrots", "lettuce", "spinach", "chard"],
        "bad_with": ["fennel", "kohlrabi"],
        "spacing": "18-24",
        "sun": "full",
        "family": "nightshade"
    },
    "eggplant": {
        "good_with": ["beans", "peppers", "spinach", "thyme", "marigolds"],
        "bad_with": ["fennel"],
        "spacing": "18-24",
        "sun": "full",
        "family": "nightshade"
    },
    "lettuce": {
        "good_with": ["carrots", "radishes", "onions", "strawberries", "tomatoes", "cucumbers"],
        "bad_with": ["parsley"],
        "spacing": "6-8",
        "sun": "partial",
        "family": "aster"
    },
    "spinach": {
        "good_with": ["strawberries", "peas", "beans", "carrots", "cabbage"],
        "bad_with": ["potatoes"],
        "spacing": "4-6",
        "sun": "partial",
        "family": "amaranth"
    },
    "kale": {
        "good_with": ["beets", "onions", "potatoes", "herbs", "marigolds"],
        "bad_with": ["tomatoes", "strawberries"],
        "spacing": "18-24",
        "sun": "partial",
        "family": "brassica"
    },
    "carrots": {
        "good_with": ["tomatoes", "onions", "lettuce", "peas", "radishes", "rosemary", "sage"],
        "bad_with": ["dill", "parsnips"],
        "spacing": "2-3",
        "sun": "partial",
        "family": "umbellifer"
    },
    "onions": {
        "good_with": ["carrots", "tomatoes", "lettuce", "beets", "cabbage", "strawberries"],
        "bad_with": ["beans", "peas"],
        "spacing": "4-6",
        "sun": "partial",
        "family": "amaryllid"
    },
    "beans": {
        "good_with": ["corn", "potatoes", "cucumbers", "carrots", "cabbage", "strawberries", "radishes"],
        "bad_with": ["onions", "garlic"],
        "spacing": "12-18",
        "sun": "full",
        "family": "legume"
    },
    "peas": {
        "good_with": ["carrots", "radishes", "turnips", "lettuce", "corn", "cucumbers"],
        "bad_with": ["onions", "garlic"],
        "spacing": "2-4",
        "sun": "partial",
        "family": "legume"
    },
    "corn": {
        "good_with": ["beans", "squash", "cucumbers", "peas", "potatoes", "melons"],
        "bad_with": ["tomatoes"],
        "spacing": "12-18",
        "sun": "full",
        "family": "grass"
    },
    "cucumber": {
        "good_with": ["beans", "corn", "peas", "radishes", "marigolds", "sunflowers"],
        "bad_with": ["potatoes", "sage"],
        "spacing": "24-36",
        "sun": "full",
        "family": "cucurbit"
    },
    "squash": {
        "good_with": ["corn", "beans", "radishes", "marigolds", "nasturtium"],
        "bad_with": ["potatoes"],
        "spacing": "24-48",
        "sun": "full",
        "family": "cucurbit"
    },
    "potatoes": {
        "good_with": ["beans", "corn", "cabbage", "peas", "marigolds", "nasturtium"],
        "bad_with": ["tomatoes", "cucumbers", "squash", "sunflowers"],
        "spacing": "12-15",
        "sun": "full",
        "family": "nightshade"
    },
    "radishes": {
        "good_with": ["lettuce", "carrots", "onions", "spinach", "peas", "beans"],
        "bad_with": ["grapes", "hyssop"],
        "spacing": "2-3",
        "sun": "partial",
        "family": "brassica"
    },
    "beets": {
        "good_with": ["onions", "lettuce", "cabbage", "kale", "spinach", "brussels-sprouts"],
        "bad_with": ["pole beans", "mustard"],
        "spacing": "3-4",
        "sun": "partial",
        "family": "amaranth"
    },
    "cabbage": {
        "good_with": ["onions", "beets", "celery", "dill", "marigolds", "nasturtium"],
        "bad_with": ["tomatoes", "strawberries", "pole beans"],
        "spacing": "18-24",
        "sun": "partial",
        "family": "brassica"
    },
    "broccoli": {
        "good_with": ["beets", "carrots", "onions", "celery", "dill", "marigolds", "nasturtium"],
        "bad_with": ["tomatoes", "strawberries", "pole beans"],
        "spacing": "18-24",
        "sun": "partial",
        "family": "brassica"
    },
    "cauliflower": {
        "good_with": ["beets", "carrots", "onions", "celery", "sage", "thyme", "marigolds"],
        "bad_with": ["tomatoes", "strawberries", "pole beans"],
        "spacing": "18-24",
        "sun": "partial",
        "family": "brassica"
    },
    "brussels-sprouts": {
        "good_with": ["beets", "carrots", "onions", "celery", "dill", "marigolds", "nasturtium"],
        "bad_with": ["tomatoes", "strawberries", "pole beans"],
        "spacing": "18-24",
        "sun": "partial",
        "family": "brassica"
    },
    "basil": {
        "good_with": ["tomatoes", "peppers", "asparagus", "petunias"],
        "bad_with": ["rue"],
        "spacing": "12-18",
        "sun": "full",
        "family": "mint"
    },
    "rosemary": {
        "good_with": ["cabbage", "carrots", "beans", "sage", "thyme"],
        "bad_with": ["cucumbers"],
        "spacing": "24-36",
        "sun": "full",
        "family": "mint"
    },
    "thyme": {
        "good_with": ["cabbage", "tomatoes", "eggplant", "potatoes", "strawberries"],
        "bad_with": [],
        "spacing": "12-18",
        "sun": "full",
        "family": "mint"
    },
    "sage": {
        "good_with": ["cabbage", "carrots", "rosemary", "thyme", "broccoli", "cauliflower"],
        "bad_with": ["cucumbers"],
        "spacing": "18-24",
        "sun": "full",
        "family": "mint"
    },
    "marigolds": {
        "good_with": ["tomatoes", "peppers", "cabbage", "cucumbers", "squash", "potatoes"],
        "bad_with": ["beans"],
        "spacing": "6-12",
        "sun": "full",
        "family": "aster"
    },
    "nasturtium": {
        "good_with": ["cabbage", "broccoli", "cauliflower", "cucumbers", "squash", "radishes"],
        "bad_with": [],
        "spacing": "12-18",
        "sun": "full",
        "family": "tropaeolaceae"
    },
    "strawberries": {
        "good_with": ["lettuce", "spinach", "beans", "onions", "borage", "thyme", "sage"],
        "bad_with": ["cabbage", "brussels-sprouts", "broccoli", "cauliflower", "tomatoes"],
        "spacing": "12-18",
        "sun": "full",
        "family": "rose"
    },
    "asparagus": {
        "good_with": ["tomatoes", "basil", "parsley", "nasturtium", "marigolds"],
        "bad_with": ["onions", "garlic", "potatoes"],
        "spacing": "12-18",
        "sun": "full",
        "family": "asparagaceae"
    },
    "melons": {
        "good_with": ["corn", "beans", "squash", "pumpkins", "marigolds"],
        "bad_with": ["potatoes", "cucumbers"],
        "spacing": "24-48",
        "sun": "full",
        "family": "cucurbit"
    },
    "pumpkins": {
        "good_with": ["corn", "beans", "melons", "marigolds", "nasturtium"],
        "bad_with": ["potatoes"],
        "spacing": "24-48",
        "sun": "full",
        "family": "cucurbit"
    }
}

def load_db():
    """Load garden layout database."""
    if not DB_PATH.exists():
        return {"beds": {}, "season": None}
    try:
        with open(DB_PATH, 'r') as f:
            return json.load(f)
    except:
        return {"beds": {}, "season": None}

def save_db(db):
    """Save garden layout database."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(DB_PATH, 'w') as f:
        json.dump(db, f, indent=2)

def add_bed(name, width, length, sun):
    """Add a garden bed."""
    db = load_db()
    
    if name in db["beds"]:
        print(f"❌ Bed '{name}' already exists. Use 'layout' to view details.")
        return False
    
    db["beds"][name] = {
        "width": width,
        "length": length,
        "sun": sun,
        "plants": [],
        "created": datetime.now().isoformat()
    }
    
    save_db(db)
    print(f"✓ Added bed: {name}")
    print(f"  Dimensions: {width}' x {length}'")
    print(f"  Sun exposure: {sun}")
    return True

def add_plant(bed_name, plant, row, col):
    """Add a plant to a bed."""
    db = load_db()
    
    if bed_name not in db["beds"]:
        print(f"❌ Bed '{bed_name}' not found.")
        print("   Use 'add-bed' to create beds first.")
        return False
    
    bed = db["beds"][bed_name]
    
    bed["plants"].append({
        "plant": plant,
        "row": row,
        "col": col,
        "added": datetime.now().isoformat()
    })
    
    save_db(db)
    print(f"✓ Added {plant} to {bed_name}")
    print(f"  Position: Row {row}, Column {col}")
    
    # Check companion suggestions
    if plant.lower() in COMPANION_PLANTS:
        plant_data = COMPANION_PLANTS[plant.lower()]
        existing_plants = [p["plant"].lower() for p in bed["plants"]]
        
        # Check for good companions already planted
        good_companions = [g for g in plant_data["good_with"] if g in existing_plants]
        if good_companions:
            print(f"  ✨ Good companion(s) nearby: {', '.join(good_companions)}")
        
        # Check for incompatible plants
        bad_neighbors = [b for b in plant_data["bad_with"] if b in existing_plants]
        if bad_neighbors:
            print(f"  ⚠️  Warning: Nearby {', '.join(bad_neighbors)} are incompatible with {plant}")
    
    return True

def get_companions(plant):
    """Get companion planting information."""
    plant = plant.lower()
    
    if plant not in COMPANION_PLANTS:
        print(f"❌ No companion data for '{plant}'")
        print("   Available plants: " + ", ".join(sorted(COMPANION_PLANTS.keys())[:10]) + "...")
        return False
    
    data = COMPANION_PLANTS[plant]
    
    print(f"\n🌿 Companion Info: {plant.capitalize()}")
    print("=" * 70)
    print(f"Good companions: {', '.join(data['good_with'])}")
    print(f"Bad neighbors: {', '.join(data['bad_with'])}")
    print(f"Spacing: {data['spacing']} inches apart")
    print(f"Sun: {data['sun'].capitalize()}")
    print(f"Family: {data['family'].capitalize()}")
    print()
    return True

def get_spacing(plant):
    """Get spacing requirements for a plant."""
    plant = plant.lower()
    
    if plant not in COMPANION_PLANTS:
        print(f"❌ No spacing data for '{plant}'")
        return False
    
    data = COMPANION_PLANTS[plant]
    
    print(f"\n📏 Spacing: {plant.capitalize()}")
    print("=" * 70)
    print(f"Space plants {data['spacing']} inches apart")
    print(f"Sun requirements: {data['sun'].capitalize()}")
    
    # Calculate how many plants fit in a 4x8 bed
    spacing_nums = data['spacing'].split('-')
    min_spacing = int(spacing_nums[0]) / 12  # Convert to feet
    if len(spacing_nums) > 1:
        max_spacing = int(spacing_nums[1]) / 12
    else:
        max_spacing = min_spacing
    
    plants_per_row = int(8 / max_spacing)
    rows = int(4 / max_spacing)
    total_plants = plants_per_row * rows
    
    print(f"In a 4'x8' bed (32 sq ft): ~{total_plants} plants")
    print()
    return True

def show_layout():
    """Show complete garden layout."""
    db = load_db()
    beds = db["beds"]
    
    if not beds:
        print("🌱 No garden beds yet.")
        print("   Use 'add-bed' to start planning your garden.")
        return False
    
    print(f"\n📐 Garden Layout")
    print("=" * 70)
    
    if db.get("season"):
        print(f"Season: {db['season']}\n")
    
    for bed_name, bed in sorted(beds.items()):
        print(f"\n🛏️  {bed_name}")
        print("-" * 70)
        print(f"Dimensions: {bed['width']}' x {bed['length']}'")
        print(f"Sun: {bed['sun'].capitalize()}")
        
        if not bed["plants"]:
            print("  No plants added yet.")
            continue
        
        # Group plants by row
        by_row = {}
        for p in bed["plants"]:
            row = p["row"]
            if row not in by_row:
                by_row[row] = []
            by_row[row].append(p)
        
        # Display rows
        for row_num in sorted(by_row.keys()):
            row_plants = by_row[row_num]
            row_display = f"  Row {row_num}: "
            for p in sorted(row_plants, key=lambda x: x["col"]):
                row_display += f"{p['plant']} "
            print(row_display)
    
    print()
    return True

def export_layout(output_file):
    """Export layout to markdown file."""
    db = load_db()
    beds = db["beds"]
    
    if not beds:
        print("🌱 No beds to export.")
        return False
    
    # Security: Validate output path
    output_path = Path(output_file)
    if not is_safe_path(output_path):
        print(f"❌ Security error: Cannot write to '{output_path}'")
        print("   Path must be within workspace or home directory (not system paths)")
        return False
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    md = f"# Garden Layout\n\n"
    md += f"**Exported:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    
    if db.get("season"):
        md += f"**Season:** {db['season']}\n\n"
    
    md += "---\n\n"
    
    for bed_name, bed in sorted(beds.items()):
        md += f"## {bed_name}\n\n"
        md += f"- **Dimensions:** {bed['width']}' x {bed['length']}'\n"
        md += f"- **Sun:** {bed['sun'].capitalize()}\n\n"
        
        if bed["plants"]:
            md += f"### Plants ({len(bed['plants'])})\n\n"
            
            # Group by row
            by_row = {}
            for p in bed["plants"]:
                row = p["row"]
                if row not in by_row:
                    by_row[row] = []
                by_row[row].append(p)
            
            for row_num in sorted(by_row.keys()):
                row_plants = sorted(by_row[row_num], key=lambda x: x["col"])
                row_plant_names = [p["plant"] for p in row_plants]
                md += f"- **Row {row_num}:** {', '.join(row_plant_names)}\n"
            
            # Check companion compatibility
            all_plants = [p["plant"].lower() for p in bed["plants"]]
            good_pairs = []
            bad_pairs = []
            
            for p_data in bed["plants"]:
                plant = p_data["plant"]
                if plant.lower() in COMPANION_PLANTS:
                    companions = COMPANION_PLANTS[plant.lower()]["good_with"]
                    incompatible = COMPANION_PLANTS[plant.lower()]["bad_with"]
                    
                    for c in companions:
                        if c in all_plants:
                            good_pairs.append(f"{plant} + {c}")
                    
                    for i in incompatible:
                        if i in all_plants:
                            bad_pairs.append(f"{plant} + {i}")
            
            if good_pairs:
                md += f"\n✨ Good companions: {', '.join(good_pairs)}\n"
            if bad_pairs:
                md += f"\n⚠️  Incompatible: {', '.join(bad_pairs)}\n"
            
            md += "\n"
        else:
            md += "No plants added yet.\n\n"
        
        md += "---\n\n"
    
    output_path.write_text(md)
    print(f"✓ Exported garden layout to {output_path}")
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
        print("Garden Layout Planner - Usage:")
        print("  add-bed <name> --width <feet> --length <feet> --sun <exposure>")
        print("  add-plant <bed> <plant> --row <row> --col <col>")
        print("  companions <plant>                - Get companion planting info")
        print("  spacing <plant>                    - Get spacing requirements")
        print("  layout                            - Show complete garden layout")
        print("  export <output_file>               - Export to markdown")
        return

    command = sys.argv[1]
    parser = argparse.ArgumentParser()

    if command == "add-bed":
        parser.add_argument("name", help="Bed name")
        parser.add_argument("--width", required=True, type=int, help="Width in feet")
        parser.add_argument("--length", required=True, type=int, help="Length in feet")
        parser.add_argument("--sun", required=True, help="Sun exposure (full/partial/shade)")
        args = parser.parse_args(sys.argv[2:])
        add_bed(args.name, args.width, args.length, args.sun)

    elif command == "add-plant":
        parser.add_argument("bed", help="Bed name")
        parser.add_argument("plant", help="Plant name")
        parser.add_argument("--row", required=True, type=int, help="Row position")
        parser.add_argument("--col", required=True, type=int, help="Column position")
        args = parser.parse_args(sys.argv[2:])
        add_plant(args.bed, args.plant, args.row, args.col)

    elif command == "companions":
        if len(sys.argv) < 3:
            print("Usage: companions <plant>")
            return
        get_companions(sys.argv[2])

    elif command == "spacing":
        if len(sys.argv) < 3:
            print("Usage: spacing <plant>")
            return
        get_spacing(sys.argv[2])

    elif command == "layout":
        show_layout()

    elif command == "export":
        if len(sys.argv) < 3:
            print("Usage: export <output_file>")
            return
        export_layout(sys.argv[2])

    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main()
