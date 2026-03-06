"""setup.py - One-shot installer for handsfree-windows.

This script is run automatically by the agent on first use of the skill.
It installs the handsfree-windows CLI and (optionally) Playwright browsers.

It is safe to run multiple times (idempotent).

Usage:
    python scripts/setup.py [--no-browser] [--install-dir <path>]

Flags:
    --no-browser     Skip Playwright browser download (~200 MB)
    --install-dir    Where to clone the repo (default: ~/.handsfree-windows/cli)

What this script does (transparent):
    1. Clones https://github.com/lijinlar/handsfree-windows.git
       into --install-dir (default: ~/.handsfree-windows/cli/)
    2. Runs: pip install -e <install-dir>
    3. (Unless --no-browser) runs: python -m playwright install chromium
    4. Runs check_setup.py to verify the result

Data written to disk:
    - Source code    : <install-dir>  (default ~/.handsfree-windows/cli)
    - pip editable   : site-packages/handsfree-windows.egg-link (standard pip)
    - Browser bins   : ~/.handsfree-windows/browser-profiles/ (only if browser installed)
    - Playwright bins: platform default (~AppData/Local/ms-playwright on Windows, ~800 MB)

Nothing is sent over the network except:
    - git clone from github.com/lijinlar/handsfree-windows (public repo, read-only)
    - pip dependencies from pypi.org
    - Playwright browser binaries from cdn.playwright.dev (only if --no-browser is NOT set)
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_URL = "https://github.com/lijinlar/handsfree-windows.git"
DEFAULT_INSTALL_DIR = Path.home() / ".handsfree-windows" / "cli"


def run(cmd: list[str], cwd: Path | None = None, desc: str = "") -> int:
    print(f"\n>>> {desc or ' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(cwd) if cwd else None)
    if result.returncode != 0:
        print(f"[ERROR] Command failed (exit {result.returncode}): {' '.join(cmd)}")
    return result.returncode


def is_installed() -> bool:
    """Check if handsfree_windows package is importable."""
    import importlib.util

    return importlib.util.find_spec("handsfree_windows") is not None


def clone_or_pull(install_dir: Path) -> bool:
    if (install_dir / ".git").exists():
        print(f"\n[INFO] Repo already exists at {install_dir}. Pulling latest...")
        rc = run(["git", "pull", "--ff-only"], cwd=install_dir, desc="git pull")
    else:
        print(f"\n[INFO] Cloning handsfree-windows into {install_dir} ...")
        install_dir.parent.mkdir(parents=True, exist_ok=True)
        rc = run(
            ["git", "clone", REPO_URL, str(install_dir)],
            desc=f"git clone {REPO_URL}",
        )
    return rc == 0


def pip_install(install_dir: Path) -> bool:
    print(f"\n[INFO] Installing handsfree-windows (editable) from {install_dir} ...")
    rc = run(
        [sys.executable, "-m", "pip", "install", "-e", str(install_dir)],
        desc="pip install -e",
    )
    return rc == 0


def install_playwright_chromium() -> bool:
    print("\n[INFO] Installing Playwright + Chromium browser (~200 MB download, one-time) ...")
    # Ensure playwright Python package is installed first
    rc = run(
        [sys.executable, "-m", "pip", "install", "playwright"],
        desc="pip install playwright",
    )
    if rc != 0:
        return False
    rc = run(
        [sys.executable, "-m", "playwright", "install", "chromium"],
        desc="playwright install chromium",
    )
    return rc == 0


def run_check(script_dir: Path) -> None:
    check = script_dir / "check_setup.py"
    if check.exists():
        print("\n[INFO] Running environment check ...")
        subprocess.run([sys.executable, str(check)])
    else:
        print("\n[WARN] check_setup.py not found, skipping verification.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Install handsfree-windows CLI")
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Skip Playwright browser download (~200 MB). Browser commands will not work.",
    )
    parser.add_argument(
        "--install-dir",
        type=Path,
        default=DEFAULT_INSTALL_DIR,
        help=f"Where to clone the repo (default: {DEFAULT_INSTALL_DIR})",
    )
    args = parser.parse_args()

    install_dir: Path = args.install_dir.expanduser().resolve()

    print("=" * 50)
    print("handsfree-windows setup")
    print("=" * 50)
    print(f"Install dir : {install_dir}")
    print(f"Browser     : {'skipped (--no-browser)' if args.no_browser else 'chromium (~200 MB download)'}")
    print()

    # Step 1: Clone or update repo
    if not clone_or_pull(install_dir):
        print("\n[ERROR] Failed to clone/pull repo. Check git is installed and you have internet access.")
        return 1

    # Step 2: pip install -e
    if not pip_install(install_dir):
        print("\n[ERROR] pip install failed.")
        return 1

    # Step 3: Playwright (optional)
    if not args.no_browser:
        if not install_playwright_chromium():
            print(
                "\n[WARN] Playwright browser install failed. "
                "Browser commands will not work. "
                "Retry manually: python -m playwright install chromium"
            )
    else:
        print(
            "\n[SKIP] Browser install skipped. "
            "Run later with: python -m playwright install chromium"
        )

    # Step 4: Verify
    script_dir = Path(__file__).parent
    run_check(script_dir)

    print("\n[DONE] handsfree-windows is ready.")
    print(f"  CLI source  : {install_dir}")
    print("  Run 'hf --help' to see all commands.")
    if args.no_browser:
        print("  Browser commands require: python -m playwright install chromium")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
