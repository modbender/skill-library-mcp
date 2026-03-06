#!/usr/bin/env python3
"""
Brain CMS — NREM Sleep Cycle
Fast nightly compression. No LLM required. Run on shutdown.

Trigger: user says "good night", "shutting down", "heading off"
Runtime: ~15-30 seconds.
"""

import json, datetime, subprocess, sys
from pathlib import Path

WORKSPACE   = Path(__file__).parent.parent
MEMORY_DIR  = WORKSPACE / "memory"
BRAIN_DIR   = Path(__file__).parent
LOG_FILE    = BRAIN_DIR / "sleep_log.json"

def today_str():    return datetime.datetime.now().strftime("%Y-%m-%d")
def yesterday_str():
    return (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

def extract_anchors(text: str) -> list[str]:
    return [l.replace("[ANCHOR]", "").strip()
            for l in text.split("\n") if "[ANCHOR]" in l and l.replace("[ANCHOR]","").strip()]

def promote_anchors(anchors: list[str], date_str: str) -> int:
    if not anchors: return 0
    path = MEMORY_DIR / "ANCHORS.md"
    if not path.exists(): return 0
    existing = path.read_text(encoding="utf-8")
    new_entries = [f"\n### {date_str} | Auto-promoted | {a}\nStatus: Active\n"
                   for a in anchors if a[:40] not in existing]
    if new_entries:
        with open(path, "a") as f: f.write("\n".join(new_entries))
    return len(new_entries)

def compress_log(text: str) -> str:
    lines, prev_blank = [], False
    for line in text.split("\n"):
        if line.strip() == "":
            if prev_blank: continue
            prev_blank = True
        else:
            prev_blank = False
        lines.append(line)
    return "\n".join(lines)

def reindex():
    venv_py = BRAIN_DIR / ".venv" / "bin" / "python3"
    python  = str(venv_py) if venv_py.exists() else sys.executable
    try:
        r = subprocess.run([python, str(BRAIN_DIR / "index_memory.py")],
                          capture_output=True, text=True, timeout=120)
        print("[NREM] Vector store re-indexed ✅" if r.returncode == 0
              else f"[NREM] Indexer error: {r.stderr[:100]}")
    except Exception as e: print(f"[NREM] Indexer failed: {e}")

def log_run(stats: dict):
    runs = []
    if LOG_FILE.exists():
        try: runs = json.loads(LOG_FILE.read_text())
        except: runs = []
    LOG_FILE.write_text(json.dumps(runs[-29:] + [stats], indent=2))

def main():
    print("\n💤 NREM Sleep Cycle starting...")
    start = datetime.datetime.now()
    stats = {"date": today_str(), "type": "nrem", "anchors_promoted": 0, "logs_processed": 0}

    for d in [today_str(), yesterday_str()]:
        path = MEMORY_DIR / f"{d}.md"
        if not path.exists(): continue
        text = path.read_text(encoding="utf-8")
        stats["logs_processed"] += 1
        stats["anchors_promoted"] += promote_anchors(extract_anchors(text), d)
        compressed = compress_log(text)
        if len(compressed) < len(text):
            path.write_text(compressed, encoding="utf-8")
            print(f"[NREM] Compressed {d}.md ({len(text)}→{len(compressed)} chars)")

    reindex()
    stats["elapsed_seconds"] = (datetime.datetime.now() - start).seconds
    log_run(stats)

    print(f"\n✅ NREM complete in {stats['elapsed_seconds']}s")
    print(f"   Logs: {stats['logs_processed']} | Anchors: {stats['anchors_promoted']}")
    print("   Sweet dreams 🌙\n")

if __name__ == "__main__":
    main()
