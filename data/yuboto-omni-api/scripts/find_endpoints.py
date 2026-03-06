#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(description='Search Yuboto swagger endpoints by keyword')
    ap.add_argument('--swagger', default=str(Path(__file__).resolve().parents[1] / 'references' / 'swagger_v1.json'))
    ap.add_argument('--q', required=True, help='keyword regex to search in path/summary/operationId')
    args = ap.parse_args()

    data = json.loads(Path(args.swagger).read_text(encoding='utf-8'))
    rgx = re.compile(args.q, re.I)

    found = 0
    for path, item in data.get('paths', {}).items():
        for method, op in item.items():
            if method.lower() not in {'get', 'post', 'put', 'patch', 'delete'}:
                continue
            text = ' | '.join([
                path,
                op.get('summary', ''),
                op.get('description', ''),
                op.get('operationId', ''),
                ' '.join(op.get('tags', [])),
            ])
            if rgx.search(text):
                found += 1
                print(f"{method.upper():6} {path}")
                if op.get('summary'):
                    print(f"  summary: {op['summary']}")
                if op.get('operationId'):
                    print(f"  operationId: {op['operationId']}")
    if not found:
        print('No endpoints matched.')


if __name__ == '__main__':
    main()
