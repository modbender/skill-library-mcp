#!/usr/bin/python3
"""
CRM Query Tool - Search and filter contacts
Usage:
    python crm-query.py --tag investor
    python crm-query.py --company "Horizon Ventures"
    python crm-query.py --introduced-by bob-smith
    python crm-query.py --location singapore
    python crm-query.py --follow-up-before 2026-02-01
    python crm-query.py --status dormant
    python crm-query.py --search "supply chain"
    python crm-query.py --list all
"""

import argparse
import os
import re
import sys
from pathlib import Path
from datetime import datetime, timedelta
import yaml

CONTACTS_DIR = Path(__file__).parent.parent
PEOPLE_DIR = CONTACTS_DIR / "people"
COMPANIES_DIR = CONTACTS_DIR / "companies"
EVENTS_DIR = CONTACTS_DIR / "events"


def parse_frontmatter(filepath: Path) -> dict | None:
    """Extract YAML frontmatter from a markdown file."""
    try:
        content = filepath.read_text()
        if not content.startswith("---"):
            return None
        
        # Find the closing ---
        end = content.find("---", 3)
        if end == -1:
            return None
        
        yaml_content = content[3:end].strip()
        return yaml.safe_load(yaml_content)
    except Exception as e:
        print(f"Error parsing {filepath}: {e}", file=sys.stderr)
        return None


def get_body(filepath: Path) -> str:
    """Get markdown body after frontmatter."""
    content = filepath.read_text()
    if not content.startswith("---"):
        return content
    end = content.find("---", 3)
    if end == -1:
        return content
    return content[end + 3:].strip()


def load_all_contacts(contact_type: str = "all") -> list[tuple[Path, dict]]:
    """Load all contacts with their frontmatter."""
    contacts = []
    
    dirs = []
    if contact_type in ("all", "people"):
        dirs.append(PEOPLE_DIR)
    if contact_type in ("all", "companies"):
        dirs.append(COMPANIES_DIR)
    if contact_type in ("all", "events"):
        dirs.append(EVENTS_DIR)
    
    for dir_path in dirs:
        if not dir_path.exists():
            continue
        for filepath in dir_path.glob("*.md"):
            fm = parse_frontmatter(filepath)
            if fm:
                contacts.append((filepath, fm))
    
    return contacts


def filter_by_tag(contacts: list, tag: str) -> list:
    """Filter contacts by tag."""
    tag = tag.lower()
    return [(p, fm) for p, fm in contacts 
            if tag in [t.lower() for t in fm.get("tags", [])]]


def filter_by_company(contacts: list, company: str) -> list:
    """Filter contacts by company."""
    company = company.lower()
    return [(p, fm) for p, fm in contacts 
            if company in str(fm.get("company", "")).lower()]


def filter_by_location(contacts: list, location: str) -> list:
    """Filter contacts by location."""
    location = location.lower()
    return [(p, fm) for p, fm in contacts 
            if location in str(fm.get("location", "")).lower()]


def filter_by_introduced_by(contacts: list, introducer: str) -> list:
    """Filter contacts by who introduced them."""
    introducer = introducer.lower()
    return [(p, fm) for p, fm in contacts 
            if introducer in str(fm.get("introduced_by", "")).lower()]


def filter_by_status(contacts: list, status: str) -> list:
    """Filter contacts by status."""
    status = status.lower()
    return [(p, fm) for p, fm in contacts 
            if fm.get("status", "active").lower() == status]


def filter_by_follow_up(contacts: list, before_date: str) -> list:
    """Filter contacts with follow_up before a certain date."""
    try:
        target = datetime.strptime(before_date, "%Y-%m-%d")
    except ValueError:
        print(f"Invalid date format: {before_date}. Use YYYY-MM-DD", file=sys.stderr)
        return []
    
    result = []
    for p, fm in contacts:
        follow_up = fm.get("follow_up")
        if follow_up:
            try:
                if isinstance(follow_up, str):
                    fu_date = datetime.strptime(follow_up, "%Y-%m-%d")
                else:
                    fu_date = datetime.combine(follow_up, datetime.min.time())
                if fu_date <= target:
                    result.append((p, fm))
            except (ValueError, TypeError):
                pass
    return result


