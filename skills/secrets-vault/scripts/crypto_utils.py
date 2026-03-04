#!/usr/bin/env python3
"""Encryption utilities for secrets vault using AES-256-GCM."""

import os
import json
import base64
import hashlib
from datetime import datetime
from typing import Optional, Dict, Any

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.backends import default_backend
except ImportError:
    print("Error: cryptography library not installed.")
    print("Run: pip install cryptography")
    exit(1)

# Constants
KEY_LENGTH = 32  # 256 bits
SALT_LENGTH = 16
NONCE_LENGTH = 12
PBKDF2_ITERATIONS = 600000  # OWASP recommended


def derive_key(password: str, salt: bytes) -> bytes:
    """Derive encryption key from password using PBKDF2."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_LENGTH,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
        backend=default_backend()
    )
    return kdf.derive(password.encode('utf-8'))


def encrypt_data(data: bytes, password: str) -> bytes:
    """Encrypt data using AES-256-GCM."""
    salt = os.urandom(SALT_LENGTH)
    key = derive_key(password, salt)
    nonce = os.urandom(NONCE_LENGTH)

    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, data, None)

    # Format: salt (16) + nonce (12) + ciphertext
    return salt + nonce + ciphertext


def decrypt_data(encrypted: bytes, password: str) -> bytes:
    """Decrypt data using AES-256-GCM."""
    if len(encrypted) < SALT_LENGTH + NONCE_LENGTH:
        raise ValueError("Invalid encrypted data format")

    salt = encrypted[:SALT_LENGTH]
    nonce = encrypted[SALT_LENGTH:SALT_LENGTH + NONCE_LENGTH]
    ciphertext = encrypted[SALT_LENGTH + NONCE_LENGTH:]

    key = derive_key(password, salt)
    aesgcm = AESGCM(key)

    return aesgcm.decrypt(nonce, ciphertext, None)


def generate_password(length: int = 24) -> str:
    """Generate a strong random password."""
    import string
    import secrets as sec
    chars = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    password = ''.join(sec.choice(chars) for _ in range(length))
    # Ensure at least one of each type
    password = list(password)
    password[0] = sec.choice(string.ascii_uppercase)
    password[1] = sec.choice(string.ascii_lowercase)
    password[2] = sec.choice(string.digits)
    password[3] = sec.choice("!@#$%^&*")
    return ''.join(password)


def check_password_strength(password: str) -> Dict[str, Any]:
    """Check password strength and return analysis."""
    result = {
        'length': len(password),
        'has_upper': any(c.isupper() for c in password),
        'has_lower': any(c.islower() for c in password),
        'has_digit': any(c.isdigit() for c in password),
        'has_special': any(c in "!@#$%^&*()-_=+[]{}|;:',.<>?/" for c in password),
        'score': 0,
        'rating': 'weak'
    }

    # Calculate score
    if len(password) >= 8:
        result['score'] += 1
    if len(password) >= 12:
        result['score'] += 1
    if len(password) >= 20:
        result['score'] += 1
    if result['has_upper']:
        result['score'] += 1
    if result['has_lower']:
        result['score'] += 1
    if result['has_digit']:
        result['score'] += 1
    if result['has_special']:
        result['score'] += 2

    # Common password check
    common = ['password', '123456', 'qwerty', 'admin', 'letmein']
    if password.lower() in common:
        result['score'] = 0
        result['is_common'] = True

    # Rating
    if result['score'] >= 7:
        result['rating'] = 'strong'
    elif result['score'] >= 4:
        result['rating'] = 'medium'

    return result
