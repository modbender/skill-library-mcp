#!/usr/bin/env python3
"""Create an execution manifest for async subcalls from an async plan.
It outputs a JSONL file with one entry per subcall, suitable for a controller
that will call sessions_spawn in parallel batches.

Usage:
  rlm_async_spawn.py --async-plan <async_plan.json> --out <spawn.jsonl>
"""
import argparse, json, os, sys
from rlm_path import validate_path as _validate_path

# --- Safelist enforcement ---
ALLOWED_ACTION = "sessions_spawn"
MAX_SUBCALLS = 32
MAX_BATCHES = 8

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--async-plan', required=True)
    p.add_argument('--out', required=True)
    args = p.parse_args()

    rp_in = _validate_path(args.async_plan)
    rp_out = _validate_path(args.out)
    with open(rp_in, 'r', encoding='utf-8') as f:
        ap = json.load(f)

    with open(rp_out, 'w', encoding='utf-8') as f:
        batch_id = 0
        total_entries = 0
        for batch in ap.get('batches', []):
            batch_id += 1
            if batch_id > MAX_BATCHES:
                print(f"ERROR: batch count {batch_id} exceeds limit of {MAX_BATCHES}", file=sys.stderr)
                sys.exit(1)
            for item in batch:
                total_entries += 1
                if total_entries > MAX_SUBCALLS:
                    print(f"ERROR: subcall count exceeds limit of {MAX_SUBCALLS}", file=sys.stderr)
                    sys.exit(1)
                entry = {
                    "batch": batch_id,
                    "prompt_file": item.get('file'),
                    "slice_start": item.get('start'),
                    "slice_end": item.get('end'),
                    "kw": item.get('kw',''),
                    "action": ALLOWED_ACTION
                }
                f.write(json.dumps(entry) + "\n")

    print(json.dumps({"out": args.out, "batches": batch_id}, indent=2))

if __name__ == '__main__':
    main()
