"""check_setup.py - Validate handsfree-windows environment.

Checks all prerequisites WITHOUT installing anything.
Run this before using any handsfree-windows commands.

Usage:
    python scripts/check_setup.py
"""

from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path


def ok(msg: str) -> None:
    print(f"  [OK] {msg}")


def fail(msg: str, fix: str = "") -> None:
    print(f"  [MISSING] {msg}")
    if fix:
        print(f"         Fix: {fix}")


def warn(msg: str) -> None:
    print(f"  [WARN] {msg}")


def check_python() -> bool:
    v = sys.version_info
    if v >= (3, 10):
        ok(f"Python {v.major}.{v.minor}.{v.micro}")
        return True
    fail(f"Python {v.major}.{v.minor} (need 3.10+)", "Upgrade Python to 3.10 or newer")
    return False


def check_package(import_name: str, pip_name: str) -> bool:
    spec = importlib.util.find_spec(import_name)
    if spec is not None:
        ok(f"{import_name} installed")
        return True
    fail(f"{import_name} not found", f"pip install {pip_name}")
    return False


def check_hf_cli() -> bool:
    """Check if the handsfree-windows CLI is importable."""
    spec = importlib.util.find_spec("handsfree_windows")
    if spec is not None:
        ok("handsfree_windows package found")
        return True
    fail(
        "handsfree_windows package not found",
        "git clone git@github.com:lijinlar/handsfree-windows.git && pip install -e handsfree-windows",
    )
    return False


def check_playwright_browsers() -> None:
    """Check if Playwright browser binaries are downloaded (optional)."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "playwright", "install", "--dry-run"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        # If chromium is installed, playwright won't print a download prompt
        # This is a best-effort check.
        ok("Playwright accessible via python -m playwright")
    except FileNotFoundError:
        fail("playwright CLI not found", "pip install playwright")
        return

    # Check known binary paths (Windows)
    ms_pw = Path.home() / "AppData" / "Local" / "ms-playwright"
    if ms_pw.exists():
        engines = [d.name for d in ms_pw.iterdir() if d.is_dir()]
        ok(f"Playwright browser binaries at {ms_pw}: {engines}")
    else:
        warn(
            "Playwright browser binaries not found (browser commands will fail). "
            "Run: python -m playwright install chromium"
        )


def check_state_paths() -> None:
    """Report on all persistent state paths used by this skill."""
    base = Path.home() / ".handsfree-windows"
    print()
    print("  Persistent state paths:")
    profile_dir = base / "browser-profiles"
    state_file = base / "browser-state.json"

    if profile_dir.exists():
        engines = [d.name for d in profile_dir.iterdir() if d.is_dir()]
        print(f"    Browser profiles : {profile_dir} ({engines})")
    else:
        print(f"    Browser profiles : {profile_dir} (not yet created)")

    if state_file.exists():
        print(f"    Browser state    : {state_file} (exists)")
    else:
        print(f"    Browser state    : {state_file} (not yet created)")

    ms_pw = Path.home() / "AppData" / "Local" / "ms-playwright"
    if ms_pw.exists():
        size_mb = sum(f.stat().st_size for f in ms_pw.rglob("*") if f.is_file()) // (1024 * 1024)
        print(f"    Playwright bins  : {ms_pw} (~{size_mb} MB)")
    else:
        print(f"    Playwright bins  : {ms_pw} (not installed)")


def main() -> int:
    print("handsfree-windows environment check")
    print("=" * 40)

    all_ok = True

    print()
    print("[1] Python version")
    all_ok &= check_python()

    print()
    print("[2] Core CLI")
    all_ok &= check_hf_cli()

    print()
    print("[3] Core Python dependencies")
    for imp, pip in [
        ("pywinauto", "pywinauto"),
        ("typer", "typer"),
        ("rich", "rich"),
        ("yaml", "pyyaml"),
        ("pyperclip", "pyperclip"),
    ]:
        all_ok &= check_package(imp, pip)

    print()
    print("[4] Browser automation (optional - needed for browser-* commands)")
    check_package("playwright", "playwright")
    check_playwright_browsers()

    check_state_paths()

    print()
    print("=" * 40)
    if all_ok:
        print("Core setup looks good. Browser commands require Playwright (see [4]).")
        return 0
    else:
        print("Some prerequisites are missing. See fixes above.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
