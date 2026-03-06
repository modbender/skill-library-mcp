"""
Data normalizer for standardizing collected data.

Handles:
- Missing value imputation
- Outlier filtering for baseline learning
- Time alignment across sources
- Label normalization
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import structlog

from src.models.metrics import CollectedData, Event, LogEntry, MetricDataPoint, MetricSeries

logger = structlog.get_logger()


class DataNormalizer:
    """
    Normalizes and preprocesses collected data.

    Features:
    - Aligns time series to common intervals
    - Imputes missing values
    - Filters outliers for baseline learning
    - Standardizes labels
    """

    def __init__(
        self,
        time_resolution_minutes: int = 1,
        outlier_threshold_sigma: float = 4.0,
        max_gap_minutes: int = 5,
    ):
        self.time_resolution = timedelta(minutes=time_resolution_minutes)
        self.outlier_threshold = outlier_threshold_sigma
        self.max_gap = timedelta(minutes=max_gap_minutes)

    def normalize_collected_data(self, data: CollectedData) -> CollectedData:
        """
        Normalize all collected data.

        Args:
            data: Raw collected data

        Returns:
            Normalized CollectedData
        """
        normalized_metrics = [
            self.normalize_metric_series(series) for series in data.metrics
        ]
        normalized_logs = self.normalize_logs(data.logs)
        normalized_events = self.normalize_events(data.events)

        return CollectedData(
            timestamp=data.timestamp,
            metrics=normalized_metrics,
            logs=normalized_logs,
            events=normalized_events,
        )

    def normalize_metric_series(self, series: MetricSeries) -> MetricSeries:
        """
        Normalize a single metric series.

        - Sorts by timestamp
        - Removes duplicates
        - Aligns to time resolution
        """
        if not series.data_points:
            return series

        # Sort by timestamp
        sorted_points = sorted(series.data_points, key=lambda x: x.timestamp)

        # Remove duplicates (keep last value for each timestamp)
        seen_times: Dict[datetime, MetricDataPoint] = {}
        for point in sorted_points:
            aligned_time = self._align_timestamp(point.timestamp)
            seen_times[aligned_time] = MetricDataPoint(
                timestamp=aligned_time,
                value=point.value,
                labels=point.labels,
            )

        return MetricSeries(
            name=series.name,
            category=series.category,
            unit=series.unit,
            description=series.description,
            labels=self._normalize_labels(series.labels),
            data_points=list(seen_times.values()),
        )

    def normalize_logs(self, logs: List[LogEntry]) -> List[LogEntry]:
        """
        Normalize log entries.

        - Sorts by timestamp (newest first)
        - Removes duplicates
        - Normalizes labels
        """
        # Sort by timestamp descending
        sorted_logs = sorted(logs, key=lambda x: x.timestamp, reverse=True)

        # Remove duplicates based on timestamp + message hash
        seen: Set[Tuple[datetime, int]] = set()
        unique_logs: List[LogEntry] = []

        for log in sorted_logs:
            key = (log.timestamp, hash(log.message[:200]))
            if key not in seen:
                seen.add(key)
                # Create new log with normalized labels
                unique_logs.append(
                    LogEntry(
                        timestamp=log.timestamp,
                        level=log.level,
                        message=log.message,
                        service=log.service,
                        labels=self._normalize_labels(log.labels),
                        structured_data=log.structured_data,
                        trace_id=log.trace_id,
                        span_id=log.span_id,
                        request_id=log.request_id,
                        user_id=log.user_id,
                        error_code=log.error_code,
                        error_message=log.error_message,
                    )
                )

        return unique_logs

    def normalize_events(self, events: List[Event]) -> List[Event]:
        """
        Normalize events.

        - Sorts by timestamp
        - Aggregates duplicate events
        """
        # Sort by timestamp descending
        sorted_events = sorted(events, key=lambda x: x.timestamp, reverse=True)

        # Aggregate similar events
        aggregated: Dict[str, Event] = {}

        for event in sorted_events:
            # Create key from event characteristics
            key = f"{event.namespace}:{event.kind}:{event.name}:{event.reason}"

            if key not in aggregated:
                aggregated[key] = event
            else:
                # Update count for existing event
                existing = aggregated[key]
                aggregated[key] = Event(
                    timestamp=max(event.timestamp, existing.timestamp),
                    event_type=event.event_type,
                    reason=event.reason,
                    message=event.message,
                    source=event.source,
                    labels=self._normalize_labels(event.labels),
                    namespace=event.namespace,
                    kind=event.kind,
                    name=event.name,
                    count=existing.count + event.count,
                    first_seen=min(
                        event.first_seen or event.timestamp,
                        existing.first_seen or existing.timestamp,
                    ),
                    last_seen=max(
                        event.last_seen or event.timestamp,
                        existing.last_seen or existing.timestamp,
                    ),
                )

        return list(aggregated.values())

    def filter_outliers_for_baseline(
        self, values: List[float], timestamps: Optional[List[datetime]] = None
    ) -> Optional[Tuple[List[float], List[datetime]]]:
        """
        Filter outliers from data before baseline learning.

        Uses MAD (Median Absolute Deviation) for robust outlier detection.

        Args:
            values: List of metric values
            timestamps: Optional corresponding timestamps

        Returns:
            Filtered values and timestamps
        """
        if len(values) < 10:
            return values, timestamps

        arr = np.array(values)
        median = np.median(arr)
        mad = np.median(np.abs(arr - median))

        if mad == 0:
            return values, timestamps

        # Modified Z-score using MAD
        modified_z = 0.6745 * (arr - median) / mad
        mask = np.abs(modified_z) <= self.outlier_threshold

        filtered_values = arr[mask].tolist()
        filtered_timestamps = None

        if timestamps:
            ts_arr = np.array(timestamps)
            filtered_timestamps = ts_arr[mask].tolist()

        removed_count = len(values) - len(filtered_values)
        if removed_count > 0:
            logger.debug(
                "Filtered outliers for baseline",
                total=len(values),
                removed=removed_count,
            )

        return filtered_values, filtered_timestamps

    def impute_missing_values(
        self,
        series: MetricSeries,
        start_time: datetime,
        end_time: datetime,
        method: str = "linear",
    ) -> MetricSeries:
        """
        Impute missing values in a metric series.

        Args:
            series: Metric series with potential gaps
            start_time: Expected start time
            end_time: Expected end time
            method: Imputation method ('linear', 'forward_fill', 'backward_fill', 'mean')

        Returns:
            Series with imputed values
        """
        if not series.data_points:
            return series

        # Build expected timestamps
        expected_times: List[datetime] = []
        current = self._align_timestamp(start_time)
        while current <= end_time:
            expected_times.append(current)
            current += self.time_resolution

        # Create map of existing values
        existing: Dict[datetime, float] = {
            self._align_timestamp(dp.timestamp): dp.value for dp in series.data_points
        }

        # Impute missing values
        imputed_points: List[MetricDataPoint] = []
        values_list = list(existing.values())

        for ts in expected_times:
            if ts in existing:
                value = existing[ts]
            else:
                # Check gap size
                gap_start = ts
                gap_end = ts
                while gap_end + self.time_resolution not in existing and gap_end < end_time:
                    gap_end += self.time_resolution

                if gap_end - gap_start > self.max_gap:
                    # Gap too large, skip
                    continue

                # Impute based on method
                value = self._impute_value(ts, existing, values_list, method)
                if value is None:
                    continue

            imputed_points.append(
                MetricDataPoint(
                    timestamp=ts,
                    value=value,
                    labels=series.labels,
                )
            )

        return MetricSeries(
            name=series.name,
            category=series.category,
            unit=series.unit,
            description=series.description,
            labels=series.labels,
            data_points=imputed_points,
        )

    def _impute_value(
        self,
        timestamp: datetime,
        existing: Dict[datetime, float],
        all_values: List[float],
        method: str,
    ) -> Optional[float]:
        """Impute a single missing value."""
        if method == "mean":
            return float(np.mean(all_values)) if all_values else None

        if method == "forward_fill":
            # Find previous value
            for offset in range(1, 10):
                prev_ts = timestamp - offset * self.time_resolution
                if prev_ts in existing:
                    return existing[prev_ts]
            return None

        if method == "backward_fill":
            # Find next value
            for offset in range(1, 10):
                next_ts = timestamp + offset * self.time_resolution
                if next_ts in existing:
                    return existing[next_ts]
            return None

        if method == "linear":
            # Linear interpolation
            prev_ts = prev_val = next_ts = next_val = None

            for offset in range(1, 10):
                ts = timestamp - offset * self.time_resolution
                if ts in existing:
                    prev_ts = ts
                    prev_val = existing[ts]
                    break

            for offset in range(1, 10):
                ts = timestamp + offset * self.time_resolution
                if ts in existing:
                    next_ts = ts
                    next_val = existing[ts]
                    break

            if prev_val is not None and next_val is not None and prev_ts and next_ts:
                # Linear interpolation
                total_diff = (next_ts - prev_ts).total_seconds()
                current_diff = (timestamp - prev_ts).total_seconds()
                ratio = current_diff / total_diff
                return prev_val + ratio * (next_val - prev_val)
            elif prev_val is not None:
                return prev_val
            elif next_val is not None:
                return next_val

        return None

    def _align_timestamp(self, timestamp: datetime) -> datetime:
        """Align timestamp to resolution boundary."""
        resolution_seconds = int(self.time_resolution.total_seconds())
        ts_seconds = int(timestamp.timestamp())
        aligned_seconds = (ts_seconds // resolution_seconds) * resolution_seconds
        return datetime.fromtimestamp(aligned_seconds)

    @staticmethod
    def _normalize_labels(labels: Dict[str, str]) -> Dict[str, str]:
        """Normalize label keys and values."""
        normalized: Dict[str, str] = {}
        for key, value in labels.items():
            # Convert key to lowercase with underscores
            norm_key = key.lower().replace("-", "_").replace(".", "_")
            # Strip whitespace from value
            norm_value = str(value).strip()
            if norm_value:  # Only include non-empty values
                normalized[norm_key] = norm_value
        return normalized
