#!/usr/bin/env python3
"""
Research organizer - stores and retrieves research notes in a structured format.
Usage: python3 research_organizer.py add "topic" "note"
       python3 research_organizer.py list
       python3 research_organizer.py search "query"
       python3 research_organizer.py export <topic> <output_file>
"""

import json
import sys
from pathlib import Path
from datetime import datetime

DB_PATH = Path.home() / ".openclaw" / "workspace" / "research_db.json"

def load_db():
    """Load research database from JSON file."""
    if not DB_PATH.exists():
        return {}
    try:
        with open(DB_PATH, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_db(db):
    """Save research database to JSON file."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(DB_PATH, 'w') as f:
        json.dump(db, f, indent=2)

def add(topic, note, tags=None):
    """Add a research note."""
    db = load_db()
    if topic not in db:
        db[topic] = {"notes": [], "created": datetime.now().isoformat()}
    
    db[topic]["notes"].append({
        "content": note,
        "timestamp": datetime.now().isoformat(),
        "tags": tags or []
    })
    db[topic]["last_updated"] = datetime.now().isoformat()
    
    save_db(db)
    print(f"✓ Added note to topic '{topic}'")
    return True

def list_topics():
    """List all research topics."""
    db = load_db()
    if not db:
        print("No research topics yet.")
        return
    
    print("\n📚 Research Topics:")
    for topic, data in sorted(db.items(), key=lambda x: x[1]["last_updated"], reverse=True):
        note_count = len(data["notes"])
        last_update = data["last_updated"][:10]
        print(f"  • {topic} ({note_count} notes, updated {last_update})")
    print()

def show_topic(topic):
    """Show all notes for a topic."""
    db = load_db()
    if topic not in db:
        print(f"Topic '{topic}' not found.")
        return False
    
    data = db[topic]
    print(f"\n📖 {topic}")
    print(f"Created: {data['created'][:10]} | Notes: {len(data['notes'])}")
    print("-" * 60)
    
    for i, note in enumerate(data["notes"], 1):
        ts = note["timestamp"][:19].replace("T", " ")
        tags = f" [{', '.join(note['tags'])}]" if note['tags'] else ""
        print(f"\n{i}. [{ts}]{tags}")
        print(f"   {note['content']}")
    print()
    return True

def search(query):
    """Search all notes across topics."""
    db = load_db()
    if not db:
        print("No research notes to search.")
        return
    
    query_lower = query.lower()
    results = []
    
    for topic, data in db.items():
        for i, note in enumerate(data["notes"]):
            if query_lower in note["content"].lower() or query_lower in topic.lower():
                results.append({
                    "topic": topic,
                    "note": note,
                    "index": i + 1
                })
    
    if not results:
        print(f"No results for '{query}'")
        return
    
    print(f"\n🔍 Search results for '{query}':")
    for r in results:
        ts = r["note"]["timestamp"][:19].replace("T", " ")
        preview = r["note"]["content"][:100] + "..." if len(r["note"]["content"]) > 100 else r["note"]["content"]
        print(f"\n  • {r['topic']} (note {r['index']}, {ts})")
        print(f"    {preview}")
    print()

def export_topic(topic, output_file):
    """Export a topic to a markdown file."""
    db = load_db()
    if topic not in db:
        print(f"Topic '{topic}' not found.")
        return False
    
    # Security: Validate output path
    output_path = Path(output_file)
    if not is_safe_path(output_path):
        print(f"❌ Security error: Cannot write to '{output_path}'")
        print("   Path must be within workspace or home directory (not system paths)")
        return False
    
    # Ensure parent directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    data = db[topic]
    
    md = f"# Research: {topic}\n\n"
    md += f"**Created:** {data['created'][:10]}\n"
    md += f"**Last Updated:** {data['last_updated'][:10]}\n"
    md += f"**Total Notes:** {len(data['notes'])}\n\n"
    md += "---\n\n"
    
    for i, note in enumerate(data["notes"], 1):
        ts = note["timestamp"][:19].replace("T", " ")
        tags_str = " ".join(f"#{t}" for t in note["tags"]) if note["tags"] else ""
        md += f"## Note {i} - {ts} {tags_str}\n\n"
        md += f"{note['content']}\n\n"
    
    output_path.write_text(md)
    print(f"✓ Exported '{topic}' to {output_path}")
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
        print("Research Organizer - Usage:")
        print("  add <topic> <note> [tags...]  - Add a research note")
        print("  list                           - List all topics")
        print("  show <topic>                   - Show notes for a topic")
        print("  search <query>                - Search all notes")
        print("  export <topic> <output_file>   - Export topic to markdown")
        return
    
    command = sys.argv[1]
    
    if command == "add":
        if len(sys.argv) < 4:
            print("Usage: add <topic> <note> [tags...]")
            return
        topic = sys.argv[2]
        note = sys.argv[3]
        tags = sys.argv[4:] if len(sys.argv) > 4 else None
        add(topic, note, tags)
    
    elif command == "list":
        list_topics()
    
    elif command == "show":
        if len(sys.argv) < 3:
            print("Usage: show <topic>")
            return
        show_topic(sys.argv[2])
    
    elif command == "search":
        if len(sys.argv) < 3:
            print("Usage: search <query>")
            return
        search(sys.argv[2])
    
    elif command == "export":
        if len(sys.argv) < 4:
            print("Usage: export <topic> <output_file>")
            return
        export_topic(sys.argv[2], sys.argv[3])
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
