#!/usr/bin/env python3
from __future__ import annotations

"""Thin wrapper for running skill-deps-doctor from ClawHub skill context.

Behavior:
- Prefer vendored package inside the installed skill folder: <skill>/vendor/skill_deps_doctor
- If running inside this repository, add repo root to sys.path.
- Otherwise, rely on installed package (`pip install skill-deps-doctor` or git URL).
- On import failure, print actionable install commands.
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve()


def _inject_repo_root_if_present() -> None:
    # 1) Prefer vendored package inside the installed skill folder
    skill_dir = HERE.parents[1]
    vendor_dir = skill_dir / "vendor"
    if (vendor_dir / "skill_deps_doctor").is_dir():
        sys.path.insert(0, str(vendor_dir))
        return

    # 2) Repo mode
    for candidate in (HERE.parents[3], HERE.parents[2], Path.cwd()):
        pkg_dir = candidate / "skill_deps_doctor"
        if pkg_dir.is_dir():
            sys.path.insert(0, str(candidate))
            return


_inject_repo_root_if_present()

try:
    from skill_deps_doctor.cli import main  # type: ignore[attr-defined]  # noqa: E402
except Exception as e:
    msg = (
        "Unable to import skill_deps_doctor.\n"
        "Fix options:\n"
        "  1) Ensure vendored code exists at: {baseDir}/vendor/skill_deps_doctor\n"
        "  2) Or install via pip: pip install skill-deps-doctor\n"
        '  3) Or install via git: pip install "git+https://github.com/RangeKing/skill-deps-doctor.git"\n'
        f"Import error: {e}"
    )
    print(msg, file=sys.stderr)
    raise SystemExit(2) from e


if __name__ == "__main__":
    raise SystemExit(main())
