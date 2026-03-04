#!/usr/bin/env python3
"""
SECURITY-CRITICAL: Solana wallet generator for OpenClaw agents.

- Private key is written ONLY to a file (never to stdout/stderr)
- Only the PUBLIC KEY is printed to stdout
- Designed to be called via subprocess — DO NOT import this module
- DO NOT install 'solana-keypair' package (known supply chain attack)
- Pin solders version: pip install "solders>=0.21.0,<1.0"

Usage:
    python3 create_wallet.py [--output PATH]

Output (stdout): Solana public key (Base58)
Side effects: Creates wallet file at PATH with chmod 600
"""

import argparse
import json
import os
import stat
import sys


WALLET_FILE_HEADER = (
    "# DANGER: This file contains a Solana private key.\n"
    "# NEVER read this file in conversation or print its contents.\n"
    "# Use sign_and_send.py to perform transactions instead.\n"
)


def log(msg: str) -> None:
    """Log to stderr (safe — never contains key material)."""
    print(f"[create_wallet] {msg}", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a Solana wallet securely")
    parser.add_argument(
        "--output", "-o",
        default=os.path.expanduser("memory/clawbet/.wallet"),
        help="Path to save wallet file (default: memory/clawbet/.wallet)",
    )
    args = parser.parse_args()
    wallet_path = os.path.expanduser(args.output)

    # If wallet already exists, output existing public key without overwriting
    if os.path.exists(wallet_path):
        try:
            existing_kp = _load_keypair(wallet_path)
            pubkey = str(existing_kp.pubkey())
            log(f"Wallet already exists at {wallet_path}")
            log(f"Public key: {pubkey}")
            print(pubkey)  # stdout: only public key
            return 0
        except Exception as e:
            log(f"ERROR: Existing wallet file is corrupted: {e}")
            log("Delete the file manually and re-run to create a new wallet.")
            return 1

    # Ensure parent directory exists
    parent = os.path.dirname(wallet_path)
    if parent:
        os.makedirs(parent, exist_ok=True)

    try:
        # Import here to catch missing dependency early
        from solders.keypair import Keypair  # type: ignore[import-untyped]
    except ImportError:
        log("ERROR: solders not installed. Run: pip install \"solders>=0.21.0,<1.0\"")
        log("WARNING: Do NOT install 'solana-keypair' — it is a known malicious package.")
        return 1

    # Generate keypair (uses OS-level CSPRNG entropy)
    kp = Keypair()
    pubkey = str(kp.pubkey())
    raw_bytes = list(bytes(kp))  # 64-byte array: [32 private + 32 public]

    # Write to file atomically (tmp + rename)
    # SECURITY: Use os.open with O_CREAT|O_EXCL and mode 0o600 to prevent
    # TOCTOU race condition — file is created with restricted permissions from the start
    tmp_path = wallet_path + ".tmp"
    try:
        fd = os.open(tmp_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w") as f:
            f.write(WALLET_FILE_HEADER)
            json.dump(raw_bytes, f)
            f.write("\n")
        os.rename(tmp_path, wallet_path)
    except Exception as e:
        # Clean up temp file on failure
        try:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
        except OSError:
            pass
        log(f"ERROR: Failed to write wallet file: {e}")
        return 1

    log(f"Wallet created at {wallet_path} (permissions: 600)")
    log(f"Public key: {pubkey}")

    # stdout: ONLY the public key (this is what the LLM context sees)
    print(pubkey)
    return 0


def _load_keypair(path: str):
    """Load keypair from wallet file (JSON array format)."""
    from solders.keypair import Keypair  # type: ignore[import-untyped]

    with open(path) as f:
        content = f.read()

    # Skip comment lines (WALLET_FILE_HEADER)
    lines = [line for line in content.strip().split("\n") if not line.startswith("#")]
    raw = json.loads("".join(lines))

    if not isinstance(raw, list) or len(raw) != 64:
        raise ValueError(f"Invalid wallet file: expected 64-byte array, got {type(raw).__name__} of length {len(raw) if isinstance(raw, list) else 'N/A'}")
    if not all(isinstance(b, int) and 0 <= b <= 255 for b in raw):
        raise ValueError("Invalid wallet file: all values must be integers 0-255")

    return Keypair.from_bytes(bytes(raw))


if __name__ == "__main__":
    sys.exit(main())
