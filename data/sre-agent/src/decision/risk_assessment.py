"""
Risk assessment for remediation actions.

Evaluates multi-dimensional risk to determine automation level.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

import structlog

from src.config.constants import ActionType, AnomalySeverity, MetricCategory, RiskLevel
from src.config.settings import get_settings
from src.models.anomaly import Anomaly

logger = structlog.get_logger()


class RiskFactors:
    """Risk factor scores for an action."""

    def __init__(
        self,
        severity: float = 0.0,
        urgency: float = 0.0,
        impact: float = 0.0,
        complexity: float = 0.0,
    ):
        self.severity = severity
        self.urgency = urgency
        self.impact = impact
        self.complexity = complexity

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return {
            "severity": self.severity,
            "urgency": self.urgency,
            "impact": self.impact,
            "complexity": self.complexity,
        }


class RiskAssessment:
    """Result of risk assessment."""

    def __init__(
        self,
        risk_score: float,
        risk_level: RiskLevel,
        factors: RiskFactors,
        reasoning: List[str],
    ):
        self.risk_score = risk_score
        self.risk_level = risk_level
        self.factors = factors
        self.reasoning = reasoning
        self.assessed_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "risk_score": self.risk_score,
            "risk_level": self.risk_level.value,
            "factors": self.factors.to_dict(),
            "reasoning": self.reasoning,
            "assessed_at": self.assessed_at.isoformat(),
        }


class RiskAssessor:
    """
    Multi-dimensional risk assessment for remediation actions.

    Evaluates:
    - Severity: How critical is the anomaly?
    - Urgency: How quickly must we act?
    - Impact: How much blast radius does the action have?
    - Complexity: How likely is the action to fail?
    """

    def __init__(self):
        settings = get_settings()
        self.weights = settings.risk_assessment.weights
        self.thresholds = settings.risk_assessment.thresholds

        # Action complexity scores (0-1)
        self._action_complexity: Dict[ActionType, float] = {
            ActionType.POD_RESTART: 0.2,
            ActionType.HPA_SCALE: 0.3,
            ActionType.CACHE_FLUSH: 0.3,
            ActionType.CIRCUIT_BREAKER: 0.4,
            ActionType.DEPLOYMENT_ROLLBACK: 0.6,
            ActionType.CONFIG_ROLLBACK: 0.5,
            ActionType.TRAFFIC_SHIFT: 0.6,
            ActionType.DATABASE_FAILOVER: 0.9,
            ActionType.CUSTOM_WEBHOOK: 0.5,
        }

        # Category impact multipliers
        self._category_impact: Dict[MetricCategory, float] = {
            MetricCategory.TRADING: 0.9,
            MetricCategory.MATCHING: 0.9,
            MetricCategory.RISK: 1.0,
            MetricCategory.WALLET: 1.0,
            MetricCategory.API: 0.7,
            MetricCategory.INFRASTRUCTURE: 0.6,
            MetricCategory.DATABASE: 0.8,
            MetricCategory.QUEUE: 0.7,
            MetricCategory.BUSINESS: 0.5,
        }

    def assess(
        self,
        anomaly: Anomaly,
        action_type: ActionType,
        target_namespace: str = "default",
        custom_factors: Optional[Dict[str, float]] = None,
    ) -> RiskAssessment:
        """
        Assess risk for a remediation action.

        Args:
            anomaly: The anomaly triggering remediation
            action_type: Type of remediation action
            target_namespace: Kubernetes namespace of target
            custom_factors: Optional custom risk factors

        Returns:
            RiskAssessment with score and level
        """
        reasoning: List[str] = []

        # Calculate severity factor (based on anomaly)
        severity = self._calculate_severity(anomaly)
        reasoning.append(
            f"Severity: {severity:.2f} (anomaly: {anomaly.severity.value}, "
            f"deviation: {abs(anomaly.deviation):.1f}σ)"
        )

        # Calculate urgency factor (based on duration and trend)
        urgency = self._calculate_urgency(anomaly)
        reasoning.append(
            f"Urgency: {urgency:.2f} (duration: {anomaly.duration_minutes}min)"
        )

        # Calculate impact factor (based on action scope)
        impact = self._calculate_impact(anomaly, action_type, target_namespace)
        reasoning.append(
            f"Impact: {impact:.2f} (action: {action_type.value}, "
            f"category: {anomaly.category.value})"
        )

        # Calculate complexity factor (based on action type)
        complexity = self._calculate_complexity(action_type)
        reasoning.append(f"Complexity: {complexity:.2f} (action: {action_type.value})")

        # Apply custom factors if provided
        if custom_factors:
            if "severity" in custom_factors:
                severity = custom_factors["severity"]
            if "urgency" in custom_factors:
                urgency = custom_factors["urgency"]
            if "impact" in custom_factors:
                impact = custom_factors["impact"]
            if "complexity" in custom_factors:
                complexity = custom_factors["complexity"]

        factors = RiskFactors(severity, urgency, impact, complexity)

        # Calculate weighted score
        risk_score = (
            self.weights.severity * severity
            + self.weights.urgency * urgency
            + self.weights.impact * impact
            + self.weights.complexity * complexity
        )

        # Determine risk level
        risk_level = self._determine_level(risk_score)
        reasoning.append(
            f"Final score: {risk_score:.2f} -> {risk_level.value}"
        )

        logger.info(
            "Risk assessment complete",
            anomaly_id=anomaly.id,
            action=action_type.value,
            score=risk_score,
            level=risk_level.value,
        )

        return RiskAssessment(risk_score, risk_level, factors, reasoning)

    def _calculate_severity(self, anomaly: Anomaly) -> float:
        """Calculate severity factor (0-1)."""
        # Base score from anomaly severity
        severity_scores = {
            AnomalySeverity.LOW: 0.2,
            AnomalySeverity.MEDIUM: 0.4,
            AnomalySeverity.HIGH: 0.7,
            AnomalySeverity.CRITICAL: 0.95,
        }
        base_score = severity_scores.get(anomaly.severity, 0.5)

        # Adjust based on deviation magnitude
        deviation_factor = min(abs(anomaly.deviation) / 5.0, 1.0)

        return min(base_score * 0.7 + deviation_factor * 0.3, 1.0)

    def _calculate_urgency(self, anomaly: Anomaly) -> float:
        """Calculate urgency factor (0-1)."""
        # Longer duration = less urgent (already persisted)
        # But very long duration = more urgent (not self-healing)
        duration = anomaly.duration_minutes

        if duration < 2:
            # Very new, might self-resolve
            return 0.3
        elif duration < 5:
            return 0.5
        elif duration < 15:
            return 0.7
        elif duration < 30:
            return 0.85
        else:
            # Persisted for long time, definitely needs action
            return 0.95

    def _calculate_impact(
        self,
        anomaly: Anomaly,
        action_type: ActionType,
        namespace: str,
    ) -> float:
        """Calculate impact factor (0-1)."""
        # Base impact from category
        category_impact = self._category_impact.get(anomaly.category, 0.5)

        # Namespace impact
        namespace_factors = {
            "production": 1.0,
            "prod": 1.0,
            "staging": 0.6,
            "development": 0.3,
            "dev": 0.3,
            "default": 0.7,
        }
        namespace_impact = namespace_factors.get(namespace.lower(), 0.7)

        # Action scope impact
        action_scope = {
            ActionType.POD_RESTART: 0.3,  # Single pod
            ActionType.HPA_SCALE: 0.4,  # Scaling
            ActionType.CACHE_FLUSH: 0.5,  # Affects all requests
            ActionType.CIRCUIT_BREAKER: 0.6,  # Affects traffic
            ActionType.DEPLOYMENT_ROLLBACK: 0.8,  # All pods
            ActionType.CONFIG_ROLLBACK: 0.7,  # Config change
            ActionType.TRAFFIC_SHIFT: 0.7,  # Traffic routing
            ActionType.DATABASE_FAILOVER: 0.95,  # Critical
            ActionType.CUSTOM_WEBHOOK: 0.5,  # Unknown
        }
        action_impact = action_scope.get(action_type, 0.5)

        return category_impact * 0.4 + namespace_impact * 0.3 + action_impact * 0.3

    def _calculate_complexity(self, action_type: ActionType) -> float:
        """Calculate complexity factor (0-1)."""
        return self._action_complexity.get(action_type, 0.5)

    def _determine_level(self, score: float) -> RiskLevel:
        """Determine risk level from score."""
        if score >= self.thresholds.manual:
            return RiskLevel.CRITICAL
        elif score >= self.thresholds.semi_auto:
            return RiskLevel.MANUAL
        elif score >= self.thresholds.auto:
            return RiskLevel.SEMI_AUTO
        else:
            return RiskLevel.AUTO

    def get_required_approvals(self, risk_level: RiskLevel) -> int:
        """Get number of approvals required for risk level."""
        settings = get_settings()
        approvals = {
            RiskLevel.AUTO: 0,
            RiskLevel.SEMI_AUTO: settings.approval.required_approvers_semi_auto,
            RiskLevel.MANUAL: settings.approval.required_approvers_manual,
            RiskLevel.CRITICAL: 999,  # Cannot auto-approve
        }
        return approvals.get(risk_level, 1)
