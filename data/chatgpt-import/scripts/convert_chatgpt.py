#!/usr/bin/env python3
"""Convert ChatGPT conversations.json to markdown files for OpenClaw memory search."""
import argparse
import json
import os
import re
from datetime import datetime, timezone


def sanitize_filename(s, max_len=80):
    s = re.sub(r'[^\w\s\-]', '', s or 'untitled')
    s = re.sub(r'\s+', '-', s.strip())
    return s[:max_len].rstrip('-') or 'untitled'


def extract_linear_messages(conv):
    """Walk from current_node back to root to get the linear conversation path."""
    mapping = conv.get('mapping', {})
    current = conv.get('current_node')
    if not current or current not in mapping:
        return []

    path = []
    node_id = current
    while node_id and node_id in mapping:
        path.append(node_id)
        node_id = mapping[node_id].get('parent')
    path.reverse()

    messages = []
    for nid in path:
        node = mapping[nid]
        msg = node.get('message')
        if not msg:
            continue
        role = msg.get('author', {}).get('role', '')
        if role not in ('user', 'assistant'):
            continue
        content = msg.get('content', {})
        parts = content.get('parts', [])
        text_parts = []
        for p in parts:
            if isinstance(p, str) and p.strip():
                text_parts.append(p.strip())
            elif isinstance(p, dict) and p.get('text', '').strip():
                text_parts.append(p['text'].strip())
        text = '\n'.join(text_parts)
        if text:
            messages.append((role, text))
    return messages


def main():
    parser = argparse.ArgumentParser(description='Convert ChatGPT conversations.json to markdown files')
    parser.add_argument('--input', required=True, help='Path to conversations.json')
    parser.add_argument('--output', required=True, help='Output directory for markdown files')
    parser.add_argument('--min-messages', type=int, default=2, help='Minimum messages to include a conversation (default: 2)')
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    with open(args.input) as f:
        convs = json.load(f)

    print(f"Processing {len(convs)} conversations...")

    written = 0
    skipped = 0
    seen_names = {}

    for conv in convs:
        title = conv.get('title', 'Untitled')
        create_time = conv.get('create_time')

        messages = extract_linear_messages(conv)
        if len(messages) < args.min_messages:
            skipped += 1
            continue

        if create_time:
            dt = datetime.fromtimestamp(create_time, tz=timezone.utc)
            date_str = dt.strftime('%Y-%m-%d')
        else:
            date_str = 'unknown'

        base_name = f"{date_str}_{sanitize_filename(title)}"
        if base_name in seen_names:
            seen_names[base_name] += 1
            base_name = f"{base_name}_{seen_names[base_name]}"
        else:
            seen_names[base_name] = 0

        filepath = os.path.join(args.output, f"{base_name}.md")

        lines = [f"# {title}\n"]
        if create_time:
            lines.append(f"**Date:** {date_str}\n")
        lines.append("")

        for role, text in messages:
            prefix = "**User:**" if role == 'user' else "**Assistant:**"
            if role == 'assistant' and len(text) > 4000:
                text = text[:4000] + "\n\n[...truncated...]"
            lines.append(f"{prefix}\n{text}\n")

        with open(filepath, 'w') as f:
            f.write('\n'.join(lines))
        written += 1

    total_size = sum(
        os.path.getsize(os.path.join(args.output, f))
        for f in os.listdir(args.output) if f.endswith('.md')
    )
    print(f"\nSummary:")
    print(f"  Files written: {written}")
    print(f"  Skipped:       {skipped}")
    print(f"  Total size:    {total_size / 1024 / 1024:.1f} MB")


if __name__ == '__main__':
    main()
