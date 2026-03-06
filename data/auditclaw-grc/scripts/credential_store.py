#!/usr/bin/env python3
"""Secure credential storage for AuditClaw GRC integrations.

Stores credential metadata in SQLite, secrets on filesystem.
"""

import json
import os
import sqlite3
import stat
from datetime import datetime

CREDENTIALS_DIR = os.path.expanduser("~/.openclaw/grc/credentials")

VALID_PROVIDERS = {"aws", "github", "azure", "gcp", "idp"}


def _validate_provider(provider):
    """Validate provider name against allowlist. Raises ValueError if invalid."""
    if not provider or not isinstance(provider, str):
        raise ValueError(f"Invalid provider: {provider}")
    if provider not in VALID_PROVIDERS:
        raise ValueError(f"Unknown provider '{provider}'. Must be one of: {', '.join(sorted(VALID_PROVIDERS))}")


def _ensure_dir(provider):
    """Create secure credential directory for a provider."""
    _validate_provider(provider)
    provider_dir = os.path.join(CREDENTIALS_DIR, provider)
    os.makedirs(provider_dir, mode=0o700, exist_ok=True)
    return provider_dir


def _write_secret(provider, filename, data):
    """Write secret data to a file with restrictive permissions."""
    provider_dir = _ensure_dir(provider)
    path = os.path.realpath(os.path.join(provider_dir, filename))
    allowed_base = os.path.realpath(CREDENTIALS_DIR)
    if not path.startswith(allowed_base + os.sep):
        raise ValueError(f"Invalid credential path: write target outside credentials directory")
    # Write to temp file first, then rename (atomic)
    tmp_path = path + ".tmp"
    with open(tmp_path, "w") as f:
        f.write(data if isinstance(data, str) else json.dumps(data))
    os.chmod(tmp_path, stat.S_IRUSR | stat.S_IWUSR)  # 0o600
    os.replace(tmp_path, path)
    return path


def _read_secret(path):
    """Read secret data from a file."""
    if not path or not os.path.exists(path):
        return None
    real_path = os.path.realpath(path)
    allowed_base = os.path.realpath(CREDENTIALS_DIR)
    if not real_path.startswith(allowed_base + os.sep) and real_path != allowed_base:
        return None
    with open(path, "r") as f:
        content = f.read()
    try:
        return json.loads(content)
    except (json.JSONDecodeError, ValueError):
        return content


def _delete_secret(path):
    """Securely delete a secret file by overwriting before removal."""
    if path and os.path.exists(path):
        real_path = os.path.realpath(path)
        allowed_base = os.path.realpath(CREDENTIALS_DIR)
        if not real_path.startswith(allowed_base + os.sep):
            return
        try:
            size = os.path.getsize(path)
            with open(path, 'wb') as f:
                f.write(os.urandom(size))
                f.flush()
                os.fsync(f.fileno())
        except OSError:
            pass
        os.remove(path)


def save_credential(db_path, provider, auth_method, config, secret_data=None, expires_at=None):
    """Save or update credential for a provider.

    Args:
        db_path: Path to SQLite database
        provider: Provider name (aws, github, azure, gcp, idp)
        auth_method: Auth method (iam_role, github_app, service_principal, etc.)
        config: Dict of non-secret config (role ARN, app ID, tenant ID, etc.)
        secret_data: Optional secret data to store on disk (key file, certificate, etc.)
        expires_at: Optional ISO timestamp when credential expires

    Returns:
        dict with status, id, provider, auth_method
    """
    _validate_provider(provider)
    now = datetime.now().isoformat(timespec="seconds")
    config_json = json.dumps(config) if isinstance(config, dict) else config

    credential_path = None
    if secret_data is not None:
        # Determine filename based on auth method
        filenames = {
            "iam_role": "session.json",
            "access_key": "credentials.json",
            "github_app": "private-key.pem",
            "personal_token": "token.txt",
            "service_principal": "certificate.pem",
            "client_secret": "secret.txt",
            "service_account": "key.json",
            "sa_impersonation": "config.json",
            "oauth2": "oauth.json",
            "api_token": "token.txt",
            "domain_delegation": "sa-key.json",
        }
        filename = filenames.get(auth_method, "credential.json")
        credential_path = _write_secret(provider, filename, secret_data)

    conn = sqlite3.connect(db_path, timeout=10)
    try:
        conn.row_factory = sqlite3.Row
        # Check if credential exists for this provider
        existing = conn.execute(
            "SELECT id, credential_path FROM integration_credentials WHERE provider = ?",
            (provider,)
        ).fetchone()

        if existing:
            # Update existing
            old_path = existing["credential_path"]
            if credential_path and old_path and old_path != credential_path:
                _delete_secret(old_path)

            conn.execute(
                """UPDATE integration_credentials
                   SET auth_method = ?, config = ?, credential_path = COALESCE(?, credential_path),
                       status = 'active', updated_at = ?, expires_at = ?
                   WHERE id = ?""",
                (auth_method, config_json, credential_path, now, expires_at, existing["id"])
            )
            conn.commit()
            return {
                "status": "updated",
                "id": existing["id"],
                "provider": provider,
                "auth_method": auth_method,
            }
        else:
            # Insert new
            conn.execute(
                """INSERT INTO integration_credentials
                   (provider, auth_method, config, credential_path, status, created_at, updated_at, expires_at)
                   VALUES (?, ?, ?, ?, 'active', ?, ?, ?)""",
                (provider, auth_method, config_json, credential_path, now, now, expires_at)
            )
            conn.commit()
            cred_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            return {
                "status": "created",
                "id": cred_id,
                "provider": provider,
                "auth_method": auth_method,
            }
    finally:
        conn.close()


