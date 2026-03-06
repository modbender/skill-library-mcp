#!/usr/bin/env python3
import argparse, json
from datetime import datetime, timezone
from pathlib import Path

p = argparse.ArgumentParser(description='Append date->txid mapping for on-chain anchors')
p.add_argument('--root', required=True)
p.add_argument('--date', required=True)
p.add_argument('--txid', required=True)
p.add_argument('--root-hash', required=True)
args = p.parse_args()

root = Path(args.root)
root.mkdir(parents=True, exist_ok=True)
out = root / 'onchain-anchors.jsonl'
row = {
    'ts': datetime.now(timezone.utc).isoformat(),
    'date': args.date,
    'txid': args.txid,
    'root_hash': args.root_hash,
    'status': 'anchored'
}
with out.open('a', encoding='utf-8') as f:
    f.write(json.dumps(row, ensure_ascii=False) + '\n')

print(json.dumps({'ok': True, 'recorded': row}))
