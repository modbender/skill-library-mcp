"""
Pytest configuration and fixtures.
"""

import pytest
from datetime import datetime, timedelta
import numpy as np

from src.config.constants import MetricCategory, AnomalySeverity, AnomalyType
from src.models.metrics import MetricDataPoint, MetricSeries
from src.models.anomaly import Anomaly
from src.models.baseline import Baseline, BaselineStatistics


@pytest.fixture
def sample_metric_series() -> MetricSeries:
    """Create a sample metric series for testing."""
    now = datetime.utcnow()
    data_points = [
        MetricDataPoint(
            timestamp=now - timedelta(minutes=i),
            value=100 + np.random.normal(0, 5),
            labels={"service": "test-service"},
        )
        for i in range(100)
    ]
    # Reverse to be chronological
    data_points = list(reversed(data_points))

    return MetricSeries(
        name="test_metric",
        category=MetricCategory.API,
        unit="ms",
        description="Test metric",
        labels={"service": "test-service"},
        data_points=data_points,
    )


@pytest.fixture
def sample_baseline() -> Baseline:
    """Create a sample baseline for testing."""
    now = datetime.utcnow()
    return Baseline(
        metric_name="test_metric",
        labels={"service": "test-service"},
        created_at=now - timedelta(days=7),
        updated_at=now,
        data_start=now - timedelta(days=7),
        data_end=now,
        sample_count=10000,
        global_stats=BaselineStatistics(
            mean=100.0,
            std=5.0,
            median=100.0,
            mad=3.5,
            min=85.0,
            max=115.0,
            percentile_5=92.0,
            percentile_25=97.0,
            percentile_75=103.0,
            percentile_95=108.0,
            sample_count=10000,
        ),
        hourly_baselines=[],
        quality_score=0.85,
        coverage_days=7,
    )


@pytest.fixture
def sample_anomaly() -> Anomaly:
    """Create a sample anomaly for testing."""
    return Anomaly(
        detected_at=datetime.utcnow(),
        metric_name="test_metric",
        category=MetricCategory.API,
        labels={"service": "test-service"},
        current_value=130.0,
        baseline_value=100.0,
        deviation=6.0,
        deviation_percent=30.0,
        anomaly_type=AnomalyType.POINT,
        severity=AnomalySeverity.HIGH,
    )


@pytest.fixture
def anomaly_values() -> list[float]:
    """Generate values with an anomaly at the end."""
    normal = [100 + np.random.normal(0, 5) for _ in range(95)]
    anomalous = [150 + np.random.normal(0, 5) for _ in range(5)]
    return normal + anomalous
