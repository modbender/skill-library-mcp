"""Output path sanitisation for BrickLink scripts.

Ensures output files stay within the workspace root or /tmp.
"""

import os
from pathlib import Path


def _find_workspace_root() -> Path:
    """Walk up from CWD (or OPENCLAW_WORKSPACE) to find workspace root."""
    env = os.environ.get("OPENCLAW_WORKSPACE")
    if env:
        return Path(env).expanduser().resolve()

    cwd = Path.cwd()
    if (cwd / "skills").is_dir():
        return cwd

    d = Path(__file__).resolve().parent
    for _ in range(6):
        if (d / "skills").is_dir() and d != d.parent:
            return d
        d = d.parent
    return cwd


_ALLOWED_ROOTS: list[Path] | None = None


def _get_allowed_roots() -> list[Path]:
    global _ALLOWED_ROOTS
    if _ALLOWED_ROOTS is None:
        _ALLOWED_ROOTS = [
            _find_workspace_root(),
            Path("/tmp").resolve(),
            Path(os.environ.get("TMPDIR", "/tmp")).resolve(),
        ]
    return _ALLOWED_ROOTS


def safe_output_path(raw: str) -> Path:
    """Resolve an output path and verify it's under an allowed root.

    Allowed roots: workspace directory, /tmp, $TMPDIR.
    Raises ValueError if the resolved path escapes all allowed roots.
    """
    p = Path(raw).expanduser().resolve()
    for root in _get_allowed_roots():
        try:
            if p == root or p.is_relative_to(root):
                return p
        except AttributeError:
            if str(p).startswith(str(root) + "/") or p == root:
                return p

    roots_str = ", ".join(str(r) for r in _get_allowed_roots())
    raise ValueError(
        f"Output path '{raw}' resolves to '{p}' which is outside allowed directories: {roots_str}"
    )
