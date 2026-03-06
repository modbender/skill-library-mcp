#!/usr/bin/env python3
"""Generate activity reports from Palest Ink records."""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

PALEST_INK_HOME = Path(os.environ.get('PALEST_INK_HOME', os.path.expanduser('~/.palest-ink')))
RECORDS_FILE = PALEST_INK_HOME / 'records.json'
REPORTS_DIR = PALEST_INK_HOME / 'daily_reports'

def load_records():
    """Load all records."""
    if not RECORDS_FILE.exists():
        return []
    with open(RECORDS_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def parse_date(date_str):
    """Parse date string."""
    if date_str.lower() == 'today':
        return datetime.now()
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            print(f"Error: Invalid date format '{date_str}'. Use YYYY-MM-DD or 'today'")
            sys.exit(1)

def filter_records_by_date(records, from_date, to_date):
    """Filter records by date range."""
    filtered = []
    for record in records:
        record_time = datetime.fromisoformat(record['timestamp'])
        if from_date and record_time < from_date:
            continue
        if to_date:
            # Add one day to include end date fully
            end_date = to_date + timedelta(days=1)
            if record_time >= end_date:
                continue
        filtered.append(record)
    return filtered

def group_by_type(records):
    """Group records by type."""
    grouped = {
        'git': [],
        'web': [],
        'task': [],
        'note': []
    }
    for record in records:
        if record['type'] in grouped:
            grouped[record['type']].append(record)
    return grouped

def group_by_tag(records):
    """Group records by tags."""
    by_tag = {}
    for record in records:
        for tag in record.get('tags', []):
            if tag not in by_tag:
                by_tag[tag] = []
            by_tag[tag].append(record)
    return by_tag

def format_record_brief(record):
    """Format a record briefly for reports."""
    record_time = datetime.fromisoformat(record['timestamp'])
    time_str = record_time.strftime('%H:%M')

    if record['type'] == 'git':
        msg = record['data'].get('message', '')
        repo = record['data'].get('repo', '')
        commit = record['data'].get('commit', '')
        parts = []
        if repo:
            parts.append(f"`{repo}`")
        if commit:
            parts.append(f"({commit[:7]})")
        repo_info = ' '.join(parts)
        return f"- **{time_str}** {msg} {repo_info}"

    elif record['type'] == 'web':
        title = record['data'].get('title', '')
        url = record['data'].get('url', '')
        if title:
            return f"- **{time_str}** [{title}]({url})"
        return f"- **{time_str}** [{url}]({url})"

    elif record['type'] == 'task':
        cmd = record['data'].get('command', '')
        desc = record['data'].get('description', '')
        if cmd:
            return f"- **{time_str}** `{cmd}` - {desc}"
        return f"- **{time_str}** {desc}"

    elif record['type'] == 'note':
        content = record['data'].get('content', '')
        return f"- **{time_str}** {content}"

    return f"- **{time_str}** {record['type']}"

def generate_report(records, title, subtitle=None):
    """Generate a markdown report."""
    if not records:
        return f"""# {title}

{subtitle if subtitle else ''}

No activity recorded during this period.
"""

    grouped = group_by_type(records)
    by_tag = group_by_tag(records)

    # Calculate date range
    timestamps = [datetime.fromisoformat(r['timestamp']) for r in records]
    start_date = min(timestamps)
    end_date = max(timestamps)

    lines = []
    lines.append(f"# {title}")
    lines.append("")
    if subtitle:
        lines.append(subtitle)
        lines.append("")
    lines.append(f"**Period:** {start_date.strftime('%Y-%m-%d %H:%M')} - {end_date.strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"**Total Activities:** {len(records)}")
    lines.append("")

    # Git operations
    if grouped['git']:
        lines.append("## 🔀 Git Operations")
        lines.append("")
        for record in sorted(grouped['git'], key=lambda r: r['timestamp']):
            lines.append(format_record_brief(record))
        lines.append("")

    # Web pages
    if grouped['web']:
        lines.append("## 🌐 Web Pages")
        lines.append("")
        for record in sorted(grouped['web'], key=lambda r: r['timestamp']):
            lines.append(format_record_brief(record))
        lines.append("")

    # Tasks/Commands
    if grouped['task']:
        lines.append("## ⚡ Tasks & Commands")
        lines.append("")
        for record in sorted(grouped['task'], key=lambda r: r['timestamp']):
            lines.append(format_record_brief(record))
        lines.append("")

    # Notes
    if grouped['note']:
        lines.append("## 📝 Notes")
        lines.append("")
        for record in sorted(grouped['note'], key=lambda r: r['timestamp']):
            lines.append(format_record_brief(record))
        lines.append("")

    # Tag-based grouping
    if by_tag:
        lines.append("## 🏷️ By Tag")
        lines.append("")
        for tag in sorted(by_tag.keys()):
            tag_records = by_tag[tag]
            lines.append(f"### {tag} ({len(tag_records)})")
            lines.append("")
            for record in sorted(tag_records, key=lambda r: r['timestamp'])[:5]:  # Show top 5
                lines.append(format_record_brief(record))
            if len(tag_records) > 5:
                lines.append(f"- ... and {len(tag_records) - 5} more")
            lines.append("")

    # Statistics
    lines.append("## 📊 Statistics")
    lines.append("")
    for rtype in ['git', 'web', 'task', 'note']:
        count = len(grouped[rtype])
        if count > 0:
            icon = {'git': '🔀', 'web': '🌐', 'task': '⚡', 'note': '📝'}[rtype]
            lines.append(f"- {icon} **{rtype.upper()}**: {count}")
    lines.append("")

    return '\n'.join(lines)

def main():
    args = sys.argv[1:]

    # Parse options
    from_date = None
    to_date = None
    output_file = None

    i = 0
    while i < len(args):
        if args[i] == '--day' and i + 1 < len(args):
            day_date = parse_date(args[i + 1])
            from_date = day_date.replace(hour=0, minute=0, second=0, microsecond=0)
            to_date = from_date
            i += 2
        elif args[i] == '--week':
            from_date = datetime.now() - timedelta(days=7)
            to_date = datetime.now()
            i += 1
        elif args[i] == '--from' and i + 1 < len(args):
            from_date = parse_date(args[i + 1])
            i += 2
        elif args[i] == '--to' and i + 1 < len(args):
            to_date = parse_date(args[i + 1])
            i += 2
        elif args[i] == '--output' and i + 1 < len(args):
            output_file = args[i + 1]
            i += 2
        else:
            i += 1

    if not from_date and not to_date:
        # Default to today if no date specified
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        from_date = today
        to_date = today

    # Load and filter records
    all_records = load_records()
    filtered_records = filter_records_by_date(all_records, from_date, to_date)

    # Determine report title
    if from_date == to_date:
        title = f"Daily Report - {from_date.strftime('%Y-%m-%d')}"
        subtitle = f"Activities for {from_date.strftime('%B %d, %Y')}"
    else:
        days_diff = (to_date - from_date).days
        if days_diff == 7:
            title = "Weekly Report"
        else:
            title = f"Activity Report ({days_diff} days)"
        subtitle = f"{from_date.strftime('%Y-%m-%d')} to {to_date.strftime('%Y-%m-%d')}"

    # Generate report
    report = generate_report(filtered_records, title, subtitle)

    # Output
    if output_file:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(report)
        print(f"✓ Report saved to: {output_file}")
        print(f"  ({len(filtered_records)} activities)")
    else:
        print(report)

if __name__ == '__main__':
    main()
