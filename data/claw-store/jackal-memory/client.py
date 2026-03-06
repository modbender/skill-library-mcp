#!/usr/bin/env python3
"""
Jackal Memory client for AI agents.

Usage:
  python client.py keygen           — show/generate AES encryption key
  python client.py walletgen        — generate Jackal wallet and register with API
  python client.py wallet           — show current Jackal wallet address
  python client.py save <key> <content>
  python client.py load <key>
  python client.py usage            — show storage quota usage

Auth: reads JACKAL_MEMORY_API_KEY from environment.

Requires: pip install cryptography
"""

import base64
import hashlib
import hmac
import json
import os
import pathlib
import struct
import sys
import urllib.error
import urllib.request

BASE_URL = "https://web-production-5cce7.up.railway.app"

_KEY_FILE    = pathlib.Path.home() / ".config" / "jackal-memory" / "key"
_WALLET_FILE = pathlib.Path.home() / ".config" / "jackal-memory" / "jackal-mnemonic"


# ── Encryption (mandatory) ────────────────────────────────────────────────────

def _encryption_key() -> bytes:
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


# ── Jackal wallet (BIP39/BIP44 — no extra dependencies) ──────────────────────

_BIP39_WORDS = None  # lazy-loaded

def _load_wordlist() -> list:
    global _BIP39_WORDS
    if _BIP39_WORDS is None:
        # BIP39 English wordlist embedded as a compact resource.
        # Fetched once from the canonical source and cached in memory.
        try:
            url = "https://raw.githubusercontent.com/trezor/python-mnemonic/master/src/mnemonic/wordlist/english.txt"
            with urllib.request.urlopen(url, timeout=10) as r:
                _BIP39_WORDS = r.read().decode().split()
        except Exception:
            print("[jackal-memory] Could not fetch BIP39 wordlist. Check your internet connection.", file=sys.stderr)
            sys.exit(1)
    return _BIP39_WORDS


def _generate_mnemonic() -> str:
    """Generate a 24-word BIP39 mnemonic from 256 bits of entropy."""
    words = _load_wordlist()
    entropy = os.urandom(32)  # 256 bits
    # Checksum: first (256/32)=8 bits of SHA256(entropy)
    h = hashlib.sha256(entropy).digest()
    bits = bin(int.from_bytes(entropy, 'big'))[2:].zfill(256) + bin(h[0])[2:].zfill(8)
    return ' '.join(words[int(bits[i*11:(i+1)*11], 2)] for i in range(24))


def _mnemonic_to_seed(mnemonic: str) -> bytes:
    """BIP39: mnemonic → 64-byte seed via PBKDF2-HMAC-SHA512."""
    return hashlib.pbkdf2_hmac(
        'sha512',
        mnemonic.encode('utf-8'),
        b'mnemonic',
        2048,
    )


_SECP256K1_ORDER = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


def _bip32_derive(seed: bytes, path: str) -> bytes:
    """Derive a private key from seed using BIP32/BIP44 path (e.g. m/44'/118'/0'/0/0)."""
    I = hmac.new(b'Bitcoin seed', seed, hashlib.sha512).digest()
    key, chain = I[:32], I[32:]

    for part in path.lstrip('m/').split('/'):
        hardened = part.endswith("'")
        index = int(part.rstrip("'")) + (0x80000000 if hardened else 0)
        if hardened:
            data = b'\x00' + key + struct.pack('>I', index)
        else:
            data = _privkey_to_pubkey(key) + struct.pack('>I', index)
        I = hmac.new(chain, data, hashlib.sha512).digest()
        il = int.from_bytes(I[:32], 'big')
        key_int = (il + int.from_bytes(key, 'big')) % _SECP256K1_ORDER
        key = key_int.to_bytes(32, 'big')
        chain = I[32:]

    return key


def _privkey_to_pubkey(privkey: bytes) -> bytes:
    """secp256k1 compressed public key from private key."""
    from cryptography.hazmat.primitives.asymmetric.ec import (
        SECP256K1, derive_private_key, EllipticCurvePublicKey,
    )
    from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
    priv = derive_private_key(int.from_bytes(privkey, 'big'), SECP256K1())
    return priv.public_key().public_bytes(Encoding.X962, PublicFormat.CompressedPoint)


def _pubkey_to_address(pubkey: bytes, hrp: str) -> str:
    """Cosmos address: RIPEMD160(SHA256(pubkey)) → bech32(hrp)."""
    sha = hashlib.sha256(pubkey).digest()
    try:
        rip = hashlib.new('ripemd160', sha).digest()
    except ValueError:
        # OpenSSL 3.0+ may disable RIPEMD160 — use cryptography library fallback
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.hashes import Hash
        h = Hash(hashes.RIPEMD160())
        h.update(sha)
        rip = h.finalize()
    return _bech32_encode(hrp, rip)


