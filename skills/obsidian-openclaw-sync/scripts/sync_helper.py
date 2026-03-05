#!/usr/bin/env python3
"""
OpenClaw iCloud Sync Helper

This script helps identify and sync OpenClaw configuration between local and iCloud.
Supports multi-agent workspace templates (media, workspace_xxx, etc.)
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, List, Any


class OpenClawSyncHelper:
    """Helper class for OpenClaw iCloud sync operations."""

    def __init__(self):
        self.icloud_obsidian_path: Optional[Path] = None
        self.local_vault: Optional[Path] = None
        self.icloud_vault: Optional[Path] = None
        self.icloud_vaults: List[Path] = []

    def find_icloud_obsidian_path(self) -> Optional[Path]:
        """Find iCloud Obsidian path (iCloud~md~obsidian)."""
        home = Path.home()

        # Obsidian iCloud path: ~/Library/Mobile Documents/iCloud~md~obsidian/Documents
        obsidian_path = home / "Library" / "Mobile Documents" / "iCloud~md~obsidian" / "Documents"

        if obsidian_path.exists():
            return obsidian_path

        return None

    def find_openclaw_icloud_vault(self, icloud_path: Path) -> Optional[Path]:
        """Find OpenClaw vault by scanning for .obsidian directory.

        A vault is identified by the presence of .obsidian directory inside it.
        Scans in order:
        1. Common known paths
        2. Direct children of icloud_path
        3. Second level children (e.g., Obsidian/OpenClaw)
        """
        def is_vault(dir_path: Path) -> bool:
            """Check if a directory is an Obsidian vault (has .obsidian folder)."""
            if not dir_path.is_dir():
                return False
            return (dir_path / ".obsidian").exists()

        # First try common paths
        possible_paths = [
            icloud_path / "openclaw-workspace",
            icloud_path / "OpenClaw",
            icloud_path / "Obsidian" / "OpenClaw",
            icloud_path / "Vaults" / "OpenClaw",
        ]

        for path in possible_paths:
            if path.exists() and is_vault(path):
                return path

        # Scan first level children
        if icloud_path.exists():
            try:
                for item in icloud_path.iterdir():
                    if is_vault(item):
                        return item
            except PermissionError:
                pass

        # Scan second level (e.g., Obsidian/OpenClaw)
        if icloud_path.exists():
            try:
                for level1 in icloud_path.iterdir():
                    if level1.is_dir():
                        for level2 in level1.iterdir():
                            if is_vault(level2):
                                return level2
            except PermissionError:
                pass

        return None

    def find_all_vaults(self, icloud_path: Path) -> List[Path]:
        """Find all vaults under the given iCloud path."""
        vaults = []

        def collect_vaults(dir_path: Path, max_depth: int = 3, current_depth: int = 0):
            if current_depth >= max_depth:
                return
            try:
                for item in dir_path.iterdir():
                    if item.is_dir():
                        # Check if this is a vault
                        if (item / ".obsidian").exists():
                            vaults.append(item)
                        # Recurse into subdirectories
                        elif not item.name.startswith("."):
                            collect_vaults(item, max_depth, current_depth + 1)
            except PermissionError:
                pass

        collect_vaults(icloud_path)
        return vaults

    def is_valid_openclaw_vault(self, vault_path: Path) -> bool:
        """Check if a vault is a valid OpenClaw vault.

        A valid OpenClaw vault must have:
        1. .obsidian directory (identifies it as an Obsidian vault)

        Note: openclaw.json is recommended but not strictly required.
        It may exist in iCloud as a template, and locally with machine-specific config.
        """
        return (vault_path / ".obsidian").exists()

    def get_vault_info(self, vault_path: Path) -> dict:
        """Get vault validity status and info.

        Returns dict with:
        - is_valid: True if vault has .obsidian
        - has_openclaw_json: True if openclaw.json exists
        - missing: List of missing items (for display)
        """
        result = {
            "is_valid": False,
            "has_obsidian": False,
            "has_openclaw_json": False,
            "missing": [],
            "warnings": []
        }

        # Check .obsidian (required)
        has_obsidian = (vault_path / ".obsidian").exists()
        result["has_obsidian"] = has_obsidian

        if not has_obsidian:
            result["missing"].append(".obsidian/")

        # Check openclaw.json (recommended)
        has_openclaw_json = (
            (vault_path / "openclaw.json").exists() or
            (vault_path / ".openclaw" / "openclaw.json").exists()
        )
        result["has_openclaw_json"] = has_openclaw_json

        if not has_openclaw_json:
            result["warnings"].append("openclaw.json not found (recommended)")

        # Valid if has .obsidian
        result["is_valid"] = has_obsidian

        return result

    def get_vault_details(self, vault_path: Path) -> Dict[str, Any]:
        """Get agents and skills from a vault directory."""
        agents = []
        skills = []

        # Find agents (workspace_* or workspace-* directories)
        if vault_path.exists():
            try:
                for d in vault_path.iterdir():
                    if d.is_dir():
                        if d.name.startswith("workspace_") or d.name.startswith("workspace-"):
                            agent_name = d.name.replace("workspace_", "").replace("workspace-", "")
                            agents.append(agent_name)
            except PermissionError:
                pass

        # Find skills
        skills_dir = vault_path / "skills"
        if skills_dir.exists():
            try:
                for d in skills_dir.iterdir():
                    if d.is_dir() and not d.name.startswith("."):
                        skills.append(d.name)
            except PermissionError:
                pass

        return {
            "agents": sorted(agents),
            "skills": sorted(skills),
        }

    def get_local_openclaw_vault(self) -> Optional[Path]:
        """Find local OpenClaw config directory (~/.openclaw)."""
        home = Path.home()
        local_path = home / ".openclaw"

        if local_path.exists():
            return local_path

        return None

    def get_local_symlinks(self, local_path: Path) -> Dict[str, str]:
        """Get all symlinks in the local config directory with their targets."""
        symlinks = {}
        if not local_path.exists():
            return symlinks

        try:
            for item in local_path.iterdir():
                if item.is_symlink():
                    target = os.readlink(item)
                    symlinks[item.name] = target
        except PermissionError:
            pass

        return symlinks


def cmd_status(helper: OpenClawSyncHelper) -> int:
    """Show sync status."""
    print("OpenClaw iCloud Sync Status")
    print("=" * 50)

    # Find iCloud Obsidian path (primary)
    helper.icloud_obsidian_path = helper.find_icloud_obsidian_path()
    if helper.icloud_obsidian_path:
        print(f"✓ iCloud Obsidian: {helper.icloud_obsidian_path}")
    else:
        print("❌ iCloud Obsidian path not found")
        return 1

    # Find all iCloud vaults
    icloud_path = helper.icloud_obsidian_path
    all_vaults = helper.find_all_vaults(icloud_path)

    # Separate valid and invalid vaults
    valid_vaults = []
    invalid_vaults = []
    vault_info = {}

    for vault in all_vaults:
        info = helper.get_vault_info(vault)
        vault_info[vault] = info
        if info["is_valid"]:
            valid_vaults.append(vault)
        else:
            invalid_vaults.append(vault)

    # Find local config directory
    helper.local_vault = helper.get_local_openclaw_vault()

    def print_vault_info(indent: str, vault_path: Path):
        """Print vault details in unified format."""
        details = helper.get_vault_details(vault_path)
        if details["agents"]:
            print(f"{indent}Agents ({len(details['agents'])}): {', '.join(details['agents'])}")
        if details["skills"]:
            print(f"{indent}Skills ({len(details['skills'])}): {', '.join(details['skills'])}")

    # Print iCloud vaults
    print()
    if valid_vaults:
        print(f"✓ Valid Vaults ({len(valid_vaults)}):")
        for vault in valid_vaults:
            info = vault_info[vault]
            marker = "✓" if info["has_openclaw_json"] else "○"
            print(f"  {marker} {vault.name}")
            print_vault_info("      ", vault)
            if info["warnings"]:
                print(f"      ⚠️  {', '.join(info['warnings'])}")

    if invalid_vaults:
        if valid_vaults:
            print()
        print(f"✗ Invalid Vaults ({len(invalid_vaults)}):")
        for vault in invalid_vaults:
            info = vault_info[vault]
            missing = ", ".join(info["missing"])
            print(f"  ✗ {vault.name} (missing: {missing})")
            print_vault_info("      ", vault)

    if not all_vaults:
        print("❌ iCloud Vault: Not found")

    # Print local config
    print()
    if helper.local_vault:
        print(f"Local Config: {helper.local_vault.name}")
        print_vault_info("  ", helper.local_vault)
    else:
        print("Local Config: ~/.openclaw (not initialized)")

    return 0


def cmd_setup(helper: OpenClawSyncHelper, vault_index: int = -1, overwrite: bool = False, confirm: bool = True) -> int:
    """Interactive setup to sync vault to local.

    Args:
        vault_index: Pre-selected vault index (-1 for interactive selection)
        overwrite: If True, overwrite local openclaw.json with symlink to iCloud version
        confirm: If True, ask for confirmation before creating symlinks
    """
    print("OpenClaw Setup")
    print("=" * 50)

    # Find iCloud Obsidian path
    helper.icloud_obsidian_path = helper.find_icloud_obsidian_path()
    if not helper.icloud_obsidian_path:
        print("❌ iCloud Obsidian path not found")
        return 1

    print(f"✓ iCloud Obsidian: {helper.icloud_obsidian_path}")

    # Find all vaults
    all_vaults = helper.find_all_vaults(helper.icloud_obsidian_path)

    if not all_vaults:
        print("❌ No iCloud vaults found")
        return 1

    # Separate valid and invalid vaults
    valid_vaults = []
    invalid_vaults = []
    vault_info = {}  # vault_path -> info dict

    for vault in all_vaults:
        info = helper.get_vault_info(vault)
        vault_info[vault] = info

        if info["is_valid"]:
            valid_vaults.append(vault)
        else:
            invalid_vaults.append(vault)

    # Sort: valid vaults first, then invalid vaults
    helper.icloud_vaults = valid_vaults + invalid_vaults

    # Step 1: Show vaults
    print()
    print("Available iCloud Vaults:")
    print()

    # Show valid vaults first
    if valid_vaults:
        print("✓ Valid Vaults:")
        for vault in valid_vaults:
            i = helper.icloud_vaults.index(vault)
            selected = "➤" if i == vault_index else " "
            info = vault_info[vault]
            warning = ""
            if info["warnings"]:
                warning = f" [{', '.join(info['warnings'])}]"
            print(f"  [{i}] {selected} {vault.name}{warning}")
            details = helper.get_vault_details(vault)
            if details["agents"]:
                print(f"      Agents: {', '.join(details['agents'])}")
            if details["skills"]:
                print(f"      Skills: {', '.join(details['skills'])}")
        print()

    # Show invalid vaults
    if invalid_vaults:
        print("✗ Invalid Vaults (missing .obsidian):")
        for vault in invalid_vaults:
            i = helper.icloud_vaults.index(vault)
            selected = "➤" if i == vault_index else " "
            info = vault_info[vault]
            missing = ", ".join(info["missing"])
            print(f"  [{i}] {selected} {vault.name} (missing: {missing})")
            details = helper.get_vault_details(vault)
            if details["agents"]:
                print(f"      Agents: {', '.join(details['agents'])}")
            if details["skills"]:
                print(f"      Skills: {', '.join(details['skills'])}")
        print()

    # Step 2: Select vault
    print()

    # Filter to only allow valid vault selection
    valid_indices = [i for i, v in enumerate(helper.icloud_vaults) if vault_info[v]["is_valid"]]

    if vault_index < 0:
        try:
            selected = input("Select vault [0]: ").strip()
            vault_index = int(selected) if selected else 0
        except (ValueError, EOFError):
            vault_index = 0

    # Validate selection - only allow valid vaults
    if vault_index not in valid_indices:
        if valid_indices:
            print(f"⚠️  Index {vault_index} is not a valid vault. Using first valid vault.")
            vault_index = valid_indices[0]
        else:
            print("❌ No valid vaults available for selection.")
            return 1

    helper.icloud_vault = helper.icloud_vaults[vault_index]
    print(f"\n➤ Selected: {helper.icloud_vault.name}")

    # Step 3: Show local config
    helper.local_vault = helper.get_local_openclaw_vault()
    print()
    if helper.local_vault:
        print(f"Local Config: {helper.local_vault}")
    else:
        print("Local Config: ~/.openclaw (not found)")
        return 1

    # Step 4: Generate symlink commands
    print()
    print(f"Symlinks to create in {helper.local_vault}:\n")

    # Core directories
    core_dirs = ["media", "projects", "team", "skills"]
    for dir_name in core_dirs:
        src = helper.icloud_vault / dir_name
        if src.exists():
            print(f"  {dir_name} -> {src}/")

    # Workspace directories (support both workspace- and workspace_)
    workspaces = [
        d.name for d in helper.icloud_vault.iterdir()
        if d.is_dir() and (d.name.startswith("workspace-") or d.name.startswith("workspace_"))
    ]
    for ws in sorted(workspaces):
        src = helper.icloud_vault / ws
        print(f"  {ws} -> {src}/")

    # Config files in .openclaw/
    config_files = []
    openclaw_dir = helper.icloud_vault / ".openclaw"
    if openclaw_dir.exists():
        for f in openclaw_dir.iterdir():
            if f.is_file() and f.suffix == ".json" and not f.name.startswith("."):
                config_files.append(f".openclaw/{f.name}")
                print(f"  .openclaw/{f.name} -> {openclaw_dir}/{f.name}")

    # Check for openclaw.json in iCloud vault root
    icloud_openclaw_json = helper.icloud_vault / "openclaw.json"
    symlink_openclaw_json = False
    if icloud_openclaw_json.exists():
        local_openclaw_json = helper.local_vault / "openclaw.json"
        local_exists = local_openclaw_json.exists() and not local_openclaw_json.is_symlink()

        # Determine if we should symlink openclaw.json
        if overwrite:
            symlink_openclaw_json = True
            if local_exists:
                print(f"  openclaw.json -> {icloud_openclaw_json} (will overwrite local)")
            else:
                print(f"  openclaw.json -> {icloud_openclaw_json}")
        else:
            # Don't overwrite by default, just show info
            if local_exists:
                print(f"  openclaw.json -> {icloud_openclaw_json} (skipped: --overwrite to replace)")
            else:
                symlink_openclaw_json = True
                print(f"  openclaw.json -> {icloud_openclaw_json}")

    # Ask for confirmation
    if confirm:
        print()
        response = input("Create these symlinks? [y/N]: ").strip().lower()
    else:
        response = 'y'

    if response in ['y', 'yes']:
        print()
        created_count = 0

        # Create core directory symlinks
        for dir_name in core_dirs:
            src = helper.icloud_vault / dir_name
            if src.exists():
                symlink_path = helper.local_vault / dir_name
                if symlink_path.exists() or symlink_path.is_symlink():
                    symlink_path.unlink()
                symlink_path.symlink_to(src)
                print(f"  ✓ Created: {dir_name}")
                created_count += 1

        # Create workspace symlinks
        for ws in sorted(workspaces):
            src = helper.icloud_vault / ws
            symlink_path = helper.local_vault / ws
            if symlink_path.exists() or symlink_path.is_symlink():
                symlink_path.unlink()
            symlink_path.symlink_to(src)
            print(f"  ✓ Created: {ws}")
            created_count += 1

        # Create config file symlinks
        if config_files:
            local_openclaw_dir = helper.local_vault / ".openclaw"
            local_openclaw_dir.mkdir(exist_ok=True)
            for config_file in config_files:
                file_name = config_file.replace(".openclaw/", "")
                src = openclaw_dir / file_name
                symlink_path = local_openclaw_dir / file_name
                if symlink_path.exists() or symlink_path.is_symlink():
                    symlink_path.unlink()
                symlink_path.symlink_to(src)
                print(f"  ✓ Created: {config_file}")
                created_count += 1

        # Create openclaw.json symlink (remove local file first if exists)
        if symlink_openclaw_json:
            local_openclaw_json = helper.local_vault / "openclaw.json"
            if local_openclaw_json.exists() or local_openclaw_json.is_symlink():
                local_openclaw_json.unlink()
            local_openclaw_json.symlink_to(icloud_openclaw_json)
            print(f"  ✓ Created: openclaw.json -> iCloud")
            created_count += 1

        print(f"\nCreated {created_count} symlinks")
    else:
        print("\nCancelled")

    return 0


def cmd_unset(helper: OpenClawSyncHelper) -> int:
    """List and remove local symlinks."""
    print("OpenClaw Unset Symlinks")
    print("=" * 50)

    # Find local config directory
    helper.local_vault = helper.get_local_openclaw_vault()

    if not helper.local_vault:
        print("❌ Local config ~/.openclaw not found")
        return 1

    # Get all symlinks
    symlinks = helper.get_local_symlinks(helper.local_vault)

    if not symlinks:
        print("No symlinks found in local config")
        return 0

    print(f"\nLocal Config: {helper.local_vault}")
    print(f"\nFound {len(symlinks)} symlink(s):\n")

    # List symlinks
    for name, target in sorted(symlinks.items()):
        print(f"  - {name}")
        print(f"    -> {target}")

    # Ask for confirmation
    print()
    response = input("Remove these symlinks? [y/N]: ").strip().lower()

    if response in ['y', 'yes']:
        print()
        removed_count = 0
        for name in symlinks:
            symlink_path = helper.local_vault / name
            try:
                symlink_path.unlink()
                print(f"  ✓ Removed: {name}")
                removed_count += 1
            except Exception as e:
                print(f"  ❌ Failed to remove {name}: {e}")

        print(f"\nRemoved {removed_count}/{len(symlinks)} symlinks")
    else:
        print("\nCancelled")

    return 0


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="OpenClaw iCloud Sync Helper - Sync Obsidian OpenClaw config across multiple iCloud devices",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s setup                    # Interactive setup with prompts
  %(prog)s setup --overwrite        # Overwrite local openclaw.json with iCloud version
  %(prog)s setup --no-confirm       # Skip confirmation prompt
  %(prog)s setup --vault 1          # Select vault by index
  %(prog)s status                   # Show all iCloud vaults status
  %(prog)s unset                    # Remove local symlinks
"""
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="status",
        choices=["status", "setup", "unset"],
        help="Command to run"
    )
    parser.add_argument(
        "--vault", "-v",
        type=int,
        default=-1,
        help="Vault index to select (default: interactive)"
    )
    parser.add_argument(
        "--overwrite", "-w",
        action="store_true",
        help="Overwrite local openclaw.json with symlink to iCloud version"
    )
    parser.add_argument(
        "--no-confirm", "-y",
        action="store_true",
        help="Skip confirmation prompt (auto-confirm)"
    )

    args = parser.parse_args()

    helper = OpenClawSyncHelper()

    # Initialize paths
    helper.icloud_obsidian_path = helper.find_icloud_obsidian_path()
    if helper.icloud_obsidian_path:
        helper.icloud_vaults = helper.find_all_vaults(helper.icloud_obsidian_path)
        if helper.icloud_vaults:
            helper.icloud_vault = helper.icloud_vaults[0]

    helper.local_vault = helper.get_local_openclaw_vault()

    # Command dispatch
    if args.command == "setup":
        confirm = not args.no_confirm
        return cmd_setup(helper, args.vault, args.overwrite, confirm)
    elif args.command == "unset":
        return cmd_unset(helper)

    return cmd_status(helper)


if __name__ == "__main__":
    exit(main())
