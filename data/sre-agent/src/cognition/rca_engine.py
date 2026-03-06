"""
Root Cause Analysis Engine.

Combines rule-based analysis with LLM-powered insights
to identify root causes of anomalies.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import numpy as np
import structlog
from anthropic import Anthropic

from src.cognition.rca_rules import RCARuleEngine, RCARule
from src.config.settings import get_settings
from src.models.anomaly import Anomaly, AnomalyContext
from src.models.metrics import LogEntry, Event, MetricSeries

logger = structlog.get_logger()


class RCAResult:
    """Result of root cause analysis."""

    def __init__(
        self,
        anomaly_id: str,
        root_causes: List[str],
        matched_rules: List[RCARule],
        correlated_anomalies: List[str],
        llm_analysis: Optional[str] = None,
        confidence: float = 0.0,
        suggested_actions: Optional[List[Dict[str, Any]]] = None,
    ):
        self.anomaly_id = anomaly_id
        self.root_causes = root_causes
        self.matched_rules = matched_rules
        self.correlated_anomalies = correlated_anomalies
        self.llm_analysis = llm_analysis
        self.confidence = confidence
        self.suggested_actions = suggested_actions or []
        self.created_at = datetime.utcnow()


class RCAEngine:
    """
    Root Cause Analysis Engine.

    Features:
    - Rule-based root cause matching
    - LLM-powered analysis for complex cases
    - Correlation analysis across metrics
    - Historical pattern matching
    """

    def __init__(
        self,
        use_llm: Optional[bool] = None,
        lookback_minutes: Optional[int] = None,
        correlation_threshold: Optional[float] = None,
    ):
        settings = get_settings()
        self.use_llm = use_llm if use_llm is not None else settings.rca.use_llm
        self.lookback_minutes = lookback_minutes or settings.rca.lookback_minutes
        self.correlation_threshold = correlation_threshold or settings.rca.correlation_threshold

        self._rule_engine = RCARuleEngine()
        self._llm_client: Optional[Anthropic] = None

        if self.use_llm and settings.llm.api_key:
            self._llm_client = Anthropic(api_key=settings.llm.api_key)

    def analyze(
        self,
        anomaly: Anomaly,
        related_metrics: Optional[List[MetricSeries]] = None,
        recent_logs: Optional[List[LogEntry]] = None,
        recent_events: Optional[List[Event]] = None,
    ) -> RCAResult:
        """
        Perform root cause analysis for an anomaly.

        Args:
            anomaly: The anomaly to analyze
            related_metrics: Related metric series
            recent_logs: Recent log entries
            recent_events: Recent events

        Returns:
            RCAResult with analysis findings
        """
        related_metrics = related_metrics or []
        recent_logs = recent_logs or []
        recent_events = recent_events or []

        root_causes: List[str] = []
        confidence = 0.0

        # Extract correlated metric values
        correlated_values = self._extract_correlated_values(related_metrics)

        # Extract log patterns
        log_patterns = self._extract_log_patterns(recent_logs)

        # Extract event types
        event_types = [e.reason for e in recent_events if e.reason]

        # Find matching rules
        matched_rules = self._rule_engine.find_matching_rules(
            metric_name=anomaly.metric_name,
            metric_value=anomaly.current_value,
            correlated_values=correlated_values,
            log_patterns_found=log_patterns,
            recent_events=event_types,
        )

        # Extract root causes from matched rules
        for rule in matched_rules:
            if rule.root_cause not in root_causes:
                root_causes.append(rule.root_cause)

        # Calculate correlation-based causes
        correlation_causes = self._analyze_correlations(
            anomaly, related_metrics
        )
        root_causes.extend([c for c in correlation_causes if c not in root_causes])

        # Calculate confidence based on evidence
        confidence = self._calculate_confidence(
            matched_rules, correlation_causes, log_patterns, event_types
        )

        # Find correlated anomalies
        correlated_anomalies = self._find_correlated_anomalies(
            anomaly, related_metrics
        )

        # Get LLM analysis for complex cases
        llm_analysis = None
        if self.use_llm and self._llm_client and confidence < 0.7:
            llm_analysis = self._get_llm_analysis(
                anomaly, root_causes, recent_logs, recent_events
            )
            if llm_analysis:
                # LLM may have found additional causes
                confidence = min(confidence + 0.2, 1.0)

        # Generate suggested actions
        suggested_actions = self._generate_suggested_actions(matched_rules)

        # Update anomaly context
        anomaly.context = AnomalyContext(
            related_metrics=[m.name for m in related_metrics],
            recent_events=[f"{e.kind}/{e.name}: {e.reason}" for e in recent_events[:5]],
            log_patterns=log_patterns[:10],
            potential_causes=root_causes,
            similar_incidents=[],  # Would come from RAG
        )

        return RCAResult(
            anomaly_id=anomaly.id,
            root_causes=root_causes,
            matched_rules=matched_rules,
            correlated_anomalies=correlated_anomalies,
            llm_analysis=llm_analysis,
            confidence=confidence,
            suggested_actions=suggested_actions,
        )

    def _extract_correlated_values(
        self, metrics: List[MetricSeries]
    ) -> Dict[str, float]:
        """Extract latest values from related metrics."""
        values: Dict[str, float] = {}
        for series in metrics:
            if series.latest_value is not None:
                values[series.name] = series.latest_value
        return values

    def _extract_log_patterns(self, logs: List[LogEntry]) -> List[str]:
        """Extract significant patterns from logs."""
        patterns: List[str] = []

        # Common error patterns
        error_patterns = [
            "timeout", "deadline exceeded", "connection refused",
            "out of memory", "oom", "disk full", "no space left",
            "permission denied", "authentication failed",
            "rate limit", "throttled", "circuit breaker",
            "panic", "fatal", "crash", "killed",
        ]

        for log in logs:
            msg_lower = log.message.lower()
            for pattern in error_patterns:
                if pattern in msg_lower and pattern not in patterns:
                    patterns.append(pattern)

            # Extract error codes
            if log.error_code and log.error_code not in patterns:
                patterns.append(log.error_code)

        return patterns

    def _analyze_correlations(
        self,
        anomaly: Anomaly,
        related_metrics: List[MetricSeries],
    ) -> List[str]:
        """Analyze metric correlations to find potential causes."""
        causes: List[str] = []

        # Get correlation patterns from rule engine
        for pattern in self._rule_engine.correlations:
            if anomaly.metric_name not in pattern.metrics:
                continue

            other_metrics = [m for m in pattern.metrics if m != anomaly.metric_name]
            for other_name in other_metrics:
                other_series = next(
                    (m for m in related_metrics if m.name == other_name), None
                )
                if not other_series or not other_series.data_points:
                    continue

                # Simple correlation check based on recent values
                if other_series.latest_value and abs(anomaly.deviation) > 2:
                    # Check if other metric is also elevated
                    other_recent = other_series.values[-10:]
                    other_mean = np.mean(other_recent)
                    other_std = np.std(other_recent)

                    if other_std > 0:
                        other_zscore = abs(other_series.latest_value - other_mean) / other_std
                        if other_zscore > 2:
                            causes.append(
                                f"Correlated anomaly in {other_name} "
                                f"({pattern.expected_correlation} correlation)"
                            )

        return causes

    def _calculate_confidence(
        self,
        matched_rules: List[RCARule],
        correlation_causes: List[str],
        log_patterns: List[str],
        event_types: List[str],
    ) -> float:
        """Calculate confidence score for the analysis."""
        confidence = 0.0

        # Rule matches (most reliable)
        if matched_rules:
            confidence += min(0.4, len(matched_rules) * 0.15)

        # Correlation evidence
        if correlation_causes:
            confidence += min(0.25, len(correlation_causes) * 0.1)

        # Log pattern evidence
        if log_patterns:
            confidence += min(0.2, len(log_patterns) * 0.05)

        # Event evidence
        if event_types:
            confidence += min(0.15, len(event_types) * 0.05)

        return min(confidence, 1.0)

    def _find_correlated_anomalies(
        self,
        anomaly: Anomaly,
        related_metrics: List[MetricSeries],
    ) -> List[str]:
        """Find other metrics that are also anomalous."""
        correlated: List[str] = []

        for series in related_metrics:
            if series.name == anomaly.metric_name:
                continue

            if not series.data_points or len(series.data_points) < 10:
                continue

            # Simple anomaly check
            values = series.values
            mean = np.mean(values)
            std = np.std(values)

            if std > 0 and series.latest_value is not None:
                zscore = abs(series.latest_value - mean) / std
                if zscore > 2.5:  # Above 2.5 sigma
                    correlated.append(series.name)

        return correlated

    def _get_llm_analysis(
        self,
        anomaly: Anomaly,
        current_causes: List[str],
        logs: List[LogEntry],
        events: List[Event],
    ) -> Optional[str]:
        """Get LLM-powered analysis for complex cases."""
        if not self._llm_client:
            return None

        try:
            # Build context
            log_summary = "\n".join(
                f"- [{log.level.value}] {log.service}: {log.message[:100]}"
                for log in logs[:10]
            )

            event_summary = "\n".join(
                f"- {e.kind}/{e.name}: {e.reason} - {e.message[:100]}"
                for e in events[:10]
            )

            prompt = f"""Analyze this system anomaly and provide root cause insights.

