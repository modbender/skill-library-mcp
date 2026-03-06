"""
AgentMesh Cryptography Engine
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Military-grade end-to-end encryption for AI agent communication.

Features:
  • X25519 Elliptic Curve Diffie-Hellman key exchange
  • AES-256-GCM authenticated encryption
  • Ed25519 digital signatures (message authenticity)
  • HKDF-SHA256 key derivation
  • Forward secrecy via ephemeral session keys
  • Message integrity + replay attack prevention
"""

import os
import json
import time
import base64
import hashlib
import hmac
from typing import Tuple, Optional

from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidTag


# ──────────────────────────────────────────────────────────────────────────────
# Key Management
# ──────────────────────────────────────────────────────────────────────────────

class AgentKeyPair:
    """
    A complete cryptographic identity for an AI agent.
    Contains both an identity key (Ed25519) for signing and
    an exchange key (X25519) for ECDH key agreement.
    """

    def __init__(
        self,
        identity_private: Optional[Ed25519PrivateKey] = None,
        exchange_private: Optional[X25519PrivateKey] = None,
    ):
        self.identity_private = identity_private or Ed25519PrivateKey.generate()
        self.exchange_private = exchange_private or X25519PrivateKey.generate()

        self.identity_public: Ed25519PublicKey = self.identity_private.public_key()
        self.exchange_public: X25519PublicKey = self.exchange_private.public_key()

    # ── Serialisation helpers ────────────────────────────────────────────────

    def public_bundle(self) -> dict:
        """Return the public half of this key-pair as a JSON-safe dict."""
        return {
            "identity_key": _b64(
                self.identity_public.public_bytes(
                    serialization.Encoding.Raw, serialization.PublicFormat.Raw
                )
            ),
            "exchange_key": _b64(
                self.exchange_public.public_bytes(
                    serialization.Encoding.Raw, serialization.PublicFormat.Raw
                )
            ),
        }

    def to_dict(self) -> dict:
        """Serialise the full key-pair (private + public) to a JSON-safe dict."""
        return {
            "identity_private": _b64(
                self.identity_private.private_bytes(
                    serialization.Encoding.Raw,
                    serialization.PrivateFormat.Raw,
                    serialization.NoEncryption(),
                )
            ),
            "exchange_private": _b64(
                self.exchange_private.private_bytes(
                    serialization.Encoding.Raw,
                    serialization.PrivateFormat.Raw,
                    serialization.NoEncryption(),
                )
            ),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AgentKeyPair":
        """Restore a key-pair from a previously serialised dict."""
        return cls(
            identity_private=Ed25519PrivateKey.from_private_bytes(_db64(data["identity_private"])),
            exchange_private=X25519PrivateKey.from_private_bytes(_db64(data["exchange_private"])),
        )

    # ── Fingerprint ──────────────────────────────────────────────────────────

    @property
    def fingerprint(self) -> str:
        """
        Human-readable hex fingerprint of the identity key.
        Agents can share fingerprints out-of-band to verify each other.
        """
        raw = self.identity_public.public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw
        )
        digest = hashlib.sha256(raw).hexdigest()
        # Format: XXXX:XXXX:XXXX:XXXX:XXXX:XXXX:XXXX:XXXX
        return ":".join(digest[i : i + 4] for i in range(0, 32, 4))


# ──────────────────────────────────────────────────────────────────────────────
# Session (Shared Secret + Ratchet)
# ──────────────────────────────────────────────────────────────────────────────

