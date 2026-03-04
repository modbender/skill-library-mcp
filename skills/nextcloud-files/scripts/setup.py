#!/usr/bin/env python3
"""
setup.py - Interactive setup for the Nextcloud skill.
Run this after installing the skill to configure credentials and behavior.

Usage: python3 scripts/setup.py
"""

import json
import sys
from pathlib import Path

import base64
import urllib.request
import urllib.error

SKILL_DIR   = Path(__file__).resolve().parent.parent
_CONFIG_DIR = Path.home() / ".openclaw" / "config" / "nextcloud"
CONFIG_FILE = _CONFIG_DIR / "config.json"
CREDS_FILE  = Path.home() / ".openclaw" / "secrets" / "nextcloud_creds"

_DEFAULT_CONFIG = {
    "base_path": "/",
    "allow_write": False,
    "allow_delete": False,
    "readonly_mode": False,
}


def _ask(prompt: str, default: str = "", secret: bool = False) -> str:
    display = f"[{'***' if secret else default}] " if default else ""
    try:
        if secret:
            import getpass
            val = getpass.getpass(f"  {prompt} {display}: ")
        else:
            val = input(f"  {prompt} {display}: ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\nAborted.")
        sys.exit(0)
    return val if val else default


def _ask_bool(prompt: str, default: bool, hint: str = "") -> bool:
    default_str = "Y/n" if default else "y/N"
    hint_str    = f"  ({hint})" if hint else ""
    try:
        val = input(f"  {prompt}{hint_str} [{default_str}]: ").strip().lower()
    except (KeyboardInterrupt, EOFError):
        print("\nAborted.")
        sys.exit(0)
    return (val.startswith("y") if val else default)


def _load_existing_creds() -> dict:
    creds = {}
    if CREDS_FILE.exists():
        for line in CREDS_FILE.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                creds[k.strip()] = v.strip()
    return creds


def _load_existing_config() -> dict:
    cfg = dict(_DEFAULT_CONFIG)
    if CONFIG_FILE.exists():
        try:
            cfg.update(json.loads(CONFIG_FILE.read_text()))
        except Exception:
            pass
    return cfg


def _write_creds(nc_url: str, nc_user: str, nc_pass: str):
    CREDS_FILE.parent.mkdir(parents=True, exist_ok=True)
    CREDS_FILE.write_text(f"NC_URL={nc_url}\nNC_USER={nc_user}\nNC_APP_KEY={nc_pass}\n")
    CREDS_FILE.chmod(0o600)


def _write_config(cfg: dict):
    _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n")


def _test_connection(nc_url: str, nc_user: str, nc_pass: str) -> bool:
    try:
        url = f"{nc_url.rstrip('/')}/ocs/v2.php/cloud/user"
        cred = base64.b64encode(f"{nc_user}:{nc_pass}".encode()).decode()
        req = urllib.request.Request(url, headers={
            "Authorization": f"Basic {cred}",
            "OCS-APIRequest": "true",
            "Accept": "application/json",
        })
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except urllib.error.HTTPError as exc:
        print(f"    HTTP {exc.code}")
        return False
    except Exception as e:
        print(f"    Connection error: {e}")
        return False


def main():
    print("┌─────────────────────────────────────────┐")
    print("│   Nextcloud Skill - Setup               │")
    print("└─────────────────────────────────────────┘")

    # ── Step 1: Credentials ────────────────────────────────────────────────────
    print("\n● Step 1/3 - Credentials\n")

    existing = _load_existing_creds()
    nc_url = nc_user = nc_pass = ""

    if existing:
        print(f"  Existing credentials found in {CREDS_FILE}")
        if not _ask_bool("Update credentials?", default=False):
            nc_url  = existing.get("NC_URL",  "")
            nc_user = existing.get("NC_USER", "")
            nc_pass = existing.get("NC_APP_KEY", "")
            print("  → Keeping existing credentials.")
        else:
            existing = {}

    if not existing:
        print(f"  Credentials will be saved to {CREDS_FILE} (chmod 600)\n")
        print("  To create an App Password in Nextcloud:")
        print("  → Settings → Security → App passwords → Enter a name → Create\n")
        nc_url  = _ask("Nextcloud URL", default="https://cloud.example.com").rstrip("/")
        nc_user = _ask("Username")
        nc_pass = _ask("App Password", secret=True)

        print("\n  Testing connection...", end=" ", flush=True)
        if _test_connection(nc_url, nc_user, nc_pass):
            print("✓ OK")
        else:
            print("✗ Failed")
            if not _ask_bool("  Save credentials anyway?", default=False):
                print("  Aborted - no files written.")
                sys.exit(1)

        _write_creds(nc_url, nc_user, nc_pass)
        print(f"  ✓ Saved to {CREDS_FILE}")

    # ── Step 2: Scope ──────────────────────────────────────────────────────────
    print("\n● Step 2/3 - Scope\n")
    print("  Limit the agent to a specific subtree of your Nextcloud.")
    print("  Example: /Jarvis  →  agent can only act inside /Jarvis/\n")

    cfg = _load_existing_config()
    cfg["base_path"] = _ask(
        "Restrict agent to folder (leave empty = full access /)",
        default=cfg.get("base_path", "/"),
    ) or "/"

    # ── Step 3: Permissions ────────────────────────────────────────────────────
    print("\n● Step 3/3 - Permissions\n")
    print("  Configure what operations the agent is allowed to perform.\n")

    print("  ── File & folder operations ──")
    cfg["allow_write"] = _ask_bool(
        "Allow creating and modifying files/folders?",
        default=cfg.get("allow_write", False),
        hint="mkdir, write, rename, copy",
    )
    cfg["allow_delete"] = _ask_bool(
        "Allow deleting files and folders?",
        default=cfg.get("allow_delete", False),
        hint="recommended: false unless you trust the agent fully",
    )

    print("\n  ── Safety ──")
    cfg["readonly_mode"] = _ask_bool(
        "Enable readonly mode? (overrides all above - no writes at all)",
        default=cfg.get("readonly_mode", False),
    )

    _write_config(cfg)
    print(f"\n  ✓ Config saved to {CONFIG_FILE}")

    # ── Summary ────────────────────────────────────────────────────────────────
    print("\n┌─────────────────────────────────────────┐")
    print("│   Setup complete ✓                      │")
    print("└─────────────────────────────────────────┘")
    print(f"\n  Instance  : {nc_url}")
    print(f"  User      : {nc_user}")
    print(f"  Scope     : {cfg['base_path']}")
    print(f"  Write     : {'✓' if cfg['allow_write']   and not cfg['readonly_mode'] else '✗'}")
    print(f"  Delete    : {'✓' if cfg['allow_delete']  and not cfg['readonly_mode'] else '✗'}")
    print(f"  Readonly  : {'⚠ ON - all writes blocked' if cfg['readonly_mode'] else '✗ off'}")
    print()
    print("  Run init.py to validate that all permissions work:")
    print("    python3 scripts/init.py")
    print()


def cleanup():
    """Remove all persistent files written by this skill (credentials + config)."""
    print("Removing Nextcloud skill persistent files...")
    removed = []
    for path in [CREDS_FILE, CONFIG_FILE]:
        if path.exists():
            path.unlink()
            removed.append(str(path))
    try:
        _CONFIG_DIR.rmdir()
    except OSError:
        pass
    if removed:
        for p in removed:
            print(f"  Removed: {p}")
        print("Done. Re-run setup.py to reconfigure.")
    else:
        print("  Nothing to remove.")


if __name__ == "__main__":
    if "--cleanup" in sys.argv:
        cleanup()
    else:
        main()
