"""
ClawShield integration client.

Provides Ed25519-signed artifact minting for testing.
In production, ClawShield mints these artifacts externally.
"""

import uuid
import base64
import datetime
from openexec.crypto import canonical_hash
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

def generate_test_keypair():
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    public_key_pem = public_key.public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo).decode()
    return private_key, public_key_pem

def mint_approval_artifact(
    action_request: dict,
    private_key: Ed25519PrivateKey,
    tenant_id: str,
    ttl_seconds: int = 300
) -> dict:
    approval_id = str(uuid.uuid4())
    action_hash = canonical_hash(action_request)
    issued_at = datetime.datetime.utcnow().isoformat()
    expires_at = (datetime.datetime.utcnow() + datetime.timedelta(seconds=ttl_seconds)).isoformat()

    message = (
        approval_id
        + tenant_id
        + action_hash
        + issued_at
        + expires_at
    ).encode()

    signature = private_key.sign(message)
    signature_b64 = base64.b64encode(signature).decode()

    return {
        "approval_id": approval_id,
        "tenant_id": tenant_id,
        "action_hash": action_hash,
        "issued_at": issued_at,
        "expires_at": expires_at,
        "signature": signature_b64
    }
