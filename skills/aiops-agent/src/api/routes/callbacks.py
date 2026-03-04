"""
Callback routes for external service integrations.

Handles:
- Lark (Feishu) card action callbacks
- Webhook callbacks for approvals
"""

import json
from typing import Any, Dict, Optional

import structlog
from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel

from src.config.settings import get_settings

logger = structlog.get_logger()

router = APIRouter(prefix="/callbacks", tags=["Callbacks"])


# Dependency injection placeholders - set by main.py
_action_planner = None
_lark_notifier = None


def set_action_planner(planner):
    """Set the action planner instance for callbacks."""
    global _action_planner
    _action_planner = planner


def set_lark_notifier(notifier):
    """Set the Lark notifier instance for callbacks."""
    global _lark_notifier
    _lark_notifier = notifier


class LarkCallbackResponse(BaseModel):
    """Response model for Lark callbacks."""

    challenge: Optional[str] = None  # For URL verification


class ApprovalResponse(BaseModel):
    """Response for approval actions."""

    success: bool
    plan_id: str
    status: str
    message: Optional[str] = None


@router.post("/lark")
async def handle_lark_callback(
    request: Request,
    x_lark_request_timestamp: Optional[str] = Header(None, alias="X-Lark-Request-Timestamp"),
    x_lark_request_nonce: Optional[str] = Header(None, alias="X-Lark-Request-Nonce"),
    x_lark_signature: Optional[str] = Header(None, alias="X-Lark-Signature"),
) -> Dict[str, Any]:
    """
    Handle Lark card action callbacks.

    This endpoint receives callbacks when users click buttons on Lark cards.

    Callback types:
    1. URL Verification (challenge-response)
    2. Card action (approve/reject buttons)

    Returns:
        Updated card content or verification response
    """
    body = await request.body()
    body_str = body.decode("utf-8")

    try:
        data = json.loads(body_str)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # Handle URL verification challenge
    if "challenge" in data:
        logger.info("Lark URL verification challenge received")
        return {"challenge": data["challenge"]}

    # Handle encrypted message (if encrypt_key is configured)
    if "encrypt" in data:
        data = _decrypt_lark_message(data["encrypt"])
        if data is None:
            raise HTTPException(status_code=400, detail="Failed to decrypt message")

    # Verify signature if configured
    settings = get_settings()
    if settings.lark.verification_token and _lark_notifier:
        if not all([x_lark_request_timestamp, x_lark_request_nonce, x_lark_signature]):
            logger.warning("Missing Lark signature headers")
            # Continue anyway for now - some Lark setups don't include signatures
        elif not _lark_notifier.verify_callback_signature(
            x_lark_request_timestamp,
            x_lark_request_nonce,
            body_str,
            x_lark_signature,
        ):
            raise HTTPException(status_code=401, detail="Invalid signature")

    # Handle card action
    if data.get("type") == "card":
        return await _handle_card_action(data)

    # Handle event callbacks
    if "event" in data:
        return await _handle_event_callback(data)

    logger.warning("Unknown Lark callback type", data=data)
    return {"status": "ok"}


