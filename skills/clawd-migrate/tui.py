"""
Interactive terminal UI for clawd_migrate.
Shows a lobster on load and guides users through discover -> backup -> migrate.
Works for moltbot or clawdbot on any user's system.
"""

import json
import os
import sys
from pathlib import Path

from . import create_backup, discover_source_assets, run_migration
from .openclaw_setup import install_openclaw_and_onboard

# ANSI codes (Windows Terminal, PowerShell 7+, macOS Terminal, Linux)
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
MAGENTA = "\033[35m"
RED = "\033[31m"


def style(s: str, *codes: str) -> str:
    return "".join(codes) + s + RESET


# ASCII lobster (side view); raw string so backslashes display correctly
LOBSTER_LINES = r"""
                             ,.---._
                   ,,,,     /       `,
                    \\\\   /    '\_  ;
                     |||| /\/``-.__\;'
                     ::::/\/_
     {{`-.__.-'(`(^^(^^^(^ 9 `.========='
    {{{{{{ { ( ( (  (   (-----:=
     {{.-'~~'-.(,(,,(,,,(__6_.'=========.
                     ::::\/\
                     |||| \/\  ,-'/,
                    ////   \ `` _/ ;
                   ''''     \  `  .'
                             `---'
"""


def print_banner() -> None:
    """Print the lobster ASCII art and welcome message."""
    print()
    for line in LOBSTER_LINES.splitlines():
        if not line.strip():
            print()
            continue
        print(style(line, RED))
    print(style("  Migrate from moltbot or clawdbot to openclaw safely  ", BOLD, CYAN))
    print(style("  Discover -> Backup -> Migrate  ", DIM))
    print()


def get_root() -> Path:
    """Prompt for root path or use cwd."""
    cwd = Path(os.getcwd()).resolve()
    print(style(f"  Working directory: {cwd}", DIM))
    raw = input(style("  Use this directory? [Y/n] or enter a path: ", YELLOW)).strip()
    if not raw or raw.lower() == "y" or raw.lower() == "yes":
        return cwd
    p = Path(raw).expanduser().resolve()
    if not p.is_dir():
        print(style(f"  Not a directory: {p}", RED))
        return cwd
    return p


def do_discover(root: Path) -> None:
    """Run discover and print results in a readable way."""
    print(style("\n  Discovering assets (moltbot / clawdbot)...\n", CYAN))
    assets = discover_source_assets(root)
    print(style("  Root: ", DIM) + assets["root"])
    for key in ("memory", "config", "clawdbook", "extra"):
        items = assets.get(key, [])
        label = key.capitalize()
        print(style(f"  {label}: {len(items)} item(s)", GREEN if items else DIM))
        for path in items[:10]:
            print(style("    ", DIM) + path)
        if len(items) > 10:
            print(style(f"    ... and {len(items) - 10} more", DIM))
    print()
    if input(style("  Show full JSON? [y/N]: ", YELLOW)).strip().lower() == "y":
        print(json.dumps(assets, indent=2))
    print()


def do_backup(root: Path) -> None:
    """Create a timestamped backup."""
    print(style("\n  Creating backup...\n", CYAN))
    try:
        path = create_backup(root=root)
        print(style(f"  Backup created: {path}", GREEN))
    except Exception as e:
        print(style(f"  Error: {e}", RED))
    print()


def print_verification(verification: dict) -> None:
    """Display verification results in a clear, readable format."""
    if verification is None:
        print(style("  Verification: skipped", DIM))
        return
    total = verification["total_expected"]
    verified = verification["total_verified"]
    missing = verification["missing"]
    errors = verification["errors"]

    if verification["passed"]:
        print(style(f"\n  Verification PASSED: {verified}/{total} files confirmed", BOLD, GREEN))
    else:
        print(style(f"\n  Verification FAILED: {verified}/{total} files confirmed", BOLD, RED))

    # Show verified files
    if verification["verified"]:
        print(style("  Verified files:", GREEN))
        for entry in verification["verified"]:
            name = Path(entry["destination"]).name
            ftype = entry["type"]
            size_ok = entry.get("size_match", None)
            size_str = " (size OK)" if size_ok else (" (size MISMATCH)" if size_ok is False else "")
            print(style(f"    [{ftype}] {name}{size_str}", GREEN))

    # Show missing files
    if missing:
        print(style("  MISSING files:", RED))
        for entry in missing:
            src_name = Path(entry["source"]).name
            dest = entry["destination"]
            ftype = entry["type"]
            print(style(f"    [{ftype}] {src_name} -> expected at {dest}", RED))

    # Show cross-check errors
    if errors:
        print(style("  Verification errors:", RED))
        for e in errors:
            print(style(f"    {e}", RED))


