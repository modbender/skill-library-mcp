#!/usr/bin/python3
"""
CRM Add Tool - Add new contacts from command line or interactively
Usage:
    python crm-add.py person "Alice Chen" --company "Acme Corp" --tags investor,crypto
    python crm-add.py company "Acme Corp" --industry "Technology"
    python crm-add.py event "ETHDenver 2026" --date 2026-02-28
    python crm-add.py person "Bob Smith"  # Interactive mode for missing fields
"""

import argparse
import os
import sys
from pathlib import Path
from datetime import datetime
import re

CONTACTS_DIR = Path(__file__).parent.parent
TEMPLATES_DIR = CONTACTS_DIR / "_templates"


def slugify(name: str) -> str:
    """Convert a name to a filename-safe slug."""
    slug = name.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    return slug


def get_output_dir(contact_type: str) -> Path:
    """Get the output directory for a contact type."""
    type_dirs = {
        "person": "people",
        "company": "companies",
        "event": "events"
    }
    dir_name = type_dirs.get(contact_type, contact_type + "s")
    return CONTACTS_DIR / dir_name


def prompt_if_missing(value: str | None, prompt: str, required: bool = False) -> str:
    """Prompt for a value if not provided."""
    if value:
        return value
    
    while True:
        result = input(f"{prompt}: ").strip()
        if result or not required:
            return result
        print("This field is required.")


def create_contact(
    contact_type: str,
    name: str,
    **fields
) -> Path:
    """Create a new contact file."""
    
    slug = slugify(name)
    output_dir = get_output_dir(contact_type)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    filepath = output_dir / f"{slug}.md"
    
    if filepath.exists():
        print(f"Contact already exists: {filepath}", file=sys.stderr)
        overwrite = input("Overwrite? [y/N]: ").strip().lower()
        if overwrite != "y":
            sys.exit(1)
    
    # Build frontmatter
    today = datetime.now().strftime("%Y-%m-%d")
    
    fm_lines = [
        "---",
        f"name: {name}",
        f"type: {contact_type}",
    ]
    
    # Handle tags specially (convert comma-separated to list)
    tags = fields.pop("tags", None)
    if tags:
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",")]
        fm_lines.append(f"tags: [{', '.join(tags)}]")
    else:
        fm_lines.append("tags: []")
    
    # Add other fields
    field_order = [
        "company", "role", "industry", "email", "phone", "telegram", 
        "twitter", "linkedin", "website", "location", "size",
        "introduced_by", "met_at", "date", "end_date",
        "first_contact", "last_contact", "follow_up", "status"
    ]
    
    for field in field_order:
        value = fields.get(field)
        if value:
            fm_lines.append(f"{field}: {value}")
    
    # Set defaults
    if "first_contact" not in fields:
        fm_lines.append(f"first_contact: {today}")
    if "last_contact" not in fields:
        fm_lines.append(f"last_contact: {today}")
    if "status" not in fields:
        fm_lines.append("status: active")
    
    fm_lines.append("---")
    
    # Build body
    body_lines = [
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
        ""
    ]
    
    content = "\n".join(fm_lines + body_lines)
    filepath.write_text(content)
    
    return filepath


def main():
    parser = argparse.ArgumentParser(description="Add a new contact")
    parser.add_argument("type", choices=["person", "company", "event"],
                        help="Type of contact")
    parser.add_argument("name", help="Contact name")
    
    # Person fields
    parser.add_argument("--company", "-c", help="Company name")
    parser.add_argument("--role", "-r", help="Role/title")
    parser.add_argument("--email", "-e", help="Email address")
    parser.add_argument("--phone", help="Phone number")
    parser.add_argument("--telegram", help="Telegram handle")
    parser.add_argument("--twitter", help="Twitter handle")
    parser.add_argument("--linkedin", help="LinkedIn URL")
    
    # Company fields
    parser.add_argument("--industry", help="Industry (for companies)")
    parser.add_argument("--website", help="Website URL")
    parser.add_argument("--size", help="Company size")
    
    # Event fields
    parser.add_argument("--date", help="Event date (YYYY-MM-DD)")
    parser.add_argument("--end-date", help="Event end date (YYYY-MM-DD)")
    
    # Common fields
    parser.add_argument("--tags", "-t", help="Comma-separated tags")
    parser.add_argument("--location", "-l", help="Location")
    parser.add_argument("--introduced-by", help="Who introduced this contact")
    parser.add_argument("--met-at", help="Event where you met")
    parser.add_argument("--follow-up", help="Follow-up date (YYYY-MM-DD)")
    parser.add_argument("--status", choices=["active", "dormant", "archived"],
                        default="active", help="Contact status")
    
    # Options
    parser.add_argument("--interactive", "-i", action="store_true",
                        help="Prompt for missing fields")
    
    args = parser.parse_args()
    
    # Collect fields
    fields = {}
    for field in ["company", "role", "email", "phone", "telegram", "twitter",
                  "linkedin", "industry", "website", "size", "date", "end_date",
                  "tags", "location", "introduced_by", "met_at", "follow_up", "status"]:
        # Handle hyphens in arg names
        arg_name = field.replace("_", "-")
        value = getattr(args, field.replace("-", "_"), None)
        if value:
            fields[field] = value
    
    # Interactive mode
    if args.interactive:
        if args.type == "person":
            fields["company"] = prompt_if_missing(fields.get("company"), "Company")
            fields["role"] = prompt_if_missing(fields.get("role"), "Role")
            fields["email"] = prompt_if_missing(fields.get("email"), "Email")
            fields["tags"] = prompt_if_missing(fields.get("tags"), "Tags (comma-separated)")
            fields["location"] = prompt_if_missing(fields.get("location"), "Location")
        elif args.type == "company":
            fields["industry"] = prompt_if_missing(fields.get("industry"), "Industry")
            fields["website"] = prompt_if_missing(fields.get("website"), "Website")
            fields["location"] = prompt_if_missing(fields.get("location"), "Location")
        elif args.type == "event":
            fields["date"] = prompt_if_missing(fields.get("date"), "Date (YYYY-MM-DD)", required=True)
            fields["location"] = prompt_if_missing(fields.get("location"), "Location")
    
    # Remove empty fields
    fields = {k: v for k, v in fields.items() if v}
    
    # Create the contact
    filepath = create_contact(args.type, args.name, **fields)
    print(f"Created: {filepath.relative_to(CONTACTS_DIR.parent)}")


if __name__ == "__main__":
    main()
