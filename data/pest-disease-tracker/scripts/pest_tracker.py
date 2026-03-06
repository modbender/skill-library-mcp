#!/usr/bin/env python3
"""
Pest and disease tracker - track and manage garden pests and diseases with treatments.
Usage: python3 pest_tracker.py add --type <pest|disease> --name <name> --plants <plants>
       python3 pest_tracker.py treat <id> --method <method> --product <product> [options]
       python3 pest_tracker.py list
       python3 pest_tracker.py show <id>
       python3 pest_tracker.py search <query>
       python3 pest_tracker.py recommend <problem>
       python3 pest_tracker.py export <output_file>
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime

DB_PATH = Path.home() / ".openclaw" / "workspace" / "pest_tracker_db.json"

# Treatment recommendations database
TREATMENTS = {
    "aphids": {
        "type": "pest",
        "methods": ["spray", "natural", "biological"],
        "products": ["neem oil", "insecticidal soap", "ladybugs", "strong water spray"],
        "timing": "Every 2-3 days for 2 weeks",
        "notes": "Apply in evening, wash off edible parts before harvest"
    },
    "slugs": {
        "type": "pest",
        "methods": ["traps", "barriers", "natural", "biological"],
        "products": ["beer traps", "diatomaceous earth", "copper tape", "beneficial nematodes"],
        "timing": "Check daily, refresh traps weekly",
        "notes": "Set traps in evening, remove in morning"
    },
    "caterpillars": {
        "type": "pest",
        "methods": ["spray", "biological", "manual"],
        "products": ["Bacillus thuringiensis (Bt)", "neem oil", "hand-picking"],
        "timing": "Treat every 5-7 days",
        "notes": "Bt works best on young caterpillars, apply in evening"
    },
    "cucumber beetles": {
        "type": "pest",
        "methods": ["barriers", "traps", "manual"],
        "products": ["row covers", "sticky traps", "hand-picking"],
        "timing": "Daily monitoring",
        "notes": "Remove by hand in morning when they're sluggish"
    },
    "japanese beetles": {
        "type": "pest",
        "methods": ["traps", "manual", "biological"],
        "products": ["pheromone traps", "milky spore disease", "hand-picking"],
        "timing": "Traps in June-July",
        "notes": "Traps attract beetles, place upwind from garden"
    },
    "spider mites": {
        "type": "pest",
        "methods": ["spray", "natural", "manual"],
        "products": ["neem oil", "insecticidal soap", "water spray", "ladybugs"],
        "timing": "Every 2-3 days",
        "notes": "Increase humidity to discourage mites, wash plants"
    },
    "thrips": {
        "type": "pest",
        "methods": ["spray", "blue traps", "biological"],
        "products": ["neem oil", "blue sticky traps", "lacewings"],
        "timing": "Every 3-5 days",
        "notes": "Blue traps attract thrips, replace weekly"
    },
    "whiteflies": {
        "type": "pest",
        "methods": ["traps", "spray", "natural"],
        "products": ["yellow sticky traps", "neem oil", "ladybugs", "parasitic wasps"],
        "timing": "Check weekly, replace traps monthly",
        "notes": "Yellow traps attract whiteflies, hang at plant height"
    },
    "early blight": {
        "type": "disease",
        "methods": ["remove", "spray", "prevent"],
        "products": ["copper fungicide", "remove affected leaves", "improve air circulation", "avoid overhead watering"],
        "timing": "Treat immediately, prevent before wet weather",
        "notes": "Remove severely affected leaves, apply preventatively in humid conditions"
    },
    "late blight": {
        "type": "disease",
        "methods": ["remove", "spray"],
        "products": ["chlorothalonil", "copper fungicide", "mancozeb"],
        "timing": "Every 5-7 days",
        "notes": "Treat preventatively, no cure once infected"
    },
    "powdery mildew": {
        "type": "disease",
        "methods": ["spray", "prevent"],
        "products": ["sulfur fungicide", "neem oil", "milk spray", "baking soda spray"],
        "timing": "Every 3-5 days",
        "notes": "Improve airflow, remove severely affected leaves"
    },
    "downy mildew": {
        "type": "disease",
        "methods": ["spray", "prevent"],
        "products": ["copper fungicide", "mancozeb", "improve airflow", "avoid overhead watering"],
        "timing": "Every 5-7 days",
        "notes": "More common in cool, wet conditions"
    },
    "blossom end rot": {
        "type": "disease",
        "methods": ["spray", "prevent"],
        "products": ["calcium spray", "consistent watering", "avoid excess nitrogen"],
        "timing": "At flowering and fruit set",
        "notes": "Prevent with consistent moisture and calcium"
    },
    "verticillium wilt": {
        "type": "disease",
        "methods": ["remove", "prevent"],
        "products": ["soil solarization", "resistant varieties", "crop rotation", "clean tools"],
        "timing": "Prevention only, no cure",
        "notes": "Soil-borne, remove infected plants, rotate crops"
    },
    "bacterial spot": {
        "type": "disease",
        "methods": ["spray", "remove"],
        "products": ["copper fungicide", "remove affected leaves", "avoid overhead watering"],
        "timing": "Every 5-7 days",
        "notes": "Water-soaked spots, remove severely affected tissue"
    },
    "anthracnose": {
        "type": "disease",
        "methods": ["spray", "remove", "prevent"],
        "products": ["copper fungicide", "chlorothalonil", "crop rotation", "resistant varieties"],
        "timing": "Every 7-10 days",
        "notes": "Sunken lesions, worse in warm, wet weather"
    }
}

def load_db():
    """Load pest tracker database."""
    if not DB_PATH.exists():
        return {"problems": {}}
    try:
        with open(DB_PATH, 'r') as f:
            return json.load(f)
    except:
        return {"problems": {}}

def save_db(db):
    """Save pest tracker database."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(DB_PATH, 'w') as f:
        json.dump(db, f, indent=2)

