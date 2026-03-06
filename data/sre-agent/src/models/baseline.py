"""
Data models for baseline learning.
"""

from datetime import datetime
from typing import Optional, Dict, List, Any, Tuple, Set

import numpy as np
from pydantic import BaseModel, Field


class BaselineStatistics(BaseModel):
    """Statistical baseline for a metric."""

    mean: float
    std: float
    median: float
    mad: float  # Median Absolute Deviation
    min: float
    max: float
    percentile_5: float
    percentile_25: float
    percentile_75: float
    percentile_95: float
    sample_count: int

    @classmethod
    def from_values(cls, values: List[float]) -> "BaselineStatistics":
        """Calculate statistics from a list of values."""
        if not values:
            raise ValueError("Cannot calculate statistics from empty values")

        arr = np.array(values)
        median = float(np.median(arr))

        return cls(
            mean=float(np.mean(arr)),
            std=float(np.std(arr)),
            median=median,
            mad=float(np.median(np.abs(arr - median))),
            min=float(np.min(arr)),
            max=float(np.max(arr)),
            percentile_5=float(np.percentile(arr, 5)),
            percentile_25=float(np.percentile(arr, 25)),
            percentile_75=float(np.percentile(arr, 75)),
            percentile_95=float(np.percentile(arr, 95)),
            sample_count=len(values),
        )


class STLDecomposition(BaseModel):
    """STL time series decomposition components."""

    trend: List[float]
    seasonal: List[float]
    residual: List[float]
    period: int
    timestamps: List[datetime]


class HourlyBaseline(BaseModel):
    """Baseline statistics for a specific hour of day."""

    hour: int  # 0-23
    stats: BaselineStatistics
    day_of_week_adjustments: Dict[int, float] = Field(
        default_factory=dict
    )  # 0=Monday, 6=Sunday


class Baseline(BaseModel):
    """Complete baseline model for a metric."""

    metric_name: str
    labels: Dict[str, str] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    data_start: datetime
    data_end: datetime
    sample_count: int

    # Global statistics
    global_stats: BaselineStatistics

    # Hourly patterns (24 entries)
    hourly_baselines: List[HourlyBaseline] = Field(default_factory=list)

    # STL decomposition (optional, for advanced analysis)
    stl_decomposition: Optional[STLDecomposition] = None

    # Model quality metrics
    quality_score: float = 0.0  # 0-1, higher is better
    coverage_days: int = 0

    def get_expected_value(
        self, timestamp: datetime, use_hourly: bool = True
    ) -> Tuple[float, float]:
        """
        Get expected value and standard deviation for a timestamp.

        Returns:
            Tuple of (expected_value, expected_std)
        """
        if use_hourly and self.hourly_baselines:
            hour = timestamp.hour
            hourly = next(
                (h for h in self.hourly_baselines if h.hour == hour), None
            )
            if hourly:
                # Apply day-of-week adjustment if available
                dow = timestamp.weekday()
                adjustment = hourly.day_of_week_adjustments.get(dow, 1.0)
                return hourly.stats.mean * adjustment, hourly.stats.std

        return self.global_stats.mean, self.global_stats.std

    def get_threshold(
        self, timestamp: datetime, sigma: float = 3.0
    ) -> Tuple[float, float]:
        """
        Get upper and lower thresholds for anomaly detection.

        Returns:
            Tuple of (lower_threshold, upper_threshold)
        """
        mean, std = self.get_expected_value(timestamp)
        return mean - sigma * std, mean + sigma * std

    def is_stale(self, max_age_hours: int = 24) -> bool:
        """Check if baseline needs to be updated."""
        age = datetime.utcnow() - self.updated_at
        return age.total_seconds() > max_age_hours * 3600


class BaselineCollection(BaseModel):
    """Collection of baselines for multiple metrics."""

    baselines: Dict[str, Baseline] = Field(default_factory=dict)
    last_updated: Optional[datetime] = None

    def get_baseline(
        self, metric_name: str, labels: Optional[Dict[str, str]] = None
    ) -> Optional[Baseline]:
        """Get baseline for a metric with optional label matching."""
        key = self._make_key(metric_name, labels)
        return self.baselines.get(key)

    def set_baseline(
        self, metric_name: str, baseline: Baseline, labels: Optional[Dict[str, str]] = None
    ) -> None:
        """Store a baseline."""
        key = self._make_key(metric_name, labels)
        self.baselines[key] = baseline
        self.last_updated = datetime.utcnow()

    @staticmethod
    def _make_key(metric_name: str, labels: Optional[Dict[str, str]] = None) -> str:
        """Create a unique key for a metric+labels combination."""
        if not labels:
            return metric_name
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{metric_name}{{{label_str}}}"
