#!/usr/bin/env python3
"""
Brain CMS — REM Sleep Cycle
Weekly deep consolidation using local Ollama LLM. Zero API cost.

Trigger: Weekly (Sunday evenings), confirm before running, or "run REM cycle"
Runtime: 2-5 minutes.
"""

import json, datetime, requests, subprocess, sys
from pathlib import Path

WORKSPACE   = Path(__file__).parent.parent
MEMORY_DIR  = WORKSPACE / "memory"
BRAIN_DIR   = Path(__file__).parent
LOG_FILE    = BRAIN_DIR / "sleep_log.json"
OLLAMA_URL  = "http://localhost:11434/api/generate"
REM_MODEL   = "llama3.2:3b"

def get_schema_files() -> dict[str, Path]:
    """Auto-detect schema files → {domain_name: path}"""
    schemas = {}
    for p in MEMORY_DIR.rglob("*.md"):
        name = p.name
        if name[0].isdigit() or name in ("INDEX.md", "ANCHORS.md"): continue
        domain = p.stem.lower().replace("-", "_")
        schemas[domain] = p
    return schemas

def load_weekly_logs() -> str:
    parts = []
    for i in range(7):
        day  = datetime.datetime.now() - datetime.timedelta(days=i)
        path = MEMORY_DIR / f"{day.strftime('%Y-%m-%d')}.md"
        if path.exists():
            parts.append(f"\n## {day.strftime('%Y-%m-%d')}\n{path.read_text(encoding='utf-8')}")
    return "\n".join(reversed(parts))

def ollama_generate(prompt: str, max_tokens: int = 600) -> str:
    try:
        r = requests.post(OLLAMA_URL, json={"model": REM_MODEL, "prompt": prompt,
            "stream": False, "options": {"num_predict": max_tokens, "temperature": 0.3}}, timeout=120)
        r.raise_for_status()
        return r.json().get("response", "").strip()
    except Exception as e:
        print(f"[REM] Ollama error: {e}")
        return ""

def extract_updates(weekly_logs: str, domains: list[str]) -> dict:
    domain_list = ", ".join(f'"{d}"' for d in domains)
    prompt = f"""You are a memory consolidation system. Read the week's logs and extract NEW factual updates per domain.

Output ONLY valid JSON with keys: {{{domain_list}}}
Each value: list of short factual strings (max 15 words). Empty list [] if nothing new.
Only include genuinely new facts, decisions, or status changes — not general knowledge.

LOGS:
{weekly_logs[:4000]}

JSON:"""
    response = ollama_generate(prompt)
    try:
        start, end = response.find("{"), response.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(response[start:end])
    except Exception as e:
        print(f"[REM] Parse error: {e}")
    return {}

def reindex():
    venv_py = BRAIN_DIR / ".venv" / "bin" / "python3"
    python  = str(venv_py) if venv_py.exists() else sys.executable
    try:
        r = subprocess.run([python, str(BRAIN_DIR / "index_memory.py")],
                          capture_output=True, text=True, timeout=180)
        print("[REM] Vector store re-indexed ✅" if r.returncode == 0
              else f"[REM] Indexer error: {r.stderr[:100]}")
    except Exception as e: print(f"[REM] Indexer failed: {e}")

def log_run(stats: dict):
    runs = []
    if LOG_FILE.exists():
        try: runs = json.loads(LOG_FILE.read_text())
        except: runs = []
    LOG_FILE.write_text(json.dumps(runs[-29:] + [stats], indent=2))

def main():
    print("\n🌙 REM Sleep Cycle starting...")
    print("   Using local Ollama — zero API cost\n")
    start = datetime.datetime.now()
    date_str = start.strftime("%Y-%m-%d")
    stats = {"date": date_str, "type": "rem", "domains_updated": 0, "total_updates": 0}

    weekly_logs = load_weekly_logs()
    if not weekly_logs:
        print("[REM] No daily logs found. Nothing to consolidate.")
        return
    print(f"[REM] Loaded weekly logs ({len(weekly_logs)} chars)")

    schemas = get_schema_files()
    if not schemas:
        print("[REM] No schema files found. Create some in memory/.")
        return

    print(f"[REM] Synthesizing {len(schemas)} domains with {REM_MODEL}...")
    updates = extract_updates(weekly_logs, list(schemas.keys()))

    for domain, new_facts in updates.items():
        if not new_facts: continue
        schema_path = schemas.get(domain)
        if not schema_path: continue
        section = f"\n\n## REM Update — {date_str}\n" + "".join(f"- {f}\n" for f in new_facts[:10])
        with open(schema_path, "a", encoding="utf-8") as f: f.write(section)
        print(f"[REM] {domain}: {len(new_facts)} new facts")
        stats["domains_updated"] += 1
        stats["total_updates"] += len(new_facts)

    reindex()

    stats["elapsed_seconds"] = (datetime.datetime.now() - start).seconds
    log_run(stats)
    print(f"\n✅ REM complete in {stats['elapsed_seconds']}s")
    print(f"   Domains: {stats['domains_updated']} | New facts: {stats['total_updates']}")
    print("   Memory consolidated. Good morning. 🌅\n")

if __name__ == "__main__":
    main()
