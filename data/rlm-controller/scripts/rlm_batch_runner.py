#!/usr/bin/env python3
"""Batch runner helper (assistant-driven):
Reads toolcall batches JSON (from rlm_emit_toolcalls.py) and outputs
an ordered list of sessions_spawn calls for execution by the OpenClaw agent.

Usage:
  rlm_batch_runner.py --toolcalls <batches.json>
"""
import argparse, json, os, sys
from rlm_path import validate_path as _validate_path

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--toolcalls', required=True)
    args = p.parse_args()

    rp = _validate_path(args.toolcalls)
    with open(rp, 'r', encoding='utf-8') as f:
        batches = json.load(f)

    print("# OpenClaw Batch Runner (assistant-driven)\n")
    print("Execute each batch in parallel using sessions_spawn, then wait for results before the next batch.\n")
    for b in batches:
        print(f"## Batch {b['batch']}")
        for call in b['calls']:
            print(json.dumps(call, indent=2))
        print("\n")

if __name__ == '__main__':
    main()
