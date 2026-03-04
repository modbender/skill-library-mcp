#!/usr/bin/python3
"""
CRM Export Tool - Export contacts to CSV or vCard
Usage:
    python crm-export.py --csv contacts.csv
    python crm-export.py --vcard contacts.vcf
    python crm-export.py --csv contacts.csv --tag investor
    python crm-export.py --vcard all.vcf --type people
"""

import argparse
import csv
import sys
from pathlib import Path
from datetime import datetime
import yaml

CONTACTS_DIR = Path(__file__).parent.parent


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


def load_contacts(contact_type: str = "all", tag: str = None) -> list[tuple[Path, dict]]:
    """Load contacts with optional filtering."""
    contacts = []
    
    dirs = []
    if contact_type in ("all", "people"):
        dirs.append(CONTACTS_DIR / "people")
    if contact_type in ("all", "companies"):
        dirs.append(CONTACTS_DIR / "companies")
    if contact_type in ("all", "events"):
        dirs.append(CONTACTS_DIR / "events")
    
    for dir_path in dirs:
        if not dir_path.exists():
            continue
        for filepath in dir_path.glob("*.md"):
            fm = parse_frontmatter(filepath)
            if fm:
                # Filter by tag if specified
                if tag:
                    tags = [t.lower() for t in fm.get("tags", [])]
                    if tag.lower() not in tags:
                        continue
                contacts.append((filepath, fm))
    
    return sorted(contacts, key=lambda x: x[1].get("name", ""))


def export_csv(contacts: list[tuple[Path, dict]], output_path: Path):
    """Export contacts to CSV."""
    if not contacts:
        print("No contacts to export.")
        return
    
    # Determine fields from all contacts
    all_fields = set()
    for _, fm in contacts:
        all_fields.update(fm.keys())
    
    # Order fields nicely
    priority_fields = ["name", "type", "company", "role", "email", "phone", 
                       "telegram", "twitter", "linkedin", "location", "tags",
                       "first_contact", "last_contact", "follow_up", "status"]
    
    fields = [f for f in priority_fields if f in all_fields]
    fields += sorted([f for f in all_fields if f not in priority_fields])
    
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        
        for filepath, fm in contacts:
            row = {}
            for field in fields:
                value = fm.get(field, "")
                if isinstance(value, list):
                    value = ", ".join(str(v) for v in value)
                elif value is None:
                    value = ""
                row[field] = value
            writer.writerow(row)
    
    print(f"Exported {len(contacts)} contacts to {output_path}")


def export_vcard(contacts: list[tuple[Path, dict]], output_path: Path):
    """Export contacts to vCard format."""
    if not contacts:
        print("No contacts to export.")
        return
    
    lines = []
    
    for filepath, fm in contacts:
        if fm.get("type") != "person":
            continue  # vCard is for people
        
        name = fm.get("name", "")
        name_parts = name.split(" ", 1)
        first_name = name_parts[0] if name_parts else ""
        last_name = name_parts[1] if len(name_parts) > 1 else ""
        
        lines.append("BEGIN:VCARD")
        lines.append("VERSION:3.0")
        lines.append(f"FN:{name}")
        lines.append(f"N:{last_name};{first_name};;;")
        
        if fm.get("email"):
            lines.append(f"EMAIL:{fm['email']}")
        
        if fm.get("phone"):
            lines.append(f"TEL:{fm['phone']}")
        
        if fm.get("company") or fm.get("role"):
            org = fm.get("company", "")
            if org:
                lines.append(f"ORG:{org}")
            if fm.get("role"):
                lines.append(f"TITLE:{fm['role']}")
        
        if fm.get("location"):
            lines.append(f"ADR:;;{fm['location']};;;;")
        
        if fm.get("linkedin"):
            lines.append(f"URL:{fm['linkedin']}")
        
        if fm.get("twitter"):
            twitter = fm["twitter"]
            if not twitter.startswith("http"):
                twitter = f"https://twitter.com/{twitter.lstrip('@')}"
            lines.append(f"URL:{twitter}")
        
        if fm.get("telegram"):
            tg = fm["telegram"]
            if not tg.startswith("http"):
                tg = f"https://t.me/{tg.lstrip('@')}"
            lines.append(f"URL:{tg}")
        
        lines.append("END:VCARD")
        lines.append("")
    
    output_path.write_text("\n".join(lines))
    
    # Count actual vCards written
    vcard_count = sum(1 for _, fm in contacts if fm.get("type") == "person")
    print(f"Exported {vcard_count} contacts to {output_path}")


