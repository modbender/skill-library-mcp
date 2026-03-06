#!/usr/bin/env python3
import argparse, hashlib, json
from datetime import datetime, timezone
from pathlib import Path


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode('utf-8')).hexdigest()


p = argparse.ArgumentParser()
p.add_argument('--root', required=True)
p.add_argument('--date', default=datetime.now(timezone.utc).date().isoformat())
p.add_argument('--mode', default='daily-consolidation')
args = p.parse_args()

root = Path(args.root)
ledger = root / 'ledger.jsonl'
if not ledger.exists():
    raise SystemExit('ledger.jsonl not found')

lines = [ln.strip() for ln in ledger.read_text(encoding='utf-8').splitlines() if ln.strip()]
ledger_tip = json.loads(lines[-1])['chain_hash'] if lines else 'GENESIS'
root_hash = sha256_text('\n'.join(lines))

payload = {
    'v': 1,
    'mode': args.mode,
    'date': args.date,
    'root_hash': root_hash,
    'entries': len(lines),
    'ledger_tip': ledger_tip,
}
print(json.dumps(payload, ensure_ascii=False, separators=(',', ':')))
