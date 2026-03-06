"""
Data models for metrics, logs, and events.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field

from src.config.constants import EventType, LogLevel, MetricCategory


class MetricDataPoint(BaseModel):
    """A single metric data point."""

    timestamp: datetime
    value: float
    labels: Dict[str, str] = Field(default_factory=dict)

    class Config:
        frozen = True


class MetricSeries(BaseModel):
    """A time series of metric data points."""

    name: str
    category: MetricCategory
    unit: str
    description: str = ""
    labels: Dict[str, str] = Field(default_factory=dict)
    data_points: List[MetricDataPoint] = Field(default_factory=list)

    @property
    def values(self) -> List[float]:
        """Get just the values from the data points."""
        return [dp.value for dp in self.data_points]

    @property
    def timestamps(self) -> List[datetime]:
        """Get just the timestamps from the data points."""
        return [dp.timestamp for dp in self.data_points]

    @property
    def latest_value(self) -> Optional[float]:
        """Get the most recent value."""
        if not self.data_points:
            return None
        return self.data_points[-1].value

    @property
    def latest_timestamp(self) -> Optional[datetime]:
        """Get the most recent timestamp."""
        if not self.data_points:
            return None
        return self.data_points[-1].timestamp

    def get_values_in_range(
        self, start: datetime, end: datetime
    ) -> List[Tuple[datetime, float]]:
        """Get values within a time range."""
        return [
            (dp.timestamp, dp.value)
            for dp in self.data_points
            if start <= dp.timestamp <= end
        ]


class LogEntry(BaseModel):
    """A structured log entry from Loki."""

    timestamp: datetime
    level: LogLevel
    message: str
    service: str
    labels: Dict[str, str] = Field(default_factory=dict)
    structured_data: Dict[str, Any] = Field(default_factory=dict)

    # Common fields extracted from log
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    request_id: Optional[str] = None
    user_id: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None

    class Config:
        frozen = True


class Event(BaseModel):
    """A Kubernetes event or configuration change event."""

    timestamp: datetime
    event_type: EventType
    reason: str
    message: str
    source: str
    labels: Dict[str, str] = Field(default_factory=dict)

    # Kubernetes specific fields
    namespace: Optional[str] = None
    kind: Optional[str] = None
    name: Optional[str] = None
    count: int = 1
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None

    # For config change events
    config_key: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None

    class Config:
        frozen = True


class MetricQuery(BaseModel):
    """A metric query definition."""

    name: str
    query: str
    category: MetricCategory
    unit: str
    description: str = ""
    labels: Dict[str, str] = Field(default_factory=dict)


class CollectedData(BaseModel):
    """Container for all collected data in a collection cycle."""

    timestamp: datetime
    metrics: List[MetricSeries] = Field(default_factory=list)
    logs: List[LogEntry] = Field(default_factory=list)
    events: List[Event] = Field(default_factory=list)

    @property
    def metric_count(self) -> int:
        """Total number of metric data points."""
        return sum(len(m.data_points) for m in self.metrics)

    @property
    def log_count(self) -> int:
        """Number of log entries."""
        return len(self.logs)

    @property
    def event_count(self) -> int:
        """Number of events."""
        return len(self.events)
