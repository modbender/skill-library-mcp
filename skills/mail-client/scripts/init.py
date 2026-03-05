#!/usr/bin/env python3
"""
init.py - Connection and permission validation for OpenClaw mail-client skill.
Tests each enabled capability and reports pass/fail/skip.
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
CREDS_PATH  = pathlib.Path.home() / ".openclaw" / "secrets" / "mail_creds"

# ---------------------------------------------------------------------------
# Results reporter
# ---------------------------------------------------------------------------


class Results:
    """Accumulate and display check results."""

    def __init__(self) -> None:
        self._items: list[tuple[str, str, str]] = []  # (status, name, detail)

    def ok(self, name: str, detail: str = "") -> None:
        self._items.append(("OK  ", name, detail))
        print(f"  [OK  ] {name}" + (f" - {detail}" if detail else ""))

    def fail(self, name: str, detail: str = "") -> None:
        self._items.append(("FAIL", name, detail))
        print(f"  [FAIL] {name}" + (f" - {detail}" if detail else ""), file=sys.stderr)

    def skip(self, name: str, detail: str = "") -> None:
        self._items.append(("SKIP", name, detail))
        print(f"  [SKIP] {name}" + (f" - {detail}" if detail else ""))

    def summary(self) -> bool:
        ok_count = sum(1 for s, _, _ in self._items if s == "OK  ")
        fail_count = sum(1 for s, _, _ in self._items if s == "FAIL")
        skip_count = sum(1 for s, _, _ in self._items if s == "SKIP")
        print()
        print(f"  Summary: {ok_count} OK, {fail_count} FAIL, {skip_count} SKIP")
        if fail_count > 0:
            print("  Status: FAILED")
            return False
        print("  Status: PASSED")
        return True


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------


def load_creds() -> dict:
    """Load credentials from file then override with environment variables."""
    creds: dict = {}
    if CREDS_PATH.exists():
        with open(CREDS_PATH, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, _, value = line.partition("=")
                creds[key.strip()] = value.strip()
    # Environment variables override file values
    for key in ("MAIL_USER", "MAIL_APP_KEY", "MAIL_SMTP_HOST", "MAIL_IMAP_HOST"):
        if key in os.environ:
            creds[key] = os.environ[key]
    if not creds.get("MAIL_USER") or not creds.get("MAIL_APP_KEY"):
        print(f"[error] Credentials missing. Provide env vars or run scripts/setup.py.")
        sys.exit(1)
    return creds


def load_config() -> dict:
    defaults = {
        "allow_send": False,
        "allow_read": False,
        "allow_search": False,
        "allow_delete": False,
        "default_folder": "INBOX",
        "max_results": 20,
    }
    if not CONFIG_PATH.exists():
        print(f"  [WARN] config.json not found, using defaults (all capabilities disabled)")
        return defaults
    with open(CONFIG_PATH, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    merged = dict(defaults)
    merged.update(data)
    return merged


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------


def check_creds_file(results: Results) -> None:
    if not CREDS_PATH.exists():
        results.fail("creds-file", f"not found: {CREDS_PATH}")
        return
    mode = oct(CREDS_PATH.stat().st_mode)[-3:]
    if mode == "600":
        results.ok("creds-file", f"exists, chmod {mode}")
    else:
        results.fail("creds-file", f"chmod {mode} (expected 600 - fix with: chmod 600 {CREDS_PATH})")


def check_config_file(results: Results) -> None:
    if CONFIG_PATH.exists():
        results.ok("config-file", str(CONFIG_PATH))
    else:
        results.skip("config-file", "not found (run setup.py to create)")


def check_imap_login(creds: dict, config: dict, results: Results) -> bool:
    if not config.get("allow_read", False) and not config.get("allow_search", False):
        results.skip("imap-login", "allow_read and allow_search are false")
        return False
    host = creds.get("MAIL_IMAP_HOST", "")
    port = int(config.get("imap_port", 993))
    user = creds.get("MAIL_USER", "")
    app_key = creds.get("MAIL_APP_KEY", "")
    try:
        ctx = ssl.create_default_context()
        imap = imaplib.IMAP4_SSL(host, port, ssl_context=ctx, timeout=10)
        imap.login(user, app_key)
        imap.logout()
        results.ok("imap-login", f"{user}@{host}:{port}")
        return True
    except imaplib.IMAP4.error as exc:
        results.fail("imap-login", str(exc))
        return False
    except OSError as exc:
        results.fail("imap-login", str(exc))
        return False


def check_imap_list(creds: dict, config: dict, results: Results) -> None:
    if not config.get("allow_read", False):
        results.skip("imap-list-folder", "allow_read is false")
        return
    host = creds.get("MAIL_IMAP_HOST", "")
    port = int(config.get("imap_port", 993))
    user = creds.get("MAIL_USER", "")
    app_key = creds.get("MAIL_APP_KEY", "")
    folder = config.get("default_folder", "INBOX")
    try:
        ctx = ssl.create_default_context()
        imap = imaplib.IMAP4_SSL(host, port, ssl_context=ctx)
        imap.login(user, app_key)
        status, data = imap.select(folder, readonly=True)
        imap.logout()
        if status == "OK":
            count = data[0].decode() if data and data[0] else "?"
            results.ok("imap-list-folder", f"{folder} ({count} messages)")
        else:
            results.fail("imap-list-folder", f"SELECT {folder} returned {status}")
    except (imaplib.IMAP4.error, OSError) as exc:
        results.fail("imap-list-folder", str(exc))


def check_imap_search(creds: dict, config: dict, results: Results) -> None:
    if not config.get("allow_search", False):
        results.skip("imap-search", "allow_search is false")
        return
    host = creds.get("MAIL_IMAP_HOST", "")
    port = int(config.get("imap_port", 993))
    user = creds.get("MAIL_USER", "")
    app_key = creds.get("MAIL_APP_KEY", "")
    folder = config.get("default_folder", "INBOX")
    try:
        ctx = ssl.create_default_context()
        imap = imaplib.IMAP4_SSL(host, port, ssl_context=ctx)
        imap.login(user, app_key)
        imap.select(folder, readonly=True)
        typ, data = imap.uid("search", None, "ALL")
        imap.logout()
        if typ == "OK":
            uids = data[0].split() if data and data[0] else []
            results.ok("imap-search", f"found {len(uids)} UIDs in {folder}")
        else:
            results.fail("imap-search", f"SEARCH returned {typ}")
    except (imaplib.IMAP4.error, OSError) as exc:
        results.fail("imap-search", str(exc))


def check_smtp(creds: dict, config: dict, results: Results) -> None:
    if not config.get("allow_send", False):
        results.skip("smtp-login", "allow_send is false")
        return
    host = creds.get("MAIL_SMTP_HOST", "")
    port = int(config.get("smtp_port", 587))
    user = creds.get("MAIL_USER", "")
    app_key = creds.get("MAIL_APP_KEY", "")
    try:
        ctx = ssl.create_default_context()
        with smtplib.SMTP(host, port, timeout=10) as srv:
            srv.ehlo()
            srv.starttls(context=ctx)
            srv.ehlo()
            srv.login(user, app_key)
        results.ok("smtp-login", f"{user}@{host}:{port} (STARTTLS)")
    except smtplib.SMTPException as exc:
        results.fail("smtp-login", str(exc))
    except OSError as exc:
        results.fail("smtp-login", str(exc))


def check_required_cred_keys(creds: dict, results: Results) -> None:
    required = [
        "MAIL_SMTP_HOST",
        "MAIL_IMAP_HOST",
        "MAIL_USER", "MAIL_APP_KEY",
    ]
    missing = [k for k in required if not creds.get(k)]
    if missing:
        results.fail("creds-keys", f"Missing keys: {', '.join(missing)}")
    else:
        results.ok("creds-keys", "all required keys present")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    print()
    print("=" * 60)
    print("  OpenClaw mail-client - Validation (init.py)")
    print("=" * 60)
    print()

    results = Results()

    creds = load_creds()
    config = load_config()

    check_creds_file(results)
    check_required_cred_keys(creds, results)
    check_config_file(results)

    imap_ok = check_imap_login(creds, config, results)
    if imap_ok:
        check_imap_list(creds, config, results)
        check_imap_search(creds, config, results)

    check_smtp(creds, config, results)

    print()
    print("-" * 60)
    passed = results.summary()
    print("=" * 60)
    print()

    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
