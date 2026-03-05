"""
Playbook execution statistics models.

Tracks execution history and statistics for playbooks to enable
learning and automatic risk adjustment.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class PlaybookExecution(BaseModel):
    """Record of a single playbook execution."""

    id: str = Field(default_factory=lambda: f"exec-{uuid4().hex[:8]}")
    playbook_id: str
    plan_id: str
    anomaly_id: str
    executed_at: datetime = Field(default_factory=datetime.utcnow)

    # Execution results
    success: bool
    duration_seconds: int = 0
    steps_total: int = 0
    steps_succeeded: int = 0
    steps_failed: int = 0
    steps_skipped: int = 0

    # Error details
    error_message: Optional[str] = None
    error_step: Optional[str] = None
    rolled_back: bool = False

    # Context
    risk_score: float = 0.0
    target: str = ""
    namespace: str = ""

    # Additional metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PlaybookStats(BaseModel):
    """Aggregated statistics for a playbook."""

    playbook_id: str
    playbook_name: str = ""

    # Execution counts
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    rolled_back_executions: int = 0

    # Computed metrics
    success_rate: float = 0.0
    avg_duration_seconds: float = 0.0
    min_duration_seconds: int = 0
    max_duration_seconds: int = 0

    # Time tracking
    first_execution: Optional[datetime] = None
    last_execution: Optional[datetime] = None
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None

    # Learning metrics
    confidence_score: float = 0.0  # Based on execution count and success rate
    suggested_risk_adjustment: float = 0.0  # Positive = increase risk, negative = decrease

    # Recent executions for trend analysis
    recent_execution_ids: List[str] = Field(default_factory=list)

    def update_from_execution(self, execution: PlaybookExecution) -> None:
        """Update statistics from a new execution record."""
        self.total_executions += 1

        if execution.success:
            self.successful_executions += 1
            self.last_success = execution.executed_at
        else:
            self.failed_executions += 1
            self.last_failure = execution.executed_at

        if execution.rolled_back:
            self.rolled_back_executions += 1

        # Update time tracking
        if self.first_execution is None:
            self.first_execution = execution.executed_at
        self.last_execution = execution.executed_at

        # Update duration statistics
        if execution.duration_seconds > 0:
            if self.min_duration_seconds == 0:
                self.min_duration_seconds = execution.duration_seconds
            else:
                self.min_duration_seconds = min(
                    self.min_duration_seconds, execution.duration_seconds
                )
            self.max_duration_seconds = max(
                self.max_duration_seconds, execution.duration_seconds
            )

            # Update average (using cumulative formula)
            n = self.total_executions
            prev_avg = self.avg_duration_seconds
            self.avg_duration_seconds = prev_avg + (execution.duration_seconds - prev_avg) / n

        # Update success rate
        self.success_rate = self.successful_executions / self.total_executions

        # Update confidence score (based on execution count and consistency)
        self._update_confidence_score()

        # Update risk adjustment suggestion
        self._update_risk_adjustment()

        # Keep track of recent executions (max 20)
        self.recent_execution_ids.append(execution.id)
        if len(self.recent_execution_ids) > 20:
            self.recent_execution_ids = self.recent_execution_ids[-20:]

    def _update_confidence_score(self) -> None:
        """Calculate confidence score based on execution history."""
        # Confidence increases with more executions up to a maximum
        execution_factor = min(self.total_executions / 20, 1.0)

        # Higher success rate increases confidence
        success_factor = self.success_rate

        # Recent failures decrease confidence
        if self.last_failure and self.last_success:
            if self.last_failure > self.last_success:
                # Most recent was a failure - reduce confidence
                success_factor *= 0.8

        # Combined confidence score
        self.confidence_score = execution_factor * success_factor

    def _update_risk_adjustment(self) -> None:
        """Calculate suggested risk adjustment based on performance."""
        if self.total_executions < 3:
            # Not enough data for adjustment
            self.suggested_risk_adjustment = 0.0
            return

        # High success rate suggests risk can be reduced
        if self.success_rate >= 0.95:
            self.suggested_risk_adjustment = -0.15
        elif self.success_rate >= 0.90:
            self.suggested_risk_adjustment = -0.10
        elif self.success_rate >= 0.80:
            self.suggested_risk_adjustment = -0.05
        elif self.success_rate >= 0.70:
            self.suggested_risk_adjustment = 0.0
        elif self.success_rate >= 0.50:
            self.suggested_risk_adjustment = 0.05
        else:
            # Low success rate - increase risk
            self.suggested_risk_adjustment = 0.15

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the statistics."""
        return {
            "playbook_id": self.playbook_id,
            "playbook_name": self.playbook_name,
            "total_executions": self.total_executions,
            "success_rate": f"{self.success_rate:.1%}",
            "avg_duration": f"{self.avg_duration_seconds:.1f}s",
            "confidence": f"{self.confidence_score:.2f}",
            "risk_adjustment": f"{self.suggested_risk_adjustment:+.2f}",
            "last_execution": (
                self.last_execution.isoformat() if self.last_execution else None
            ),
        }


