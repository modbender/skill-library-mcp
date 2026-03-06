#!/usr/bin/env python3
import argparse, json
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path


def read_jsonl(path: Path):
    if not path.exists() or path.stat().st_size == 0:
        return []
    out = []
    with path.open('r', encoding='utf-8') as f:
        for ln in f:
            ln = ln.strip()
            if ln:
                out.append(json.loads(ln))
    return out


def append_jsonl(path: Path, row: dict):
    with path.open('a', encoding='utf-8') as f:
        f.write(json.dumps(row, ensure_ascii=False) + '\n')


p = argparse.ArgumentParser()
p.add_argument('--root', required=True)
p.add_argument('--hours', type=int, default=24)
p.add_argument('--promote-tag-threshold', type=int, default=3)
args = p.parse_args()

root = Path(args.root)
events_p = root / 'events.jsonl'
semantic_p = root / 'semantic.jsonl'
log_p = root / 'consolidation-log.jsonl'
for fp in (events_p, semantic_p, log_p):
    if not fp.exists():
        fp.touch()

now = datetime.now(timezone.utc)
cutoff = now - timedelta(hours=args.hours)
events = []
for e in read_jsonl(events_p):
    try:
        ts = datetime.fromisoformat(e['ts'])
    except Exception:
        continue
    if ts >= cutoff:
        events.append(e)

promoted = []
tag_counts = Counter(t for e in events for t in e.get('tags', []))
for tag, count in tag_counts.items():
    if count >= args.promote_tag_threshold:
        fact = {
            'id': f'sem-{int(now.timestamp())}-{tag}',
            'ts': now.isoformat(),
            'type': 'semantic',
            'source': 'consolidate_daily',
            'importance': 0.7,
            'tags': [tag],
            'content': f'Active recurring theme: {tag} ({count} events in {args.hours}h).',
            'status': 'active'
        }
        append_jsonl(semantic_p, fact)
        promoted.append({'tag': tag, 'count': count})

append_jsonl(log_p, {
    'ts': now.isoformat(),
    'source': 'consolidate_daily',
    'events_scanned': len(events),
    'promoted': promoted,
    'contradictions': [],
    'status': 'ok'
})

print(json.dumps({'ok': True, 'events_scanned': len(events), 'promoted_count': len(promoted)}, ensure_ascii=False))
