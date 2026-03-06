"""Secure credential storage backends.

Retrieves passwords and secrets from secure stores instead of storing
them as plain text in config files.  Supported backends:

* **1Password CLI** (``op://vault/item/field``)
* **macOS Keychain** (``keychain://service/account``)
* **Environment variable** (``env://VAR_NAME``)
* **Plain text** — returned as-is (with a logged warning)

Usage in config.yaml::

    accounts:
      work:
        imap:
          host: imap.company.com
          password: "op://Work/IMAP/password"     # 1Password
        smtp:
          host: smtp.company.com
          password: "keychain://smtp.company.com/alice"  # macOS Keychain
      personal:
        imap:
          password: "env://GMAIL_APP_PASSWORD"     # env var
"""

from __future__ import annotations

import logging
import platform
import shutil
import subprocess

logger = logging.getLogger("clawMail.credentials")


def resolve(value: str) -> str:
    """Resolve a credential reference to its secret value.

    If *value* matches a known URI scheme the secret is fetched from the
    corresponding backend.  Otherwise it is returned as-is (plain text)
    with a warning.
    """
    if not value:
        return value

    if value.startswith("op://"):
        return _resolve_1password(value)

    if value.startswith("keychain://"):
        return _resolve_keychain(value)

    if value.startswith("env://"):
        return _resolve_env(value)

    # Plain-text fallback
    if len(value) > 4:
        logger.warning(
            "Password appears to be stored as plain text in config. "
            "Consider using op://, keychain://, or env:// for secure storage."
        )
    return value


# ── 1Password CLI ────────────────────────────────────────────────────


def _resolve_1password(ref: str) -> str:
    """Fetch a secret via the 1Password CLI (``op read``)."""
    op_path = shutil.which("op")
    if op_path is None:
        raise RuntimeError(
            f"1Password CLI ('op') not found on PATH. "
            f"Install it to use {ref!r} credential references. "
            f"See https://developer.1password.com/docs/cli/get-started/"
        )
    try:
        result = subprocess.run(
            [op_path, "read", ref, "--no-newline"],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"1Password CLI failed for {ref!r}: {result.stderr.strip()}"
            )
        return result.stdout
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"1Password CLI timed out reading {ref!r}")


# ── macOS Keychain ───────────────────────────────────────────────────


def _resolve_keychain(ref: str) -> str:
    """Fetch a secret from the macOS Keychain via ``security``."""
    if platform.system() != "Darwin":
        raise RuntimeError(
            f"keychain:// credential references are only supported on macOS. "
            f"Current platform: {platform.system()}"
        )

    # Parse keychain://service/account
    path = ref[len("keychain://"):]
    parts = path.split("/", 1)
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise ValueError(
            f"Invalid keychain reference: {ref!r}. "
            f"Expected format: keychain://service-name/account-name"
        )
    service, account = parts

    security_path = shutil.which("security")
    if security_path is None:
        raise RuntimeError("macOS 'security' command not found on PATH")

    try:
        result = subprocess.run(
            [
                security_path, "find-generic-password",
                "-s", service, "-a", account, "-w",
            ],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"macOS Keychain lookup failed for service={service!r}, "
                f"account={account!r}: {result.stderr.strip()}"
            )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        raise RuntimeError(
            f"macOS Keychain lookup timed out for {ref!r}"
        )


# ── Environment variables ────────────────────────────────────────────


def _resolve_env(ref: str) -> str:
    """Read a secret from an environment variable."""
    import os

    var_name = ref[len("env://"):]
    if not var_name:
        raise ValueError(f"Empty env variable name in {ref!r}")

    value = os.environ.get(var_name)
    if value is None:
        raise RuntimeError(
            f"Environment variable {var_name!r} is not set "
            f"(referenced by {ref!r})"
        )
    return value
