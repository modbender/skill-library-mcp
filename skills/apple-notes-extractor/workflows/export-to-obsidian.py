#!/usr/bin/env python3
"""
Example workflow: Export Apple Notes to Obsidian vault
"""
import json
import shutil
from pathlib import Path

def export_to_obsidian(notes_file, obsidian_vault_path):
    """Export notes to Obsidian vault"""
    vault_path = Path(obsidian_vault_path)
    notes_dir = vault_path / "Apple Notes"
    notes_dir.mkdir(exist_ok=True)
    
    with open(notes_file) as f:
        notes = json.load(f)
    
    for note in notes:
        filename = f"{note['title'].replace('/', '-')}.md"
        filepath = notes_dir / filename
        
        with open(filepath, 'w') as f:
            f.write(f"# {note['title']}\n\n")
            f.write(f"Created: {note['created']}\n")
            f.write(f"Modified: {note['modified']}\n\n")
            f.write(note['body'])

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python export-to-obsidian.py <notes_json_file> <obsidian_vault_path>")
        sys.exit(1)
    
    export_to_obsidian(sys.argv[1], sys.argv[2])
