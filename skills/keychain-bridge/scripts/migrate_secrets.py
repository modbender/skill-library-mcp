#!/usr/bin/env python3
"""Migrate plaintext secret files to macOS Keychain.

Scans a directory for secret files, injects each into the keychain from
all detected Python versions (for ACL coverage), verifies the round-trip,
and optionally deletes the original files.

Usage:
    python3 migrate_secrets.py --dir ~/.openclaw/secrets/ --account moltbot --dry-run
    python3 migrate_secrets.py --dir ~/.openclaw/secrets/ --account moltbot
    python3 migrate_secrets.py --dir ~/.openclaw/secrets/ --account moltbot --delete-originals

Requirements:
    pip install keyring  (for each Python version on the system)
"""

import argparse
import glob
import os
import subprocess
import sys


def detect_python_versions():
    """Find all Python 3 binaries on the system."""
    candidates = [
        "/usr/bin/python3",
        "/opt/homebrew/bin/python3",
        "/opt/homebrew/opt/python@3.14/bin/python3.14",
        "/opt/homebrew/opt/python@3.13/bin/python3.13",
        "/opt/homebrew/opt/python@3.12/bin/python3.12",
        "/opt/homebrew/opt/python@3.11/bin/python3.11",
    ]
    # Also check pyenv
    pyenv_root = os.path.expanduser("~/.pyenv/versions")
    if os.path.isdir(pyenv_root):
        for ver in os.listdir(pyenv_root):
            py = os.path.join(pyenv_root, ver, "bin", "python3")
            if os.path.isfile(py):
                candidates.append(py)

    found = []
    seen_realpaths = set()
    for path in candidates:
        if not os.path.isfile(path):
            continue
        real = os.path.realpath(path)
        if real in seen_realpaths:
            continue
        seen_realpaths.add(real)
        # Check if keyring is available
        result = subprocess.run(
            [path, "-c", "import keyring; print('ok')"],
            capture_output=True, text=True, timeout=10
        )
        has_keyring = result.returncode == 0 and "ok" in result.stdout
        # Get version string
        ver_result = subprocess.run(
            [path, "--version"], capture_output=True, text=True, timeout=5
        )
        version = ver_result.stdout.strip() or ver_result.stderr.strip()
        found.append({
            "path": path,
            "realpath": real,
            "version": version,
            "has_keyring": has_keyring,
        })
    return found


def inject_secret(python_path, service, account, value):
    """Inject a secret into keychain using a specific Python binary."""
    # Use a temp file to avoid shell escaping issues with the value
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(f"""
import keyring
keyring.set_password({service!r}, {account!r}, open({f.name + '.val'!r}).read())
""")
        script_path = f.name
    val_path = script_path + '.val'
    try:
        with open(val_path, 'w') as vf:
            vf.write(value)
        result = subprocess.run(
            [python_path, script_path],
            capture_output=True, text=True, timeout=30
        )
        return result.returncode == 0, result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "timeout (30s) — may indicate keychain access issue"
    except Exception as e:
        return False, str(e)
    finally:
        for p in [script_path, val_path]:
            try:
                os.unlink(p)
            except OSError:
                pass


def verify_secret(service, account, expected):
    """Verify we can read the secret back from keychain."""
    try:
        import keyring
        value = keyring.get_password(service, account)
        if value == expected:
            return True, "match"
        elif value is None:
            return False, "keychain returned None"
        else:
            return False, f"mismatch (got {len(value)} chars, expected {len(expected)})"
    except Exception as e:
        return False, str(e)


def scan_secrets_dir(directory):
    """Find all secret files in directory."""
    secrets = {}
    for name in sorted(os.listdir(directory)):
        path = os.path.join(directory, name)
        if name.startswith('.') or os.path.isdir(path):
            continue
        try:
            with open(path) as f:
                secrets[name] = f.read().strip()
        except Exception:
            pass
    return secrets


def main():
    parser = argparse.ArgumentParser(description="Migrate plaintext secrets to macOS Keychain")
    parser.add_argument("--dir", required=True, help="Directory containing secret files")
    parser.add_argument("--account", default="moltbot", help="Keychain account name (default: moltbot)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    parser.add_argument("--delete-originals", action="store_true", help="Delete original files after verified migration")
    parser.add_argument("--skip", nargs="*", default=[], help="Service names to skip")
    args = parser.parse_args()

    directory = os.path.expanduser(args.dir)
    if not os.path.isdir(directory):
        print(f"ERROR: {directory} is not a directory")
        sys.exit(1)

    # Detect Python versions
    print("Detecting Python versions...")
    pythons = detect_python_versions()
    if not pythons:
        print("ERROR: No Python 3 binaries found")
        sys.exit(1)

    for py in pythons:
        status = "keyring OK" if py["has_keyring"] else "NO keyring"
        print(f"  {py['path']} ({py['version']}) [{status}]")

    pythons_with_keyring = [p for p in pythons if p["has_keyring"]]
    if not pythons_with_keyring:
        print("\nERROR: No Python versions have keyring installed.")
        print("Install: pip3 install keyring")
        sys.exit(1)

    # Scan secrets
    print(f"\nScanning {directory}...")
    secrets = scan_secrets_dir(directory)
    if not secrets:
        print("No secret files found.")
        return

    skip_set = set(args.skip)
    to_migrate = {k: v for k, v in secrets.items() if k not in skip_set}
    print(f"Found {len(secrets)} files, migrating {len(to_migrate)} (skipping {len(skip_set)})")

    if args.dry_run:
        print("\n--- DRY RUN ---")
        for name, value in to_migrate.items():
            print(f"  Would migrate: {name} ({len(value)} chars) → keychain '{name}' account='{args.account}'")
            for py in pythons_with_keyring:
                print(f"    Inject via: {py['path']}")
        print(f"\n  Would inject from {len(pythons_with_keyring)} Python version(s)")
        if args.delete_originals:
            print(f"  Would delete {len(to_migrate)} original files after verification")
        return

    # Migrate
    migrated = 0
    failed = 0

    for name, value in to_migrate.items():
        print(f"\nMigrating: {name} ({len(value)} chars)")
        all_ok = True

        for py in pythons_with_keyring:
            ok, msg = inject_secret(py["path"], name, args.account, value)
            status = "OK" if ok else f"FAIL: {msg}"
            print(f"  {py['path']}: {status}")
            if not ok:
                all_ok = False

        # Verify
        ok, msg = verify_secret(name, args.account, value)
        print(f"  Verify: {msg}")

        if ok and all_ok:
            migrated += 1
            if args.delete_originals:
                path = os.path.join(directory, name)
                os.unlink(path)
                print(f"  Deleted: {path}")
        else:
            failed += 1
            print(f"  SKIPPED deletion (verification failed)")

    print(f"\n{'='*40}")
    print(f"Migrated: {migrated}")
    print(f"Failed:   {failed}")
    print(f"Total:    {len(to_migrate)}")
    if failed > 0:
        print("\nSome migrations failed. Check output above for details.")
        print("Common fix: install keyring for all Python versions.")


if __name__ == "__main__":
    main()
