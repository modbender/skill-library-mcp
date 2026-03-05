"""
RCA (Root Cause Analysis) rule definitions and matching.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
import structlog

from src.config.constants import AnomalySeverity

logger = structlog.get_logger()


@dataclass
class CorrelatedMetric:
    """Definition of a correlated metric in a rule."""

    metric: str
    threshold: float
    correlation: str = "positive"  # positive or negative


@dataclass
class RemediationAction:
    """Definition of a remediation action."""

    action: str
    target: str
    priority: int = 1


@dataclass
class RCARule:
    """Definition of an RCA rule."""

    id: str
    name: str
    condition: Dict[str, Any]
    root_cause: str
    remediation: List[RemediationAction]
    severity: AnomalySeverity

    # Parsed conditions
    primary_metric: str = ""
    primary_threshold: float = 0.0
    correlated_metrics: List[CorrelatedMetric] = field(default_factory=list)
    log_patterns: List[str] = field(default_factory=list)
    event_types: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Parse conditions after initialization."""
        self.primary_metric = self.condition.get("primary_metric", "")
        self.primary_threshold = self.condition.get("primary_threshold", 0.0)

        # Parse correlated metrics
        correlated = self.condition.get("correlated_metrics", [])
        self.correlated_metrics = [
            CorrelatedMetric(
                metric=cm.get("metric", ""),
                threshold=cm.get("threshold", 0.0),
                correlation=cm.get("correlation", "positive"),
            )
            for cm in correlated
        ]

        # Parse log patterns
        self.log_patterns = self.condition.get("log_patterns", [])

        # Parse event types
        event_type = self.condition.get("event_type")
        if event_type:
            self.event_types = [event_type]
        else:
            self.event_types = []


@dataclass
class CorrelationPattern:
    """Definition of a metric correlation pattern."""

    name: str
    metrics: List[str]
    expected_correlation: str
    lag_minutes: int = 0


