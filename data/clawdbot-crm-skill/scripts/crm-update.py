#!/usr/bin/python3
"""
CRM Update Tool - Update contacts and log interactions
Usage:
    python crm-update.py alice-chen --interaction "Called about pilot program"
    python crm-update.py alice-chen --set-follow-up 2026-02-15
    python crm-update.py alice-chen --add-tag vip
    python crm-update.py alice-chen --set-status dormant
"""

import argparse
import os
import re
import sys
from pathlib import Path
from datetime import datetime
import yaml

CONTACTS_DIR = Path(__file__).parent.parent


def find_contact(slug: str) -> Path | None:
    """Find a contact file by slug."""
    for subdir in ["people", "companies", "events"]:
        dir_path = CONTACTS_DIR / subdir
        if not dir_path.exists():
            continue
        
        # Try exact match
        filepath = dir_path / f"{slug}.md"
        if filepath.exists():
            return filepath
        
        # Try partial match
        for filepath in dir_path.glob("*.md"):
            if slug in filepath.stem:
                return filepath
    
    return None


def parse_file(filepath: Path) -> tuple[dict, str]:
    """Parse a markdown file into frontmatter dict and body string."""
    content = filepath.read_text()
    
    if not content.startswith("---"):
        return {}, content
    
    end = content.find("---", 3)
    if end == -1:
        return {}, content
    
    yaml_content = content[3:end].strip()
    frontmatter = yaml.safe_load(yaml_content) or {}
    body = content[end + 3:].strip()
    
    return frontmatter, body


def write_file(filepath: Path, frontmatter: dict, body: str):
    """Write frontmatter and body back to file."""
    # Build YAML frontmatter
    yaml_str = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True, sort_keys=False)
    content = f"---\n{yaml_str}---\n\n{body}\n"
    filepath.write_text(content)


def add_interaction(body: str, note: str) -> str:
    """Add an interaction to the Interactions section."""
    today = datetime.now().strftime("%Y-%m-%d")
    interaction_line = f"- **{today}**: {note}"
    
    # Find the Interactions section
    lines = body.split("\n")
    new_lines = []
    in_interactions = False
    added = False
    
    for i, line in enumerate(lines):
        new_lines.append(line)
        
        if line.strip() == "## Interactions":
            in_interactions = True
            continue
        
        if in_interactions and not added:
            # Add after the section header (skip empty lines)
            if line.strip() == "" and i + 1 < len(lines):
                # Check if next line is content or another section
                next_line = lines[i + 1].strip()
                if next_line.startswith("##") or next_line.startswith("-"):
                    new_lines.append(interaction_line)
                    added = True
                elif next_line == "":
                    new_lines.append(interaction_line)
                    added = True
            elif line.strip().startswith("-"):
                # Insert before existing interactions
                new_lines.pop()  # Remove the line we just added
                new_lines.append(interaction_line)
                new_lines.append(line)
                added = True
                in_interactions = False
        
        if in_interactions and line.strip().startswith("##") and "Interactions" not in line:
            in_interactions = False
    
    # If we didn't find a good place, append to Interactions section
    if not added:
        # Find Interactions and append
        for i, line in enumerate(new_lines):
            if line.strip() == "## Interactions":
                # Find next section or end
                j = i + 1
                while j < len(new_lines) and not new_lines[j].strip().startswith("##"):
                    j += 1
                new_lines.insert(j, interaction_line)
                new_lines.insert(j, "")
                break
    
    return "\n".join(new_lines)


def main():
    parser = argparse.ArgumentParser(description="Update a contact")
    parser.add_argument("contact", help="Contact slug or partial name")
    
    # Update actions
    parser.add_argument("--interaction", "-i", help="Log an interaction")
    parser.add_argument("--note", "-n", help="Add a note (appends to Notes section)")
    parser.add_argument("--set-follow-up", "-f", help="Set follow-up date (YYYY-MM-DD)")
    parser.add_argument("--clear-follow-up", action="store_true", help="Clear follow-up date")
    parser.add_argument("--add-tag", "-t", help="Add a tag")
    parser.add_argument("--remove-tag", help="Remove a tag")
    parser.add_argument("--set-status", "-s", choices=["active", "dormant", "archived"],
                        help="Set status")
    parser.add_argument("--touch", action="store_true", 
                        help="Update last_contact to today")
    
    # Options
    parser.add_argument("--dry-run", action="store_true", help="Show changes without saving")
    
    args = parser.parse_args()
    
    # Find the contact
    filepath = find_contact(args.contact)
    if not filepath:
        print(f"Contact not found: {args.contact}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Updating: {filepath.relative_to(CONTACTS_DIR)}")
    
    # Parse the file
    frontmatter, body = parse_file(filepath)
    today = datetime.now().strftime("%Y-%m-%d")
    changes = []
    
    # Apply updates
    if args.interaction:
        body = add_interaction(body, args.interaction)
        frontmatter["last_contact"] = today
        changes.append(f"Added interaction: {args.interaction}")
        changes.append(f"Updated last_contact: {today}")
    
    if args.note:
        # Append to Notes section
        note_line = f"- {args.note}"
        if "## Notes" in body:
            body = body.replace("## Notes\n", f"## Notes\n{note_line}\n", 1)
        else:
            body += f"\n## Notes\n{note_line}\n"
        changes.append(f"Added note: {args.note}")
    
    if args.set_follow_up:
        frontmatter["follow_up"] = args.set_follow_up
        changes.append(f"Set follow_up: {args.set_follow_up}")
    
    if args.clear_follow_up:
        if "follow_up" in frontmatter:
            del frontmatter["follow_up"]
            changes.append("Cleared follow_up")
    
    if args.add_tag:
        tags = frontmatter.get("tags", [])
        if args.add_tag not in tags:
            tags.append(args.add_tag)
            frontmatter["tags"] = tags
            changes.append(f"Added tag: {args.add_tag}")
    
    if args.remove_tag:
        tags = frontmatter.get("tags", [])
        if args.remove_tag in tags:
            tags.remove(args.remove_tag)
            frontmatter["tags"] = tags
            changes.append(f"Removed tag: {args.remove_tag}")
    
    if args.set_status:
        frontmatter["status"] = args.set_status
        changes.append(f"Set status: {args.set_status}")
    
    if args.touch:
        frontmatter["last_contact"] = today
        changes.append(f"Updated last_contact: {today}")
    
    # Show changes
    if not changes:
        print("No changes specified.")
        sys.exit(0)
    
    print("\nChanges:")
    for change in changes:
        print(f"  • {change}")
    
    # Save or show dry-run
    if args.dry_run:
        print("\n[Dry run - no changes saved]")
    else:
        write_file(filepath, frontmatter, body)
        print("\n✓ Saved")


if __name__ == "__main__":
    main()
