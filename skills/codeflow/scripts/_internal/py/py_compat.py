"""Python version compatibility helpers for Codeflow.

Keep this module syntax compatible with Python 3.8+ so it can emit a readable
error message instead of a SyntaxError on older interpreters.
"""

from __future__ import annotations

import os
import sys
from typing import Iterable, Optional, Sequence, Tuple


MIN_PYTHON: Tuple[int, int] = (3, 10)


def _version_tuple(v: Sequence[int]) -> Tuple[int, int, int]:
    major = int(v[0]) if len(v) > 0 else 0
    minor = int(v[1]) if len(v) > 1 else 0
    micro = int(v[2]) if len(v) > 2 else 0
    return major, minor, micro


def _prog_name(default: str = "codeflow") -> str:
    return (os.path.basename(sys.argv[0]) or default).strip() or default


def is_python_supported(
    version_info: Optional[Sequence[int]] = None, *, min_version: Tuple[int, int] = MIN_PYTHON
) -> bool:
    v = _version_tuple(version_info or sys.version_info)
    return (v[0], v[1]) >= tuple(min_version)


def require_python310(*, prog: Optional[str] = None, version_info: Optional[Sequence[int]] = None) -> None:
    if is_python_supported(version_info):
        return

    v = _version_tuple(version_info or sys.version_info)
    want = f"{MIN_PYTHON[0]}.{MIN_PYTHON[1]}"
    got = f"{v[0]}.{v[1]}.{v[2]}"
    p = prog or _prog_name()

    sys.stderr.write(
        f"❌ Error: {p} requires Python >= {want} (found {got}).\n"
        "   Fix: install a newer python3 and ensure `python3` points to it.\n"
    )
    raise SystemExit(2)
