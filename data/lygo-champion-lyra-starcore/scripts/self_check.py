"""Self-check for the LYGO Champion: LYRA skill pack.

Purpose: quick deterministic validation that the pack is internally consistent.
Does NOT contact network services.

Usage:
  python scripts/self_check.py

Exit codes:
  0 = OK
  2 = missing/invalid canon
  3 = missing required files
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQ = [
    ROOT / "SKILL.md",
    ROOT / "references" / "canon.json",
    ROOT / "references" / "persona_pack.md",
    ROOT / "references" / "verifier_usage.md",
]

missing = [str(p) for p in REQ if not p.exists()]
if missing:
    print("MISSING_FILES:")
    for m in missing:
        print(" -", m)
    raise SystemExit(3)

canon_path = ROOT / "references" / "canon.json"
canon = json.loads(canon_path.read_text(encoding="utf-8"))

if canon.get("champion") != "LYRA":
    print("BAD_CANON: champion != LYRA")
    raise SystemExit(2)

h = canon.get("lygo_mint_sha256")
if not isinstance(h, str) or len(h) != 64:
    print("BAD_CANON: lygo_mint_sha256 missing/invalid")
    raise SystemExit(2)

# quick sanity on verifier link presence
vu = (ROOT / "references" / "verifier_usage.md").read_text(encoding="utf-8", errors="replace")
if "https://clawhub.ai/DeepSeekOracle/lygo-mint-verifier" not in vu:
    print("BAD_REF: verifier link missing")
    raise SystemExit(2)

print("OK")
print("HASH", h)
