"""WebSocket endpoint for real-time approval flow.

The local dashboard (or terminal UI) connects here to receive approval requests
and can send back decisions without polling.
"""

from __future__ import annotations

import json
from typing import Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.models.schemas import Approval, ApprovalDecision
from app.services.approval_service import ApprovalService

router = APIRouter(tags=["websocket"])

_approval_svc: ApprovalService = None  # type: ignore
_connected_clients: Set[WebSocket] = set()


def init(approval_svc: ApprovalService):
    global _approval_svc
    _approval_svc = approval_svc


async def broadcast_approval_request(approval: Approval):
    """Push a new approval request to all connected dashboard clients."""
    payload = json.dumps({
        "type": "approval_request",
        "data": approval.model_dump(mode="json"),
    })
    disconnected = set()
    for ws in _connected_clients:
        try:
            await ws.send_text(payload)
        except Exception:
            disconnected.add(ws)
    _connected_clients -= disconnected


@router.websocket("/ws/approvals")
async def ws_approvals(ws: WebSocket):
    """WebSocket for the local approval dashboard.

    Receives: { "type": "decide", "approval_id": "...", "approved": true/false, "file_patterns": [], "ttl_minutes": null }
    Sends:    { "type": "approval_request", "data": { ...approval... } }
    """
    await ws.accept()
    _connected_clients.add(ws)

    try:
        while True:
            raw = await ws.receive_text()
            msg = json.loads(raw)

            if msg.get("type") == "decide":
                decision = ApprovalDecision(
                    approved=msg["approved"],
                    file_patterns=msg.get("file_patterns", []),
                    ttl_minutes=msg.get("ttl_minutes"),
                )
                try:
                    result = _approval_svc.resolve(msg["approval_id"], decision)
                    await ws.send_text(json.dumps({
                        "type": "decision_result",
                        "data": result.model_dump(mode="json"),
                    }))
                except KeyError as e:
                    await ws.send_text(json.dumps({
                        "type": "error",
                        "detail": str(e),
                    }))

    except WebSocketDisconnect:
        _connected_clients.discard(ws)
    except Exception:
        _connected_clients.discard(ws)
