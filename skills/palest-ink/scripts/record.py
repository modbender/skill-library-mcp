#!/usr/bin/env python3
"""Record activities for Palest Ink."""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

PALEST_INK_HOME = Path(os.environ.get('PALEST_INK_HOME', os.path.expanduser('~/.palest-ink')))
RECORDS_FILE = PALEST_INK_HOME / 'records.json'

def load_records():
    """Load all records from JSON file."""
    if not RECORDS_FILE.exists():
        return []
    with open(RECORDS_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_records(records):
    """Save records to JSON file."""
    PALEST_INK_HOME.mkdir(parents=True, exist_ok=True)
    with open(RECORDS_FILE, 'w') as f:
        json.dump(records, f, indent=2)

def generate_id(records):
    """Generate a unique ID for a new record."""
    if not records:
        return 1
    return max(r.get('id', 0) for r in records) + 1

def parse_tags(tags_str):
    """Parse comma-separated tags string."""
    if not tags_str:
        return []
    return [tag.strip() for tag in tags_str.split(',') if tag.strip()]

def record_git(args):
    """Record a git operation."""
    record = {
        'id': generate_id(load_records()),
        'type': 'git',
        'timestamp': datetime.now().isoformat(),
        'data': {}
    }

    # Parse arguments
    i = 0
    while i < len(args):
        if args[i] == '--message' and i + 1 < len(args):
            record['data']['message'] = args[i + 1]
            i += 2
        elif args[i] == '--repo' and i + 1 < len(args):
            record['data']['repo'] = args[i + 1]
            i += 2
        elif args[i] == '--commit' and i + 1 < len(args):
            record['data']['commit'] = args[i + 1]
            i += 2
        elif args[i] == '--pr' and i + 1 < len(args):
            record['data']['pr'] = args[i + 1]
            i += 2
        elif args[i] == '--tags' and i + 1 < len(args):
            record['tags'] = parse_tags(args[i + 1])
            i += 2
        else:
            i += 1

    # Validate
    if 'message' not in record['data']:
        print("Error: --message is required for git records")
        sys.exit(1)

    return record

def record_web(args):
    """Record a web page visit."""
    record = {
        'id': generate_id(load_records()),
        'type': 'web',
        'timestamp': datetime.now().isoformat(),
        'data': {}
    }

    i = 0
    while i < len(args):
        if args[i] == '--url' and i + 1 < len(args):
            record['data']['url'] = args[i + 1]
            i += 2
        elif args[i] == '--title' and i + 1 < len(args):
            record['data']['title'] = args[i + 1]
            i += 2
        elif args[i] == '--tags' and i + 1 < len(args):
            record['tags'] = parse_tags(args[i + 1])
            i += 2
        else:
            i += 1

    if 'url' not in record['data']:
        print("Error: --url is required for web records")
        sys.exit(1)

    if 'title' not in record['data']:
        record['data']['title'] = record['data']['url']

    return record

def record_task(args):
    """Record a command or task."""
    record = {
        'id': generate_id(load_records()),
        'type': 'task',
        'timestamp': datetime.now().isoformat(),
        'data': {}
    }

    i = 0
    while i < len(args):
        if args[i] == '--command' and i + 1 < len(args):
            record['data']['command'] = args[i + 1]
            i += 2
        elif args[i] == '--desc' and i + 1 < len(args):
            record['data']['description'] = args[i + 1]
            i += 2
        elif args[i] == '--tags' and i + 1 < len(args):
            record['tags'] = parse_tags(args[i + 1])
            i += 2
        else:
            i += 1

    return record

def record_note(args):
    """Record a free-form note."""
    record = {
        'id': generate_id(load_records()),
        'type': 'note',
        'timestamp': datetime.now().isoformat(),
        'data': {}
    }

    i = 0
    while i < len(args):
        if args[i] == '--content' and i + 1 < len(args):
            record['data']['content'] = args[i + 1]
            i += 2
        elif args[i] == '--tags' and i + 1 < len(args):
            record['tags'] = parse_tags(args[i + 1])
            i += 2
        else:
            i += 1

    if 'content' not in record['data']:
        print("Error: --content is required for note records")
        sys.exit(1)

    return record

def main():
    if len(sys.argv) < 2:
        print("Error: record type required (git, web, task, note)")
        sys.exit(1)

    record_type = sys.argv[1]
    args = sys.argv[2:]

    if record_type == 'git':
        record = record_git(args)
    elif record_type == 'web':
        record = record_web(args)
    elif record_type == 'task':
        record = record_task(args)
    elif record_type == 'note':
        record = record_note(args)
    else:
        print(f"Error: Unknown record type '{record_type}'")
        sys.exit(1)

    # Add tags if not present
    if 'tags' not in record:
        record['tags'] = []

    # Save record
    records = load_records()
    records.append(record)
    save_records(records)

    # Format output
    print(f"✓ Recorded {record_type} activity (ID: {record['id']})")
    if record['tags']:
        print(f"  Tags: {', '.join(record['tags'])}")

if __name__ == '__main__':
    main()
