"""Approval management endpoints.

Claude requests approval → user is notified (via WS or polling) → user approves/denies.
"""

from __future__ import annotations

import asyncio

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.middleware.auth import require_token
from app.models.schemas import (
    Approval,
    ApprovalDecision,
    ApprovalRequest,
    ApprovalStatus,
    AuditAction,
)
from app.services.approval_service import ApprovalService
from app.services.audit_service import AuditService
from app.services.file_service import FileService

router = APIRouter(prefix="/approvals", tags=["approvals"])

_approval_svc: ApprovalService = None  # type: ignore
_file_svc: FileService = None  # type: ignore
_audit_svc: AuditService = None  # type: ignore

# Callback for notifying the local UI (terminal or web dashboard)
_notify_callback = None


def init(
    approval_svc: ApprovalService,
    file_svc: FileService,
    audit_svc: AuditService,
    notify_callback=None,
):
    global _approval_svc, _file_svc, _audit_svc, _notify_callback
    _approval_svc = approval_svc
    _file_svc = file_svc
    _audit_svc = audit_svc
    _notify_callback = notify_callback


# ── Claude-facing (token-protected) ──────────────────────────────────────────

@router.post("/request", response_model=Approval, dependencies=[Depends(require_token)])
async def request_approval(req: ApprovalRequest, wait: bool = Query(True)):
    """Claude requests access to a file or directory.

    If wait=true (default), the call blocks until the user decides or timeout.
    If wait=false, returns immediately with status=PENDING.
    """
    try:
        resolved = str(_file_svc.resolve_and_validate(req.path))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    # Check if already approved
    existing = _approval_svc.get_approval_for(resolved, req.access)
    if existing:
        return existing

    approval = _approval_svc.create_request(req, resolved)
    _audit_svc.log(AuditAction.APPROVAL_REQUESTED, resolved, detail=req.reason)

    # Notify local user
    if _notify_callback:
        await _notify_callback(approval)

    if not wait:
        return approval

    # Block until user decides (5 min timeout)
    try:
        resolved_approval = await _approval_svc.wait_for_decision(approval.id, timeout=300)
        return resolved_approval
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail="Approval request timed out — user did not respond within 5 minutes",
        )


# ── User-facing (local dashboard, no token needed for localhost) ─────────────

@router.get("/", response_model=list[Approval])
async def list_approvals(include_expired: bool = Query(False)):
    """List all approval records."""
    return _approval_svc.list_all(include_expired=include_expired)


@router.get("/pending", response_model=list[Approval])
async def list_pending():
    """List only pending approval requests awaiting user decision."""
    return [
        a for a in _approval_svc.list_all() if a.status == ApprovalStatus.PENDING
    ]


@router.post("/{approval_id}/decide", response_model=Approval)
async def decide_approval(approval_id: str, decision: ApprovalDecision):
    """User approves or denies an access request."""
    try:
        approval = _approval_svc.resolve(approval_id, decision)
    except KeyError:
        raise HTTPException(status_code=404, detail="Approval not found")

    action = (
        AuditAction.APPROVAL_GRANTED if decision.approved else AuditAction.APPROVAL_DENIED
    )
    _audit_svc.log(action, approval.resolved_path)
    return approval


@router.delete("/{approval_id}", response_model=Approval)
async def revoke_approval(approval_id: str):
    """Revoke an existing approval."""
    try:
        approval = _approval_svc.revoke(approval_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Approval not found")

    _audit_svc.log(AuditAction.APPROVAL_REVOKED, approval.resolved_path)
    return approval
