#!/usr/bin/env python3
"""
setup.py - Interactive setup wizard for OpenClaw mail-client skill.
Writes credentials to ~/.openclaw/secrets/mail_creds (chmod 600)
and config.json next to this script's parent directory.
"""

import imaplib
import json
import os
import pathlib
import smtplib
import ssl
import sys

SKILL_DIR   = pathlib.Path(__file__).resolve().parent.parent
_CONFIG_DIR = pathlib.Path.home() / ".openclaw" / "config" / "mail-client"
CONFIG_PATH = _CONFIG_DIR / "config.json"
SECRETS_DIR = pathlib.Path.home() / ".openclaw" / "secrets"
CREDS_PATH  = SECRETS_DIR / "mail_creds"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def prompt(text: str, default: str = "") -> str:
    """Prompt with optional default."""
    display = f" [{default}]" if default else ""
    try:
        value = input(f"{text}{display}: ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\nAborted.")
        sys.exit(1)
    return value if value else default


def prompt_bool(text: str, default: bool = False) -> bool:
    """Prompt for yes/no."""
    default_str = "y" if default else "n"
    raw = prompt(f"{text} (y/n)", default=default_str).lower()
    return raw in ("y", "yes", "1", "true")


def prompt_int(text: str, default: int) -> int:
    """Prompt for integer."""
    raw = prompt(text, default=str(default))
    try:
        return int(raw)
    except ValueError:
        print(f"  Invalid integer '{raw}', using default {default}")
        return default


def hr(char: str = "-", width: int = 60) -> None:
    print(char * width)


# ---------------------------------------------------------------------------
# Steps
# ---------------------------------------------------------------------------


def step_credentials() -> dict:
    print()
    hr("=")
    print("  Step 1: Mail server credentials")
    hr("=")
    print("  Credentials are stored in:", CREDS_PATH)
    print("  They will be chmod 600 and never committed to git.")
    hr()

    smtp_host = prompt("SMTP host", default="mail.example.com")
    imap_host = prompt("IMAP host", default=smtp_host)
    mail_user = prompt("Mail user (email address)")
    mail_app_key = prompt("App key / password (input visible)")

    return {
        "MAIL_SMTP_HOST": smtp_host,
        "MAIL_IMAP_HOST": imap_host,
        "MAIL_USER": mail_user,
        "MAIL_APP_KEY": mail_app_key,
    }


def step_permissions() -> dict:
    print()
    hr("=")
    print("  Step 2: Capabilities (all disabled by default)")
    hr("=")
    print("  Enable only what the agent should be allowed to do.")
    hr()

    allow_send = prompt_bool("allow_send   - send email via SMTP", default=False)
    allow_read = prompt_bool("allow_read   - read/list messages via IMAP", default=False)
    allow_search = prompt_bool("allow_search - search messages via IMAP SEARCH", default=False)
    allow_delete = prompt_bool("allow_delete - delete/move messages via IMAP", default=False)

    return {
        "allow_send": allow_send,
        "allow_read": allow_read,
        "allow_search": allow_search,
        "allow_delete": allow_delete,
    }


def step_defaults(mail_user: str = "") -> dict:
    print()
    hr("=")
    print("  Step 3: Defaults")
    hr("=")

    smtp_port = prompt_int("SMTP port (587 for STARTTLS, 465 for SSL)", default=587)
    imap_port = prompt_int("IMAP port (993 for SSL)", default=993)
    mail_from = prompt("From address (leave empty to use MAIL_USER)", default=mail_user)
    default_folder = prompt("Default IMAP folder", default="INBOX")
    max_results = prompt_int("Max messages returned per query", default=20)

    return {
        "smtp_port": smtp_port,
        "imap_port": imap_port,
        "mail_from": mail_from,
        "default_folder": default_folder,
        "max_results": max_results,
    }


# ---------------------------------------------------------------------------
# Connection tests
# ---------------------------------------------------------------------------


