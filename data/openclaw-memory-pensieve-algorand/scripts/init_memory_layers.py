#!/usr/bin/env python3
from pathlib import Path
import argparse

FILES = [
    'events.jsonl',
    'semantic.jsonl',
    'procedural.jsonl',
    'self_model.jsonl',
    'consolidation-log.jsonl',
    'ledger.jsonl',
    'onchain-anchors.jsonl',
]

p = argparse.ArgumentParser()
p.add_argument('--root', required=True)
args = p.parse_args()

root = Path(args.root)
root.mkdir(parents=True, exist_ok=True)
for name in FILES:
    fp = root / name
    if not fp.exists():
        fp.touch()
        print(f'created {fp}')
    else:
        print(f'exists  {fp}')