def do_migrate(root: Path, no_backup: bool) -> None:
    """Run migration with verification, then reinstall openclaw and run onboard."""
    if not no_backup:
        print(style("  Migration will create a backup first.", DIM))
    else:
        print(style("  Skipping backup (--no-backup).", YELLOW))
    confirm = input(style("  Proceed with migration? [y/N]: ", YELLOW)).strip().lower()
    if confirm != "y" and confirm != "yes":
        print(style("  Cancelled.", DIM))
        return
    print(style("\n  Migrating...\n", CYAN))
    result = run_migration(root=root, backup_first=not no_backup, output_root=None, verify=True)
    out_root = root
    if result["backup_path"]:
        print(style(f"  Backup: {result['backup_path']}", GREEN))
    print(style(f"  Memory copied: {len(result['memory_copied'])} files", GREEN))
    print(style(f"  Config copied: {len(result['config_copied'])} files", GREEN))
    print(style(f"  Clawdbook (safe): {len(result['clawdbook_copied'])} files", GREEN))

    if result["errors"]:
        print(style("  Migration errors:", RED))
        for e in result["errors"]:
            print(style(f"    {e}", RED))

    # --- Verification ---
    verification = result.get("verification")
    print_verification(verification)

    if verification and not verification["passed"]:
        print(style("\n  Migration completed with issues. Check the missing files above.", YELLOW))
        retry = input(style("  Continue with openclaw reinstall anyway? [y/N]: ", YELLOW)).strip().lower()
        if retry != "y" and retry != "yes":
            print(style("  Skipping openclaw setup. Fix missing files and re-run.", DIM))
            print()
            return

    if not result["errors"] or (verification and verification["passed"]):
        print(style("\n  Migration complete.", BOLD, GREEN))
        print(style("  Your files are in the openclaw layout (memory/, .config/openclaw/, .config/clawdbook/).", DIM))

    # --- Always reinstall openclaw ---
    print(style("\n  Reinstalling openclaw (npm i -g openclaw)...", CYAN))
    print(style("  This ensures you have the latest version.\n", DIM))
    setup_result = install_openclaw_and_onboard(out_root)
    if setup_result["install_ok"]:
        print(style(f"  {setup_result['install_message']}", GREEN))
    else:
        print(style(f"  Install: {setup_result['install_message']}", RED))
    if setup_result["onboard_ok"]:
        print(style(f"  {setup_result['onboard_message']}", GREEN))
    else:
        print(style(f"  Onboard: {setup_result['onboard_message']}", RED))
    if setup_result["errors"]:
        for e in setup_result["errors"]:
            print(style(f"    {e}", RED))
    elif setup_result["install_ok"] and setup_result["onboard_ok"]:
        print(style("\n  Openclaw is installed and this directory is onboarded.", BOLD, GREEN))
        if verification and verification["passed"]:
            print(style("  All files verified. Migration is complete!", BOLD, GREEN))
    print()


def main_menu(root: Path) -> bool:
    """Show main menu; return False to exit."""
    print(style("  [1] Discover assets (config, memory, clawdbook)", CYAN))
    print(style("  [2] Create backup only (no migration)", CYAN))
    print(style("  [3] Run full migration (backup first, then migrate)", CYAN))
    print(style("  [4] Migrate without backup (not recommended)", YELLOW))
    print(style("  [5] Change working directory", DIM))
    print(style("  [q] Quit", DIM))
    print()
    choice = input(style("  Choose [1-5 / q]: ", BOLD, MAGENTA)).strip().lower()
    if choice == "q" or choice == "quit":
        return False
    if choice == "1":
        do_discover(root)
        return True
    if choice == "2":
        do_backup(root)
        return True
    if choice == "3":
        do_migrate(root, no_backup=False)
        return True
    if choice == "4":
        do_migrate(root, no_backup=True)
        return True
    if choice == "5":
        new_root = get_root()
        return main_menu(new_root)
    print(style("  Unknown option.", RED))
    return True


def run_tui() -> int:
    """Entry point for the interactive TUI. Returns exit code."""
    print_banner()
    root = get_root()
    while main_menu(root):
        pass
    print(style("\n  Bye!\n", DIM))
    return 0
