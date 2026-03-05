from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional


_DEFAULT_ROOTS = ("~/.researchvault", "/tmp")


def _resolve_abs_path(raw: str) -> Optional[Path]:
    cleaned = (raw or "").strip()
    if not cleaned:
        return None
    expanded = os.path.expanduser(cleaned)
    p = Path(expanded)
    if not p.is_absolute():
        return None
    try:
        return p.resolve()
    except Exception:
        return None


def default_allowed_db_roots() -> List[Path]:
    out: List[Path] = []
    for raw in _DEFAULT_ROOTS:
        rp = _resolve_abs_path(raw)
        if rp and rp not in out:
            out.append(rp)
    return out


def allowed_db_roots() -> List[Path]:
    raw = os.getenv("RESEARCHVAULT_PORTAL_ALLOWED_DB_ROOTS", "")
    if not raw.strip():
        return default_allowed_db_roots()

    out: List[Path] = []
    for item in raw.split(","):
        rp = _resolve_abs_path(item)
        if rp and rp not in out:
            out.append(rp)

    return out or default_allowed_db_roots()


def allowed_db_roots_as_strings() -> List[str]:
    return [str(p) for p in allowed_db_roots()]


def path_within_allowed_roots(path: Path) -> bool:
    try:
        rp = path.resolve()
    except Exception:
        return False

    for root in allowed_db_roots():
        if rp == root or str(rp).startswith(str(root) + os.sep):
            return True
    return False
