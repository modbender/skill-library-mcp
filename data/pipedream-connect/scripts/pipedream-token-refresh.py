#!/usr/bin/env python3
"""
Pipedream Token Refresh Script

Refreshes OAuth access tokens for all Pipedream MCP servers in mcporter.json.
Tokens expire after 1 hour, so this should run at least every 50 minutes.

Setup:
  1. Copy to ~/openclaw/scripts/pipedream-token-refresh.py
  2. Add cron job: */45 * * * * python3 ~/openclaw/scripts/pipedream-token-refresh.py

Usage:
  python3 pipedream-token-refresh.py [--config PATH] [--quiet]

Options:
  --config PATH      Path to mcporter.json (default: ~/.openclaw/workspace/config/mcporter.json)
  --quiet            Only output errors

Credential Sources (in priority order):
  1. OpenClaw vault  — ~/.openclaw/secrets.json  (keys: PIPEDREAM_CLIENT_ID, PIPEDREAM_CLIENT_SECRET)
  2. Legacy file     — ~/.openclaw/workspace/config/pipedream-credentials.json  (pre-v1.3 fallback)
  3. Legacy mcporter — PIPEDREAM_CLIENT_ID / PIPEDREAM_CLIENT_SECRET in mcporter.json env (pre-v1.2 fallback)
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

# ── Paths ─────────────────────────────────────────────────────────────────────

DEFAULT_CONFIG    = Path.home() / ".openclaw" / "workspace" / "config" / "mcporter.json"
CREDENTIALS_FILE  = Path.home() / ".openclaw" / "workspace" / "config" / "pipedream-credentials.json"
VAULT_FILE        = Path.home() / ".openclaw" / "secrets.json"
LOG_FILE          = Path.home() / ".openclaw" / "logs" / "pipedream-token-refresh.log"

# ── Argument parsing ──────────────────────────────────────────────────────────

quiet = "--quiet" in sys.argv or "-q" in sys.argv
config_path = DEFAULT_CONFIG

for i, arg in enumerate(sys.argv[1:], 1):
    if arg in ("--config", "-c") and i < len(sys.argv) - 1:
        config_path = Path(sys.argv[i + 1])


# ── Logging ───────────────────────────────────────────────────────────────────

def log(message: str, is_error: bool = False):
    if quiet and not is_error:
        return
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().isoformat()
    entry = f"[{timestamp}] {message}\n"
    try:
        with open(LOG_FILE, "a") as f:
            f.write(entry)
    except Exception:
        pass
    if is_error:
        print(entry.strip(), file=sys.stderr)
    else:
        print(entry.strip())


# ── Token request ─────────────────────────────────────────────────────────────

def get_new_token(client_id: str, client_secret: str) -> dict:
    """Request a new access token from Pipedream."""
    url = "https://api.pipedream.com/v1/oauth/token"
    data = json.dumps({
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    }).encode("utf-8")
    req = Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else str(e)
        raise Exception(f"HTTP {e.code}: {error_body}")
    except URLError as e:
        raise Exception(f"URL Error: {e.reason}")


# ── Credential resolution ─────────────────────────────────────────────────────

def get_credentials_from_vault() -> tuple:
    """Read clientId/clientSecret from ~/.openclaw/secrets.json (OpenClaw vault)."""
    if not VAULT_FILE.exists():
        return None, None
    try:
        vault = json.loads(VAULT_FILE.read_text())
        client_id = vault.get("PIPEDREAM_CLIENT_ID")
        client_secret = vault.get("PIPEDREAM_CLIENT_SECRET")
        if client_id and client_secret:
            log(f"Loaded credentials from vault ({VAULT_FILE})")
            return client_id, client_secret
    except Exception as e:
        log(f"WARNING: Failed to read vault {VAULT_FILE}: {e}")
    return None, None


def get_credentials() -> tuple:
    """Get Pipedream credentials.

    Priority:
      1. OpenClaw vault  (~/.openclaw/secrets.json)         ← primary since v1.3
      2. pipedream-credentials.json                         ← legacy fallback
      3. mcporter.json env vars                             ← legacy fallback
    """
    # 1. Vault
    client_id, client_secret = get_credentials_from_vault()
    if client_id and client_secret:
        return client_id, client_secret

    # 2. Legacy credentials file
    if CREDENTIALS_FILE.exists():
        try:
            creds = json.loads(CREDENTIALS_FILE.read_text())
            if creds.get("clientId") and creds.get("clientSecret"):
                log(f"Loaded credentials from {CREDENTIALS_FILE} (legacy — run gateway once to migrate to vault)")
                return creds["clientId"], creds["clientSecret"]
        except Exception as e:
            log(f"WARNING: Failed to read {CREDENTIALS_FILE}: {e}")

    # 3. Legacy mcporter env vars
    if config_path.exists():
        try:
            config = json.loads(config_path.read_text())
            for name, server in config.get("mcpServers", {}).items():
                if name.startswith("pipedream"):
                    env = server.get("env", {})
                    cid = env.get("PIPEDREAM_CLIENT_ID")
                    csec = env.get("PIPEDREAM_CLIENT_SECRET")
                    if cid and csec:
                        log("Loaded credentials from mcporter env (legacy)")
                        return cid, csec
        except Exception:
            pass

    return None, None


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if not config_path.exists():
        log(f"ERROR: mcporter config not found: {config_path}", is_error=True)
        sys.exit(1)

    client_id, client_secret = get_credentials()
    if not client_id or not client_secret:
        log("ERROR: No Pipedream credentials found.", is_error=True)
        log(f"  Vault:       {VAULT_FILE}", is_error=True)
        log(f"  Credentials: {CREDENTIALS_FILE}", is_error=True)
        log(f"  mcporter:    {config_path}", is_error=True)
        sys.exit(1)

    log("Requesting new access token...")
    try:
        response = get_new_token(client_id, client_secret)
    except Exception as e:
        log(f"ERROR: Failed to get token: {e}", is_error=True)
        sys.exit(1)

    new_token = response.get("access_token")
    if not new_token:
        log(f"ERROR: No access_token in response: {response}", is_error=True)
        sys.exit(1)

    expires_in = response.get("expires_in", 3600)
    log(f"New token obtained, expires in {expires_in}s")

    config = json.loads(config_path.read_text())
    updated = 0
    for name, server in config.get("mcpServers", {}).items():
        if name.startswith("pipedream"):
            if "headers" not in server:
                server["headers"] = {}
            server["headers"]["Authorization"] = f"Bearer {new_token}"
            updated += 1

    if updated == 0:
        log("WARNING: No Pipedream servers found in mcporter config")
        sys.exit(0)

    # Atomic write
    temp = config_path.with_suffix(".tmp")
    temp.write_text(json.dumps(config, indent=2))
    temp.rename(config_path)

    log(f"Updated {updated} Pipedream server(s) with new token")


if __name__ == "__main__":
    main()
