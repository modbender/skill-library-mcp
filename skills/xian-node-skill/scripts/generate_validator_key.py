#!/usr/bin/env python3
"""Generate a new Xian validator key pair."""

import argparse
import base64
import hashlib
import json
import secrets


def generate_keypair():
    """Generate ed25519 keypair using PyNaCl."""
    try:
        from nacl.signing import SigningKey
    except ImportError:
        print("Error: PyNaCl not installed. Run: pip install pynacl")
        raise SystemExit(1)
    
    sk = SigningKey(secrets.token_bytes(32))
    pk = sk.verify_key
    
    return sk.encode().hex(), pk.encode().hex()


def pubkey_to_address(pubkey_hex: str) -> str:
    """Convert ed25519 pubkey to CometBFT validator address."""
    pubkey_bytes = bytes.fromhex(pubkey_hex)
    sha = hashlib.sha256(pubkey_bytes).digest()
    return sha[:20].hex().upper()


def pubkey_to_base64(pubkey_hex: str) -> str:
    """Convert hex pubkey to base64 for genesis file."""
    return base64.b64encode(bytes.fromhex(pubkey_hex)).decode()


def main():
    parser = argparse.ArgumentParser(description="Generate Xian validator keys")
    parser.add_argument(
        "--name",
        default="validator",
        help="Validator name for genesis entry"
    )
    parser.add_argument(
        "--power",
        default="10",
        help="Voting power (default: 10)"
    )
    parser.add_argument(
        "--genesis-entry",
        action="store_true",
        help="Output genesis validator entry JSON"
    )
    args = parser.parse_args()

    private_key, public_key = generate_keypair()
    address = pubkey_to_address(public_key)
    pubkey_b64 = pubkey_to_base64(public_key)

    if args.genesis_entry:
        entry = {
            "address": address,
            "pub_key": {
                "type": "tendermint/PubKeyEd25519",
                "value": pubkey_b64
            },
            "power": args.power,
            "name": args.name
        }
        print("Genesis validator entry:")
        print(json.dumps(entry, indent=2))
        print(f"\nPrivate key (keep secret!): {private_key}")
    else:
        print(f"Private key: {private_key}")
        print(f"Public key:  {public_key}")
        print(f"Address:     {address}")
        print(f"Base64 key:  {pubkey_b64}")
        print(f"\nUse --genesis-entry for ready-to-use genesis JSON")


if __name__ == "__main__":
    main()
