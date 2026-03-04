#!/usr/bin/env python3
import argparse, hashlib, json, uuid
from datetime import datetime, timezone
from pathlib import Path

LAYER_FILE = {
    'events': 'events.jsonl',
    'semantic': 'semantic.jsonl',
    'procedural': 'procedural.jsonl',
    'self_model': 'self_model.jsonl',
}


def sha256(s: str) -> str:
    return hashlib.sha256(s.encode('utf-8')).hexdigest()


def canonical(d: dict) -> str:
    return json.dumps(d, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def read_last_chain_hash(ledger_path: Path) -> str:
    if not ledger_path.exists() or ledger_path.stat().st_size == 0:
        return 'GENESIS'
    with ledger_path.open('r', encoding='utf-8') as f:
        lines = [ln.strip() for ln in f if ln.strip()]
    if not lines:
        return 'GENESIS'
    return json.loads(lines[-1])['chain_hash']


def append_jsonl(path: Path, row: dict) -> None:
    with path.open('a', encoding='utf-8') as f:
        f.write(json.dumps(row, ensure_ascii=False) + '\n')


p = argparse.ArgumentParser()
p.add_argument('--root', required=True)
p.add_argument('--layer', required=True, choices=list(LAYER_FILE.keys()))
p.add_argument('--source', default='manual')
p.add_argument('--importance', type=float, default=0.5)
p.add_argument('--tags', default='')
p.add_argument('--content', required=True)
args = p.parse_args()

root = Path(args.root)
root.mkdir(parents=True, exist_ok=True)
layer_path = root / LAYER_FILE[args.layer]
ledger_path = root / 'ledger.jsonl'
for fp in (layer_path, ledger_path):
    if not fp.exists():
        fp.touch()

tags = [t.strip() for t in args.tags.split(',') if t.strip()]
entry = {
    'id': str(uuid.uuid4()),
    'ts': datetime.now(timezone.utc).isoformat(),
    'type': args.layer,
    'source': args.source,
    'importance': max(0.0, min(1.0, args.importance)),
    'tags': tags,
    'content': args.content,
    'status': 'active',
}
entry_hash = sha256(canonical(entry))
prev_hash = read_last_chain_hash(ledger_path)
chain_hash = sha256(prev_hash + entry_hash)

stored = {**entry, 'entry_hash': entry_hash, 'prev_hash': prev_hash, 'chain_hash': chain_hash}
append_jsonl(layer_path, stored)
append_jsonl(ledger_path, {
    'ts': entry['ts'],
    'entry_id': entry['id'],
    'layer': args.layer,
    'entry_hash': entry_hash,
    'prev_hash': prev_hash,
    'chain_hash': chain_hash,
})

print(json.dumps({'ok': True, 'entry_id': entry['id'], 'chain_hash': chain_hash}, ensure_ascii=False))
