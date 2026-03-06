"""File access endpoints — all gated behind approval checks."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.middleware.auth import require_token
from app.models.schemas import (
    AccessLevel,
    AuditAction,
    FileNode,
    FileReadResponse,
    FileWriteRequest,
    FileWriteResponse,
)
from app.services.approval_service import ApprovalService
from app.services.audit_service import AuditService
from app.services.file_service import FileService

router = APIRouter(prefix="/files", tags=["files"], dependencies=[Depends(require_token)])

# These get injected at app startup via router.state or app.state
_file_svc: FileService = None  # type: ignore
_approval_svc: ApprovalService = None  # type: ignore
_audit_svc: AuditService = None  # type: ignore


def init(file_svc: FileService, approval_svc: ApprovalService, audit_svc: AuditService):
    global _file_svc, _approval_svc, _audit_svc
    _file_svc, _approval_svc, _audit_svc = file_svc, approval_svc, audit_svc


@router.get("/tree", response_model=list[FileNode])
async def list_tree(
    path: str | None = Query(None, description="Subdirectory to list (default: all roots)"),
    depth: int = Query(3, ge=1, le=10),
):
    """List the file tree. Nodes are annotated with approval status."""

    def checker(p: str) -> bool:
        return _approval_svc.is_approved(p, AccessLevel.READ)

    try:
        nodes = _file_svc.list_tree(root_path=path, max_depth=depth, approved_checker=checker)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    _audit_svc.log(AuditAction.LIST, path or "<all roots>")
    return nodes


@router.get("/read", response_model=FileReadResponse)
async def read_file(path: str = Query(...)):
    """Read a file's contents. Requires an active READ approval."""
    try:
        resolved = str(_file_svc.resolve_and_validate(path))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    if not _approval_svc.is_approved(resolved, AccessLevel.READ):
        _audit_svc.log(AuditAction.READ, resolved, detail="DENIED — no approval", success=False)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"No active read approval for {path}. Request approval first via POST /approvals/request",
        )

    try:
        result = _file_svc.read_file(path)
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=str(e))

    _audit_svc.log(AuditAction.READ, resolved)
    return result


@router.put("/write", response_model=FileWriteResponse)
async def write_file(req: FileWriteRequest):
    """Write content to a file. Requires an active WRITE or READ_WRITE approval."""
    try:
        resolved = str(_file_svc.resolve_and_validate(req.path))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    if not _approval_svc.is_approved(resolved, AccessLevel.WRITE):
        _audit_svc.log(AuditAction.WRITE, resolved, detail="DENIED — no approval", success=False)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"No active write approval for {req.path}. Request approval first.",
        )

    try:
        result = _file_svc.write_file(req)
    except (FileNotFoundError, PermissionError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    _audit_svc.log(AuditAction.WRITE, resolved, detail=f"{result.bytes_written} bytes")
    return result
