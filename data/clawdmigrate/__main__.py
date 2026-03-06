"""
CLI for clawd_migrate. Usage:
  python -m clawd_migrate              # Interactive TUI (lobster + menu)
  python -m clawd_migrate run          # Same as above
  python -m clawd_migrate discover [--root PATH]
  python -m clawd_migrate backup  [--root PATH] [--backup-dir PATH]
  python -m clawd_migrate migrate [--root PATH] [--no-backup] [--output PATH]
"""

import argparse
import json
import os
import sys
from pathlib import Path

from . import create_backup, discover_source_assets, run_migration
from . import __version__
from .openclaw_setup import install_openclaw_and_onboard


def cmd_discover(root: Path) -> int:
    assets = discover_source_assets(root)
    print(json.dumps(assets, indent=2))
    return 0


def cmd_backup(root: Path, backup_dir: Path) -> int:
    path = create_backup(root=root, backup_dir=backup_dir)
    print(f"Backup created: {path}")
    return 0


def cmd_migrate(root: Path, no_backup: bool, output: Path, setup_openclaw: bool, skip_verify: bool) -> int:
    if no_backup:
        print("Warning: --no-backup set; no backup will be created.", file=sys.stderr)
    out_root = output or root
    result = run_migration(
        root=root,
        backup_first=not no_backup,
        output_root=out_root,
        verify=not skip_verify,
    )
    if result["backup_path"]:
        print(f"Backup: {result['backup_path']}")
    print(f"Memory copied: {len(result['memory_copied'])} files")
    print(f"Config copied: {len(result['config_copied'])} files")
    print(f"Clawdbook (safe): {len(result['clawdbook_copied'])} files")
    if result["errors"]:
        print("Errors:", file=sys.stderr)
        for e in result["errors"]:
            print(f"  {e}", file=sys.stderr)
        return 1

    # --- Verification ---
    verification = result.get("verification")
    if verification:
        total = verification["total_expected"]
        verified = verification["total_verified"]
        if verification["passed"]:
            print(f"Verification PASSED: {verified}/{total} files confirmed")
        else:
            print(f"Verification FAILED: {verified}/{total} files confirmed", file=sys.stderr)
            for entry in verification.get("missing", []):
                print(f"  MISSING [{entry['type']}]: {Path(entry['source']).name} -> {entry['destination']}", file=sys.stderr)
            for e in verification.get("errors", []):
                print(f"  {e}", file=sys.stderr)
            if not setup_openclaw:
                return 1

    # --- Always reinstall openclaw (unless user explicitly opted out via flag) ---
    if setup_openclaw or not skip_verify:
        # Default behavior: reinstall openclaw at the end
        print("Reinstalling openclaw (npm i -g openclaw)...", file=sys.stderr)
        setup_result = install_openclaw_and_onboard(out_root)
        if not setup_result["install_ok"]:
            print(f"Install failed: {setup_result['install_message']}", file=sys.stderr)
        elif not setup_result["onboard_ok"]:
            print(f"Onboard failed: {setup_result['onboard_message']}", file=sys.stderr)
        else:
            print("openclaw installed and onboard completed.", file=sys.stderr)
        if setup_result["errors"]:
            for e in setup_result["errors"]:
                print(f"  {e}", file=sys.stderr)
            return 1
        if verification and verification["passed"]:
            print("All files verified. Migration is complete!")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Migrate moltbot or clawdbot to openclaw; preserve config, memory, and clawdbook data."
    )
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=False)

    # interactive TUI (default when no command)
    p_run = sub.add_parser("run", help="Interactive terminal UI (lobster + guided menu)")
    p_run.set_defaults(func=lambda a: _run_tui())

    # discover
    p_discover = sub.add_parser("discover", help="List clawdbot assets (config, memory, clawdbook)")
    p_discover.add_argument("--root", type=Path, default=None, help="Source root (default: cwd)")
    p_discover.set_defaults(func=lambda a: cmd_discover(Path(a.root or os.getcwd())))

    # backup
    p_backup = sub.add_parser("backup", help="Create timestamped backup (no migration)")
    p_backup.add_argument("--root", type=Path, default=None, help="Clawdbot root (default: cwd)")
    p_backup.add_argument("--backup-dir", type=Path, default=None, help="Backup parent dir (default: root/backups)")
    p_backup.set_defaults(
        func=lambda a: cmd_backup(
            Path(a.root or os.getcwd()),
            Path(a.backup_dir) if a.backup_dir else None,
        )
    )

    # migrate
    p_migrate = sub.add_parser("migrate", help="Migrate to openclaw (backup first unless --no-backup)")
    p_migrate.add_argument("--root", type=Path, default=None, help="Source root (default: cwd)")
    p_migrate.add_argument("--no-backup", action="store_true", help="Skip backup (not recommended)")
    p_migrate.add_argument("--output", type=Path, default=None, help="Openclaw output root (default: root)")
    p_migrate.add_argument(
        "--setup-openclaw",
        action="store_true",
        help="After migration: npm i -g openclaw and run openclaw onboard in output dir",
    )
    p_migrate.add_argument(
        "--skip-verify",
        action="store_true",
        help="Skip post-migration file verification (not recommended)",
    )
    p_migrate.set_defaults(
        func=lambda a: cmd_migrate(
            Path(a.root or os.getcwd()),
            a.no_backup,
            Path(a.output) if a.output else None,
            a.setup_openclaw,
            a.skip_verify,
        )
    )

    args = parser.parse_args()
    if args.command is None:
        return _run_tui()
    return args.func(args)


def _run_tui() -> int:
    from .tui import run_tui
    return run_tui()


if __name__ == "__main__":
    sys.exit(main())