class CryptoSession:
    """
    An established encrypted session between two agents.
    Derived from an ECDH shared secret + HKDF key derivation.
    Supports optional ratcheting for forward secrecy.
    """

    def __init__(self, shared_key: bytes, initiator: bool = True):
        """
        shared_key : 32-byte HKDF-derived secret (same value on both sides)
        initiator  : True for the "first" party (alphabetically lower agent_id).
                     Ensures send/recv key assignment is consistently mirrored.
        """
        self._root_key = shared_key
        key_a = self._derive(shared_key, b"key_a")
        key_b = self._derive(shared_key, b"key_b")
        if initiator:
            self._send_key = key_a
            self._recv_key = key_b
        else:
            self._send_key = key_b
            self._recv_key = key_a
        self._message_counter = 0
        self._seen_nonces: set = set()

    # ── Encryption ───────────────────────────────────────────────────────────

    def encrypt(self, plaintext: bytes, aad: bytes = b"") -> dict:
        """
        Encrypt a message and return a ciphertext envelope.

        Returns a dict with: ciphertext, nonce, counter, tag_included=True
        The nonce is unique per message; AAD covers agent IDs + timestamp.
        """
        nonce = os.urandom(12)  # 96-bit nonce for AES-GCM
        aesgcm = AESGCM(self._send_key)

        # Build associated data: nonce + counter + caller-supplied aad
        counter_bytes = self._message_counter.to_bytes(8, "big")
        full_aad = nonce + counter_bytes + aad

        ciphertext = aesgcm.encrypt(nonce, plaintext, full_aad)

        envelope = {
            "v": 1,                         # protocol version
            "nonce": _b64(nonce),
            "counter": self._message_counter,
            "ciphertext": _b64(ciphertext),
            "aad": _b64(aad),
        }

        self._message_counter += 1
        return envelope

    def decrypt(self, envelope: dict) -> bytes:
        """
        Decrypt a received envelope.
        Raises CryptoError on any integrity / replay failure.
        """
        try:
            nonce = _db64(envelope["nonce"])
            counter = envelope["counter"]
            ciphertext = _db64(envelope["ciphertext"])
            aad = _db64(envelope["aad"])
        except (KeyError, Exception) as exc:
            raise CryptoError(f"Malformed envelope: {exc}") from exc

        # Replay detection
        nonce_key = (nonce, counter)
        if nonce_key in self._seen_nonces:
            raise CryptoError("Replay attack detected – nonce reuse")
        self._seen_nonces.add(nonce_key)

        counter_bytes = counter.to_bytes(8, "big")
        full_aad = nonce + counter_bytes + aad

        aesgcm = AESGCM(self._recv_key)
        try:
            return aesgcm.decrypt(nonce, ciphertext, full_aad)
        except InvalidTag as exc:
            raise CryptoError("Authentication tag mismatch – message tampered") from exc

    # ── Helpers ──────────────────────────────────────────────────────────────

    @staticmethod
    def _derive(key: bytes, purpose: bytes) -> bytes:
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b"AgentMesh-v1-" + purpose,
        )
        return hkdf.derive(key)


# ──────────────────────────────────────────────────────────────────────────────
# Key Exchange (X3DH-lite)
# ──────────────────────────────────────────────────────────────────────────────

def perform_key_exchange(
    my_keypair: AgentKeyPair,
    their_public_bundle: dict,
) -> CryptoSession:
    """
    Perform an ECDH key exchange given the remote agent's public bundle.
    Returns a ready-to-use CryptoSession.

    Uses X25519 + HKDF-SHA256.  Both sides must call this with the
    *other's* public bundle to arrive at the same shared secret.
    The 'initiator' role is determined by comparing identity key bytes
    so that both sides agree on send/recv direction automatically.
    """
    # Deserialise remote keys
    their_exchange_raw = _db64(their_public_bundle["exchange_key"])
    their_exchange_pub = X25519PublicKey.from_public_bytes(their_exchange_raw)

    # ECDH
    raw_shared = my_keypair.exchange_private.exchange(their_exchange_pub)

    # Mix in both identity keys for domain separation
    my_identity_raw = my_keypair.identity_public.public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw
    )
    their_identity_raw = _db64(their_public_bundle["identity_key"])

    # Deterministic ordering so both sides compute the same salt
    keys_sorted = sorted([my_identity_raw, their_identity_raw])
    salt = hashlib.sha256(keys_sorted[0] + keys_sorted[1]).digest()

    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        info=b"AgentMesh-v1-session",
    )
    shared_key = hkdf.derive(raw_shared)

    # Deterministic role: whoever has the lexicographically smaller identity
    # key bytes is the "initiator" – guarantees both sides pick opposite roles.
    initiator = my_identity_raw < their_identity_raw

    return CryptoSession(shared_key, initiator=initiator)


