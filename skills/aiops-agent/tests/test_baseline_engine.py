"""
Tests for baseline learning engine.
"""

import pytest
from datetime import datetime, timedelta
import numpy as np

from src.cognition.baseline_engine import BaselineEngine
from src.config.constants import MetricCategory
from src.models.metrics import MetricDataPoint, MetricSeries


class TestBaselineEngine:
    """Tests for BaselineEngine."""

    def test_learn_baseline_success(self):
        """Test successful baseline learning."""
        engine = BaselineEngine(min_history_days=1)

        # Create 8 days of data
        now = datetime.utcnow()
        data_points = [
            MetricDataPoint(
                timestamp=now - timedelta(days=8) + timedelta(minutes=i),
                value=100 + np.random.normal(0, 5),
                labels={},
            )
            for i in range(8 * 24 * 60)  # 8 days, 1 point per minute
        ]

        series = MetricSeries(
            name="test_metric",
            category=MetricCategory.API,
            unit="ms",
            data_points=data_points,
        )

        baseline = engine.learn_baseline(series)

        assert baseline is not None
        assert baseline.metric_name == "test_metric"
        assert baseline.global_stats.mean > 0
        assert baseline.quality_score > 0

    def test_learn_baseline_insufficient_data(self):
        """Test baseline learning with insufficient data."""
        engine = BaselineEngine(min_history_days=7)

        # Create only 1 day of data
        now = datetime.utcnow()
        data_points = [
            MetricDataPoint(
                timestamp=now - timedelta(hours=i),
                value=100,
                labels={},
            )
            for i in range(24)
        ]

        series = MetricSeries(
            name="test_metric",
            category=MetricCategory.API,
            unit="ms",
            data_points=data_points,
        )

        baseline = engine.learn_baseline(series)

        assert baseline is None

    def test_get_expected_value(self, sample_baseline):
        """Test getting expected value from baseline."""
        engine = BaselineEngine()
        engine._baselines.set_baseline(
            sample_baseline.metric_name,
            sample_baseline,
            sample_baseline.labels,
        )

        result = engine.get_expected_value(
            "test_metric",
            datetime.utcnow(),
            {"service": "test-service"},
        )

        assert result is not None
        mean, std = result
        assert mean == 100.0
        assert std == 5.0

    def test_baseline_export_import(self, sample_baseline):
        """Test baseline export and import."""
        engine = BaselineEngine()
        engine._baselines.set_baseline(
            sample_baseline.metric_name,
            sample_baseline,
            sample_baseline.labels,
        )

        # Export
        exported = engine.export_baselines()
        assert len(exported) == 1

        # Create new engine and import
        new_engine = BaselineEngine()
        count = new_engine.import_baselines(exported)
        assert count == 1
