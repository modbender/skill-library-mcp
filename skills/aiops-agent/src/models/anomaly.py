"""
Data models for anomaly detection.
"""

from datetime import datetime
from typing import Optional, Dict, List, Any, Tuple, Set
from uuid import uuid4

from pydantic import BaseModel, Field

from src.config.constants import AnomalySeverity, AnomalyType, MetricCategory


class AnomalyScore(BaseModel):
    """Detailed anomaly scoring."""

    algorithm: str
    score: float  # 0-1, higher means more anomalous
    threshold: float
    is_anomaly: bool
    details: Dict[str, float] = Field(default_factory=dict)


class AnomalyContext(BaseModel):
    """Contextual information about an anomaly."""

    # Related metrics that may be affected
    related_metrics: List[str] = Field(default_factory=list)

    # Recent events that may be related
    recent_events: List[str] = Field(default_factory=list)

    # Recent log patterns
    log_patterns: List[str] = Field(default_factory=list)

    # Potential root causes (from RCA)
    potential_causes: List[str] = Field(default_factory=list)

    # Similar historical incidents (from RAG)
    similar_incidents: List[str] = Field(default_factory=list)


class Anomaly(BaseModel):
    """Detected anomaly with full context."""

    id: str = Field(default_factory=lambda: f"ANO-{uuid4().hex[:8]}")
    detected_at: datetime
    metric_name: str
    category: MetricCategory
    labels: Dict[str, str] = Field(default_factory=dict)

    # Current state
    current_value: float
    baseline_value: float
    deviation: float  # How many sigmas away from baseline
    deviation_percent: float  # Percentage deviation from baseline

    # Classification
    anomaly_type: AnomalyType
    severity: AnomalySeverity

    # Scoring from multiple algorithms
    scores: List[AnomalyScore] = Field(default_factory=list)
    ensemble_score: float = 0.0  # Combined score from all algorithms

    # Timing
    started_at: Optional[datetime] = None
    duration_minutes: int = 0

    # Context
    context: AnomalyContext = Field(default_factory=AnomalyContext)

    # State tracking
    is_active: bool = True
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    resolved_at: Optional[datetime] = None

    @property
    def is_critical(self) -> bool:
        """Check if this is a critical anomaly."""
        return self.severity == AnomalySeverity.CRITICAL

    @property
    def metric_key(self) -> str:
        """Get unique key for this metric."""
        if not self.labels:
            return self.metric_name
        label_str = ",".join(f"{k}={v}" for k, v in sorted(self.labels.items()))
        return f"{self.metric_name}{{{label_str}}}"

    def to_alert_message(self) -> str:
        """Generate human-readable alert message."""
        direction = "above" if self.deviation > 0 else "below"
        return (
            f"[{self.severity.value.upper()}] {self.metric_name} is {abs(self.deviation):.1f} "
            f"sigma {direction} baseline. Current: {self.current_value:.2f}, "
            f"Expected: {self.baseline_value:.2f} ({self.deviation_percent:+.1f}%)"
        )


class AnomalyBatch(BaseModel):
    """A batch of anomalies detected in a single detection cycle."""

    detection_time: datetime
    anomalies: List[Anomaly] = Field(default_factory=list)
    total_metrics_checked: int = 0
    detection_duration_ms: int = 0

    @property
    def count(self) -> int:
        """Number of anomalies in batch."""
        return len(self.anomalies)

    @property
    def critical_count(self) -> int:
        """Number of critical anomalies."""
        return sum(1 for a in self.anomalies if a.is_critical)

    def filter_by_severity(self, severity: AnomalySeverity) -> List[Anomaly]:
        """Get anomalies of a specific severity."""
        return [a for a in self.anomalies if a.severity == severity]

    def filter_by_category(self, category: MetricCategory) -> List[Anomaly]:
        """Get anomalies in a specific category."""
        return [a for a in self.anomalies if a.category == category]


class AnomalyState(BaseModel):
    """Tracks the state of active anomalies."""

    active_anomalies: Dict[str, Anomaly] = Field(default_factory=dict)
    resolved_anomalies: List[Anomaly] = Field(default_factory=list)
    last_updated: Optional[datetime] = None

    def add_anomaly(self, anomaly: Anomaly) -> None:
        """Add or update an anomaly."""
        self.active_anomalies[anomaly.metric_key] = anomaly
        self.last_updated = datetime.utcnow()

    def resolve_anomaly(self, metric_key: str) -> Optional[Anomaly]:
        """Mark an anomaly as resolved."""
        if metric_key in self.active_anomalies:
            anomaly = self.active_anomalies.pop(metric_key)
            anomaly.is_active = False
            anomaly.resolved_at = datetime.utcnow()
            self.resolved_anomalies.append(anomaly)
            self.last_updated = datetime.utcnow()
            return anomaly
        return None

    def get_active_by_category(self, category: MetricCategory) -> List[Anomaly]:
        """Get active anomalies by category."""
        return [
            a for a in self.active_anomalies.values() if a.category == category
        ]

    @property
    def active_count(self) -> int:
        """Number of active anomalies."""
        return len(self.active_anomalies)
