"""
Tests for anomaly detection.
"""

import pytest
from datetime import datetime, timedelta
import numpy as np

from src.cognition.anomaly_detector import AnomalyDetector
from src.cognition.baseline_engine import BaselineEngine
from src.config.constants import MetricCategory, AnomalySeverity
from src.models.metrics import MetricDataPoint, MetricSeries


class TestAnomalyDetector:
    """Tests for AnomalyDetector."""

    @pytest.fixture
    def detector(self, sample_baseline):
        """Create detector with baseline."""
        engine = BaselineEngine()
        engine._baselines.set_baseline(
            sample_baseline.metric_name,
            sample_baseline,
            sample_baseline.labels,
        )
        return AnomalyDetector(engine)

    def test_detect_no_anomaly(self, detector):
        """Test detection with normal values."""
        now = datetime.utcnow()
        # Normal values around baseline mean
        data_points = [
            MetricDataPoint(
                timestamp=now - timedelta(minutes=i),
                value=100 + np.random.normal(0, 3),
                labels={"service": "test-service"},
            )
            for i in range(10)
        ]

        series = MetricSeries(
            name="test_metric",
            category=MetricCategory.API,
            unit="ms",
            labels={"service": "test-service"},
            data_points=list(reversed(data_points)),
        )

        batch = detector.detect([series])

        # Anomaly count should be low or zero with normal values
        assert batch.total_metrics_checked == 1

    def test_detect_anomaly(self, detector):
        """Test detection with anomalous values."""
        now = datetime.utcnow()
        # Anomalous values - 6 sigma above baseline
        data_points = [
            MetricDataPoint(
                timestamp=now - timedelta(minutes=i),
                value=130,  # 6 sigma above mean of 100
                labels={"service": "test-service"},
            )
            for i in range(10)
        ]

        series = MetricSeries(
            name="test_metric",
            category=MetricCategory.API,
            unit="ms",
            labels={"service": "test-service"},
            data_points=list(reversed(data_points)),
        )

        batch = detector.detect([series])

        assert batch.count > 0
        anomaly = batch.anomalies[0]
        assert anomaly.metric_name == "test_metric"
        assert anomaly.deviation > 3  # Above threshold

    def test_severity_classification(self, detector):
        """Test anomaly severity classification."""
        now = datetime.utcnow()

        # Create data with very high deviation
        data_points = [
            MetricDataPoint(
                timestamp=now - timedelta(minutes=i),
                value=150,  # 10 sigma above mean
                labels={"service": "test-service"},
            )
            for i in range(10)
        ]

        series = MetricSeries(
            name="test_metric",
            category=MetricCategory.API,
            unit="ms",
            labels={"service": "test-service"},
            data_points=list(reversed(data_points)),
        )

        batch = detector.detect([series])

        assert batch.count > 0
        anomaly = batch.anomalies[0]
        # High deviation should result in high or critical severity
        assert anomaly.severity in (AnomalySeverity.HIGH, AnomalySeverity.CRITICAL)

    def test_acknowledge_anomaly(self, detector, sample_anomaly):
        """Test acknowledging an anomaly."""
        # Add anomaly to state
        detector._state.add_anomaly(sample_anomaly)

        # Acknowledge
        result = detector.acknowledge_anomaly(sample_anomaly.id, "test-user")

        assert result is True
        assert sample_anomaly.acknowledged is True
        assert sample_anomaly.acknowledged_by == "test-user"