def add_problem(problem_type, name, plants=None, severity=None, notes=None):
    """Add a pest or disease problem."""
    db = load_db()
    
    problem_id = f"{problem_type}_{name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    db["problems"][problem_id] = {
        "type": problem_type,
        "name": name,
        "plants": plants.split(',') if plants else [],
        "severity": severity,
        "notes": notes,
        "created": datetime.now().isoformat(),
        "status": "active",
        "treatments": []
    }
    
    save_db(db)
    print(f"✓ Added {problem_type}: {name}")
    if plants:
        print(f"  Affected plants: {', '.join([p.strip() for p in plants])}")
    if severity:
        print(f"  Severity: {severity}")
    print(f"  ID: {problem_id}")
    return problem_id

def list_problems():
    """List all problems."""
    db = load_db()
    problems = db["problems"]
    
    if not problems:
        print("🐛 No problems recorded yet.")
        print("   Use 'add' to track pests and diseases.")
        return False
    
    print(f"\n🐛 Pest & Disease Tracker ({len(problems)} problems)")
    print("=" * 70)
    
    # Group by type
    by_type = {"pest": [], "disease": []}
    for pid, data in problems.items():
        if data["status"] == "active":
            by_type[data["type"]].append((pid, data))
    
    for ptype, pproblems in by_type.items():
        if not pproblems:
            continue
        
        print(f"\n{ptype.capitalize()}s ({len(pproblems)}):")
        for pid, data in sorted(pproblems, key=lambda x: x[1]["created"], reverse=True):
            plants = ", ".join(data["plants"]) if data["plants"] else "None"
            treatments = len(data.get("treatments", []))
            print(f"  • {data['name']} (Severity: {data['severity']})")
            print(f"    Plants: {plants}")
            print(f"    Treatments: {treatments} applied")
            print(f"    Since: {data['created'][:10]}")
    
    print()
    return True

