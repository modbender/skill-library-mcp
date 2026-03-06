#!/usr/bin/python3
"""
CRM Import Tool - Import contacts from CSV or vCard
Usage:
    python crm-import.py contacts.csv
    python crm-import.py contacts.vcf
    python crm-import.py linkedin-export.csv --format linkedin
    python crm-import.py contacts.csv --dry-run
"""

import argparse
import csv
import re
import sys
from pathlib import Path
from datetime import datetime

CONTACTS_DIR = Path(__file__).parent.parent
PEOPLE_DIR = CONTACTS_DIR / "people"


def slugify(name: str) -> str:
    """Convert a name to a filename-safe slug."""
    slug = name.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    return slug


def parse_vcard(content: str) -> list[dict]:
    """Parse vCard format into contact dicts."""
    contacts = []
    current = {}
    
    for line in content.split("\n"):
        line = line.strip()
        
        if line == "BEGIN:VCARD":
            current = {}
        elif line == "END:VCARD":
            if current.get("name"):
                contacts.append(current)
            current = {}
        elif ":" in line:
            # Handle property;params:value format
            prop_part, value = line.split(":", 1)
            prop = prop_part.split(";")[0].upper()
            
            if prop == "FN":
                current["name"] = value
            elif prop == "N":
                # N:Last;First;Middle;Prefix;Suffix
                parts = value.split(";")
                if len(parts) >= 2:
                    first = parts[1] if len(parts) > 1 else ""
                    last = parts[0] if parts[0] else ""
                    if not current.get("name"):
                        current["name"] = f"{first} {last}".strip()
            elif prop == "EMAIL":
                current["email"] = value
            elif prop == "TEL":
                current["phone"] = value
            elif prop == "ORG":
                current["company"] = value.replace(";", " - ")
            elif prop == "TITLE":
                current["role"] = value
            elif prop == "ADR":
                # ADR:;;Street;City;State;ZIP;Country
                parts = value.split(";")
                location_parts = [p for p in parts[3:6] if p]  # City, State, Country
                if location_parts:
                    current["location"] = ", ".join(location_parts)
            elif prop == "URL":
                if "linkedin" in value.lower():
                    current["linkedin"] = value
                elif "twitter" in value.lower() or "x.com" in value.lower():
                    current["twitter"] = value
                else:
                    current["website"] = value
            elif prop == "NOTE":
                current["notes"] = value
    
    return contacts


def parse_csv(filepath: Path, format_type: str = "auto") -> list[dict]:
    """Parse CSV into contact dicts."""
    contacts = []
    
    with open(filepath, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        headers = [h.lower().strip() for h in reader.fieldnames]
        
        # Detect format
        if format_type == "auto":
            if "first name" in headers or "first_name" in headers:
                format_type = "linkedin"
            elif "full name" in headers or "name" in headers:
                format_type = "generic"
            else:
                format_type = "generic"
        
        for row in reader:
            # Normalize keys to lowercase
            row = {k.lower().strip(): v.strip() for k, v in row.items() if v and v.strip()}
            
            contact = {}
            
            if format_type == "linkedin":
                # LinkedIn export format
                first = row.get("first name", row.get("first_name", ""))
                last = row.get("last name", row.get("last_name", ""))
                contact["name"] = f"{first} {last}".strip()
                contact["email"] = row.get("email address", row.get("email", ""))
                contact["company"] = row.get("company", "")
                contact["role"] = row.get("position", row.get("title", ""))
                contact["linkedin"] = row.get("profile url", row.get("linkedin", ""))
                contact["location"] = row.get("location", "")
            else:
                # Generic format
                contact["name"] = row.get("name", row.get("full name", row.get("full_name", "")))
                contact["email"] = row.get("email", row.get("email address", ""))
                contact["phone"] = row.get("phone", row.get("telephone", row.get("mobile", "")))
                contact["company"] = row.get("company", row.get("organization", ""))
                contact["role"] = row.get("role", row.get("title", row.get("position", "")))
                contact["location"] = row.get("location", row.get("city", ""))
                contact["linkedin"] = row.get("linkedin", "")
                contact["twitter"] = row.get("twitter", "")
                contact["telegram"] = row.get("telegram", "")
                contact["tags"] = row.get("tags", "")
                contact["notes"] = row.get("notes", row.get("note", ""))
            
            # Filter empty values
            contact = {k: v for k, v in contact.items() if v}
            
            if contact.get("name"):
                contacts.append(contact)
    
    return contacts


def create_contact_file(contact: dict, overwrite: bool = False) -> tuple[Path, bool]:
    """Create a contact markdown file. Returns (path, created)."""
    name = contact.get("name", "Unknown")
    slug = slugify(name)
    filepath = PEOPLE_DIR / f"{slug}.md"
    
    if filepath.exists() and not overwrite:
        return filepath, False
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Build frontmatter
    lines = [
        "---",
        f"name: {name}",
        "type: person",
    ]
    
    # Tags
    tags = contact.get("tags", "")
    if tags:
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]
        lines.append(f"tags: [{', '.join(tags)}]")
    else:
        lines.append("tags: [imported]")
    
    # Other fields
    field_map = {
        "company": "company",
        "role": "role",
        "email": "email",
        "phone": "phone",
        "telegram": "telegram",
        "twitter": "twitter",
        "linkedin": "linkedin",
        "website": "website",
        "location": "location",
    }
    
    for key, yaml_key in field_map.items():
        value = contact.get(key)
        if value:
            # Escape quotes in values
            if ":" in str(value) or '"' in str(value):
                value = f'"{value}"'
            lines.append(f"{yaml_key}: {value}")
    
    lines.extend([
        f"first_contact: {today}",
        f"last_contact: {today}",
        "status: active",
        "---",
        "",
        f"# {name}",
        "",
        "## Context",
        "",
        "",
        "## Interactions",
        "",
        "",
        "## Notes",
        "",
    ])
    
    # Add notes if present
    if contact.get("notes"):
        lines.append(contact["notes"])
    
    PEOPLE_DIR.mkdir(parents=True, exist_ok=True)
    filepath.write_text("\n".join(lines) + "\n")
    
    return filepath, True