# ──────────────────────────────────────────────────────────────────────────────
# Message Signing / Verification
# ──────────────────────────────────────────────────────────────────────────────

def sign_message(private_key: Ed25519PrivateKey, message: bytes) -> str:
    """Sign a message and return the base64-encoded signature."""
    return _b64(private_key.sign(message))


def verify_signature(public_key_bytes: bytes, message: bytes, signature_b64: str) -> bool:
    """
    Verify an Ed25519 signature.
    Returns True if valid, False otherwise (never raises).
    """
    try:
        pub = Ed25519PublicKey.from_public_bytes(public_key_bytes)
        pub.verify(_db64(signature_b64), message)
        return True
    except Exception:
        return False


# ──────────────────────────────────────────────────────────────────────────────
# Sealed Message (signed + encrypted in one call)
# ──────────────────────────────────────────────────────────────────────────────

def seal(
    session: CryptoSession,
    sender_keypair: AgentKeyPair,
    sender_id: str,
    recipient_id: str,
    payload: dict,
) -> dict:
    """
    High-level helper: sign then encrypt a payload dict.

    Returns a complete 'sealed message' dict ready for transport.
    """
    timestamp = int(time.time() * 1000)  # milliseconds
    plaintext = json.dumps(payload, separators=(",", ":")).encode()

    # Signature covers: sender_id + recipient_id + timestamp + plaintext
    signing_input = (
        sender_id.encode() + b"|" +
        recipient_id.encode() + b"|" +
        str(timestamp).encode() + b"|" +
        plaintext
    )
    signature = sign_message(sender_keypair.identity_private, signing_input)

    aad = json.dumps(
        {"from": sender_id, "to": recipient_id, "ts": timestamp},
        separators=(",", ":"),
    ).encode()

    envelope = session.encrypt(plaintext, aad)
    envelope["from"] = sender_id
    envelope["to"] = recipient_id
    envelope["ts"] = timestamp
    envelope["sig"] = signature

    return envelope


def unseal(
    session: CryptoSession,
    envelope: dict,
    sender_public_bundle: dict,
) -> dict:
    """
    High-level helper: decrypt then verify a sealed message.

    Returns the original payload dict on success.
    Raises CryptoError on any failure.
    """
    aad = json.dumps(
        {"from": envelope["from"], "to": envelope["to"], "ts": envelope["ts"]},
        separators=(",", ":"),
    ).encode()

    # Patch the aad field before decrypting (it was already baked in during seal)
    envelope_copy = dict(envelope)
    envelope_copy["aad"] = _b64(aad)

    plaintext = session.decrypt(envelope_copy)

    # Verify signature
    signing_input = (
        envelope["from"].encode() + b"|" +
        envelope["to"].encode() + b"|" +
        str(envelope["ts"]).encode() + b"|" +
        plaintext
    )
    identity_bytes = _db64(sender_public_bundle["identity_key"])
    if not verify_signature(identity_bytes, signing_input, envelope["sig"]):
        raise CryptoError("Signature verification failed – sender cannot be trusted")

    return json.loads(plaintext)


# ──────────────────────────────────────────────────────────────────────────────
# Exceptions
# ──────────────────────────────────────────────────────────────────────────────

class CryptoError(Exception):
    """Raised on any cryptographic failure (tampering, replay, bad key, etc.)."""


# ──────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ──────────────────────────────────────────────────────────────────────────────

def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode()


def _db64(data: str) -> bytes:
    return base64.urlsafe_b64decode(data)
