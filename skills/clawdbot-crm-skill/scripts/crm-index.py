#!/usr/bin/python3
"""
CRM Index Tool - Regenerate the _index.md file
Usage:
    python crm-index.py
    python crm-index.py --output /path/to/index.md
"""

import argparse
from collections import defaultdict
from datetime import datetime
from pathlib import Path
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


def load_contacts(subdir: str) -> list[tuple[Path, dict]]:
    """Load contacts from a subdirectory."""
    dir_path = CONTACTS_DIR / subdir
    if not dir_path.exists():
        return []
    
    contacts = []
    for filepath in sorted(dir_path.glob("*.md")):
        fm = parse_frontmatter(filepath)
        if fm:
            contacts.append((filepath, fm))
    
    return contacts


def format_date(d) -> str:
    """Format a date for display."""
    if d is None:
        return ""
    if isinstance(d, str):
        return d
    return d.strftime("%Y-%m-%d")


def generate_index() -> str:
    """Generate the index markdown content."""
    lines = [
        "# Contacts Index",
        "",
        f"*Auto-generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}. Run `crm-index.py` to refresh.*",
        "",
    ]
    
    # Load all contacts
    people = load_contacts("people")
    companies = load_contacts("companies")
    events = load_contacts("events")
    
    # People table
    if people:
        lines.extend([
            "## People",
            "",
            "| Name | Company | Role | Tags | Last Contact |",
            "|------|---------|------|------|--------------|",
        ])
        
        for filepath, fm in sorted(people, key=lambda x: x[1].get("name", "")):
            name = fm.get("name", filepath.stem)
            slug = filepath.stem
            company = fm.get("company", "")
            role = fm.get("role", "")
            tags = ", ".join(fm.get("tags", []))
            last = format_date(fm.get("last_contact"))
            
            lines.append(f"| [[{slug}\\|{name}]] | {company} | {role} | {tags} | {last} |")
        
        lines.append("")
    
    # Companies table
    if companies:
        lines.extend([
            "## Companies",
            "",
            "| Name | Industry | Location | Status |",
            "|------|----------|----------|--------|",
        ])
        
        for filepath, fm in sorted(companies, key=lambda x: x[1].get("name", "")):
            name = fm.get("name", filepath.stem)
            slug = filepath.stem
            industry = fm.get("industry", "")
            location = fm.get("location", "")
            status = fm.get("status", "active")
            
            lines.append(f"| [[{slug}\\|{name}]] | {industry} | {location} | {status} |")
        
        lines.append("")
    
    # Events table
    if events:
        lines.extend([
            "## Events",
            "",
            "| Name | Date | Location |",
            "|------|------|----------|",
        ])
        
        for filepath, fm in sorted(events, key=lambda x: str(x[1].get("date", "")), reverse=True):
            name = fm.get("name", filepath.stem)
            slug = filepath.stem
            date = format_date(fm.get("date"))
            location = fm.get("location", "")
            
            lines.append(f"| [[{slug}\\|{name}]] | {date} | {location} |")
        
        lines.append("")
    
    # Tags index
    all_contacts = people + companies + events
    tags_map = defaultdict(list)
    
    for filepath, fm in all_contacts:
        for tag in fm.get("tags", []):
            tags_map[tag].append((filepath.stem, fm.get("name", filepath.stem)))
    
    if tags_map:
        lines.extend([
            "## By Tag",
            "",
        ])
        
        for tag in sorted(tags_map.keys()):
            contacts = tags_map[tag]
            contact_links = ", ".join(f"[[{slug}\\|{name}]]" for slug, name in sorted(contacts, key=lambda x: x[1]))
            lines.append(f"### #{tag}")
            lines.append(f"{contact_links}")
            lines.append("")
    
    # Follow-ups due
    today = datetime.now().date()
    due_followups = []
    
    for filepath, fm in people:
        follow_up = fm.get("follow_up")
        if follow_up:
            try:
                if isinstance(follow_up, str):
                    fu_date = datetime.strptime(follow_up, "%Y-%m-%d").date()
                else:
                    fu_date = follow_up
                if fu_date <= today:
                    due_followups.append((filepath.stem, fm.get("name", filepath.stem), follow_up))
            except (ValueError, TypeError):
                pass
    
    if due_followups:
        lines.extend([
            "## ⚠️ Due Follow-ups",
            "",
        ])
        for slug, name, date in sorted(due_followups, key=lambda x: str(x[2])):
            lines.append(f"- [[{slug}\\|{name}]] — due {date}")
        lines.append("")
    
    # Stats
    lines.extend([
        "---",
        "",
        f"**Stats:** {len(people)} people · {len(companies)} companies · {len(events)} events · {len(tags_map)} tags",
        "",
    ])
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Regenerate CRM index")
    parser.add_argument("--output", "-o", help="Output path (default: _index.md)")
    parser.add_argument("--dry-run", action="store_true", help="Print to stdout instead of saving")
    
    args = parser.parse_args()
    
    content = generate_index()
    
    if args.dry_run:
        print(content)
    else:
        output_path = Path(args.output) if args.output else (CONTACTS_DIR / "_index.md")
        output_path.write_text(content)
        print(f"Index updated: {output_path}")


if __name__ == "__main__":
    main()
