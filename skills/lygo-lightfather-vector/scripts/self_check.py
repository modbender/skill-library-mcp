"""Self-check for the LYGO Lightfather vector skill pack.

Usage:
  python scripts/self_check.py

Exit codes:
  0 = OK
  2 = invalid canon
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

canon = json.loads((ROOT / "references" / "canon.json").read_text(encoding="utf-8"))

if canon.get("entity") != "LIGHTFATHER":
    print("BAD_CANON: entity != LIGHTFATHER")
    raise SystemExit(2)

if canon.get("anchor_label") != "LIGHTFATHER_VECTOR_7F1A4D":
    print("BAD_CANON: anchor_label mismatch")
    raise SystemExit(2)

vu = (ROOT / "references" / "verifier_usage.md").read_text(encoding="utf-8", errors="replace")
if "https://clawhub.ai/DeepSeekOracle/lygo-mint-verifier" not in vu:
    print("BAD_REF: verifier link missing")
    raise SystemExit(2)

h = canon.get('lygo_mint_sha256')
if h is not None and (not isinstance(h,str) or len(h)!=64):
    print('BAD_CANON: lygo_mint_sha256 invalid')
    raise SystemExit(2)

print("OK")