def filter_dormant(contacts: list, days: int = 90) -> list:
    """Find contacts not contacted in N days."""
    cutoff = datetime.now() - timedelta(days=days)
    result = []
    for p, fm in contacts:
        last = fm.get("last_contact")
        if last:
            try:
                if isinstance(last, str):
                    last_date = datetime.strptime(last, "%Y-%m-%d")
                else:
                    last_date = datetime.combine(last, datetime.min.time())
                if last_date < cutoff:
                    result.append((p, fm))
            except (ValueError, TypeError):
                pass
    return result


def search_content(contacts: list, query: str) -> list:
    """Search in both frontmatter and body content."""
    query = query.lower()
    result = []
    for p, fm in contacts:
        # Search in frontmatter values
        fm_text = " ".join(str(v) for v in fm.values()).lower()
        if query in fm_text:
            result.append((p, fm))
            continue
        
        # Search in body
        body = get_body(p).lower()
        if query in body:
            result.append((p, fm))
    
    return result


def format_contact(filepath: Path, fm: dict, verbose: bool = False) -> str:
    """Format a contact for display."""
    name = fm.get("name", filepath.stem)
    contact_type = fm.get("type", "unknown")
    tags = ", ".join(fm.get("tags", []))
    
    line = f"• {name}"
    
    if contact_type == "person":
        company = fm.get("company", "")
        role = fm.get("role", "")
        if role and company:
            line += f" — {role} @ {company}"
        elif role:
            line += f" — {role}"
        elif company:
            line += f" — @ {company}"
    elif contact_type == "company":
        industry = fm.get("industry", "")
        if industry:
            line += f" — {industry}"
    elif contact_type == "event":
        date = fm.get("date", "")
        if date:
            line += f" — {date}"
    
    if tags:
        line += f"  [{tags}]"
    
    if verbose:
        line += f"\n  File: {filepath.relative_to(CONTACTS_DIR)}"
        if fm.get("last_contact"):
            line += f"\n  Last contact: {fm['last_contact']}"
        if fm.get("follow_up"):
            line += f"\n  Follow-up: {fm['follow_up']}"
    
    return line


def main():
    parser = argparse.ArgumentParser(description="Query CRM contacts")
    parser.add_argument("--tag", "-t", help="Filter by tag")
    parser.add_argument("--company", "-c", help="Filter by company")
    parser.add_argument("--location", "-l", help="Filter by location")
    parser.add_argument("--introduced-by", "-i", help="Filter by introducer")
    parser.add_argument("--status", "-s", help="Filter by status (active/dormant/archived)")
    parser.add_argument("--follow-up-before", "-f", help="Show contacts with follow-up before date (YYYY-MM-DD)")
    parser.add_argument("--dormant", "-d", type=int, nargs="?", const=90, 
                        help="Show contacts not contacted in N days (default 90)")
    parser.add_argument("--search", "-q", help="Full-text search")
    parser.add_argument("--list", choices=["all", "people", "companies", "events"],
                        help="List all contacts of a type")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show more details")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    # Determine contact type to load
    contact_type = "all"
    if args.list:
        contact_type = args.list
    
    contacts = load_all_contacts(contact_type)
    
    # Apply filters
    if args.tag:
        contacts = filter_by_tag(contacts, args.tag)
    if args.company:
        contacts = filter_by_company(contacts, args.company)
    if args.location:
        contacts = filter_by_location(contacts, args.location)
    if args.introduced_by:
        contacts = filter_by_introduced_by(contacts, args.introduced_by)
    if args.status:
        contacts = filter_by_status(contacts, args.status)
    if args.follow_up_before:
        contacts = filter_by_follow_up(contacts, args.follow_up_before)
    if args.dormant:
        contacts = filter_dormant(contacts, args.dormant)
    if args.search:
        contacts = search_content(contacts, args.search)
    
    # Output
    if args.json:
        import json
        output = []
        for p, fm in contacts:
            fm["_file"] = str(p.relative_to(CONTACTS_DIR))
            output.append(fm)
        print(json.dumps(output, indent=2, default=str))
    else:
        if not contacts:
            print("No contacts found.")
        else:
            print(f"Found {len(contacts)} contact(s):\n")
            for p, fm in sorted(contacts, key=lambda x: x[1].get("name", "")):
                print(format_contact(p, fm, args.verbose))


if __name__ == "__main__":
    main()
