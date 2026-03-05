"""Approval management service.

Handles creating, resolving, checking, and expiring file-access approvals.
Stores state in memory (easily swappable to SQLite or file-backed store).
"""

from __future__ import annotations

import fnmatch
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from app.models.schemas import (
    AccessLevel,
    Approval,
    ApprovalDecision,
    ApprovalRequest,
    ApprovalScope,
    ApprovalStatus,
)


class ApprovalService:
    def __init__(self) -> None:
        self._approvals: dict[str, Approval] = {}
        # Callbacks awaiting user decisions — maps approval_id → Future
        self._pending_futures: dict[str, asyncio.Future] = {}

    # ── Create ────────────────────────────────────────────────────────────

    def create_request(
        self, req: ApprovalRequest, resolved_path: str
    ) -> Approval:
        """Register a new approval request (status=PENDING)."""
        approval = Approval(
            path=req.path,
            resolved_path=resolved_path,
            scope=req.scope,
            access=req.access,
            reason=req.reason,
            status=ApprovalStatus.PENDING,
        )
        if req.ttl_minutes:
            approval.expires_at = datetime.utcnow() + timedelta(minutes=req.ttl_minutes)

        self._approvals[approval.id] = approval

        # Create a future the caller can await for the user decision
        loop = asyncio.get_event_loop()
        self._pending_futures[approval.id] = loop.create_future()

        return approval

    # ── Resolve (user accepts / denies) ───────────────────────────────────

    def resolve(self, approval_id: str, decision: ApprovalDecision) -> Approval:
        """Mark an approval as approved or denied."""
        approval = self._approvals.get(approval_id)
        if not approval:
            raise KeyError(f"Approval {approval_id} not found")

        approval.status = (
            ApprovalStatus.APPROVED if decision.approved else ApprovalStatus.DENIED
        )
        approval.resolved_at = datetime.utcnow()

        if decision.approved:
            approval.file_patterns = decision.file_patterns
            if decision.ttl_minutes is not None:
                approval.expires_at = datetime.utcnow() + timedelta(
                    minutes=decision.ttl_minutes
                )

        # Unblock any waiters
        future = self._pending_futures.pop(approval_id, None)
        if future and not future.done():
            future.set_result(approval)

        return approval

    # ── Wait for decision (async) ─────────────────────────────────────────

    async def wait_for_decision(
        self, approval_id: str, timeout: float = 300
    ) -> Approval:
        """Await user decision on a pending approval (used by /approvals/request)."""
        future = self._pending_futures.get(approval_id)
        if not future:
            return self._approvals[approval_id]
        return await asyncio.wait_for(future, timeout=timeout)

    # ── Revoke ────────────────────────────────────────────────────────────

    def revoke(self, approval_id: str) -> Approval:
        approval = self._approvals.get(approval_id)
        if not approval:
            raise KeyError(f"Approval {approval_id} not found")
        approval.status = ApprovalStatus.REVOKED
        approval.resolved_at = datetime.utcnow()
        return approval

    # ── Check access ──────────────────────────────────────────────────────

    def is_approved(self, resolved_path: str, access: AccessLevel) -> bool:
        """Check whether a resolved path is currently approved for the given access."""
        self._expire_stale()
        target = Path(resolved_path)

        for a in self._approvals.values():
            if a.status != ApprovalStatus.APPROVED:
                continue
            if not self._access_sufficient(a.access, access):
                continue
            if self._path_matches(a, target):
                return True
        return False

    def get_approval_for(
        self, resolved_path: str, access: AccessLevel
    ) -> Optional[Approval]:
        """Return the active approval covering this path, if any."""
        self._expire_stale()
        target = Path(resolved_path)

        for a in self._approvals.values():
            if a.status != ApprovalStatus.APPROVED:
                continue
            if not self._access_sufficient(a.access, access):
                continue
            if self._path_matches(a, target):
                return a
        return None

    # ── List ──────────────────────────────────────────────────────────────

    def list_all(self, include_expired: bool = False) -> list[Approval]:
        self._expire_stale()
        if include_expired:
            return list(self._approvals.values())
        return [
            a
            for a in self._approvals.values()
            if a.status in (ApprovalStatus.PENDING, ApprovalStatus.APPROVED)
        ]

    # ── Internals ─────────────────────────────────────────────────────────

    @staticmethod
    def _access_sufficient(granted: AccessLevel, requested: AccessLevel) -> bool:
        if granted == AccessLevel.READ_WRITE:
            return True
        return granted == requested

    @staticmethod
    def _path_matches(approval: Approval, target: Path) -> bool:
        approved = Path(approval.resolved_path)

        if approval.scope == ApprovalScope.FILE:
            return target == approved

        # Directory scopes
        try:
            rel = target.relative_to(approved)
        except ValueError:
            return False

        if approval.scope == ApprovalScope.DIRECTORY_SHALLOW:
            if len(rel.parts) > 1:
                return False

        # Check glob patterns if set
        if approval.file_patterns:
            return any(
                fnmatch.fnmatch(target.name, pat) for pat in approval.file_patterns
            )
        return True

    def _expire_stale(self) -> None:
        now = datetime.utcnow()
        for a in self._approvals.values():
            if (
                a.status == ApprovalStatus.APPROVED
                and a.expires_at
                and a.expires_at < now
            ):
                a.status = ApprovalStatus.EXPIRED