def show_problem(problem_id):
    """Show details for a problem."""
    db = load_db()
    
    if problem_id not in db["problems"]:
        print(f"❌ Problem ID '{problem_id}' not found.")
        return False
    
    data = db["problems"][problem_id]
    
    print(f"\n🐛 {data['type'].capitalize()}: {data['name']}")
    print("=" * 70)
    print(f"Plants affected: {', '.join(data['plants']) if data['plants'] else 'None'}")
    print(f"Severity: {data['severity']}")
    print(f"Status: {data['status']}")
    print(f"Created: {data['created']}")
    
    if data.get("notes"):
        print(f"\nNotes:\n{data['notes']}")
    
    treatments = data.get("treatments", [])
    if treatments:
        print(f"\n📋 Treatment History ({len(treatments)}):")
        for i, t in enumerate(treatments, 1):
            ts = t["timestamp"][:19].replace("T", " ")
            status = f" [{t['status']}]" if t.get("status") else ""
            print(f"  {i}. {ts} - {t['method']}: {t['product']}{status}")
            if t.get("notes"):
                print(f"     Notes: {t['notes']}")
    else:
        print("\nNo treatments applied yet.")
    print()
    return True

def search_problems(query):
    """Search for problems."""
    db = load_db()
    problems = db["problems"]
    
    if not problems:
        print("🐛 No problems to search.")
        return False
    
    query = query.lower()
    results = []
    
    for pid, data in problems.items():
        matches = False
        if query in data["name"].lower():
            matches = True
        if query in [p.lower() for p in data["plants"]]:
            matches = True
        if query in data["type"]:
            matches = True
        if data.get("notes") and query in data["notes"].lower():
            matches = True
        
        if matches:
            results.append((pid, data))
    
    if not results:
        print(f"🔍 No results for '{query}'")
        return False
    
    print(f"\n🔍 Search results for '{query}':")
    print("-" * 70)
    
    for pid, data in results:
        plants = ", ".join(data["plants"]) if data["plants"] else "None"
        print(f"\n  {data['type'].capitalize()}: {data['name']}")
        print(f"    Plants: {plants}")
        print(f"    Severity: {data['severity']}")
        print(f"    ID: {pid}")
    
    print()
    return True

def recommend_treatment(problem):
    """Get treatment recommendations."""
    problem = problem.lower()
    
    if problem not in TREATMENTS:
        print(f"❌ No treatment data for '{problem}'")
        print("\nAvailable problems:")
        for p in sorted(TREATMENTS.keys())[:15]:
            print(f"  - {p}")
        print("\nUse 'recommend' with one of these problems.")
        return False
    
    data = TREATMENTS[problem]
    
    print(f"\n💊 Treatment Recommendations: {problem.capitalize()}")
    print("=" * 70)
    print(f"Type: {data['type'].capitalize()}")
    print(f"Methods: {', '.join(data['methods'])}")
    print(f"Products: {', '.join(data['products'])}")
    print(f"\nTiming: {data['timing']}")
    print(f"\nNotes: {data['notes']}")
    print()
    return True

def record_treatment(problem_id, method, product=None, status=None, notes=None):
    """Record a treatment for a problem."""
    db = load_db()
    
    if problem_id not in db["problems"]:
        print(f"❌ Problem ID '{problem_id}' not found.")
        print("   Use 'show' to see problem details.")
        return False
    
    problem = db["problems"][problem_id]
    
    treatment = {
        "method": method,
        "timestamp": datetime.now().isoformat()
    }
    
    if product:
        treatment["product"] = product
    if status:
        treatment["status"] = status
    if notes:
        treatment["notes"] = notes
    
    problem["treatments"].append(treatment)
    
    save_db(db)
    print(f"✓ Recorded treatment for {problem['name']}")
    print(f"  Method: {method}")
    if product:
        print(f"  Product: {product}")
    if status:
        print(f"  Status: {status}")
    if notes:
        print(f"  Notes: {notes}")
    return True

