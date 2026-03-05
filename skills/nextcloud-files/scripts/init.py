#!/usr/bin/env python3
"""
init.py - Validate the Nextcloud skill configuration.
Tests the connection and each configured permission against the real instance.

Write tests (mkdir/write/delete) are only run when both allow_write=true AND
allow_delete=true. This guarantees no test artifacts are ever left on the
Nextcloud instance.

Usage: python3 scripts/init.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from nextcloud import NextcloudClient, NextcloudError, PermissionDeniedError


SKILL_DIR   = Path(__file__).resolve().parent.parent
_CONFIG_DIR = Path.home() / ".openclaw" / "config" / "nextcloud"
CONFIG_FILE = _CONFIG_DIR / "config.json"
CREDS_FILE  = Path.home() / ".openclaw" / "secrets" / "nextcloud_creds"

TEST_DIR     = "__skill_test__"
TEST_FILE    = f"{TEST_DIR}/test.txt"
TEST_CONTENT = "nextcloud-skill-init-check"


class Results:
    def __init__(self):
        self.passed  = []
        self.failed  = []
        self.skipped = []

    def ok(self, label: str, detail: str = ""):
        self.passed.append(label)
        suffix = f"  {detail}" if detail else ""
        print(f"  ✓  {label}{suffix}")

    def fail(self, label: str, reason: str = ""):
        self.failed.append(label)
        suffix = f"  → {reason}" if reason else ""
        print(f"  ✗  {label}{suffix}")

    def skip(self, label: str, reason: str = ""):
        self.skipped.append(label)
        print(f"  ~  {label}  (skipped: {reason})")

    def summary(self):
        total   = len(self.passed) + len(self.failed)
        skipped = len(self.skipped)
        print(f"\n  {len(self.passed)}/{total} checks passed", end="")
        if skipped:
            print(f", {skipped} skipped (disabled in config)", end="")
        print()
        if self.failed:
            print("\n  Failed checks:")
            for f in self.failed:
                print(f"    ✗  {f}")


def _prefixed(path: str, base: str) -> str:
    base = base.rstrip("/") or ""
    return f"{base}/{path}"


def main():
    print("┌─────────────────────────────────────────┐")
    print("│   Nextcloud Skill - Init Check          │")
    print("└─────────────────────────────────────────┘")

    # ── Pre-flight ─────────────────────────────────────────────────────────────
    if not CREDS_FILE.exists():
        print(f"\n✗ Credentials not found: {CREDS_FILE}")
        print("  Run setup.py first:  python3 scripts/setup.py")
        sys.exit(1)

    try:
        nc = NextcloudClient()
    except NextcloudError as e:
        print(f"\n✗ {e}")
        sys.exit(1)

    cfg          = nc.cfg
    base         = cfg.get("base_path", "/").rstrip("/") or ""
    ro           = cfg.get("readonly_mode", False)
    allow_write  = cfg.get("allow_write",  False)
    allow_delete = cfg.get("allow_delete", False)

    # Write tests require both allow_write and allow_delete to guarantee cleanup.
    can_write_test = allow_write and allow_delete and not ro

    r         = Results()
    test_dir  = _prefixed(TEST_DIR,  base)
    test_file = _prefixed(TEST_FILE, base)

    # ── 1. Connection ──────────────────────────────────────────────────────────
    print("\n● Connection\n")
    try:
        info  = nc.get_user_info()
        quota = info.get("quota", {})
        used  = quota.get("used",  0)
        total = quota.get("total", 0)
        def _fmt(b):
            for unit in ("B", "KB", "MB", "GB", "TB"):
                if abs(b) < 1024.0: return f"{b:.1f} {unit}"
                b /= 1024.0
            return f"{b:.1f} PB"
        storage = f"{_fmt(used)} / {_fmt(total)}" if total > 0 else _fmt(used)
        r.ok("Connect", f"user={info.get('id', '?')}  storage={storage}")
    except Exception as e:
        r.fail("Connect", str(e))
        print("\n  Cannot proceed without a valid connection. Check credentials.")
        r.summary()
        sys.exit(1)

    # ── 2. Scope / base_path ───────────────────────────────────────────────────
    print("\n● Scope\n")
    try:
        items = nc.list_dir(base or "/")
        r.ok("Read base_path", f"path='{base or '/'}' ({len(items)} items)")
    except Exception as e:
        r.fail("Read base_path", str(e))

    # ── 3. Write + Delete (only when both are enabled) ─────────────────────────
    print("\n● Write / Delete permissions\n")

    if ro:
        r.skip("Write (mkdir)",   "readonly_mode=true")
        r.skip("Write (file)",    "readonly_mode=true")
        r.skip("Read (file)",     "readonly_mode=true")
        r.skip("Delete (file)",   "readonly_mode=true")
        r.skip("Delete (folder)", "readonly_mode=true")

    elif not allow_write:
        r.skip("Write (mkdir)",   "allow_write=false")
        r.skip("Write (file)",    "allow_write=false")
        r.skip("Read (file)",     "allow_write=false")
        r.skip("Delete (file)",   "allow_write=false")
        r.skip("Delete (folder)", "allow_write=false")

    elif not allow_delete:
        # Cannot guarantee cleanup → skip all write tests to avoid orphan artifacts.
        r.skip("Write (mkdir)",   "allow_delete=false (write test skipped - no cleanup possible)")
        r.skip("Write (file)",    "allow_delete=false (write test skipped - no cleanup possible)")
        r.skip("Read (file)",     "allow_delete=false")
        r.skip("Delete (file)",   "allow_delete=false")
        r.skip("Delete (folder)", "allow_delete=false")
        print(f"\n  ℹ  Write tests skipped: allow_delete=false ensures no test artifacts")
        print(f"     are left on the instance. Write access will be confirmed on first use.")

    else:
        # allow_write=true AND allow_delete=true - safe to create and clean up.

        # mkdir
        try:
            nc.mkdir(test_dir)
            r.ok("Write (mkdir)", f"created {test_dir}")
        except Exception as e:
            r.fail("Write (mkdir)", str(e))

        # write file
        try:
            nc.write_file(test_file, TEST_CONTENT)
            r.ok("Write (file)", f"created {test_file}")
        except Exception as e:
            r.fail("Write (file)", str(e))

        # read file back
        if nc.exists(test_file):
            try:
                content = nc.read_file(test_file)
                if content.strip() == TEST_CONTENT:
                    r.ok("Read (file)", "content matches")
                else:
                    r.fail("Read (file)", f"unexpected content: {content[:40]!r}")
            except Exception as e:
                r.fail("Read (file)", str(e))

        # cleanup: delete file then folder
        if nc.exists(test_file):
            try:
                nc.delete(test_file)
                r.ok("Delete (file)", f"removed {test_file}")
            except Exception as e:
                r.fail("Delete (file)", str(e))
                print(f"     ⚠  Manual cleanup: Nextcloud → Files → {base}/{TEST_DIR}/")

        if nc.exists(test_dir):
            try:
                nc.delete(test_dir)
                r.ok("Delete (folder)", f"removed {test_dir}")
            except Exception as e:
                r.fail("Delete (folder)", str(e))
                print(f"     ⚠  Manual cleanup: Nextcloud → Files → {base}/{TEST_DIR}/")

    # ── 4. Server capabilities ─────────────────────────────────────────────────
    print("\n● Server\n")
    try:
        caps   = nc.get_capabilities()
        nc_ver = caps.get("version", {}).get("string", "?")
        r.ok("Capabilities", f"Nextcloud {nc_ver}")
    except Exception as e:
        r.fail("Capabilities", str(e))

    # ── Summary ────────────────────────────────────────────────────────────────
    print("\n┌─────────────────────────────────────────┐")
    print("│   Init check complete                   │")
    print("└─────────────────────────────────────────┘")
    r.summary()

    if r.failed:
        print("\n  Review config.json and nextcloud_creds, then re-run setup.py.\n")
        sys.exit(1)
    else:
        print("\n  Skill is ready to use. ✓\n")


if __name__ == "__main__":
    main()
