#!/usr/bin/env python3
import json, subprocess, sys

def main():
    # ожидаем: query [limit]
    if len(sys.argv) < 2:
        print(json.dumps({"error": "usage: run.py <query> [limit]"}))
        sys.exit(1)

    query = sys.argv[1]
    limit = sys.argv[2] if len(sys.argv) >= 3 else "10"

    p = subprocess.run(
        ["/usr/local/bin/tg_search", query, limit],
        capture_output=True,
        text=True
    )

    if p.returncode != 0:
        print(json.dumps({"error": "tg_search failed", "stderr": p.stderr.strip()}))
        sys.exit(p.returncode)

    # stdout already JSON
    out = p.stdout.strip()
    # sanity check
    try:
        json.loads(out)
    except Exception:
        print(json.dumps({"error": "invalid JSON from tg_search", "stdout": out[:500]}))
        sys.exit(1)

    print(out)

if __name__ == "__main__":
    main()
