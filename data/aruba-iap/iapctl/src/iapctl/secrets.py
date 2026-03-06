"""Secret management for iapctl."""
import json
import os
from pathlib import Path
from typing import Optional, Dict

# In-memory secrets storage (for testing and simple setups)
_secrets_store: Dict[str, str] = {}


def load_secrets_file(secrets_file: Path) -> None:
    """Load secrets from a JSON file.

    Args:
        secrets_file: Path to JSON file with secrets
    """
    global _secrets_store

    if not secrets_file.exists():
        return

    try:
        with open(secrets_file) as f:
            _secrets_store.update(json.load(f))
    except Exception as e:
        raise ValueError(f"Failed to load secrets file: {e}")


def set_secret(name: str, value: str) -> None:
    """Set a secret in memory store.

    Args:
        name: Secret name
        value: Secret value
    """
    _secrets_store[name] = value


def get_secret(secret_ref: str) -> Optional[str]:
    """Resolve a secret reference.

    Supports formats:
    - `secret:<name>` - Look up in memory store
    - `env:<VAR_NAME>` - Look up in environment variables
    - `file:<path>` - Read from file
    - Plain value - Return as-is (not recommended)

    Args:
        secret_ref: Secret reference string

    Returns:
        Resolved secret value or None if not found
    """
    if not secret_ref:
        return None

    # Format: secret:<name>
    if secret_ref.startswith("secret:"):
        name = secret_ref[len("secret:"):]
        return _secrets_store.get(name)

    # Format: env:<VAR_NAME>
    if secret_ref.startswith("env:"):
        var_name = secret_ref[len("env:"):]
        return os.environ.get(var_name)

    # Format: file:<path>
    if secret_ref.startswith("file:"):
        file_path = Path(secret_ref[len("file:"):])
        try:
            return file_path.read_text().strip()
        except Exception:
            return None

    # Return plain value (not recommended but allowed)
    return secret_ref


def redact_secret(value: Optional[str]) -> str:
    """Redact a secret for logging.

    Args:
        value: Secret value to redact

    Returns:
        Redacted string
    """
    if not value or value in ["***REDACTED***", "None", ""]:
        return "***REDACTED***"

    return "***REDACTED***"


def redact_in_output(text: str, secrets: list[str]) -> str:
    """Redact secrets from command output.

    Args:
        text: Text to redact
        secrets: List of secret values to redact

    Returns:
        Redacted text
    """
    if not text or not secrets:
        return text

    result = text
    for secret in secrets:
        if secret and secret != "***REDACTED***":
            result = result.replace(secret, "***REDACTED***")

    return result
