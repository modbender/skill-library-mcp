#!/usr/bin/env python3
"""Credential helpers for Futu/MooMoo OpenD workflows."""
from __future__ import annotations

import getpass
import json
import os
import warnings

from cryptography.fernet import Fernet

try:
    import keyring
except Exception:  # pragma: no cover - environment dependent
    keyring = None

SERVICE_NAME = 'moomoo_api'
PASSWORD_KEY = 'password'
DEFAULT_CONFIG_PATH = "config.enc"
OPENCLAW_REF_ENV = "OPEND_PASSWORD_SECRET_REF"


def _warn_legacy(method: str):
    warnings.warn(
        (
            f"Credential method '{method}' bypasses OpenClaw secret refs. "
            "Prefer OPEND_PASSWORD_SECRET_REF or gateway-managed secret injection for hosted use."
        ),
        stacklevel=2,
    )


def parse_secret_ref(raw_ref: str) -> dict:
    try:
        ref = json.loads(raw_ref)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{OPENCLAW_REF_ENV} must be valid JSON") from exc
    if not isinstance(ref, dict):
        raise ValueError(f"{OPENCLAW_REF_ENV} must decode to an object")
    if "source" not in ref or "id" not in ref:
        raise ValueError(f"{OPENCLAW_REF_ENV} requires 'source' and 'id'")
    return ref


def get_password_openclaw_secret_ref():
    """Resolve an OpenClaw-compatible SecretRef from OPEND_PASSWORD_SECRET_REF."""
    raw_ref = os.getenv(OPENCLAW_REF_ENV)
    if not raw_ref:
        return None

    ref = parse_secret_ref(raw_ref)
    source = str(ref["source"]).lower()
    secret_id = str(ref["id"])

    if source == "env":
        return os.getenv(secret_id)

    if source in {"file", "exec"}:
        raise ValueError(
            f"{OPENCLAW_REF_ENV} source '{source}' must be resolved by the OpenClaw gateway before launching this skill"
        )

    raise ValueError(f"Unsupported SecretRef source: {source}")

def get_password_env():
    """Get password from environment variable MOOMOO_PASSWORD."""
    return os.getenv('MOOMOO_PASSWORD')

def get_password_keyring():
    """Get password from Python keyring."""
    if keyring is None:
        raise RuntimeError("python package 'keyring' is not available")

    password = keyring.get_password(SERVICE_NAME, PASSWORD_KEY)
    if not password:
        # Prompt to set it
        password = getpass.getpass("Enter MooMoo API password to store in keyring: ")
        keyring.set_password(SERVICE_NAME, PASSWORD_KEY, password)
    return password

def generate_key():
    """Generate a new encryption key."""
    return Fernet.generate_key()

def encrypt_data(data, key):
    """Encrypt data using the key."""
    f = Fernet(key)
    return f.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data, key):
    """Decrypt data using the key."""
    f = Fernet(key)
    return f.decrypt(encrypted_data.encode()).decode()

def save_encrypted_config(config, key, filepath=DEFAULT_CONFIG_PATH):
    """Save config to encrypted file."""
    json_data = json.dumps(config)
    encrypted = encrypt_data(json_data, key)
    with open(filepath, 'w') as f:
        f.write(encrypted)

def load_encrypted_config(key, filepath=DEFAULT_CONFIG_PATH):
    """Load config from encrypted file."""
    with open(filepath, 'r') as f:
        encrypted = f.read()
    json_data = decrypt_data(encrypted, key)
    return json.loads(json_data)

def get_password_config(key, filepath=DEFAULT_CONFIG_PATH):
    """Get password from encrypted config file."""
    config = load_encrypted_config(key, filepath)
    return config.get('password')

def get_password(method='openclaw'):
    """Get password using specified method."""
    if method in ('openclaw', 'secret-ref'):
        password = get_password_openclaw_secret_ref()
        if password:
            return password
        if method == 'secret-ref':
            raise ValueError(f"{OPENCLAW_REF_ENV} is not set for secret-ref method")
        password = get_password_env()
        if password:
            _warn_legacy('env')
            return password
        return None
    elif method == 'env':
        _warn_legacy('env')
        return get_password_env()
    elif method == 'keyring':
        _warn_legacy('keyring')
        return get_password_keyring()
    elif method == 'config':
        _warn_legacy('config')
        key = os.getenv('MOOMOO_CONFIG_KEY')
        if not key:
            raise ValueError("MOOMOO_CONFIG_KEY not set for config method")
        return get_password_config(key.encode('utf-8'))
    else:
        raise ValueError(f"Unknown method: {method}")

# Example usage:
# password = get_password('env')
# or
# password = get_password('keyring')
# or
# password = get_password('config')
