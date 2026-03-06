"""
Anomaly detection using multiple algorithms.

Implements ensemble-based anomaly detection combining:
- Z-Score (statistical)
- MAD (Median Absolute Deviation)
- Isolation Forest (ML-based, optional)
"""

from datetime import datetime
from typing import Optional, Dict, List, Any, Tuple, Set

import numpy as np
import structlog
from sklearn.ensemble import IsolationForest

from src.cognition.baseline_engine import BaselineEngine
from src.config.constants import AnomalySeverity, AnomalyType, MetricCategory
from src.config.settings import get_settings
from src.models.anomaly import Anomaly, AnomalyBatch, AnomalyScore, AnomalyState
from src.models.baseline import Baseline
from src.models.metrics import MetricSeries

logger = structlog.get_logger()


class AnomalyDetector:
    """
    Multi-algorithm anomaly detection engine.

    Features:
    - Z-Score detection using baseline statistics
    - MAD (Median Absolute Deviation) for robust detection
    - Isolation Forest for multi-dimensional anomalies
    - Ensemble voting for final determination
    - Severity classification
    """

    def __init__(
        self,
        baseline_engine: BaselineEngine,
        zscore_threshold: Optional[float] = None,
        mad_threshold: Optional[float] = None,
        ensemble_min_votes: Optional[int] = None,
        algorithms: Optional[List[str]] = None,
    ):
        settings = get_settings()
        self.baseline_engine = baseline_engine
        self.zscore_threshold = zscore_threshold or settings.anomaly_detection.zscore_threshold
        self.mad_threshold = mad_threshold or settings.anomaly_detection.mad_threshold
        self.ensemble_min_votes = ensemble_min_votes or settings.anomaly_detection.ensemble_min_votes
        self.algorithms = algorithms or settings.anomaly_detection.algorithms

        # Anomaly state tracking
        self._state = AnomalyState()

        # Isolation Forest model (lazy initialization)
        self._isolation_forest: Optional[IsolationForest] = None

    @property
    def state(self) -> AnomalyState:
        """Get current anomaly state."""
        return self._state

    def detect(
        self,
        metrics: List[MetricSeries],
        detection_time: Optional[datetime] = None,
    ) -> AnomalyBatch:
        """
        Detect anomalies in a batch of metrics.

        Args:
            metrics: List of metric series to analyze
            detection_time: Time of detection (defaults to now)

        Returns:
            AnomalyBatch containing detected anomalies
        """
        detection_time = detection_time or datetime.utcnow()
        start_ms = int(datetime.utcnow().timestamp() * 1000)
        anomalies: List[Anomaly] = []
        metrics_checked = 0

        for series in metrics:
            if not series.data_points:
                continue

            metrics_checked += 1
            anomaly = self._detect_metric_anomaly(series, detection_time)
            if anomaly:
                anomalies.append(anomaly)
                self._state.add_anomaly(anomaly)

        # Check for resolved anomalies
        self._check_resolved_anomalies(metrics)

        end_ms = int(datetime.utcnow().timestamp() * 1000)

        batch = AnomalyBatch(
            detection_time=detection_time,
            anomalies=anomalies,
            total_metrics_checked=metrics_checked,
            detection_duration_ms=end_ms - start_ms,
        )

        if anomalies:
            logger.info(
                "Detected anomalies",
                count=len(anomalies),
                critical=batch.critical_count,
                duration_ms=batch.detection_duration_ms,
            )

        return batch

    def _detect_metric_anomaly(
        self,
        series: MetricSeries,
        detection_time: datetime,
    ) -> Optional[Anomaly]:
        """Detect anomaly in a single metric series."""
        baseline = self.baseline_engine.get_baseline(series.name, series.labels)
        current_value = series.latest_value

        if current_value is None:
            return None

        scores: List[AnomalyScore] = []
        anomaly_votes = 0

        # Z-Score detection
        if "zscore" in self.algorithms and baseline:
            zscore_result = self._zscore_detect(current_value, baseline, detection_time)
            scores.append(zscore_result)
            if zscore_result.is_anomaly:
                anomaly_votes += 1

        # MAD detection
        if "mad" in self.algorithms and baseline:
            mad_result = self._mad_detect(current_value, baseline, detection_time)
            scores.append(mad_result)
            if mad_result.is_anomaly:
                anomaly_votes += 1

        # Isolation Forest detection
        if "isolation_forest" in self.algorithms and len(series.values) >= 100:
            if_result = self._isolation_forest_detect(series)
            scores.append(if_result)
            if if_result.is_anomaly:
                anomaly_votes += 1

        # Ensemble decision
        is_anomaly = anomaly_votes >= self.ensemble_min_votes

        if not is_anomaly:
            return None

        # Calculate deviation
        if baseline:
            expected, expected_std = baseline.get_expected_value(detection_time)
            deviation = (current_value - expected) / expected_std if expected_std > 0 else 0
            deviation_percent = ((current_value - expected) / expected * 100) if expected != 0 else 0
        else:
            expected = float(np.mean(series.values))
            expected_std = float(np.std(series.values))
            deviation = (current_value - expected) / expected_std if expected_std > 0 else 0
            deviation_percent = 0

        # Calculate ensemble score
        ensemble_score = np.mean([s.score for s in scores if s.score > 0])

        # Determine severity
        severity = self._determine_severity(abs(deviation), series.category)

        # Determine anomaly type
        anomaly_type = self._determine_type(deviation, series)

        # Check if this is an ongoing anomaly
        existing = self._state.active_anomalies.get(
            self._make_metric_key(series.name, series.labels)
        )
        started_at = existing.started_at if existing else detection_time
        duration = int((detection_time - started_at).total_seconds() / 60)

        return Anomaly(
            detected_at=detection_time,
            metric_name=series.name,
            category=series.category,
            labels=series.labels,
            current_value=current_value,
            baseline_value=expected,
            deviation=deviation,
            deviation_percent=deviation_percent,
            anomaly_type=anomaly_type,
            severity=severity,
            scores=scores,
            ensemble_score=float(ensemble_score),
            started_at=started_at,
            duration_minutes=duration,
        )

    def _zscore_detect(
        self,
        value: float,
        baseline: Baseline,
        timestamp: datetime,
    ) -> AnomalyScore:
        """Z-Score based anomaly detection."""
        expected, expected_std = baseline.get_expected_value(timestamp)

        if expected_std == 0:
            return AnomalyScore(
                algorithm="zscore",
                score=0.0,
                threshold=self.zscore_threshold,
                is_anomaly=False,
                details={"zscore": 0.0, "expected": expected, "std": 0.0},
            )

        zscore = abs(value - expected) / expected_std
        is_anomaly = zscore > self.zscore_threshold

        # Normalize score to 0-1 range
        score = min(zscore / (self.zscore_threshold * 2), 1.0)

        return AnomalyScore(
            algorithm="zscore",
            score=score,
            threshold=self.zscore_threshold,
            is_anomaly=is_anomaly,
            details={
                "zscore": zscore,
                "expected": expected,
                "std": expected_std,
            },
        )

    def _mad_detect(
        self,
        value: float,
        baseline: Baseline,
        timestamp: datetime,
    ) -> AnomalyScore:
        """MAD (Median Absolute Deviation) based detection."""
        # Use global stats for MAD calculation
        median = baseline.global_stats.median
        mad = baseline.global_stats.mad

        if mad == 0:
            return AnomalyScore(
                algorithm="mad",
                score=0.0,
                threshold=self.mad_threshold,
                is_anomaly=False,
                details={"modified_zscore": 0.0, "median": median, "mad": 0.0},
            )

        # Modified Z-score using MAD
        modified_zscore = 0.6745 * abs(value - median) / mad
        is_anomaly = modified_zscore > self.mad_threshold

        # Normalize score to 0-1 range
        score = min(modified_zscore / (self.mad_threshold * 2), 1.0)

        return AnomalyScore(
            algorithm="mad",
            score=score,
            threshold=self.mad_threshold,
            is_anomaly=is_anomaly,
            details={
                "modified_zscore": modified_zscore,
                "median": median,
                "mad": mad,
            },
        )

    def _isolation_forest_detect(
        self,
        series: MetricSeries,
    ) -> AnomalyScore:
        """Isolation Forest based detection."""
        values = np.array(series.values).reshape(-1, 1)

        # Train or use existing model
        if self._isolation_forest is None:
            self._isolation_forest = IsolationForest(
                contamination=0.1,
                random_state=42,
                n_estimators=100,
            )
            self._isolation_forest.fit(values)

        # Get anomaly score for latest value
        latest = np.array([[series.latest_value]])
        score = -self._isolation_forest.score_samples(latest)[0]

        # Normalize to 0-1 (scores are typically in [-0.5, 0.5] range)
        normalized_score = min(max((score + 0.5), 0), 1)

        # Prediction: -1 for anomaly, 1 for normal
        prediction = self._isolation_forest.predict(latest)[0]
        is_anomaly = prediction == -1

        return AnomalyScore(
            algorithm="isolation_forest",
            score=normalized_score,
            threshold=0.5,
            is_anomaly=is_anomaly,
            details={"raw_score": score},
        )

    def _determine_severity(
        self,
        deviation: float,
        category: MetricCategory,
    ) -> AnomalySeverity:
        """Determine anomaly severity based on deviation and category."""
        # Category-based severity multipliers
        category_weights = {
            MetricCategory.TRADING: 1.5,
            MetricCategory.MATCHING: 1.5,
            MetricCategory.RISK: 2.0,
            MetricCategory.WALLET: 2.0,
            MetricCategory.API: 1.2,
            MetricCategory.INFRASTRUCTURE: 1.0,
            MetricCategory.DATABASE: 1.3,
            MetricCategory.QUEUE: 1.2,
            MetricCategory.BUSINESS: 1.0,
        }

        weight = category_weights.get(category, 1.0)
        weighted_deviation = deviation * weight

        if weighted_deviation >= 5.0:
            return AnomalySeverity.CRITICAL
        elif weighted_deviation >= 4.0:
            return AnomalySeverity.HIGH
        elif weighted_deviation >= 3.0:
            return AnomalySeverity.MEDIUM
        else:
            return AnomalySeverity.LOW

    def _determine_type(
        self,
        deviation: float,
        series: MetricSeries,
    ) -> AnomalyType:
        """Determine the type of anomaly."""
        if len(series.values) < 10:
            return AnomalyType.POINT

        values = np.array(series.values)

        # Check for trend anomaly (consistent direction)
        if len(values) >= 5:
            recent = values[-5:]
            diffs = np.diff(recent)
            if np.all(diffs > 0) or np.all(diffs < 0):
                return AnomalyType.TREND

        # Default to point anomaly
        return AnomalyType.POINT

    def _check_resolved_anomalies(self, metrics: List[MetricSeries]) -> None:
        """Check if any active anomalies have resolved."""
        current_metric_keys = {
            self._make_metric_key(s.name, s.labels) for s in metrics
        }

        for metric_key in list(self._state.active_anomalies.keys()):
            anomaly = self._state.active_anomalies[metric_key]

            # Find matching series
            matching_series = None
            for series in metrics:
                if self._make_metric_key(series.name, series.labels) == metric_key:
                    matching_series = series
                    break

            if not matching_series:
                continue

            # Check if still anomalous
            baseline = self.baseline_engine.get_baseline(
                matching_series.name, matching_series.labels
            )
            if not baseline or not matching_series.latest_value:
                continue

            expected, expected_std = baseline.get_expected_value(datetime.utcnow())
            if expected_std > 0:
                current_zscore = abs(
                    matching_series.latest_value - expected
                ) / expected_std
                if current_zscore < self.zscore_threshold * 0.7:  # Hysteresis
                    resolved = self._state.resolve_anomaly(metric_key)
                    if resolved:
                        logger.info(
                            "Anomaly resolved",
                            metric=resolved.metric_name,
                            duration_minutes=resolved.duration_minutes,
                        )

    @staticmethod
    def _make_metric_key(name: str, labels: Dict[str, str]) -> str:
        """Create unique key for metric + labels."""
        if not labels:
            return name
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"

    def get_active_anomalies(
        self,
        category: Optional[MetricCategory] = None,
        severity: Optional[AnomalySeverity] = None,
    ) -> List[Anomaly]:
        """Get active anomalies with optional filtering."""
        anomalies = list(self._state.active_anomalies.values())

        if category:
            anomalies = [a for a in anomalies if a.category == category]

        if severity:
            anomalies = [a for a in anomalies if a.severity == severity]

        return sorted(anomalies, key=lambda a: a.detected_at, reverse=True)

    def acknowledge_anomaly(
        self,
        anomaly_id: str,
        acknowledged_by: str,
    ) -> bool:
        """Acknowledge an anomaly."""
        for anomaly in self._state.active_anomalies.values():
            if anomaly.id == anomaly_id:
                anomaly.acknowledged = True
                anomaly.acknowledged_by = acknowledged_by
                return True
        return False
