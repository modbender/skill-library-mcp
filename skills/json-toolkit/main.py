#!/usr/bin/env python3
"""json-formatter: Validate, pretty-print, minify, and query JSON."""

import sys
import json
import argparse


def query_json(data, path):
    """Simple dot-notation query with array index support: a.b.0.c"""
    keys = path.split('.')
    current = data
    for key in keys:
        if isinstance(current, list):
            try:
                current = current[int(key)]
            except (ValueError, IndexError):
                raise KeyError(f"Invalid array index: {key}")
        elif isinstance(current, dict):
            if key not in current:
                raise KeyError(f"Key not found: {key}")
            current = current[key]
        else:
            raise KeyError(f"Cannot traverse into {type(current).__name__} with key: {key}")
    return current


def main():
    parser = argparse.ArgumentParser(description='JSON formatter and query tool')
    parser.add_argument('input', help='Input JSON file (use - for stdin)')
    parser.add_argument('-o', '--output', help='Output file (default: stdout)')
    parser.add_argument('--indent', type=int, default=2, help='Indentation (default: 2)')
    parser.add_argument('--minify', action='store_true', help='Minify output')
    parser.add_argument('--query', '-q', help='Query path (dot notation, e.g. data.users.0.name)')
    parser.add_argument('--validate', action='store_true', help='Only validate, no output')
    parser.add_argument('--sort-keys', action='store_true', help='Sort object keys')
    args = parser.parse_args()

    # Read input
    try:
        if args.input == '-':
            raw = sys.stdin.read()
        else:
            with open(args.input, 'r') as f:
                raw = f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    # Parse
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if args.validate:
        print("✓ Valid JSON")
        # Print stats
        if isinstance(data, dict):
            print(f"  Type: object ({len(data)} keys)")
        elif isinstance(data, list):
            print(f"  Type: array ({len(data)} items)")
        else:
            print(f"  Type: {type(data).__name__}")
        print(f"  Size: {len(raw)} bytes")
        sys.exit(0)

    # Query
    if args.query:
        try:
            data = query_json(data, args.query)
        except KeyError as e:
            print(f"Query error: {e}", file=sys.stderr)
            sys.exit(1)

    # Format
    if args.minify:
        result = json.dumps(data, separators=(',', ':'), sort_keys=args.sort_keys, ensure_ascii=False)
    else:
        result = json.dumps(data, indent=args.indent, sort_keys=args.sort_keys, ensure_ascii=False)

    # Output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(result + '\n')
        print(f"Written to {args.output}", file=sys.stderr)
    else:
        print(result)


if __name__ == '__main__':
    main()