class RCARuleEngine:
    """
    Engine for loading and matching RCA rules.

    Features:
    - YAML rule loading
    - Rule matching against anomalies
    - Correlation pattern matching
    """

    def __init__(self, rules_file: Optional[str] = None):
        self._rules: List[RCARule] = []
        self._correlations: List[CorrelationPattern] = []

        rules_path = rules_file or str(
            Path(__file__).parent.parent.parent / "config" / "rca_rules.yaml"
        )
        self._load_rules(rules_path)

    def _load_rules(self, rules_file: str) -> None:
        """Load rules from YAML file."""
        try:
            rules_path = Path(rules_file)
            if not rules_path.exists():
                logger.warning("RCA rules file not found", path=rules_file)
                return

            with open(rules_path) as f:
                config = yaml.safe_load(f) or {}

            # Parse rules
            for rule_def in config.get("rules", []):
                try:
                    severity = AnomalySeverity(rule_def.get("severity", "medium"))
                    remediation = [
                        RemediationAction(
                            action=r.get("action", ""),
                            target=r.get("target", ""),
                            priority=r.get("priority", 1),
                        )
                        for r in rule_def.get("remediation", [])
                    ]

                    rule = RCARule(
                        id=rule_def.get("id", ""),
                        name=rule_def.get("name", ""),
                        condition=rule_def.get("condition", {}),
                        root_cause=rule_def.get("root_cause", ""),
                        remediation=remediation,
                        severity=severity,
                    )
                    self._rules.append(rule)
                except Exception as e:
                    logger.warning(
                        "Failed to parse RCA rule",
                        rule_id=rule_def.get("id"),
                        error=str(e),
                    )

            # Parse correlation patterns
            for corr_def in config.get("correlations", []):
                try:
                    pattern = CorrelationPattern(
                        name=corr_def.get("name", ""),
                        metrics=corr_def.get("metrics", []),
                        expected_correlation=corr_def.get("expected_correlation", "positive"),
                        lag_minutes=corr_def.get("lag_minutes", 0),
                    )
                    self._correlations.append(pattern)
                except Exception as e:
                    logger.warning(
                        "Failed to parse correlation pattern",
                        name=corr_def.get("name"),
                        error=str(e),
                    )

            logger.info(
                "Loaded RCA rules",
                rule_count=len(self._rules),
                correlation_count=len(self._correlations),
            )

        except Exception as e:
            logger.error("Failed to load RCA rules", error=str(e))

    @property
    def rules(self) -> List[RCARule]:
        """Get all loaded rules."""
        return self._rules

    @property
    def correlations(self) -> List[CorrelationPattern]:
        """Get all correlation patterns."""
        return self._correlations

    def find_matching_rules(
        self,
        metric_name: str,
        metric_value: float,
        correlated_values: Optional[Dict[str, float]] = None,
        log_patterns_found: Optional[List[str]] = None,
        recent_events: Optional[List[str]] = None,
    ) -> List[RCARule]:
        """
        Find rules matching the given conditions.

        Args:
            metric_name: Primary metric name
            metric_value: Primary metric value
            correlated_values: Values of potentially correlated metrics
            log_patterns_found: Log patterns found in recent logs
            recent_events: Recent event types

        Returns:
            List of matching rules, sorted by priority
        """
        correlated_values = correlated_values or {}
        log_patterns_found = log_patterns_found or []
        recent_events = recent_events or []

        matching_rules: List[Tuple[RCARule, float]] = []

        for rule in self._rules:
            match_score = self._calculate_match_score(
                rule,
                metric_name,
                metric_value,
                correlated_values,
                log_patterns_found,
                recent_events,
            )

            if match_score > 0:
                matching_rules.append((rule, match_score))

        # Sort by match score descending
        matching_rules.sort(key=lambda x: x[1], reverse=True)

        return [rule for rule, _ in matching_rules]

    def _calculate_match_score(
        self,
        rule: RCARule,
        metric_name: str,
        metric_value: float,
        correlated_values: Dict[str, float],
        log_patterns_found: List[str],
        recent_events: List[str],
    ) -> float:
        """Calculate how well conditions match a rule."""
        score = 0.0

        # Primary metric match
        if rule.primary_metric:
            if metric_name == rule.primary_metric and metric_value >= rule.primary_threshold:
                score += 0.4
            elif metric_name == rule.primary_metric:
                # Partial match if metric name matches but below threshold
                ratio = metric_value / rule.primary_threshold if rule.primary_threshold > 0 else 0
                if ratio > 0.5:
                    score += 0.2 * ratio

        # Correlated metrics match
        if rule.correlated_metrics:
            correlation_matches = 0
            for corr in rule.correlated_metrics:
                if corr.metric in correlated_values:
                    val = correlated_values[corr.metric]
                    if val >= corr.threshold:
                        correlation_matches += 1

            if correlation_matches > 0:
                score += 0.3 * (correlation_matches / len(rule.correlated_metrics))

        # Log pattern match
        if rule.log_patterns:
            pattern_matches = sum(
                1 for p in rule.log_patterns if p.lower() in [lp.lower() for lp in log_patterns_found]
            )
            if pattern_matches > 0:
                score += 0.15 * (pattern_matches / len(rule.log_patterns))

        # Event match
        if rule.event_types:
            event_matches = sum(
                1 for e in rule.event_types if e in recent_events
            )
            if event_matches > 0:
                score += 0.15 * (event_matches / len(rule.event_types))

        return score

    def get_rule_by_id(self, rule_id: str) -> Optional[RCARule]:
        """Get a specific rule by ID."""
        for rule in self._rules:
            if rule.id == rule_id:
                return rule
        return None

    def get_rules_for_metric(self, metric_name: str) -> List[RCARule]:
        """Get all rules that apply to a specific metric."""
        return [r for r in self._rules if r.primary_metric == metric_name]
