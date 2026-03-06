"""Keychain helper — reads secrets from macOS Keychain via Python keyring.

All secrets stored with account='moltbot' in login keychain.
Works headlessly from LaunchAgents (GUI session context).
Falls back to file read if keyring unavailable.
"""

import os

ACCOUNT = "moltbot"
SECRETS_DIR = os.path.expanduser("~/.openclaw/secrets")


def get_secret(service, account=None, secrets_dir=None):
    """Get a secret from keychain. Falls back to secrets/ file."""
    acct = account or ACCOUNT
    sdir = secrets_dir or SECRETS_DIR
    try:
        import keyring
        value = keyring.get_password(service, acct)
        if value:
            return value
    except Exception:
        pass
    # Fallback: read from file
    path = os.path.join(sdir, service)
    try:
        with open(path) as f:
            return f.read().strip()
    except Exception:
        return ""
