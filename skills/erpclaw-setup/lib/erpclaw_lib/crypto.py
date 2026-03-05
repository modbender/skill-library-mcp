"""Encryption utilities for ERPClaw — backup encryption + field-level protection.

Uses AES-256-GCM via the `cryptography` package (authenticated encryption).
Key derivation: PBKDF2-HMAC-SHA256 with 480,000 iterations (OWASP 2024).

Install: pip install cryptography

Functions:
- derive_key: PBKDF2 key derivation from passphrase + salt
- encrypt_file: Encrypt a file with AES-256-GCM + PBKDF2
- decrypt_file: Decrypt a file encrypted with encrypt_file
- encrypt_field: Encrypt a short string (tax_id, bank acct, etc.)
- decrypt_field: Decrypt a field encrypted with encrypt_field
- is_encrypted_backup: Check if a file is an encrypted ERPClaw backup
"""
import base64
import hashlib
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# PBKDF2 iterations (OWASP 2024 recommendation for HMAC-SHA256)
PBKDF2_ITERATIONS = 480_000
# Magic bytes to identify encrypted ERPClaw backups (v2 = AES-256-GCM)
MAGIC = b"ERPCLAW_ENC\x02"
# Field encryption prefix
FIELD_PREFIX = "enc:"


def derive_key(passphrase: str, salt: bytes, iterations: int = PBKDF2_ITERATIONS) -> bytes:
    """Derive a 32-byte AES-256 key from passphrase using PBKDF2.

    Args:
        passphrase: User-provided passphrase
        salt: Random 16-byte salt
        iterations: PBKDF2 iteration count

    Returns:
        32-byte key suitable for AES-256
    """
    return hashlib.pbkdf2_hmac("sha256", passphrase.encode("utf-8"), salt, iterations)


def encrypt_file(input_path: str, output_path: str, passphrase: str) -> dict:
    """Encrypt a file with AES-256-GCM + PBKDF2 key derivation.

    File format:
        MAGIC (12 bytes) | salt (16 bytes) | nonce (12 bytes) |
        ciphertext + GCM tag (variable)

    Args:
        input_path: Path to plaintext file
        output_path: Path to write encrypted file
        passphrase: Encryption passphrase

    Returns:
        Dict with original_size, encrypted_size
    """
    salt = os.urandom(16)
    nonce = os.urandom(12)
    key = derive_key(passphrase, salt)

    with open(input_path, "rb") as f:
        plaintext = f.read()

    original_size = len(plaintext)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)

    with open(output_path, "wb") as f:
        f.write(MAGIC)
        f.write(salt)
        f.write(nonce)
        f.write(ciphertext)

    encrypted_size = os.path.getsize(output_path)
    return {"original_size": original_size, "encrypted_size": encrypted_size}


def decrypt_file(input_path: str, output_path: str, passphrase: str) -> dict:
    """Decrypt a file encrypted with encrypt_file.

    Args:
        input_path: Path to encrypted file
        output_path: Path to write decrypted file
        passphrase: Encryption passphrase

    Returns:
        Dict with decrypted_size

    Raises:
        ValueError: If file is not an encrypted ERPClaw backup or decryption fails
    """
    with open(input_path, "rb") as f:
        data = f.read()

    if not data.startswith(MAGIC):
        raise ValueError("Not an encrypted ERPClaw backup")

    offset = len(MAGIC)
    salt = data[offset:offset + 16]
    offset += 16
    nonce = data[offset:offset + 12]
    offset += 12
    ciphertext = data[offset:]

    key = derive_key(passphrase, salt)
    aesgcm = AESGCM(key)

    try:
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    except Exception:
        raise ValueError("Invalid passphrase or corrupted backup")

    with open(output_path, "wb") as f:
        f.write(plaintext)

    return {"decrypted_size": len(plaintext)}


def is_encrypted_backup(file_path: str) -> bool:
    """Check if a file is an encrypted ERPClaw backup.

    Args:
        file_path: Path to check

    Returns:
        True if file starts with ERPCLAW_ENC magic bytes
    """
    try:
        with open(file_path, "rb") as f:
            header = f.read(len(MAGIC))
        return header == MAGIC
    except (OSError, IOError):
        return False


def encrypt_field(value: str, key: bytes) -> str:
    """Encrypt a short string field for at-rest protection.

    Args:
        value: Plaintext string to encrypt
        key: 32-byte encryption key

    Returns:
        Base64-encoded encrypted string prefixed with 'enc:'
    """
    if not value or value.startswith(FIELD_PREFIX):
        return value  # Already encrypted or empty

    nonce = os.urandom(12)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, value.encode("utf-8"), None)
    encoded = base64.b64encode(nonce + ciphertext).decode("ascii")
    return FIELD_PREFIX + encoded


def decrypt_field(value: str, key: bytes) -> str:
    """Decrypt a field encrypted with encrypt_field.

    Args:
        value: Encrypted string (must start with 'enc:')
        key: 32-byte encryption key (same key used for encryption)

    Returns:
        Decrypted plaintext string
    """
    if not value or not value.startswith(FIELD_PREFIX):
        return value  # Not encrypted

    raw = base64.b64decode(value[len(FIELD_PREFIX):])
    nonce = raw[:12]
    ciphertext = raw[12:]

    aesgcm = AESGCM(key)
    try:
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    except Exception:
        return value  # Return as-is if decryption fails

    return plaintext.decode("utf-8")
