"""Self-check for LYGO Universal Living Memory Library.

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
    ROOT / 'SKILL.md',
    ROOT / 'references' / 'canon.json',
    ROOT / 'references' / 'library_spec.md',
    ROOT / 'references' / 'core_files_index.json',
    ROOT / 'references' / 'audit_protocol.md',
    ROOT / 'references' / 'compression_protocol.md',
    ROOT / 'scripts' / 'audit_library.py',
]

missing = [str(p) for p in REQ if not p.exists()]
if missing:
    print('MISSING_FILES:')
    for m in missing:
        print(' -', m)
    raise SystemExit(3)

canon = json.loads((ROOT / 'references' / 'canon.json').read_text(encoding='utf-8'))
if canon.get('skill') != 'LYGO_UNIVERSAL_LIVING_MEMORY_LIBRARY':
    print('BAD_CANON: skill mismatch')
    raise SystemExit(2)

print('OK')
