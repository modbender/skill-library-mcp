#!/usr/bin/env python3
"""
context_analyzer.py — Scan workspace files for context bloat.
Reports token estimates for all files that load into agent context.
Usage: python3 context_analyzer.py [--workspace /path/to/workspace]
"""
import os, argparse

# Files loaded into context every call (adjust per deployment)
ALWAYS_LOADED = [
    "SOUL.md", "AGENTS.md", "USER.md", "IDENTITY.md",
    "TOOLS.md", "HEARTBEAT.md", "MEMORY.md"
]

CHAR_TO_TOKEN = 4  # rough approximation

def estimate_tokens(path):
    try:
        with open(path, "r", errors="ignore") as f:
            return len(f.read()) // CHAR_TO_TOKEN
    except Exception:
        return 0

def analyze(workspace):
    print(f"\nCONTEXT ANALYZER — {workspace}")
    print(f"{'='*55}")

    total = 0
    print("\n[ Always-Loaded Files ]")
    for fname in ALWAYS_LOADED:
        fpath = os.path.join(workspace, fname)
        tokens = estimate_tokens(fpath)
        total += tokens
        flag = " 🔴 TRIM" if tokens > 1000 else (" ⚠️" if tokens > 500 else "")
        print(f"  {tokens:>6} tokens  {fname}{flag}")

    print(f"\n  SUBTOTAL: {total} tokens  (~${total/1_000_000*3:.4f}/call at Sonnet rates)")

    # Scan memory files
    mem_dir = os.path.join(workspace, "memory")
    if os.path.isdir(mem_dir):
        mem_total = 0
        mem_files = [f for f in os.listdir(mem_dir) if f.endswith(".md") and not os.path.isdir(os.path.join(mem_dir, f))]
        if mem_files:
            print(f"\n[ Daily Memory Files (loaded on demand) ]")
            for f in sorted(mem_files)[-3:]:  # show last 3
                t = estimate_tokens(os.path.join(mem_dir, f))
                mem_total += t
                print(f"  {t:>6} tokens  memory/{f}")

    # Recommendations
    print(f"\n[ Recommendations ]")
    grand = total
    if grand > 3000:
        print(f"  🔴 Total always-loaded context ({grand} tokens) is HIGH.")
        print(f"     Target: <2000 tokens. Archive non-essential content to reference files.")
    elif grand > 1500:
        print(f"  ⚠️  Context ({grand} tokens) above recommended 1500-token target.")
    else:
        print(f"  ✅ Context ({grand} tokens) is within healthy range.")

    for fname in ALWAYS_LOADED:
        fpath = os.path.join(workspace, fname)
        tokens = estimate_tokens(fpath)
        if tokens > 1000:
            print(f"  🔴 {fname} ({tokens} tokens) — move details to reference files")
        elif tokens > 500:
            print(f"  ⚠️  {fname} ({tokens} tokens) — consider trimming")

    print(f"{'='*55}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=os.path.expanduser("~/.openclaw/workspace"))
    args = parser.parse_args()
    analyze(args.workspace)
