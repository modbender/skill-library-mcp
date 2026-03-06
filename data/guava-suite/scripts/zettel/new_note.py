#!/usr/bin/env python3
from __future__ import annotations
import argparse, os, datetime as dt, pathlib, re

ROOT = pathlib.Path(os.environ.get('OPENCLAW_WORKSPACE', os.path.expanduser('~/.openclaw/workspace')))
NOTES_DIR = ROOT / 'memory' / 'notes'
NOTES_DIR.mkdir(parents=True, exist_ok=True)


def slug(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r'[^a-z0-9\-\s_]', '', s)
    s = re.sub(r'[\s_]+', '-', s)
    return s[:50] or 'note'


def main():
    p = argparse.ArgumentParser(description='Create a zettel note markdown file')
    p.add_argument('--title', required=True)
    p.add_argument('--body', required=True)
    p.add_argument('--tags', default='')
    p.add_argument('--entities', default='')
    p.add_argument('--source', default='')
    p.add_argument('--confidence', type=float, default=0.7)
    p.add_argument('--supersedes', default='')
    args = p.parse_args()

    now = dt.datetime.now(dt.timezone.utc)
    zid = f"zettel-{now.strftime('%Y%m%d-%H%M%S')}-{now.microsecond:06d}"
    filename = f"{zid}-{slug(args.title)}.md"
    path = NOTES_DIR / filename

    tags = [t.strip() for t in args.tags.split(',') if t.strip()]
    entities = [e.strip() for e in args.entities.split(',') if e.strip()]
    supersedes = args.supersedes if args.supersedes else 'null'

    content = f"""---
id: {zid}
title: {args.title}
tags: [{', '.join(tags)}]
entities: [{', '.join(entities)}]
source: {args.source or 'manual'}
created_at: {now.isoformat()}
updated_at: {now.isoformat()}
supersedes: {supersedes}
links: []
confidence: {args.confidence:.2f}
---

{args.body}
"""
    path.write_text(content, encoding='utf-8')
    print(path)


if __name__ == '__main__':
    main()