class ExecutionCase(BaseModel):
    """
    A case study of an execution for knowledge base storage.

    Combines anomaly context, execution details, and outcomes
    for learning and similarity search.
    """

    id: str = Field(default_factory=lambda: f"case-{uuid4().hex[:8]}")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Anomaly context
    anomaly_id: str
    anomaly_type: str
    metric_name: str
    metric_category: str
    severity: str
    deviation: float
    duration_minutes: int

    # Execution context
    playbook_id: str
    plan_id: str
    action_types: List[str] = Field(default_factory=list)
    target: str
    namespace: str

    # Outcome
    success: bool
    duration_seconds: int
    error_message: Optional[str] = None
    rolled_back: bool = False

    # Lessons learned (extracted from failures)
    lessons_learned: List[str] = Field(default_factory=list)

    # Root cause (if known)
    root_cause: Optional[str] = None
    resolution_summary: Optional[str] = None

    # Tags for searching
    tags: List[str] = Field(default_factory=list)

    # Embedding for similarity search
    embedding: Optional[List[float]] = None

    def to_search_text(self) -> str:
        """Generate text for embedding/search."""
        parts = [
            f"Anomaly in {self.metric_name} ({self.metric_category})",
            f"Type: {self.anomaly_type}",
            f"Severity: {self.severity}",
            f"Deviation: {self.deviation:.1f} sigma",
            f"Actions: {', '.join(self.action_types)}",
            f"Target: {self.target}",
            f"Outcome: {'success' if self.success else 'failed'}",
        ]

        if self.root_cause:
            parts.append(f"Root cause: {self.root_cause}")

        if self.resolution_summary:
            parts.append(f"Resolution: {self.resolution_summary}")

        if self.lessons_learned:
            parts.append(f"Lessons: {'; '.join(self.lessons_learned)}")

        return " ".join(parts)


class PlaybookStatsStore:
    """In-memory store for playbook statistics."""

    def __init__(self):
        self._stats: Dict[str, PlaybookStats] = {}
        self._executions: Dict[str, PlaybookExecution] = {}

    def get_or_create_stats(
        self, playbook_id: str, playbook_name: str = ""
    ) -> PlaybookStats:
        """Get existing stats or create new ones."""
        if playbook_id not in self._stats:
            self._stats[playbook_id] = PlaybookStats(
                playbook_id=playbook_id,
                playbook_name=playbook_name,
            )
        return self._stats[playbook_id]

    def record_execution(self, execution: PlaybookExecution) -> PlaybookStats:
        """Record an execution and update stats."""
        self._executions[execution.id] = execution

        stats = self.get_or_create_stats(execution.playbook_id)
        stats.update_from_execution(execution)

        return stats

    def get_stats(self, playbook_id: str) -> Optional[PlaybookStats]:
        """Get stats for a playbook."""
        return self._stats.get(playbook_id)

    def get_all_stats(self) -> List[PlaybookStats]:
        """Get all playbook statistics."""
        return list(self._stats.values())

    def get_execution(self, execution_id: str) -> Optional[PlaybookExecution]:
        """Get an execution record."""
        return self._executions.get(execution_id)

    def get_executions_for_playbook(
        self, playbook_id: str, limit: int = 20
    ) -> List[PlaybookExecution]:
        """Get recent executions for a playbook."""
        executions = [
            e for e in self._executions.values() if e.playbook_id == playbook_id
        ]
        executions.sort(key=lambda x: x.executed_at, reverse=True)
        return executions[:limit]

    def get_summary(self) -> Dict[str, Any]:
        """Get overall summary."""
        total_executions = len(self._executions)
        successful = sum(1 for e in self._executions.values() if e.success)

        return {
            "total_playbooks": len(self._stats),
            "total_executions": total_executions,
            "successful_executions": successful,
            "overall_success_rate": (
                successful / total_executions if total_executions > 0 else 0.0
            ),
        }