def get_credential(db_path, provider):
    """Retrieve credential for a provider.

    Returns:
        dict with status, provider, auth_method, config, secret (if available), or None if not found
    """
    conn = sqlite3.connect(db_path, timeout=10)
    try:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM integration_credentials WHERE provider = ? AND status != 'deleted' ORDER BY id DESC LIMIT 1",
            (provider,)
        ).fetchone()

        if not row:
            return None

        # Update last_used
        now = datetime.now().isoformat(timespec="seconds")
        conn.execute(
            "UPDATE integration_credentials SET last_used = ? WHERE id = ?",
            (now, row["id"])
        )
        conn.commit()

        config = row["config"]
        try:
            config = json.loads(config)
        except (json.JSONDecodeError, ValueError, TypeError):
            pass

        result = {
            "id": row["id"],
            "provider": row["provider"],
            "auth_method": row["auth_method"],
            "config": config,
            "credential_path": row["credential_path"],
            "status": row["status"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "last_used": now,
            "expires_at": row["expires_at"],
        }

        # Read secret if path exists (only expose masked preview)
        secret = _read_secret(row["credential_path"])
        if secret is not None:
            secret_str = secret if isinstance(secret, str) else json.dumps(secret)
            result["secret_preview"] = secret_str[:4] + "..." + secret_str[-4:] if len(secret_str) > 12 else "****"
            result["secret_available"] = True

        return result
    finally:
        conn.close()


def delete_credential(db_path, provider):
    """Delete credential for a provider (DB record + secret file).

    Returns:
        dict with status
    """
    conn = sqlite3.connect(db_path, timeout=10)
    try:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT id, credential_path FROM integration_credentials WHERE provider = ?",
            (provider,)
        ).fetchone()

        if not row:
            return {"status": "not_found", "provider": provider}

        # Delete secret file
        _delete_secret(row["credential_path"])

        # Delete DB record
        conn.execute("DELETE FROM integration_credentials WHERE id = ?", (row["id"],))
        conn.commit()

        return {"status": "deleted", "id": row["id"], "provider": provider}
    finally:
        conn.close()


def rotate_credential(db_path, provider, new_secret_data):
    """Rotate the secret for an existing credential.

    Returns:
        dict with status
    """
    conn = sqlite3.connect(db_path, timeout=10)
    try:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT id, auth_method, credential_path FROM integration_credentials WHERE provider = ?",
            (provider,)
        ).fetchone()

        if not row:
            return {"status": "not_found", "provider": provider}

        # Write new secret to same path
        if row["credential_path"]:
            tmp_path = row["credential_path"] + ".tmp"
            data = new_secret_data if isinstance(new_secret_data, str) else json.dumps(new_secret_data)
            with open(tmp_path, "w") as f:
                f.write(data)
            os.chmod(tmp_path, stat.S_IRUSR | stat.S_IWUSR)
            os.replace(tmp_path, row["credential_path"])
        else:
            # No existing path — create one
            filenames = {
                "iam_role": "session.json",
                "github_app": "private-key.pem",
                "service_principal": "certificate.pem",
                "service_account": "key.json",
                "oauth2": "oauth.json",
                "api_token": "token.txt",
            }
            filename = filenames.get(row["auth_method"], "credential.json")
            new_path = _write_secret(provider, filename, new_secret_data)
            conn.execute(
                "UPDATE integration_credentials SET credential_path = ? WHERE id = ?",
                (new_path, row["id"])
            )

        now = datetime.now().isoformat(timespec="seconds")
        conn.execute(
            "UPDATE integration_credentials SET updated_at = ?, status = 'active' WHERE id = ?",
            (now, row["id"])
        )
        conn.commit()

        return {"status": "rotated", "id": row["id"], "provider": provider}
    finally:
        conn.close()


def list_credentials(db_path):
    """List all stored credentials (without secrets).

    Returns:
        list of credential dicts (no secret data included)
    """
    conn = sqlite3.connect(db_path, timeout=10)
    try:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT id, provider, auth_method, config, status, created_at, updated_at, last_used, expires_at FROM integration_credentials ORDER BY provider"
        ).fetchall()

        credentials = []
        for row in rows:
            config = row["config"]
            try:
                config = json.loads(config)
            except (json.JSONDecodeError, ValueError, TypeError):
                pass

            credentials.append({
                "id": row["id"],
                "provider": row["provider"],
                "auth_method": row["auth_method"],
                "config": config,
                "status": row["status"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "last_used": row["last_used"],
                "expires_at": row["expires_at"],
            })

        return credentials
    finally:
        conn.close()
