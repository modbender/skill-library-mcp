"""Bootstrap sys.path for the packaged skill."""

from __future__ import annotations

import sys
from pathlib import Path


def ensure_pkg_on_path() -> None:
    """Add ../pkg to sys.path so skill_health can be imported."""
    pkg_root = Path(__file__).resolve().parents[1] / "pkg"
    if str(pkg_root) not in sys.path:
        sys.path.insert(0, str(pkg_root))