def _bech32_encode(hrp: str, data: bytes) -> str:
    """Standard bech32 encoding (Cosmos compatible)."""
    CHARSET = 'qpzry9x8gf2tvdw0s3jn54khce6mua7l'
    GEN = [0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3]

    def polymod(values):
        chk = 1
        for v in values:
            b = chk >> 25
            chk = (chk & 0x1ffffff) << 5 ^ v
            for i in range(5):
                chk ^= GEN[i] if (b >> i) & 1 else 0
        return chk

    def hrp_expand(s):
        return [ord(x) >> 5 for x in s] + [0] + [ord(x) & 31 for x in s]

    def convertbits(data, frombits, tobits):
        acc = bits = 0
        ret = []
        maxv = (1 << tobits) - 1
        for v in data:
            acc = ((acc << frombits) | v) & 0xffffffff
            bits += frombits
            while bits >= tobits:
                bits -= tobits
                ret.append((acc >> bits) & maxv)
        if bits:
            ret.append((acc << (tobits - bits)) & maxv)
        return ret

    data5 = convertbits(data, 8, 5)
    chk = polymod(hrp_expand(hrp) + data5 + [0] * 6) ^ 1
    checksum = [(chk >> 5 * (5 - i)) & 31 for i in range(6)]
    return hrp + '1' + ''.join(CHARSET[d] for d in data5 + checksum)


def _jackal_mnemonic() -> str | None:
    """Return the stored Jackal wallet mnemonic, or None if not set up yet."""
    env = os.environ.get("JACKAL_MEMORY_WALLET_MNEMONIC", "").strip()
    if env:
        return env
    if _WALLET_FILE.exists():
        return _WALLET_FILE.read_text().strip()
    return None


def _mnemonic_to_jackal_address(mnemonic: str) -> str:
    """Derive jkl1... address from BIP39 mnemonic via m/44'/118'/0'/0/0."""
    seed    = _mnemonic_to_seed(mnemonic)
    privkey = _bip32_derive(seed, "m/44'/118'/0'/0/0")
    pubkey  = _privkey_to_pubkey(privkey)
    return _pubkey_to_address(pubkey, "jkl")


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


def _ensure_wallet_registered() -> None:
    """
    On first save: generate a Jackal wallet if none exists, then register
    the jkl1... address with the API. Idempotent — safe to call every save.
    """
    mnemonic = _jackal_mnemonic()

    if mnemonic is None:
        # Generate and save
        mnemonic = _generate_mnemonic()
        _WALLET_FILE.parent.mkdir(parents=True, exist_ok=True)
        _WALLET_FILE.write_text(mnemonic)
        address = _mnemonic_to_jackal_address(mnemonic)
        print(
            "\n[jackal-memory] Generated your Jackal wallet and saved the mnemonic to:\n"
            f"  {_WALLET_FILE}\n\n"
            f"  Jackal address: {address}\n\n"
            "  This wallet will own your storage on-chain. Back up the mnemonic:\n"
            f"  python client.py wallet\n",
            file=sys.stderr,
        )
    else:
        address = _mnemonic_to_jackal_address(mnemonic)

    # Register with API (server stores address, uses it for MsgBuyStorage for_address)
    try:
        _request("POST", "/register-wallet", {"jackal_address": address})
    except SystemExit:
        pass  # Registration failure is non-fatal — provisioning will fall back to sidecar


# ── Commands ──────────────────────────────────────────────────────────────────

def cmd_keygen() -> None:
    key = _encryption_key()
    key_hex = key.hex()
    print(f"\nActive encryption key:\n\n  {key_hex}\n")
    print("Set this in your environment to use the same key on other machines:")
    print(f"  export JACKAL_MEMORY_ENCRYPTION_KEY={key_hex}\n")
    print("Keep this key safe — lose it and your encrypted memories are unrecoverable.")


def cmd_walletgen() -> None:
    """Generate a Jackal wallet, save the mnemonic locally, and register with the API."""
    existing = _jackal_mnemonic()
    if existing:
        address = _mnemonic_to_jackal_address(existing)
        print(f"\nJackal wallet already exists.")
        print(f"  Address:  {address}")
        print(f"  Mnemonic: {existing}")
        print(f"\nTo regenerate, delete {_WALLET_FILE} first.")
        return

    mnemonic = _generate_mnemonic()
    _WALLET_FILE.parent.mkdir(parents=True, exist_ok=True)
    _WALLET_FILE.write_text(mnemonic)
    address = _mnemonic_to_jackal_address(mnemonic)

    print(f"\nJackal wallet generated.")
    print(f"  Address:  {address}")
    print(f"  Mnemonic: {mnemonic}")
    print(f"\nSaved to: {_WALLET_FILE}")
    print("\nRegistering with API...")

    try:
        _request("POST", "/register-wallet", {"jackal_address": address})
        print("Registered. Your storage will be provisioned under this address on first save.")
    except SystemExit:
        print("Registration failed — check your API key.", file=sys.stderr)


def cmd_wallet() -> None:
    """Show the current Jackal wallet address and mnemonic."""
    mnemonic = _jackal_mnemonic()
    if not mnemonic:
        print("No Jackal wallet found. Run: python client.py walletgen")
        return
    address = _mnemonic_to_jackal_address(mnemonic)
    print(f"\nJackal address: {address}")
    print(f"Mnemonic:       {mnemonic}")
    print(f"\nBack up the mnemonic — it controls your on-chain storage.")
    print(f"  export JACKAL_MEMORY_WALLET_MNEMONIC=\"{mnemonic}\"")


def cmd_save(key: str, content: str) -> None:
    _ensure_wallet_registered()
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


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(0)

    cmd = args[0]

    if cmd == "keygen" and len(args) == 1:
        cmd_keygen()
    elif cmd == "walletgen" and len(args) == 1:
        cmd_walletgen()
    elif cmd == "wallet" and len(args) == 1:
        cmd_wallet()
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
