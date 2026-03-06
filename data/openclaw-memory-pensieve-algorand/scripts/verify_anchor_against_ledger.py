#!/usr/bin/env python3
import argparse, json
from pathlib import Path

p = argparse.ArgumentParser(description='Verify decrypted anchor payload against local ledger')
p.add_argument('--root', required=True)
p.add_argument('--payload-file', required=True, help='JSON payload from decrypted note')
args = p.parse_args()

root = Path(args.root)
ledger = root / 'ledger.jsonl'
if not ledger.exists():
    raise SystemExit('ledger.jsonl not found')

lines = [ln.strip() for ln in ledger.read_text(encoding='utf-8').splitlines() if ln.strip()]
ledger_tip = json.loads(lines[-1])['chain_hash'] if lines else 'GENESIS'

payload = json.loads(Path(args.payload_file).read_text(encoding='utf-8'))
ok = payload.get('ledger_tip') == ledger_tip

print(json.dumps({
    'ok': True,
    'match': ok,
    'payload_ledger_tip': payload.get('ledger_tip'),
    'local_ledger_tip': ledger_tip,
    'entries_local': len(lines),
    'entries_payload': payload.get('entries')
}))
