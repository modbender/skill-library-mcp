import json
import sys
from pathlib import Path

root = Path(__file__).parent
files = list(root.rglob("*.json"))

ok, failed = 0, []

for f in files:
    try:
        text = f.read_text(encoding="utf-8")
        data = json.loads(text)
        formatted = json.dumps(data, indent=2, ensure_ascii=False)
        if formatted != text:
            f.write_text(formatted + "\n", encoding="utf-8")
            print(f"formatted: {f.relative_to(root)}")
        else:
            print(f"already ok: {f.relative_to(root)}")
        ok += 1
    except Exception as e:
        print(f"ERROR: {f.relative_to(root)} — {e}", file=sys.stderr)
        failed.append(f)

print(f"\n{ok} file(s) processed, {len(failed)} error(s).")
