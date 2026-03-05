"""
Learning engine for execution feedback and continuous improvement.

Analyzes execution outcomes to:
- Track playbook performance statistics
- Adjust risk scores based on historical success rates
- Extract lessons learned from failures
- Store execution cases in knowledge base
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

import structlog

from src.config.constants import ActionStatus
from src.config.settings import get_settings
from src.models.action_plan import ActionPlan
from src.models.anomaly import Anomaly
from src.models.playbook_stats import (
    ExecutionCase,
    PlaybookExecution,
    PlaybookStats,
    PlaybookStatsStore,
)

logger = structlog.get_logger()


class LearningEngine:
    """
    Engine for learning from execution outcomes.

    Features:
    - Playbook execution tracking
    - Success rate and performance metrics
    - Automatic risk score adjustment recommendations
    - Knowledge base integration for case storage
    - Lessons learned extraction from failures
    """

    def __init__(self, knowledge_base=None):
        """Initialize the learning engine.

        Args:
            knowledge_base: Optional KnowledgeBase instance for case storage
        """
        settings = get_settings()
        self._enabled = settings.learning.enabled
        self._min_executions = settings.learning.min_executions_for_learning
        self._success_threshold = settings.learning.success_rate_threshold
        self._auto_risk_adjustment = settings.learning.auto_risk_adjustment
        self._max_risk_reduction = settings.learning.max_risk_reduction

        self._kb = knowledge_base
        self._stats_store = PlaybookStatsStore()

        # Risk adjustment cache: playbook_id -> adjustment
        self._risk_adjustments: Dict[str, float] = {}

    @property
    def enabled(self) -> bool:
        """Check if learning is enabled."""
        return self._enabled

    async def record_execution(
        self,
        plan: ActionPlan,
        anomaly: Anomaly,
        playbook_id: str,
        playbook_name: str = "",
    ) -> PlaybookStats:
        """
        Record an execution and update statistics.

        Args:
            plan: The executed action plan
            anomaly: The anomaly that triggered the execution
            playbook_id: ID of the playbook used
            playbook_name: Name of the playbook

        Returns:
            Updated playbook statistics
        """
        if not self._enabled:
            return self._stats_store.get_or_create_stats(playbook_id, playbook_name)

        # Create execution record
        execution = self._create_execution_record(plan, anomaly, playbook_id)

        # Update playbook statistics
        stats = self._stats_store.record_execution(execution)
        stats.playbook_name = playbook_name

        logger.info(
            "Recorded execution",
            execution_id=execution.id,
            playbook_id=playbook_id,
            success=execution.success,
            duration=execution.duration_seconds,
            success_rate=f"{stats.success_rate:.1%}",
        )

        # Update risk adjustment if enough data
        if stats.total_executions >= self._min_executions:
            self._update_risk_adjustment(playbook_id, stats)

        # Store case in knowledge base
        if self._kb:
            await self._store_execution_case(plan, anomaly, execution, playbook_id)

        # Extract lessons from failures
        if not execution.success:
            await self._extract_lessons_learned(plan, anomaly, execution, playbook_id)

        return stats

    def _create_execution_record(
        self,
        plan: ActionPlan,
        anomaly: Anomaly,
        playbook_id: str,
    ) -> PlaybookExecution:
        """Create an execution record from plan results."""
        success = plan.status == ActionStatus.SUCCESS
        rolled_back = plan.status == ActionStatus.ROLLED_BACK

        # Count step outcomes
        steps_succeeded = sum(
            1 for s in plan.steps if s.status == ActionStatus.SUCCESS
        )
        steps_failed = sum(
            1 for s in plan.steps if s.status == ActionStatus.FAILED
        )
        steps_skipped = len(plan.steps) - steps_succeeded - steps_failed

        # Get error details from first failed step
        error_message = None
        error_step = None
        for step in plan.steps:
            if step.status == ActionStatus.FAILED:
                error_message = step.error_message
                error_step = step.id
                break

        # Calculate duration
        duration = 0
        if plan.started_at and plan.completed_at:
            duration = int((plan.completed_at - plan.started_at).total_seconds())

        # Get target from first step
        target = plan.steps[0].target if plan.steps else ""
        namespace = plan.steps[0].namespace if plan.steps else ""

        return PlaybookExecution(
            playbook_id=playbook_id,
            plan_id=plan.id,
            anomaly_id=anomaly.id,
            success=success,
            duration_seconds=duration,
            steps_total=len(plan.steps),
            steps_succeeded=steps_succeeded,
            steps_failed=steps_failed,
            steps_skipped=steps_skipped,
            error_message=error_message,
            error_step=error_step,
            rolled_back=rolled_back,
            risk_score=plan.risk_score,
            target=target,
            namespace=namespace,
            metadata={
                "anomaly_metric": anomaly.metric_name,
                "anomaly_severity": anomaly.severity.value,
                "risk_level": plan.risk_level.value,
            },
        )

    def _update_risk_adjustment(self, playbook_id: str, stats: PlaybookStats) -> None:
        """Update risk adjustment recommendation based on stats."""
        if not self._auto_risk_adjustment:
            return

        adjustment = stats.suggested_risk_adjustment

        # Cap the adjustment
        adjustment = max(-self._max_risk_reduction, min(adjustment, self._max_risk_reduction))

        self._risk_adjustments[playbook_id] = adjustment

        logger.info(
            "Updated risk adjustment",
            playbook_id=playbook_id,
            success_rate=f"{stats.success_rate:.1%}",
            adjustment=f"{adjustment:+.2f}",
            confidence=f"{stats.confidence_score:.2f}",
        )

    async def _store_execution_case(
        self,
        plan: ActionPlan,
        anomaly: Anomaly,
        execution: PlaybookExecution,
        playbook_id: str,
    ) -> None:
        """Store execution case in knowledge base."""
        action_types = [step.action_type.value for step in plan.steps]

        case = ExecutionCase(
            anomaly_id=anomaly.id,
            anomaly_type=anomaly.anomaly_type.value,
            metric_name=anomaly.metric_name,
            metric_category=anomaly.category.value,
            severity=anomaly.severity.value,
            deviation=anomaly.deviation,
            duration_minutes=anomaly.duration_minutes,
            playbook_id=playbook_id,
            plan_id=plan.id,
            action_types=action_types,
            target=execution.target,
            namespace=execution.namespace,
            success=execution.success,
            duration_seconds=execution.duration_seconds,
            error_message=execution.error_message,
            rolled_back=execution.rolled_back,
            root_cause=plan.root_cause,
            tags=[
                anomaly.category.value,
                anomaly.severity.value,
                "success" if execution.success else "failed",
            ],
        )

        try:
            await self._kb.add_execution_case(case)
            logger.debug("Stored execution case", case_id=case.id)
        except Exception as e:
            logger.warning("Failed to store execution case", error=str(e))

    async def _extract_lessons_learned(
        self,
        plan: ActionPlan,
        anomaly: Anomaly,
        execution: PlaybookExecution,
        playbook_id: str,
    ) -> None:
        """Extract lessons from a failed execution."""
        lessons: List[str] = []

        # Analyze failure patterns
        if execution.error_message:
            # Check for common failure patterns
            error_lower = execution.error_message.lower()

            if "timeout" in error_lower:
                lessons.append("Execution timeout - consider increasing timeout or breaking into smaller steps")
            elif "permission" in error_lower or "forbidden" in error_lower:
                lessons.append("Permission denied - check RBAC configuration")
            elif "not found" in error_lower:
                lessons.append("Resource not found - verify target exists before execution")
            elif "already" in error_lower:
                lessons.append("Conflicting state - add pre-checks for current state")
            elif "connection" in error_lower or "refused" in error_lower:
                lessons.append("Connection failed - check network/service availability")

        # Check step-level failures
        failed_steps = [s for s in plan.steps if s.status == ActionStatus.FAILED]
        if len(failed_steps) > 1:
            lessons.append("Multiple step failures - consider adding retry logic or circuit breakers")

        # Check if rollback was needed
        if execution.rolled_back:
            lessons.append("Required rollback - ensure proper state validation before execution")

        if lessons:
            logger.info(
                "Extracted lessons learned",
                playbook_id=playbook_id,
                plan_id=plan.id,
                lessons=lessons,
            )

            # Update case with lessons if stored
            # This would be done asynchronously in production

    def get_risk_adjustment(self, playbook_id: str) -> float:
        """Get risk adjustment for a playbook.

        Args:
            playbook_id: The playbook ID

        Returns:
            Risk adjustment value (negative = lower risk, positive = higher risk)
        """
        return self._risk_adjustments.get(playbook_id, 0.0)

    def get_playbook_stats(self, playbook_id: str) -> Optional[PlaybookStats]:
        """Get statistics for a playbook."""
        return self._stats_store.get_stats(playbook_id)

    def get_all_playbook_stats(self) -> List[PlaybookStats]:
        """Get statistics for all playbooks."""
        return self._stats_store.get_all_stats()

    def get_recent_executions(
        self, playbook_id: str, limit: int = 20
    ) -> List[PlaybookExecution]:
        """Get recent executions for a playbook."""
        return self._stats_store.get_executions_for_playbook(playbook_id, limit)

    def get_summary(self) -> Dict[str, Any]:
        """Get learning engine summary."""
        store_summary = self._stats_store.get_summary()
        return {
            "enabled": self._enabled,
            "auto_risk_adjustment": self._auto_risk_adjustment,
            "min_executions_for_learning": self._min_executions,
            "playbooks_with_adjustments": len(self._risk_adjustments),
            **store_summary,
        }

    def should_auto_approve(self, playbook_id: str, base_risk_score: float) -> bool:
        """
        Check if a playbook execution should be auto-approved based on learning.

        Args:
            playbook_id: The playbook ID
            base_risk_score: The original risk score

        Returns:
            True if auto-approval is recommended
        """
        stats = self._stats_store.get_stats(playbook_id)
        if not stats:
            return False

        # Need enough executions
        if stats.total_executions < self._min_executions:
            return False

        # Need high success rate
        if stats.success_rate < self._success_threshold:
            return False

        # Need good confidence
        if stats.confidence_score < 0.7:
            return False

        # Check adjusted risk score
        adjustment = self.get_risk_adjustment(playbook_id)
        adjusted_risk = base_risk_score + adjustment

        # Auto-approve if adjusted risk is low enough
        settings = get_settings()
        return adjusted_risk < settings.risk_assessment.thresholds.semi_auto

    def get_adjusted_risk_score(self, playbook_id: str, base_risk_score: float) -> float:
        """
        Get adjusted risk score based on learning.

        Args:
            playbook_id: The playbook ID
            base_risk_score: The original risk score

        Returns:
            Adjusted risk score
        """
        adjustment = self.get_risk_adjustment(playbook_id)
        adjusted = base_risk_score + adjustment

        # Ensure bounds
        return max(0.0, min(1.0, adjusted))
