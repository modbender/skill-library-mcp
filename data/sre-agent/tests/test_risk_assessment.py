"""
Tests for risk assessment.
"""

import pytest
from datetime import datetime

from src.decision.risk_assessment import RiskAssessor, RiskAssessment
from src.config.constants import ActionType, MetricCategory, AnomalySeverity, RiskLevel
from src.models.anomaly import Anomaly, AnomalyType


class TestRiskAssessor:
    """Tests for RiskAssessor."""

    @pytest.fixture
    def assessor(self):
        """Create a risk assessor."""
        return RiskAssessor()

    @pytest.fixture
    def low_severity_anomaly(self):
        """Create a low severity anomaly."""
        return Anomaly(
            detected_at=datetime.utcnow(),
            metric_name="test_metric",
            category=MetricCategory.INFRASTRUCTURE,
            current_value=110,
            baseline_value=100,
            deviation=2.0,
            deviation_percent=10,
            anomaly_type=AnomalyType.POINT,
            severity=AnomalySeverity.LOW,
            duration_minutes=1,
        )

    @pytest.fixture
    def high_severity_anomaly(self):
        """Create a high severity anomaly."""
        return Anomaly(
            detected_at=datetime.utcnow(),
            metric_name="order_latency_p99",
            category=MetricCategory.TRADING,
            current_value=500,
            baseline_value=100,
            deviation=8.0,
            deviation_percent=400,
            anomaly_type=AnomalyType.TREND,
            severity=AnomalySeverity.CRITICAL,
            duration_minutes=30,
        )

    def test_assess_low_risk(self, assessor, low_severity_anomaly):
        """Test low risk assessment."""
        assessment = assessor.assess(
            anomaly=low_severity_anomaly,
            action_type=ActionType.POD_RESTART,
            target_namespace="development",
        )

        assert isinstance(assessment, RiskAssessment)
        assert assessment.risk_score < 0.4
        assert assessment.risk_level == RiskLevel.AUTO

    def test_assess_high_risk(self, assessor, high_severity_anomaly):
        """Test high risk assessment."""
        assessment = assessor.assess(
            anomaly=high_severity_anomaly,
            action_type=ActionType.DATABASE_FAILOVER,
            target_namespace="production",
        )

        assert assessment.risk_score >= 0.6
        assert assessment.risk_level in (RiskLevel.MANUAL, RiskLevel.CRITICAL)

    def test_risk_factors(self, assessor, low_severity_anomaly):
        """Test risk factor calculation."""
        assessment = assessor.assess(
            anomaly=low_severity_anomaly,
            action_type=ActionType.POD_RESTART,
        )

        factors = assessment.factors
        assert 0 <= factors.severity <= 1
        assert 0 <= factors.urgency <= 1
        assert 0 <= factors.impact <= 1
        assert 0 <= factors.complexity <= 1

    def test_custom_factors(self, assessor, low_severity_anomaly):
        """Test custom risk factors override."""
        assessment = assessor.assess(
            anomaly=low_severity_anomaly,
            action_type=ActionType.POD_RESTART,
            custom_factors={"severity": 0.9, "complexity": 0.9},
        )

        # Custom high factors should increase risk
        assert assessment.risk_score > 0.5

    def test_required_approvals(self, assessor):
        """Test approval requirements for risk levels."""
        assert assessor.get_required_approvals(RiskLevel.AUTO) == 0
        assert assessor.get_required_approvals(RiskLevel.SEMI_AUTO) >= 1
        assert assessor.get_required_approvals(RiskLevel.MANUAL) >= 2
        assert assessor.get_required_approvals(RiskLevel.CRITICAL) > 10  # Cannot approve
