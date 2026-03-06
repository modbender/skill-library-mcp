#!/usr/bin/env python3
"""
Permission checker for security audit.
Standalone utility to check and fix file/directory permissions.
"""

import os
import sys
import stat
import argparse
from pathlib import Path
from typing import List, Tuple


def get_permissions(path: Path) -> int:
    """Get file permissions as octal integer."""
    return stat.S_IMODE(path.stat().st_mode)


def check_permissions(path: Path, expected_dir: int = 0o700, expected_file: int = 0o600) -> List[Tuple[Path, int, int, str]]:
    """Check permissions and return list of issues."""
    issues = []

    if not path.exists():
        return issues

    if path.is_dir():
        current = get_permissions(path)
        if current > expected_dir:
            issues.append((path, current, expected_dir, "directory"))

        # Recursively check contents
        for item in path.iterdir():
            issues.extend(check_permissions(item, expected_dir, expected_file))
    else:
        current = get_permissions(path)
        if current > expected_file:
            issues.append((path, current, expected_file, "file"))

    return issues


def fix_permissions(path: Path, expected_dir: int = 0o700, expected_file: int = 0o600) -> int:
    """Fix permissions for a path. Returns count of fixed items."""
    issues = check_permissions(path, expected_dir, expected_file)
    fixed = 0

    for item_path, current, expected, item_type in issues:
        try:
            os.chmod(item_path, expected)
            print(f"✓ Fixed {item_type}: {item_path} ({oct(current)} → {oct(expected)})")
            fixed += 1
        except PermissionError as e:
            print(f"✗ Failed to fix {item_path}: {e}")

    return fixed


def main():
    parser = argparse.ArgumentParser(description="Check and fix file permissions")
    parser.add_argument("--path", type=Path, required=True, help="Path to check")
    parser.add_argument("--dir-mode", type=lambda x: int(x, 8), default=0o700, help="Expected directory mode (octal, default: 700)")
    parser.add_argument("--file-mode", type=lambda x: int(x, 8), default=0o600, help="Expected file mode (octal, default: 600)")
    parser.add_argument("--fix", action="store_true", help="Fix permissions automatically")

    args = parser.parse_args()

    print(f"Checking permissions for: {args.path}")
    print(f"Expected: directories={oct(args.dir_mode)}, files={oct(args.file_mode)}")
    print()

    issues = check_permissions(args.path, args.dir_mode, args.file_mode)

    if not issues:
        print("✓ All permissions are correct!")
        return

    print(f"Found {len(issues)} items with loose permissions:\n")
    for item_path, current, expected, item_type in issues:
        print(f"  {item_type:9} {oct(current):>5} → {oct(expected):>5}  {item_path}")

    if args.fix:
        print(f"\nFixing permissions...")
        fixed = fix_permissions(args.path, args.dir_mode, args.file_mode)
        print(f"\n✓ Fixed {fixed} items.")
    else:
        print(f"\nRun with --fix to automatically fix these permissions.")


if __name__ == "__main__":
    main()
