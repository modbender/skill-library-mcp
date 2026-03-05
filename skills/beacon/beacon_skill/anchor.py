"""On-chain anchoring: hash data and submit commitments to RustChain."""

import hashlib
import json
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .storage import append_jsonl, read_jsonl_tail


def _canonical_json(data: Dict[str, Any]) -> bytes:
    """Deterministic JSON encoding for hashing."""
    return json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")


def commitment_hash(data: Union[str, bytes, Dict]) -> str:
    """Compute SHA256 commitment hash of data.

    - dict  → canonical JSON bytes → SHA256
    - str   → UTF-8 bytes → SHA256
    - bytes → raw bytes → SHA256
    """
    if isinstance(data, dict):
        raw = _canonical_json(data)
    elif isinstance(data, str):
        raw = data.encode("utf-8")
    elif isinstance(data, bytes):
        raw = data
    else:
        raw = str(data).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


_HEX64 = re.compile(r"^[0-9a-f]{64}$")

ANCHOR_LOG = "anchors.jsonl"


class AnchorManager:
    """Submit and verify hash anchors on RustChain."""

    def __init__(
        self,
        client: Any,
        keypair: Any = None,
        identity: Any = None,
    ):
        self._client = client
        self._keypair = keypair
        self._identity = identity

    # ── signing ──

    def _sign_commitment(self, commitment: str) -> tuple:
        """Sign commitment bytes, return (signature_hex, public_key_hex)."""
        msg = commitment.encode("utf-8")
        if self._keypair is not None:
            from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
            from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, PublicFormat, NoEncryption

            sk = Ed25519PrivateKey.from_private_bytes(bytes.fromhex(self._keypair.private_key_hex))
            sig = sk.sign(msg).hex()
            return sig, self._keypair.public_key_hex
        if self._identity is not None:
            sig = self._identity.sign_hex(msg)
            return sig, self._identity.public_key_hex
        raise RuntimeError("No keypair or identity available for signing")

    # ── submit ──

    def anchor(
        self,
        data: Union[str, bytes, Dict],
        data_type: str = "arbitrary",
        metadata: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Hash data, sign commitment, submit to RustChain. Returns anchor record."""
        commit = commitment_hash(data)
        return self._submit(commit, data_type, metadata)

    def anchor_bytes(
        self,
        raw: bytes,
        data_type: str,
        metadata: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Anchor pre-computed bytes."""
        commit = hashlib.sha256(raw).hexdigest()
        return self._submit(commit, data_type, metadata)

    def _submit(
        self,
        commitment: str,
        data_type: str,
        metadata: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        sig, pubkey = self._sign_commitment(commitment)
        meta_str = json.dumps(metadata, separators=(",", ":")) if metadata else ""

        payload = {
            "commitment": commitment,
            "data_type": data_type,
            "metadata": meta_str,
            "signature": sig,
            "public_key": pubkey,
        }

        try:
            result = self._client.anchor_submit(payload)
            log_entry = {
                "ts": int(time.time()),
                "commitment": commitment,
                "data_type": data_type,
                "status": "ok",
                "anchor_id": result.get("anchor_id"),
            }
            append_jsonl(ANCHOR_LOG, log_entry)
            return result
        except Exception as e:
            err_str = str(e)
            # Handle 409 (duplicate) gracefully — still a success
            if "commitment_exists" in err_str:
                log_entry = {
                    "ts": int(time.time()),
                    "commitment": commitment,
                    "data_type": data_type,
                    "status": "duplicate",
                }
                append_jsonl(ANCHOR_LOG, log_entry)
                return {"ok": False, "error": "commitment_exists", "commitment": commitment}
            log_entry = {
                "ts": int(time.time()),
                "commitment": commitment,
                "data_type": data_type,
                "status": "error",
                "error": err_str,
            }
            append_jsonl(ANCHOR_LOG, log_entry)
            raise

    # ── verify ──

    def verify(self, commitment: str) -> Optional[Dict[str, Any]]:
        """Check if a commitment exists on-chain. Returns anchor dict or None."""
        result = self._client.anchor_verify(commitment)
        if result.get("found"):
            return result.get("anchor")
        return None

    def verify_data(self, data: Union[str, bytes, Dict]) -> Optional[Dict[str, Any]]:
        """Hash data and check if that hash is anchored."""
        commit = commitment_hash(data)
        return self.verify(commit)

    # ── history ──

    def my_anchors(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List anchors submitted by this identity."""
        if self._keypair is not None:
            from .transports.rustchain import _rtc_address_from_public_key_bytes
            submitter = _rtc_address_from_public_key_bytes(bytes.fromhex(self._keypair.public_key_hex))
        elif self._identity is not None:
            from .transports.rustchain import _rtc_address_from_public_key_bytes
            submitter = _rtc_address_from_public_key_bytes(bytes.fromhex(self._identity.public_key_hex))
        else:
            return []
        result = self._client.anchor_list(submitter=submitter, limit=limit)
        return result.get("anchors", [])

    def history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Local JSONL log of all anchor attempts."""
        return read_jsonl_tail(ANCHOR_LOG, limit=limit)


# ── Convenience functions ──


def anchor_action(action_result: Dict[str, Any], manager: AnchorManager) -> Optional[Dict[str, Any]]:
    """Anchor a completed executor action (outbox drain result)."""
    if action_result.get("status") != "sent":
        return None
    data = {
        "action_id": action_result.get("action_id", ""),
        "method": action_result.get("method", ""),
        "ts": action_result.get("ts", int(time.time())),
    }
    metadata = {"action_id": data["action_id"]}
    return manager.anchor(data, data_type="beacon_action", metadata=metadata)


def anchor_epoch(
    epoch: int,
    settlements: List[Dict[str, Any]],
    manager: AnchorManager,
) -> Optional[Dict[str, Any]]:
    """Anchor an epoch settlement summary."""
    data = {
        "epoch": epoch,
        "settlement_count": len(settlements),
        "settlements": settlements,
    }
    metadata = {"epoch": epoch, "count": len(settlements)}
    return manager.anchor(data, data_type="epoch_settlement", metadata=metadata)
