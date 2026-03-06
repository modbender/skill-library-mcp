#!/usr/bin/env python3
"""Audit plaintext secrets and keychain health.

Checks for:
- Unexpected plaintext files in secrets directory
- Keychain items that exist but can't be read (ACL issues)
- Files that exist but aren't in keychain (unmigrated)
- Python keyring installation status

Usage:
    python3 audit_secrets.py --dir ~/.openclaw/secrets/ --account moltbot
    python3 audit_secrets.py --dir ~/.openclaw/secrets/ --account moltbot --group-b key1 key2
"""

import argparse
import os
import subprocess
import sys


def check_keyring_installed():
    """Check if keyring is available in current Python."""
    try:
        import keyring
        try:
            ver = keyring.__version__
        except AttributeError:
            ver = "installed"
        return True, ver
    except ImportError:
        return False, None


def check_keychain_item(service, account):
    """Try to read a keychain item. Returns (exists, readable, error)."""
    try:
        import keyring
        value = keyring.get_password(service, account)
        if value is not None:
            return True, True, None
        return False, False, "not found"
    except Exception as e:
        err = str(e)
        if "-25308" in err:
            return True, False, "errSecInteractionNotAllowed (no GUI session)"
        return True, False, err


def scan_directory(directory):
    """List files in secrets directory."""
    files = []
    if not os.path.isdir(directory):
        return files
    for name in sorted(os.listdir(directory)):
        path = os.path.join(directory, name)
        if name.startswith('.') or os.path.isdir(path):
            continue
        size = os.path.getsize(path)
        files.append({"name": name, "path": path, "size": size})
    return files


def detect_python_keyring_status():
    """Check keyring availability across Python versions."""
    candidates = [
        "/usr/bin/python3",
        "/opt/homebrew/bin/python3",
        "/opt/homebrew/opt/python@3.14/bin/python3.14",
        "/opt/homebrew/opt/python@3.13/bin/python3.13",
        "/opt/homebrew/opt/python@3.12/bin/python3.12",
    ]
    results = []
    seen = set()
    for path in candidates:
        if not os.path.isfile(path):
            continue
        real = os.path.realpath(path)
        if real in seen:
            continue
        seen.add(real)
        try:
            result = subprocess.run(
                [path, "-c", "import keyring; print(getattr(keyring, '__version__', 'installed'))"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                ver = result.stdout.strip()
                results.append({"path": path, "status": "OK", "version": ver})
            else:
                results.append({"path": path, "status": "NOT INSTALLED", "version": None})
        except Exception as e:
            results.append({"path": path, "status": f"ERROR: {e}", "version": None})
    return results


def main():
    parser = argparse.ArgumentParser(description="Audit plaintext secrets and keychain health")
    parser.add_argument("--dir", required=True, help="Secrets directory to audit")
    parser.add_argument("--account", default="moltbot", help="Keychain account (default: moltbot)")
    parser.add_argument("--group-b", nargs="*", default=[], help="Expected Group B files (allowed on disk)")
    args = parser.parse_args()

    directory = os.path.expanduser(args.dir)
    group_b = set(args.group_b)
    issues = []
    warnings = []

    print("=" * 50)
    print("Keychain Bridge Audit")
    print("=" * 50)

    # 1. Check keyring in current Python
    print("\n--- Python Keyring Status ---")
    installed, version = check_keyring_installed()
    if installed:
        print(f"  Current Python: keyring {version} OK")
    else:
        print("  Current Python: keyring NOT INSTALLED")
        issues.append("keyring not installed in current Python")

    # Check across all Python versions
    print("\n  All Python versions:")
    py_status = detect_python_keyring_status()
    for ps in py_status:
        if ps["status"] == "OK":
            print(f"    {ps['path']}: keyring {ps['version']}")
        else:
            print(f"    {ps['path']}: {ps['status']}")
            if "NOT INSTALLED" in ps["status"]:
                warnings.append(f"keyring not installed in {ps['path']}")

    # 2. Scan secrets directory
    print(f"\n--- Secrets Directory: {directory} ---")
    files = scan_directory(directory)
    if not files:
        print("  (empty or not found)")
    else:
        for f in files:
            in_group_b = f["name"] in group_b
            tag = " [Group B]" if in_group_b else " [UNEXPECTED]"
            print(f"  {f['name']}: {f['size']} bytes{tag}")
            if not in_group_b:
                issues.append(f"Unexpected plaintext file: {f['name']} ({f['size']} bytes)")

    # 3. Check keychain items for all files found
    if installed:
        print("\n--- Keychain Verification ---")
        all_names = set(f["name"] for f in files) | group_b
        for name in sorted(all_names):
            exists, readable, error = check_keychain_item(name, args.account)
            has_file = any(f["name"] == name for f in files)
            if readable:
                file_status = "+ file" if has_file else "no file"
                print(f"  {name}: keychain OK ({file_status})")
            elif exists:
                print(f"  {name}: keychain EXISTS but NOT READABLE ({error})")
                warnings.append(f"{name}: keychain exists but unreadable ({error})")
            else:
                if has_file:
                    print(f"  {name}: NOT in keychain (file exists — unmigrated?)")
                    warnings.append(f"{name}: file exists but not in keychain")
                else:
                    print(f"  {name}: NOT in keychain, no file")

    # 4. Summary
    print(f"\n{'=' * 50}")
    print("AUDIT SUMMARY")
    print(f"{'=' * 50}")
    print(f"  Files on disk:  {len(files)}")
    print(f"  Group B (expected): {len(group_b)}")
    print(f"  Issues:    {len(issues)}")
    print(f"  Warnings:  {len(warnings)}")

    if issues:
        print("\n  ISSUES (action needed):")
        for i in issues:
            print(f"    ! {i}")

    if warnings:
        print("\n  WARNINGS:")
        for w in warnings:
            print(f"    ~ {w}")

    if not issues and not warnings:
        print("\n  All clear. No plaintext leaks detected.")

    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