def export_data(output_file):
    """Export pest tracker data to markdown."""
    db = load_db()
    problems = db["problems"]
    
    if not problems:
        print("🐛 No data to export.")
        return False
    
    # Security: Validate output path
    output_path = Path(output_file)
    if not is_safe_path(output_path):
        print(f"❌ Security error: Cannot write to '{output_path}'")
        print("   Path must be within workspace or home directory (not system paths)")
        return False
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    md = f"# Pest & Disease Tracker\n\n"
    md += f"**Exported:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    md += "---\n\n"
    
    # Group by type
    by_type = {"pest": [], "disease": []}
    for pid, data in problems.items():
        by_type[data["type"]].append((pid, data))
    
    for ptype, pproblems in by_type.items():
        if not pproblems:
            continue
        
        md += f"## {ptype.capitalize()}s ({len(pproblems)})\n\n"
        
        for pid, data in sorted(pproblems, key=lambda x: x[1]["created"]):
            plants = ", ".join(data["plants"]) if data["plants"] else "None"
            md += f"### {data['name']}\n\n"
            md += f"- **Severity:** {data['severity']}\n"
            md += f"- **Plants:** {plants}\n"
            md += f"- **Status:** {data['status']}\n"
            md += f"- **Created:** {data['created']}\n"
            
            if data.get("notes"):
                md += f"- **Notes:** {data['notes']}\n"
            
            treatments = data.get("treatments", [])
            if treatments:
                md += f"### Treatments ({len(treatments)})\n\n"
                for t in treatments:
                    ts = t["timestamp"][:19].replace("T", " ")
                    status_str = f" - Status: {t['status']}" if t.get("status") else ""
                    notes_str = f"\n  Notes: {t['notes']}" if t.get("notes") else ""
                    md += f"- {ts}: **{t['method']}** - {t.get('product', 'No product')}{status_str}{notes_str}\n"
            else:
                md += "No treatments applied yet.\n\n"
            
            md += "---\n\n"
    
    output_path.write_text(md)
    print(f"✓ Exported pest tracker data to {output_path}")
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
        print("Pest & Disease Tracker - Usage:")
        print("  add --type <pest|disease> --name <name> --plants <plants> [--severity <level>]")
        print("  treat <id> --method <method> [--product <product>] [--status <status>] [--notes <notes>]")
        print("  list                           - List all problems")
        print("  show <id>                     - Show problem details")
        print("  search <query>                 - Search problems")
        print("  recommend <problem>               - Get treatment recommendations")
        print("  export <output_file>            - Export to markdown")
        return

    command = sys.argv[1]
    parser = argparse.ArgumentParser()

    if command == "add":
        parser.add_argument("--type", required=True, choices=["pest", "disease"], help="Problem type")
        parser.add_argument("--name", required=True, help="Problem name")
        parser.add_argument("--plants", help="Affected plants (comma-separated)")
        parser.add_argument("--severity", default="moderate", help="Severity level (low/moderate/high/critical)")
        parser.add_argument("--notes", help="Additional notes")
        args = parser.parse_args(sys.argv[2:])
        add_problem(args.type, args.name, args.plants, args.severity, args.notes)

    elif command == "treat":
        parser.add_argument("id", help="Problem ID")
        parser.add_argument("--method", required=True, help="Treatment method")
        parser.add_argument("--product", help="Product used")
        parser.add_argument("--status", choices=["effective", "partial", "failed"], help="Treatment result")
        parser.add_argument("--notes", help="Treatment notes")
        args = parser.parse_args(sys.argv[2:])
        record_treatment(args.id, args.method, args.product, args.status, args.notes)

    elif command == "list":
        list_problems()

    elif command == "show":
        if len(sys.argv) < 3:
            print("Usage: show <problem_id>")
            return
        show_problem(sys.argv[2])

    elif command == "search":
        if len(sys.argv) < 3:
            print("Usage: search <query>")
            return
        search_problems(sys.argv[2])

    elif command == "recommend":
        if len(sys.argv) < 3:
            print("Usage: recommend <problem>")
            return
        recommend_treatment(sys.argv[2])

    elif command == "export":
        if len(sys.argv) < 3:
            print("Usage: export <output_file>")
            return
        export_data(sys.argv[2])

    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main()
