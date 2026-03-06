"""Audit log endpoint."""

from fastapi import APIRouter, Query

from app.models.schemas import AuditEntry
from app.services.audit_service import AuditService

router = APIRouter(prefix="/audit", tags=["audit"])

_audit_svc: AuditService = None  # type: ignore


def init(audit_svc: AuditService):
    global _audit_svc
    _audit_svc = audit_svc


@router.get("/", response_model=list[AuditEntry])
async def get_audit_log(limit: int = Query(100, ge=1, le=1000)):
    return _audit_svc.recent(limit)


@router.get("/path", response_model=list[AuditEntry])
async def get_audit_for_path(path: str, limit: int = Query(50)):
    return _audit_svc.for_path(path, limit)