def export_markdown(contacts: list[tuple[Path, dict]], output_path: Path):
    """Export contacts to a single markdown file."""
    if not contacts:
        print("No contacts to export.")
        return
    
    lines = [
        f"# Contacts Export",
        f"",
        f"*Exported on {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
        f"",
        f"---",
        f"",
    ]
    
    for filepath, fm in contacts:
        name = fm.get("name", filepath.stem)
        contact_type = fm.get("type", "unknown")
        
        lines.append(f"## {name}")
        lines.append("")
        
        # Key fields
        if fm.get("company"):
            lines.append(f"- **Company:** {fm['company']}")
        if fm.get("role"):
            lines.append(f"- **Role:** {fm['role']}")
        if fm.get("email"):
            lines.append(f"- **Email:** {fm['email']}")
        if fm.get("phone"):
            lines.append(f"- **Phone:** {fm['phone']}")
        if fm.get("location"):
            lines.append(f"- **Location:** {fm['location']}")
        if fm.get("tags"):
            tags = ", ".join(fm["tags"])
            lines.append(f"- **Tags:** {tags}")
        
        lines.append("")
        lines.append("---")
        lines.append("")
    
    output_path.write_text("\n".join(lines))
    print(f"Exported {len(contacts)} contacts to {output_path}")


def validate_output_path(path: Path) -> Path:
    """Ensure output path is safe (not escaping workspace)."""
    resolved = path.resolve()
    # Allow writing to current directory or subdirectories
    cwd = Path.cwd().resolve()
    if not str(resolved).startswith(str(cwd)) and not str(resolved).startswith("/tmp"):
        # Also allow absolute paths within home
        home = Path.home().resolve()
        if not str(resolved).startswith(str(home)):
            raise ValueError(f"Output path must be within workspace or home: {path}")
    return resolved


def main():
    parser = argparse.ArgumentParser(description="Export CRM contacts")
    
    # Output format (mutually exclusive)
    output_group = parser.add_mutually_exclusive_group(required=True)
    output_group.add_argument("--csv", metavar="FILE", help="Export to CSV")
    output_group.add_argument("--vcard", "--vcf", metavar="FILE", help="Export to vCard")
    output_group.add_argument("--markdown", "--md", metavar="FILE", help="Export to Markdown")
    
    # Filters
    parser.add_argument("--type", "-t", choices=["all", "people", "companies", "events"],
                        default="all", help="Contact type to export")
    parser.add_argument("--tag", help="Only export contacts with this tag")
    parser.add_argument("--status", choices=["active", "dormant", "archived"],
                        help="Only export contacts with this status")
    
    args = parser.parse_args()
    
    # Load contacts
    contacts = load_contacts(args.type, args.tag)
    
    # Filter by status if specified
    if args.status:
        contacts = [(p, fm) for p, fm in contacts 
                    if fm.get("status", "active") == args.status]
    
    if not contacts:
        print("No contacts match the criteria.")
        sys.exit(1)
    
    # Export
    try:
        if args.csv:
            export_csv(contacts, validate_output_path(Path(args.csv)))
        elif args.vcard:
            export_vcard(contacts, validate_output_path(Path(args.vcard)))
        elif args.markdown:
            export_markdown(contacts, validate_output_path(Path(args.markdown)))
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
