import hashlib
import json
import base64
import os
from typing import Union
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.exceptions import InvalidSignature

def canonical_hash(data: Union[dict, str]) -> str:
    if isinstance(data, dict):
        data = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(data.encode()).hexdigest()

def verify_ed25519_signature(public_key_pem: str, message: bytes, signature_b64: str) -> bool:
    try:
        public_key = load_pem_public_key(public_key_pem.encode())
        if not isinstance(public_key, Ed25519PublicKey):
            return False
        signature = base64.b64decode(signature_b64)
        public_key.verify(signature, message)
        return True
    except (InvalidSignature, ValueError, Exception):
        return False
