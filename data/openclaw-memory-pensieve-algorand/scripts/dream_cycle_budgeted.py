#!/usr/bin/env python3
"""Budgeted dream cycle: bounded scan/promotions for predictable runtime/cost."""
import argparse, json
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path


def read_jsonl_tail(path: Path, max_lines: int):
    if not path.exists() or path.stat().st_size == 0:
        return []
    lines = path.read_text(encoding='utf-8').splitlines()
    out = []
    for ln in lines[-max_lines:]:
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
p.add_argument('--max-events', type=int, default=200)
p.add_argument('--max-semantic', type=int, default=20)
p.add_argument('--max-procedural', type=int, default=10)
p.add_argument('--max-self', type=int, default=5)
args = p.parse_args()

root = Path(args.root)
events_p = root / 'events.jsonl'
sem_p = root / 'semantic.jsonl'
proc_p = root / 'procedural.jsonl'
self_p = root / 'self_model.jsonl'
log_p = root / 'consolidation-log.jsonl'
for fp in (events_p, sem_p, proc_p, self_p, log_p):
    if not fp.exists():
        fp.touch()

now = datetime.now(timezone.utc)
cutoff = now - timedelta(hours=args.hours)
rows = read_jsonl_tail(events_p, args.max_events * 3)

events = []
for e in rows:
    try:
        ts = datetime.fromisoformat(e.get('ts'))
    except Exception:
        continue
    if ts >= cutoff:
        events.append(e)

events = events[-args.max_events:]
tag_counts = Counter(t for e in events for t in e.get('tags', []))
source_counts = Counter(e.get('source', 'unknown') for e in events)

prom_sem = prom_proc = prom_self = 0
for tag, n in tag_counts.most_common():
    if prom_sem >= args.max_semantic:
        break
    if n >= 3:
        append_jsonl(sem_p, {
            'id': f'sem-{int(now.timestamp())}-{prom_sem}',
            'ts': now.isoformat(), 'type': 'semantic', 'source': 'dream_cycle_budgeted',
            'importance': 0.7, 'tags': [tag],
            'content': f'Recurring focus: {tag} ({n} events/{args.hours}h).', 'status': 'active'
        })
        prom_sem += 1

for src, n in source_counts.most_common():
    if prom_proc >= args.max_procedural:
        break
    if src not in ('unknown', 'manual') and n >= 3:
        append_jsonl(proc_p, {
            'id': f'proc-{int(now.timestamp())}-{prom_proc}',
            'ts': now.isoformat(), 'type': 'procedural', 'source': 'dream_cycle_budgeted',
            'importance': 0.65, 'tags': ['workflow', src],
            'content': f'Repeated workflow signal: source={src} appears {n} times/{args.hours}h.', 'status': 'active'
        })
        prom_proc += 1

if tag_counts.get('memory', 0) >= 5 and prom_self < args.max_self:
    append_jsonl(self_p, {
        'id': f'self-{int(now.timestamp())}-0',
        'ts': now.isoformat(), 'type': 'self_model', 'source': 'dream_cycle_budgeted',
        'importance': 0.8, 'tags': ['identity', 'memory'],
        'content': 'Prioritize durable memory consistency and append-only integrity checks.', 'status': 'active'
    })
    prom_self += 1

append_jsonl(log_p, {
    'ts': now.isoformat(),
    'source': 'dream_cycle_budgeted',
    'window_hours': args.hours,
    'events_scanned': len(events),
    'caps': {
        'max_events': args.max_events,
        'max_semantic': args.max_semantic,
        'max_procedural': args.max_procedural,
        'max_self': args.max_self,
    },
    'promoted': {'semantic': prom_sem, 'procedural': prom_proc, 'self_model': prom_self},
    'status': 'ok'
})

print(json.dumps({'ok': True, 'events_scanned': len(events), 'promoted_semantic': prom_sem, 'promoted_procedural': prom_proc, 'promoted_self_model': prom_self}))
