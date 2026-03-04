"""
Audit logger for tracking all remediation operations.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import structlog

from src.config.settings import get_settings
from src.models.audit import AuditLog, AuditTrail

logger = structlog.get_logger()


class AuditLogger:
    """
    Logs all remediation actions for audit purposes.

    Features:
    - Persistent file logging
    - In-memory trail for queries
    - Structured audit records
    """

    def __init__(self, log_file: Optional[str] = None):
        settings = get_settings()
        self._enabled = settings.audit.enabled
        self._log_file = log_file or settings.audit.log_file
        self._trail = AuditTrail()

        # Ensure log directory exists
        if self._enabled:
            log_path = Path(self._log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

    @property
    def trail(self) -> AuditTrail:
        """Get audit trail."""
        return self._trail

    def log_action(
        self,
        action_type: str,
        target: str,
        status: str,
        plan_id: Optional[str] = None,
        step_id: Optional[str] = None,
        anomaly_id: Optional[str] = None,
        actor_type: str = "system",
        actor_id: str = "sre-agent",
        duration_seconds: Optional[int] = None,
        error_message: Optional[str] = None,
        state_before: Optional[Dict[str, Any]] = None,
        state_after: Optional[Dict[str, Any]] = None,
        parameters: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditLog:
        """
        Log an action.

        Args:
            action_type: Type of action performed
            target: Target of the action
            status: Action status (started, success, failed, rolled_back)
            plan_id: Associated plan ID
            step_id: Associated step ID
            anomaly_id: Associated anomaly ID
            actor_type: Type of actor (system, user, approval)
            actor_id: Actor identifier
            duration_seconds: Duration of action
            error_message: Error message if failed
            state_before: State before action
            state_after: State after action
            parameters: Action parameters
            metadata: Additional metadata

        Returns:
            Created AuditLog
        """
        audit_log = AuditLog(
            action_type=action_type,
            action_target=target,
            action_parameters=parameters or {},
            actor_type=actor_type,
            actor_id=actor_id,
            plan_id=plan_id,
            anomaly_id=anomaly_id,
            step_id=step_id,
            status=status,
            duration_seconds=duration_seconds,
            error_message=error_message,
            state_before=state_before or {},
            state_after=state_after or {},
            metadata=metadata or {},
        )

        # Add to in-memory trail
        self._trail.add_log(audit_log)

        # Write to file
        if self._enabled:
            self._write_to_file(audit_log)

        # Log to structured logger
        logger.info(
            "Audit log created",
            audit_id=audit_log.id,
            action_type=action_type,
            target=target,
            status=status,
            plan_id=plan_id,
        )

        return audit_log

    def _write_to_file(self, audit_log: AuditLog) -> None:
        """Write audit log to file."""
        try:
            log_entry = {
                "id": audit_log.id,
                "timestamp": audit_log.timestamp.isoformat(),
                "action_type": audit_log.action_type,
                "action_target": audit_log.action_target,
                "action_parameters": audit_log.action_parameters,
                "actor_type": audit_log.actor_type,
                "actor_id": audit_log.actor_id,
                "plan_id": audit_log.plan_id,
                "anomaly_id": audit_log.anomaly_id,
                "step_id": audit_log.step_id,
                "status": audit_log.status,
                "duration_seconds": audit_log.duration_seconds,
                "error_message": audit_log.error_message,
                "state_before": audit_log.state_before,
                "state_after": audit_log.state_after,
                "metadata": audit_log.metadata,
            }

            with open(self._log_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")

        except Exception as e:
            logger.error("Failed to write audit log to file", error=str(e))

    def get_logs_by_plan(self, plan_id: str) -> List[AuditLog]:
        """Get all logs for a plan."""
        return self._trail.get_by_plan(plan_id)

    def get_logs_by_anomaly(self, anomaly_id: str) -> List[AuditLog]:
        """Get all logs for an anomaly."""
        return self._trail.get_by_anomaly(anomaly_id)

    def get_recent_logs(
        self, limit: int = 100, action_type: Optional[str] = None
    ) -> List[AuditLog]:
        """Get recent audit logs."""
        return self._trail.get_recent(limit, action_type)

    def get_failures(self, limit: int = 50) -> List[AuditLog]:
        """Get recent failed operations."""
        return self._trail.get_failures(limit)

    def load_from_file(self, days: int = 7) -> int:
        """
        Load audit logs from file into memory.

        Args:
            days: Number of days to load

        Returns:
            Number of logs loaded
        """
        if not Path(self._log_file).exists():
            return 0

        cutoff = datetime.utcnow().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        from datetime import timedelta
        cutoff = cutoff - timedelta(days=days)

        loaded = 0
        try:
            with open(self._log_file) as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        timestamp = datetime.fromisoformat(data["timestamp"])
                        if timestamp >= cutoff:
                            audit_log = AuditLog(
                                id=data["id"],
                                timestamp=timestamp,
                                action_type=data["action_type"],
                                action_target=data["action_target"],
                                action_parameters=data.get("action_parameters", {}),
                                actor_type=data.get("actor_type", "system"),
                                actor_id=data.get("actor_id", "unknown"),
                                plan_id=data.get("plan_id"),
                                anomaly_id=data.get("anomaly_id"),
                                step_id=data.get("step_id"),
                                status=data["status"],
                                duration_seconds=data.get("duration_seconds"),
                                error_message=data.get("error_message"),
                                state_before=data.get("state_before", {}),
                                state_after=data.get("state_after", {}),
                                metadata=data.get("metadata", {}),
                            )
                            self._trail.add_log(audit_log)
                            loaded += 1
                    except (json.JSONDecodeError, KeyError):
                        continue

        except Exception as e:
            logger.error("Failed to load audit logs from file", error=str(e))

        return loaded
