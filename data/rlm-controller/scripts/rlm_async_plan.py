#!/usr/bin/env python3
"""Generate an async subcall execution plan from plan.json.
This does not execute subcalls; it outputs a JSON plan with suggested parallel batches.

Usage:
  rlm_async_plan.py --plan <plan.json> --batch-size 4
"""
import argparse, json, os, sys
from rlm_path import validate_path as _validate_path

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--plan', required=True)
    p.add_argument('--batch-size', type=int, default=4)
    args = p.parse_args()

    rp = _validate_path(args.plan)
    with open(rp, 'r', encoding='utf-8') as f:
        plan = json.load(f)

    prompts = plan.get('subcall_prompts', [])
    batches = [prompts[i:i+args.batch_size] for i in range(0, len(prompts), args.batch_size)]

    out = {
        "ctx": plan.get("ctx"),
        "goal": plan.get("goal"),
        "batch_size": args.batch_size,
        "batches": batches,
        "notes": "Execute each batch in parallel with sessions_spawn; aggregate results in root controller."
    }
    print(json.dumps(out, indent=2))

if __name__ == '__main__':
    main()
