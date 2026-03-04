import os
import datetime
from openexec.crypto import canonical_hash, verify_ed25519_signature

class ApprovalError(Exception):
    pass

def validate_approval(action_request: dict, artifact: dict) -> None:
    request_hash = canonical_hash(action_request)
    if artifact.get("action_hash") != request_hash:
        raise ApprovalError("Action hash mismatch: approval does not match this request")

    expires_at = artifact.get("expires_at", "")
    if expires_at:
        try:
            expiry_time = datetime.datetime.fromisoformat(expires_at)
            if expiry_time < datetime.datetime.utcnow():
                raise ApprovalError("Approval artifact expired")
        except ValueError:
            raise ApprovalError("Invalid expires_at timestamp")
    else:
        raise ApprovalError("Missing expires_at in approval artifact")

    message = (
        artifact["approval_id"]
        + artifact["tenant_id"]
        + artifact["action_hash"]
        + artifact["issued_at"]
        + artifact["expires_at"]
    ).encode()

    public_key_pem = os.getenv("CLAWSHIELD_PUBLIC_KEY", "")
    if not public_key_pem:
        raise ApprovalError("CLAWSHIELD_PUBLIC_KEY not configured")

    signature_b64 = artifact.get("signature", "")
    if not verify_ed25519_signature(public_key_pem, message, signature_b64):
        raise ApprovalError("Invalid signature: approval artifact is not authentic")

    expected_tenant = os.getenv("CLAWSHIELD_TENANT_ID", "")
    if expected_tenant and artifact.get("tenant_id") != expected_tenant:
        raise ApprovalError(f"Tenant mismatch: expected {expected_tenant}, got {artifact.get('tenant_id')}")