async def _handle_card_action(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle card button action."""
    action = data.get("action", {})
    action_value = action.get("value", {})

    action_type = action_value.get("action")
    plan_id = action_value.get("plan_id")

    if not action_type or not plan_id:
        logger.warning("Missing action or plan_id in card action", action=action_value)
        return {"status": "error", "message": "Missing action or plan_id"}

    # Get user info
    user_id = data.get("user_id", "unknown")
    open_id = data.get("open_id", user_id)

    logger.info(
        "Lark card action received",
        action=action_type,
        plan_id=plan_id,
        user=open_id,
    )

    if not _action_planner:
        logger.error("Action planner not available")
        return _build_error_card("Service temporarily unavailable")

    if action_type == "approve":
        result = _action_planner.approve_plan(plan_id, open_id)
        if result:
            return _build_result_card(plan_id, "approved", open_id)
        else:
            return _build_error_card(f"Plan {plan_id} not found")

    elif action_type == "reject":
        # Get rejection reason if provided
        reason = action_value.get("reason", "Rejected by user")
        result = _action_planner.reject_plan(plan_id, open_id, reason)
        if result:
            return _build_result_card(plan_id, "rejected", open_id, reason)
        else:
            return _build_error_card(f"Plan {plan_id} not found")

    else:
        logger.warning("Unknown card action", action=action_type)
        return _build_error_card(f"Unknown action: {action_type}")


async def _handle_event_callback(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle Lark event callbacks."""
    event = data.get("event", {})
    event_type = event.get("type")

    logger.info("Lark event received", event_type=event_type)

    # Add handlers for other event types as needed
    return {"status": "ok"}


def _decrypt_lark_message(encrypted: str) -> Optional[Dict[str, Any]]:
    """Decrypt Lark encrypted message."""
    settings = get_settings()
    encrypt_key = settings.lark.encrypt_key

    if not encrypt_key:
        logger.warning("Lark encrypt_key not configured")
        return None

    try:
        import base64
        import hashlib
        from Crypto.Cipher import AES

        # Derive key from encrypt_key
        key = hashlib.sha256(encrypt_key.encode()).digest()

        # Decode encrypted content
        encrypted_bytes = base64.b64decode(encrypted)

        # Extract IV and ciphertext
        iv = encrypted_bytes[:16]
        ciphertext = encrypted_bytes[16:]

        # Decrypt
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(ciphertext)

        # Remove PKCS7 padding
        padding_len = decrypted[-1]
        decrypted = decrypted[:-padding_len]

        return json.loads(decrypted.decode("utf-8"))

    except ImportError:
        logger.warning("pycryptodome not installed, cannot decrypt Lark messages")
        return None
    except Exception as e:
        logger.error("Failed to decrypt Lark message", error=str(e))
        return None


def _build_result_card(
    plan_id: str,
    status: str,
    approver: str,
    reason: Optional[str] = None,
) -> Dict[str, Any]:
    """Build updated card showing approval result."""
    if status == "approved":
        color = "green"
        status_text = "APPROVED"
    else:
        color = "red"
        status_text = "REJECTED"

    elements = [
        {
            "tag": "div",
            "text": {
                "content": f"**Plan ID:** `{plan_id}`",
                "tag": "lark_md",
            },
        },
        {
            "tag": "div",
            "text": {
                "content": f"**Status:** {status_text}",
                "tag": "lark_md",
            },
        },
        {
            "tag": "div",
            "text": {
                "content": f"**By:** {approver}",
                "tag": "lark_md",
            },
        },
    ]

    if reason:
        elements.append({
            "tag": "div",
            "text": {
                "content": f"**Reason:** {reason}",
                "tag": "lark_md",
            },
        })

    from datetime import datetime

    elements.append({
        "tag": "note",
        "elements": [
            {
                "tag": "plain_text",
                "content": f"Updated at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
            },
        ],
    })

    # Return updated card
    return {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": {
                "content": f"Approval {status_text}",
                "tag": "plain_text",
            },
            "template": color,
        },
        "elements": elements,
    }


def _build_error_card(message: str) -> Dict[str, Any]:
    """Build error card."""
    return {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": {
                "content": "Error",
                "tag": "plain_text",
            },
            "template": "red",
        },
        "elements": [
            {
                "tag": "div",
                "text": {
                    "content": f"**Error:** {message}",
                    "tag": "lark_md",
                },
            },
        ],
    }


# Additional webhook callback route for generic approvals
@router.post("/approval/{plan_id}")
async def handle_approval_callback(
    plan_id: str,
    action: str,
    approver: str = "api",
    reason: Optional[str] = None,
) -> ApprovalResponse:
    """
    Handle approval via API callback.

    This endpoint can be used by external systems to approve/reject plans.

    Args:
        plan_id: The action plan ID
        action: "approve" or "reject"
        approver: Identifier of the approver
        reason: Rejection reason (required for reject)
    """
    if not _action_planner:
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")

    if action == "approve":
        result = _action_planner.approve_plan(plan_id, approver)
        if result:
            return ApprovalResponse(
                success=True,
                plan_id=plan_id,
                status=result.status.value,
                message="Plan approved",
            )
        else:
            raise HTTPException(status_code=404, detail=f"Plan {plan_id} not found")

    elif action == "reject":
        result = _action_planner.reject_plan(plan_id, approver, reason or "Rejected via API")
        if result:
            return ApprovalResponse(
                success=True,
                plan_id=plan_id,
                status=result.status.value,
                message="Plan rejected",
            )
        else:
            raise HTTPException(status_code=404, detail=f"Plan {plan_id} not found")

    else:
        raise HTTPException(status_code=400, detail=f"Invalid action: {action}")
