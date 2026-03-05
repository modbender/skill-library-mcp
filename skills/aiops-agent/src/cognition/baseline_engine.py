"""
Baseline learning engine using STL decomposition.

Learns normal system behavior patterns from historical data
to establish baselines for anomaly detection.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import structlog
from statsmodels.tsa.seasonal import STL

from src.config.settings import get_settings
from src.models.baseline import (
    Baseline,
    BaselineCollection,
    BaselineStatistics,
    HourlyBaseline,
    STLDecomposition,
)
from src.models.metrics import MetricSeries
from src.perception.normalizer import DataNormalizer

logger = structlog.get_logger()


class BaselineEngine:
    """
    Learns and maintains baselines for metrics.

    Features:
    - STL time series decomposition
    - Hourly pattern learning
    - Day-of-week adjustments
    - Incremental updates
    - Quality scoring
    """

    def __init__(
        self,
        min_history_days: Optional[int] = None,
        optimal_history_days: Optional[int] = None,
        stl_period: Optional[int] = None,
    ):
        settings = get_settings()
        self.min_history_days = min_history_days or settings.baseline.min_history_days
        self.optimal_history_days = optimal_history_days or settings.baseline.optimal_history_days
        self.stl_period = stl_period or settings.baseline.stl_period

        self._normalizer = DataNormalizer()
        self._baselines = BaselineCollection()

    @property
    def baselines(self) -> BaselineCollection:
        """Get current baseline collection."""
        return self._baselines

    def learn_baseline(
        self,
        series: MetricSeries,
        filter_outliers: bool = True,
    ) -> Optional[Baseline]:
        """
        Learn baseline from a metric series.

        Args:
            series: Historical metric data
            filter_outliers: Whether to filter outliers before learning

        Returns:
            Learned Baseline or None if insufficient data
        """
        if not series.data_points:
            logger.warning(
                "Cannot learn baseline from empty series",
                metric=series.name,
            )
            return None

        # Check minimum data requirement
        data_span = series.data_points[-1].timestamp - series.data_points[0].timestamp
        if data_span.days < self.min_history_days:
            logger.warning(
                "Insufficient data for baseline learning",
                metric=series.name,
                days=data_span.days,
                required=self.min_history_days,
            )
            return None

        values = series.values
        timestamps = series.timestamps

        # Filter outliers if requested
        if filter_outliers:
            values, timestamps = self._normalizer.filter_outliers_for_baseline(
                values, timestamps
            )

        if len(values) < 24:  # Need at least 24 points
            logger.warning(
                "Too few data points after filtering",
                metric=series.name,
                count=len(values),
            )
            return None

        # Calculate global statistics
        global_stats = BaselineStatistics.from_values(values)

        # Calculate hourly baselines
        hourly_baselines = self._calculate_hourly_baselines(values, timestamps)

        # Perform STL decomposition if enough data
        stl_decomposition = None
        if len(values) >= self.stl_period * 2:
            stl_decomposition = self._perform_stl(values, timestamps)

        # Calculate quality score
        quality_score = self._calculate_quality_score(
            len(values), data_span.days, global_stats
        )

        baseline = Baseline(
            metric_name=series.name,
            labels=series.labels,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            data_start=timestamps[0] if timestamps else series.data_points[0].timestamp,
            data_end=timestamps[-1] if timestamps else series.data_points[-1].timestamp,
            sample_count=len(values),
            global_stats=global_stats,
            hourly_baselines=hourly_baselines,
            stl_decomposition=stl_decomposition,
            quality_score=quality_score,
            coverage_days=data_span.days,
        )

        # Store in collection
        self._baselines.set_baseline(series.name, baseline, series.labels)

        logger.info(
            "Learned baseline",
            metric=series.name,
            samples=len(values),
            quality=quality_score,
            days=data_span.days,
        )

        return baseline

    def _calculate_hourly_baselines(
        self,
        values: List[float],
        timestamps: Optional[List[datetime]],
    ) -> List[HourlyBaseline]:
        """Calculate per-hour baselines."""
        if not timestamps:
            return []

        # Group values by hour
        hourly_values: Dict[int, List[float]] = {h: [] for h in range(24)}
        dow_hourly_values: Dict[int, Dict[int, List[float]]] = {
            h: {d: [] for d in range(7)} for h in range(24)
        }

        for ts, val in zip(timestamps, values):
            hour = ts.hour
            dow = ts.weekday()
            hourly_values[hour].append(val)
            dow_hourly_values[hour][dow].append(val)

        baselines: List[HourlyBaseline] = []
        for hour in range(24):
            if len(hourly_values[hour]) < 5:
                continue

            stats = BaselineStatistics.from_values(hourly_values[hour])

            # Calculate day-of-week adjustments
            adjustments: Dict[int, float] = {}
            for dow in range(7):
                dow_vals = dow_hourly_values[hour][dow]
                if len(dow_vals) >= 3 and stats.mean != 0:
                    dow_mean = float(np.mean(dow_vals))
                    adjustments[dow] = dow_mean / stats.mean

            baselines.append(
                HourlyBaseline(
                    hour=hour,
                    stats=stats,
                    day_of_week_adjustments=adjustments,
                )
            )

        return baselines

    def _perform_stl(
        self,
        values: List[float],
        timestamps: Optional[List[datetime]],
    ) -> Optional[STLDecomposition]:
        """Perform STL decomposition."""
        try:
            arr = np.array(values)

            # Handle any remaining NaN values
            if np.any(np.isnan(arr)):
                arr = np.nan_to_num(arr, nan=np.nanmean(arr))

            stl = STL(arr, period=self.stl_period, robust=True)
            result = stl.fit()

            return STLDecomposition(
                trend=result.trend.tolist(),
                seasonal=result.seasonal.tolist(),
                residual=result.resid.tolist(),
                period=self.stl_period,
                timestamps=timestamps or [],
            )
        except Exception as e:
            logger.warning("STL decomposition failed", error=str(e))
            return None

    def _calculate_quality_score(
        self,
        sample_count: int,
        coverage_days: int,
        stats: BaselineStatistics,
    ) -> float:
        """
        Calculate baseline quality score (0-1).

        Factors:
        - Sample count (more is better)
        - Coverage days (closer to optimal is better)
        - Coefficient of variation (lower is better for stability)
        """
        # Sample count factor (0-0.3)
        expected_samples = self.optimal_history_days * 24 * 60  # 1-minute resolution
        sample_factor = min(sample_count / expected_samples, 1.0) * 0.3

        # Coverage factor (0-0.4)
        coverage_factor = min(coverage_days / self.optimal_history_days, 1.0) * 0.4

        # Stability factor (0-0.3)
        if stats.mean != 0:
            cv = stats.std / abs(stats.mean)
            stability_factor = max(0, 1 - cv) * 0.3
        else:
            stability_factor = 0.15  # Neutral if mean is 0

        return sample_factor + coverage_factor + stability_factor

    def get_baseline(
        self,
        metric_name: str,
        labels: Optional[Dict[str, str]] = None,
    ) -> Optional[Baseline]:
        """Get baseline for a metric."""
        return self._baselines.get_baseline(metric_name, labels)

    def get_expected_value(
        self,
        metric_name: str,
        timestamp: datetime,
        labels: Optional[Dict[str, str]] = None,
    ) -> Optional[Tuple[float, float]]:
        """
        Get expected value and std for a metric at a timestamp.

        Returns:
            Tuple of (expected_value, expected_std) or None if no baseline
        """
        baseline = self.get_baseline(metric_name, labels)
        if not baseline:
            return None
        return baseline.get_expected_value(timestamp)

    def update_baseline(
        self,
        series: MetricSeries,
        incremental: bool = True,
    ) -> Optional[Baseline]:
        """
        Update existing baseline with new data.

        Args:
            series: New metric data
            incremental: If True, merge with existing; if False, replace

        Returns:
            Updated Baseline
        """
        existing = self.get_baseline(series.name, series.labels)

        if not existing or not incremental:
            return self.learn_baseline(series)

        # Merge new data with existing baseline
        # For simplicity, we'll re-learn with full data
        # In production, this could be optimized with incremental updates
        return self.learn_baseline(series)

    def get_stale_baselines(self, max_age_hours: int = 24) -> List[str]:
        """Get list of baselines that need updating."""
        stale: List[str] = []
        for key, baseline in self._baselines.baselines.items():
            if baseline.is_stale(max_age_hours):
                stale.append(key)
        return stale

    def export_baselines(self) -> Dict[str, Any]:
        """Export all baselines as dictionary."""
        return {
            key: baseline.model_dump()
            for key, baseline in self._baselines.baselines.items()
        }

    def import_baselines(self, data: Dict[str, Any]) -> int:
        """
        Import baselines from dictionary.

        Returns:
            Number of baselines imported
        """
        count = 0
        for key, baseline_data in data.items():
            try:
                baseline = Baseline.model_validate(baseline_data)
                self._baselines.baselines[key] = baseline
                count += 1
            except Exception as e:
                logger.warning(
                    "Failed to import baseline",
                    key=key,
                    error=str(e),
                )
        return count
