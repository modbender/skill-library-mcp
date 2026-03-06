"""
Data models for audit logging.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class AuditLog(BaseModel):
    """Audit log entry for tracking all operations."""

    id: str = Field(default_factory=lambda: f"AUDIT-{uuid4().hex[:8]}")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Action details
    action_type: str
    action_target: str
    action_parameters: Dict[str, Any] = Field(default_factory=dict)

    # Actor
    actor_type: str  # "system", "user", "approval"
    actor_id: str

    # Context
    plan_id: Optional[str] = None
    anomaly_id: Optional[str] = None
    step_id: Optional[str] = None

    # Result
    status: str  # "started", "success", "failed", "rolled_back"
    duration_seconds: Optional[int] = None
    error_message: Optional[str] = None

    # Before/After state for rollback
    state_before: Dict[str, Any] = Field(default_factory=dict)
    state_after: Dict[str, Any] = Field(default_factory=dict)

    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AuditTrail(BaseModel):
    """Collection of audit logs."""

    logs: List[AuditLog] = Field(default_factory=list)

    def add_log(self, log: AuditLog) -> None:
        """Add a log entry."""
        self.logs.append(log)

    def get_by_plan(self, plan_id: str) -> List[AuditLog]:
        """Get all logs for a plan."""
        return [log for log in self.logs if log.plan_id == plan_id]

    def get_by_anomaly(self, anomaly_id: str) -> List[AuditLog]:
        """Get all logs for an anomaly."""
        return [log for log in self.logs if log.anomaly_id == anomaly_id]

    def get_by_actor(self, actor_id: str) -> List[AuditLog]:
        """Get all logs for an actor."""
        return [log for log in self.logs if log.actor_id == actor_id]

    def get_recent(
        self, limit: int = 100, action_type: Optional[str] = None
    ) -> List[AuditLog]:
        """Get recent logs with optional filtering."""
        logs = self.logs
        if action_type:
            logs = [log for log in logs if log.action_type == action_type]
        return sorted(logs, key=lambda x: x.timestamp, reverse=True)[:limit]

    def get_failures(self, limit: int = 50) -> List[AuditLog]:
        """Get recent failed operations."""
        failed = [log for log in self.logs if log.status == "failed"]
        return sorted(failed, key=lambda x: x.timestamp, reverse=True)[:limit]
