#!/usr/bin/env python3
"""Fast O(1) capture path: append event + ledger receipt, no LLM/network."""
import argparse, hashlib, json, uuid
from datetime import datetime, timezone
from pathlib import Path


def sha256(s: str) -> str:
    return hashlib.sha256(s.encode('utf-8')).hexdigest()


def canonical(d: dict) -> str:
    return json.dumps(d, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def read_last_chain_hash(ledger: Path) -> str:
    if not ledger.exists() or ledger.stat().st_size == 0:
        return 'GENESIS'
    with ledger.open('r', encoding='utf-8') as f:
        lines = [ln.strip() for ln in f if ln.strip()]
    return json.loads(lines[-1])['chain_hash'] if lines else 'GENESIS'


def append_jsonl(path: Path, row: dict):
    with path.open('a', encoding='utf-8') as f:
        f.write(json.dumps(row, ensure_ascii=False) + '\n')


p = argparse.ArgumentParser()
p.add_argument('--root', required=True)
p.add_argument('--source', default='agent')
p.add_argument('--importance', type=float, default=0.5)
p.add_argument('--tags', default='')
p.add_argument('--content', required=True)
args = p.parse_args()

root = Path(args.root)
root.mkdir(parents=True, exist_ok=True)
events = root / 'events.jsonl'
ledger = root / 'ledger.jsonl'
for fp in (events, ledger):
    if not fp.exists():
        fp.touch()

entry = {
    'id': str(uuid.uuid4()),
    'ts': datetime.now(timezone.utc).isoformat(),
    'type': 'events',
    'source': args.source,
    'importance': max(0.0, min(1.0, args.importance)),
    'tags': [t.strip() for t in args.tags.split(',') if t.strip()],
    'content': args.content,
    'status': 'active',
}
entry_hash = sha256(canonical(entry))
prev_hash = read_last_chain_hash(ledger)
chain_hash = sha256(prev_hash + entry_hash)

stored = {**entry, 'entry_hash': entry_hash, 'prev_hash': prev_hash, 'chain_hash': chain_hash}
append_jsonl(events, stored)
append_jsonl(ledger, {
    'ts': entry['ts'],
    'entry_id': entry['id'],
    'layer': 'events',
    'entry_hash': entry_hash,
    'prev_hash': prev_hash,
    'chain_hash': chain_hash,
})

print(json.dumps({'ok': True, 'entry_id': entry['id'], 'chain_hash': chain_hash}))