def main():
    parser = argparse.ArgumentParser(description="Import contacts to CRM")
    parser.add_argument("file", help="File to import (CSV or vCard)")
    parser.add_argument("--format", "-f", choices=["auto", "csv", "vcard", "linkedin"],
                        default="auto", help="Input format (default: auto-detect)")
    parser.add_argument("--overwrite", action="store_true",
                        help="Overwrite existing contacts")
    parser.add_argument("--dry-run", "-n", action="store_true",
                        help="Show what would be imported without creating files")
    parser.add_argument("--tags", "-t", help="Add these tags to all imports (comma-separated)")
    
    args = parser.parse_args()
    
    filepath = Path(args.file)
    if not filepath.exists():
        print(f"File not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    
    # Detect and parse format
    content = filepath.read_text(encoding="utf-8-sig")
    
    if args.format == "vcard" or filepath.suffix.lower() in (".vcf", ".vcard"):
        contacts = parse_vcard(content)
        format_name = "vCard"
    else:
        format_type = "linkedin" if args.format == "linkedin" else "auto"
        contacts = parse_csv(filepath, format_type)
        format_name = "CSV"
    
    if not contacts:
        print("No contacts found in file.")
        sys.exit(1)
    
    print(f"Found {len(contacts)} contact(s) in {format_name} file.\n")
    
    # Add extra tags if specified
    if args.tags:
        extra_tags = [t.strip() for t in args.tags.split(",")]
        for contact in contacts:
            existing = contact.get("tags", "")
            if isinstance(existing, str) and existing:
                existing = [t.strip() for t in existing.split(",")]
            elif not existing:
                existing = []
            contact["tags"] = list(set(existing + extra_tags))
    
    # Import contacts
    created = 0
    skipped = 0
    
    for contact in contacts:
        name = contact.get("name", "Unknown")
        
        if args.dry_run:
            slug = slugify(name)
            exists = (PEOPLE_DIR / f"{slug}.md").exists()
            status = "EXISTS" if exists else "NEW"
            print(f"  [{status}] {name}")
            if exists:
                skipped += 1
            else:
                created += 1
        else:
            path, was_created = create_contact_file(contact, args.overwrite)
            if was_created:
                print(f"  ✓ Created: {name}")
                created += 1
            else:
                print(f"  - Skipped (exists): {name}")
                skipped += 1
    
    print(f"\nSummary: {created} created, {skipped} skipped")
    
    if not args.dry_run and created > 0:
        print("\nRun `crm-index.py` to update the index.")


if __name__ == "__main__":
    main()
