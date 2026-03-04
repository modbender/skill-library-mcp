#!/usr/bin/env python3
"""
flatten_transcript.py — Flatten an OpenClaw JSONL session transcript to plain text.

Usage:
  python3 flatten_transcript.py <path_to_jsonl> [output_path]
  python3 flatten_transcript.py <path_to_jsonl> --since-minutes 60
  python3 flatten_transcript.py <path_to_jsonl> --since-minutes 60 --output /tmp/flat.txt

Options:
  --since-minutes N   Only include entries from the last N minutes (time-based filter).
                      Reads the 'timestamp' or 'ts' field from each JSONL entry.
  --output PATH       Write output to file instead of stdout.
"""

import json
import sys
import os
import time
import argparse


def flatten_transcript(file_path, since_minutes=None):
    cutoff_ts = None
    if since_minutes is not None:
        cutoff_ts = time.time() - (since_minutes * 60)

    output = []
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)

                # Time-based filtering: check timestamp field
                if cutoff_ts is not None:
                    ts = data.get('timestamp') or data.get('ts') or data.get('created_at')
                    if ts is not None:
                        # Handle ISO strings and unix floats
                        if isinstance(ts, str):
                            from datetime import datetime, timezone
                            try:
                                parsed = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                                ts = parsed.timestamp()
                            except Exception:
                                ts = None
                        if ts is not None and ts < cutoff_ts:
                            continue  # Skip entries older than cutoff

                if data.get('type') == 'message':
                    msg = data.get('message', {})
                    role = msg.get('role', 'unknown')
                    content = msg.get('content', [])

                    text_parts = []
                    for part in content:
                        if isinstance(part, str):
                            text_parts.append(part)
                        elif isinstance(part, dict):
                            if part.get('type') == 'text':
                                text_parts.append(part.get('text', ''))
                            elif part.get('type') == 'toolCall':
                                text_parts.append(f"[Tool: {part.get('name')}]")
                            elif part.get('type') == 'toolResult':
                                # Only include the result text, skip raw JSON blobs
                                result_content = part.get('content', '')
                                if isinstance(result_content, list):
                                    for rc in result_content:
                                        if isinstance(rc, dict) and rc.get('type') == 'text':
                                            text_parts.append(f"[Result: {rc.get('text', '')[:500]}]")
                                elif isinstance(result_content, str):
                                    text_parts.append(f"[Result: {result_content[:500]}]")

                    if text_parts:
                        output.append(f"{role.upper()}: {' '.join(text_parts)}")

            except (json.JSONDecodeError, KeyError, TypeError):
                continue

    return "\n\n".join(output)


def main():
    parser = argparse.ArgumentParser(description='Flatten an OpenClaw JSONL session transcript.')
    parser.add_argument('file_path', help='Path to the .jsonl transcript file')
    parser.add_argument('output_path', nargs='?', help='Optional output file path (positional)')
    parser.add_argument('--since-minutes', type=int, default=None,
                        help='Only include entries from the last N minutes')
    parser.add_argument('--output', dest='output_file', default=None,
                        help='Write output to this file instead of stdout')
    args = parser.parse_args()

    if not os.path.exists(args.file_path):
        print(f"Error: File not found: {args.file_path}", file=sys.stderr)
        sys.exit(1)

    result = flatten_transcript(args.file_path, since_minutes=args.since_minutes)

    out_path = args.output_file or args.output_path
    if out_path:
        with open(out_path, 'w') as f:
            f.write(result)
        char_count = len(result)
        print(f"Written {char_count:,} chars to {out_path}", file=sys.stderr)
    else:
        print(result)


if __name__ == "__main__":
    main()
