#!/usr/bin/env python3
"""Query and search Palest Ink records."""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

PALEST_INK_HOME = Path(os.environ.get('PALEST_INK_HOME', os.path.expanduser('~/.palest-ink')))
RECORDS_FILE = PALEST_INK_HOME / 'records.json'

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
    """Parse date string to datetime."""
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            print(f"Error: Invalid date format '{date_str}'. Use YYYY-MM-DD")
            sys.exit(1)

def parse_tags(tags_str):
    """Parse comma-separated tags."""
    if not tags_str:
        return []
    return [tag.strip() for tag in tags_str.split(',') if tag.strip()]

def matches_filters(record, filters):
    """Check if record matches all filters."""
    # Type filter
    if filters.get('type') and record['type'] != filters['type']:
        return False

    # Tags filter (OR logic for single tags, AND logic for multiple --tags calls)
    if filters.get('tags'):
        record_tags = set(record.get('tags', []))
        for tag_set in filters['tags']:
            if not record_tags.intersection(tag_set):
                return False

    # Keywords filter
    if filters.get('keywords'):
        text = ''
        if record['type'] == 'git':
            text = record['data'].get('message', '')
        elif record['type'] == 'web':
            text = f"{record['data'].get('title', '')} {record['data'].get('url', '')}"
        elif record['type'] == 'task':
            text = f"{record['data'].get('command', '')} {record['data'].get('description', '')}"
        elif record['type'] == 'note':
            text = record['data'].get('content', '')

        text = text.lower()
        for keyword in filters['keywords']:
            if keyword.lower() not in text:
                return False

    # Date range filter
    if filters.get('from_date'):
        record_time = datetime.fromisoformat(record['timestamp'])
        if record_time < filters['from_date']:
            return False

    if filters.get('to_date'):
        record_time = datetime.fromisoformat(record['timestamp'])
        # Add one day to include the end date fully
        to_date = filters['to_date'] + timedelta(days=1)
        if record_time >= to_date:
            return False

    return True

def format_record(record, show_details=True):
    """Format a record for display."""
    record_time = datetime.fromisoformat(record['timestamp'])
    time_str = record_time.strftime('%Y-%m-%d %H:%M')

    icon = {
        'git': '🔀',
        'web': '🌐',
        'task': '⚡',
        'note': '📝'
    }.get(record['type'], '📌')

    lines = [f"{icon} [{time_str}] {record['type'].upper()}"]

    if record['type'] == 'git':
        msg = record['data'].get('message', '')
        repo = record['data'].get('repo', '')
        commit = record['data'].get('commit', '')
        pr = record['data'].get('pr', '')

        if msg:
            lines.append(f"   {msg}")
        if repo or commit:
            parts = []
            if repo:
                parts.append(f"repo:{repo}")
            if commit:
                parts.append(f"commit:{commit[:7]}")
            if pr:
                parts.append(f"pr:{pr}")
            lines.append(f"   ({', '.join(parts)})")

    elif record['type'] == 'web':
        title = record['data'].get('title', '')
        url = record['data'].get('url', '')

        if title:
            lines.append(f"   {title}")
        if url:
            lines.append(f"   {url}")

    elif record['type'] == 'task':
        cmd = record['data'].get('command', '')
        desc = record['data'].get('description', '')

        if cmd:
            lines.append(f"   $ {cmd}")
        if desc:
            lines.append(f"   {desc}")

    elif record['type'] == 'note':
        content = record['data'].get('content', '')
        lines.append(f"   {content}")

    if record.get('tags'):
        lines.append(f"   Tags: {', '.join(record['tags'])}")

    return '\n'.join(lines)

def list_all_tags(records):
    """List all unique tags across all records."""
    all_tags = set()
    for record in records:
        all_tags.update(record.get('tags', []))

    if not all_tags:
        print("No tags found in records.")
        return

    print("All tags:")
    for tag in sorted(all_tags):
        count = sum(1 for r in records if tag in r.get('tags', []))
        print(f"  - {tag} ({count})")

def main():
    args = sys.argv[1:]

    # Parse filters
    filters = {
        'type': None,
        'tags': [],
        'keywords': [],
        'from_date': None,
        'to_date': None
    }

    i = 0
    while i < len(args):
        if args[i] == '--type' and i + 1 < len(args):
            filters['type'] = args[i + 1]
            i += 2
        elif args[i] == '--tags' and i + 1 < len(args):
            tags = parse_tags(args[i + 1])
            filters['tags'].append(set(tags))
            i += 2
        elif args[i] == '--keywords' and i + 1 < len(args):
            filters['keywords'].extend(parse_tags(args[i + 1]))
            i += 2
        elif args[i] == '--today':
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            filters['from_date'] = today
            filters['to_date'] = today
            i += 1
        elif args[i] == '--days' and i + 1 < len(args):
            try:
                days = int(args[i + 1])
            except ValueError:
                print("Error: --days requires a number")
                sys.exit(1)
            filters['from_date'] = datetime.now() - timedelta(days=days)
            filters['to_date'] = datetime.now()
            i += 2
        elif args[i] == '--from' and i + 1 < len(args):
            filters['from_date'] = parse_date(args[i + 1])
            i += 2
        elif args[i] == '--to' and i + 1 < len(args):
            filters['to_date'] = parse_date(args[i + 1])
            i += 2
        elif args[i] == '--list-tags':
            records = load_records()
            list_all_tags(records)
            sys.exit(0)
        else:
            i += 1

    # Load and filter records
    all_records = load_records()
    filtered_records = [r for r in all_records if matches_filters(r, filters)]

    # Sort by timestamp (newest first)
    filtered_records.sort(key=lambda r: r['timestamp'], reverse=True)

    # Display results
    if not filtered_records:
        print("No records found matching your criteria.")
        if filters.get('type'):
            print(f"  Type: {filters['type']}")
        if filters.get('tags'):
            print(f"  Tags: {', '.join(' & '.join(t) for t in filters['tags'])}")
        if filters.get('keywords'):
            print(f"  Keywords: {', '.join(filters['keywords'])}")
        if filters.get('from_date') or filters.get('to_date'):
            date_info = []
            if filters['from_date']:
                date_info.append(f"from {filters['from_date'].strftime('%Y-%m-%d')}")
            if filters['to_date']:
                date_info.append(f"to {filters['to_date'].strftime('%Y-%m-%d')}")
            print(f"  Date: {' '.join(date_info)}")
        sys.exit(0)

    print(f"Found {len(filtered_records)} record(s):\n")

    for record in filtered_records:
        print(format_record(record))
        print()

    # Show summary
    print("---")
    print(f"Total: {len(filtered_records)} records")

    # Count by type
    by_type = {}
    for r in filtered_records:
        by_type[r['type']] = by_type.get(r['type'], 0) + 1
    if by_type:
        print(f"By type: {', '.join(f'{k}:{v}' for k, v in by_type.items())}")

if __name__ == '__main__':
    main()