ANOMALY:
- Metric: {anomaly.metric_name}
- Category: {anomaly.category.value}
- Current Value: {anomaly.current_value:.4f}
- Baseline Value: {anomaly.baseline_value:.4f}
- Deviation: {anomaly.deviation:.2f} sigma ({anomaly.deviation_percent:+.1f}%)
- Duration: {anomaly.duration_minutes} minutes

CURRENT HYPOTHESES:
{chr(10).join(f'- {c}' for c in current_causes) if current_causes else '- No strong hypotheses yet'}

RECENT LOGS:
{log_summary if log_summary else 'No relevant logs'}

RECENT EVENTS:
{event_summary if event_summary else 'No recent events'}

Based on this information:
1. What is the most likely root cause?
2. What additional evidence should we look for?
3. What immediate action should be taken?

Keep response concise (max 200 words)."""

            response = self._llm_client.messages.create(
                model=get_settings().llm.model,
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}],
            )

            return response.content[0].text

        except Exception as e:
            logger.warning("LLM analysis failed", error=str(e))
            return None

    def _generate_suggested_actions(
        self, matched_rules: List[RCARule]
    ) -> List[Dict[str, Any]]:
        """Generate suggested remediation actions from matched rules."""
        actions: List[Dict[str, Any]] = []
        seen_actions: Set[str] = set()

        for rule in matched_rules:
            for action in rule.remediation:
                action_key = f"{action.action}:{action.target}"
                if action_key not in seen_actions:
                    seen_actions.add(action_key)
                    actions.append({
                        "action": action.action,
                        "target": action.target,
                        "priority": action.priority,
                        "from_rule": rule.id,
                        "severity": rule.severity.value,
                    })

        # Sort by priority
        actions.sort(key=lambda x: x["priority"])

        return actions