def test_imap(creds: dict, defaults: dict) -> bool:
    print("\n  Testing IMAP connection ...", end=" ", flush=True)
    host = creds["MAIL_IMAP_HOST"]
    port = int(defaults.get("imap_port", 993))
    user = creds["MAIL_USER"]
    app_key = creds["MAIL_APP_KEY"]
    try:
        ctx = ssl.create_default_context()
        imap = imaplib.IMAP4_SSL(host, port, ssl_context=ctx)
        imap.login(user, app_key)
        imap.logout()
        print("OK")
        return True
    except imaplib.IMAP4.error as exc:
        print(f"FAILED\n  IMAP error: {exc}")
        return False
    except OSError as exc:
        print(f"FAILED\n  Connection error: {exc}")
        return False


def test_smtp(creds: dict, defaults: dict) -> bool:
    print("  Testing SMTP connection ...", end=" ", flush=True)
    host = creds["MAIL_SMTP_HOST"]
    port = int(defaults.get("smtp_port", 587))
    user = creds["MAIL_USER"]
    app_key = creds["MAIL_APP_KEY"]
    try:
        ctx = ssl.create_default_context()
        with smtplib.SMTP(host, port, timeout=10) as srv:
            srv.ehlo()
            srv.starttls(context=ctx)
            srv.ehlo()
            srv.login(user, app_key)
        print("OK")
        return True
    except smtplib.SMTPException as exc:
        print(f"FAILED\n  SMTP error: {exc}")
        return False
    except OSError as exc:
        print(f"FAILED\n  Connection error: {exc}")
        return False


# ---------------------------------------------------------------------------
# Write outputs
# ---------------------------------------------------------------------------


def write_creds(creds: dict) -> None:
    SECRETS_DIR.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "# OpenClaw mail-client credentials",
        "# chmod 600 - never commit this file",
        "",
    ]
    for key, value in creds.items():
        lines.append(f"{key}={value}")
    lines.append("")
    content = "\n".join(lines)

    CREDS_PATH.write_text(content, encoding="utf-8")
    CREDS_PATH.chmod(0o600)
    print(f"\n  Credentials written to: {CREDS_PATH} (chmod 600)")


def write_config(permissions: dict, defaults: dict) -> None:
    _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    config = {
        "allow_send": permissions["allow_send"],
        "allow_read": permissions["allow_read"],
        "allow_search": permissions["allow_search"],
        "allow_delete": permissions["allow_delete"],
        "smtp_port": defaults["smtp_port"],
        "imap_port": defaults["imap_port"],
        "mail_from": defaults["mail_from"],
        "default_folder": defaults["default_folder"],
        "max_results": defaults["max_results"],
    }
    with open(CONFIG_PATH, "w", encoding="utf-8") as fh:
        json.dump(config, fh, indent=2)
        fh.write("\n")
    print(f"  Config written to:       {CONFIG_PATH}")


# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------


def cleanup() -> None:
    """Remove all persistent files written by this skill (credentials + config)."""
    print("Removing mail-client skill persistent files...")
    removed = []
    for path in [CREDS_PATH, CONFIG_PATH]:
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


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    if "--cleanup" in sys.argv:
        cleanup()
        return

    print()
    print("=" * 60)
    print("  OpenClaw mail-client - Setup Wizard")
    print("=" * 60)

    creds = step_credentials()
    permissions = step_permissions()
    defaults = step_defaults(mail_user=creds.get("MAIL_USER", ""))

    print()
    hr("=")
    print("  Running connection tests")
    hr("=")

    imap_ok = test_imap(creds, defaults)
    smtp_ok = test_smtp(creds, defaults) if permissions["allow_send"] else True

    if not imap_ok:
        print("\n  Warning: IMAP test failed. Check host/port/credentials.")
        proceed = prompt_bool("Continue and save credentials anyway", default=False)
        if not proceed:
            print("  Setup aborted.")
            sys.exit(1)

    if not smtp_ok:
        print("\n  Warning: SMTP test failed. Check host/port/credentials.")
        proceed = prompt_bool("Continue and save credentials anyway", default=False)
        if not proceed:
            print("  Setup aborted.")
            sys.exit(1)

    print()
    hr("=")
    print("  Writing files")
    hr("=")

    write_creds(creds)
    write_config(permissions, defaults)

    print()
    hr("=")
    print("  Setup complete!")
    print("  Run  python3 scripts/init.py  to validate all capabilities.")
    hr("=")
    print()


if __name__ == "__main__":
    main()
