#!/usr/bin/env python3
"""
Jackal Memory client for AI agents.

Usage:
  python client.py keygen       — show your current encryption key (or generate one)
  python client.py save <key> <content>
  python client.py load <key>
  python client.py usage        — show storage quota usage

Auth: reads JACKAL_MEMORY_API_KEY from environment.

Requires: pip install cryptography
"""

import base64
import json
import os
import pathlib
import sys
import urllib.error
import urllib.request

BASE_URL = "https://web-production-5cce7.up.railway.app"

_KEY_FILE = pathlib.Path.home() / ".config" / "jackal-memory" / "key"


# ── Encryption (mandatory) ────────────────────────────────────────────────────

def _encryption_key() -> bytes:
    """
    Return the AES-256 encryption key. Resolution order:
      1. JACKAL_MEMORY_ENCRYPTION_KEY env var
      2. ~/.config/jackal-memory/key file
      3. Auto-generate, save to key file, print one-time notice
    Encryption is always on — there is no opt-out.
    """
    key_hex = os.environ.get("JACKAL_MEMORY_ENCRYPTION_KEY", "").strip()
    if key_hex:
        return bytes.fromhex(key_hex)

    if _KEY_FILE.exists():
        return bytes.fromhex(_KEY_FILE.read_text().strip())

    key_hex = os.urandom(32).hex()
    _KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
    _KEY_FILE.write_text(key_hex)
    print(
        "\n[jackal-memory] Generated a new encryption key and saved it to:\n"
        f"  {_KEY_FILE}\n\n"
        "Your memories are encrypted with this key. Back it up:\n"
        f"  export JACKAL_MEMORY_ENCRYPTION_KEY={key_hex}\n",
        file=sys.stderr,
    )
    return bytes.fromhex(key_hex)


def _encrypt(plaintext: str) -> str:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    key   = _encryption_key()
    nonce = os.urandom(12)
    ct    = AESGCM(key).encrypt(nonce, plaintext.encode(), None)
    return base64.b64encode(nonce + ct).decode()


def _decrypt(ciphertext_b64: str) -> str:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    key  = _encryption_key()
    data = base64.b64decode(ciphertext_b64)
    nonce, ct = data[:12], data[12:]
    return AESGCM(key).decrypt(nonce, ct, None).decode()


# ── API ───────────────────────────────────────────────────────────────────────

def _api_key() -> str:
    key = os.environ.get("JACKAL_MEMORY_API_KEY", "")
    if not key:
        print("Error: JACKAL_MEMORY_API_KEY is not set.", file=sys.stderr)
        sys.exit(1)
    return key


def _request(method: str, path: str, body: dict | None = None) -> dict:
    url  = BASE_URL + path
    data = json.dumps(body).encode() if body else None
    req  = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {_api_key()}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        error = json.loads(e.read())
        print(f"Error {e.code}: {error.get('detail', e.reason)}", file=sys.stderr)
        sys.exit(1)


def cmd_keygen() -> None:
    key = _encryption_key()
    key_hex = key.hex()
    print(f"\nActive encryption key:\n\n  {key_hex}\n")
    print("Set this in your environment to use the same key on other machines:")
    print(f"  export JACKAL_MEMORY_ENCRYPTION_KEY={key_hex}\n")
    print("Keep this key safe — lose it and your encrypted memories are unrecoverable.")


def cmd_save(key: str, content: str) -> None:
    result   = _request("POST", "/save", {"key": key, "content": _encrypt(content)})
    used_mb  = result.get("bytes_used", 0) / 1024 ** 2
    quota_mb = result.get("quota_bytes", 0) / 1024 ** 2
    print(f"Saved — key: {result['key']}  cid: {result['cid']}  "
          f"used: {used_mb:.1f} MB / {quota_mb:.0f} MB")
    for w in result.get("warnings", []):
        print(f"WARNING: {w['message']}", file=sys.stderr)


def cmd_load(key: str) -> None:
    result = _request("GET", f"/load/{key}")
    print(_decrypt(result["content"]))


def cmd_usage() -> None:
    data     = _request("GET", "/usage")
    used_mb  = data["bytes_used"] / 1024 ** 2
    quota_mb = data["quota_bytes"] / 1024 ** 2
    pct      = data["percent_used"] * 100
    print(f"Storage: {used_mb:.1f} MB / {quota_mb:.0f} MB ({pct:.1f}% used)")


def main() -> None:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(0)

    cmd = args[0]

    if cmd == "keygen" and len(args) == 1:
        cmd_keygen()
    elif cmd == "save" and len(args) == 3:
        cmd_save(args[1], args[2])
    elif cmd == "load" and len(args) == 2:
        cmd_load(args[1])
    elif cmd == "usage" and len(args) == 1:
        cmd_usage()
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
