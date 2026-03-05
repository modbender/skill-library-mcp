"""
Action planner for generating remediation plans.

Combines risk assessment, playbooks, and RCA to create action plans.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import structlog

from src.cognition.rca_engine import RCAResult
from src.config.constants import ActionStatus, ActionType, RiskLevel
from src.config.settings import get_settings
from src.decision.playbook_engine import Playbook, PlaybookEngine
from src.decision.risk_assessment import RiskAssessor
from src.models.action_plan import ActionPlan, ActionStep, PlanHistory
from src.models.anomaly import Anomaly

logger = structlog.get_logger()


class ActionPlanner:
    """
    Generates action plans for anomaly remediation.

    Features:
    - Playbook-based plan generation
    - Risk-based automation decisions
    - RCA-informed action selection
    - Approval workflow integration
    """

    def __init__(self):
        self._risk_assessor = RiskAssessor()
        self._playbook_engine = PlaybookEngine()
        self._history = PlanHistory()

        settings = get_settings()
        self._approval_timeout_minutes = settings.approval.timeout_minutes
        self._enabled = settings.auto_remediation.enabled

    @property
    def history(self) -> PlanHistory:
        """Get plan history."""
        return self._history

    def create_plan(
        self,
        anomaly: Anomaly,
        rca_result: Optional[RCAResult] = None,
        playbook_id: Optional[str] = None,
    ) -> Optional[ActionPlan]:
        """
        Create an action plan for an anomaly.

        Args:
            anomaly: The anomaly to remediate
            rca_result: Root cause analysis result
            playbook_id: Specific playbook to use (optional)

        Returns:
            ActionPlan or None if no suitable plan
        """
        if not self._enabled:
            logger.info("Auto-remediation disabled, skipping plan creation")
            return None

        # Find appropriate playbook
        playbook = None
        if playbook_id:
            playbook = self._playbook_engine.get_playbook(playbook_id)
        else:
            # Find matching playbooks
            matching = self._playbook_engine.find_matching_playbooks(
                metric_name=anomaly.metric_name,
                anomaly_type=anomaly.anomaly_type.value,
            )
            if matching:
                playbook = matching[0]  # Use first matching playbook

        # If no playbook, try to generate plan from RCA suggestions
        if not playbook and rca_result and rca_result.suggested_actions:
            return self._create_plan_from_rca(anomaly, rca_result)

        if not playbook:
            logger.info(
                "No playbook found for anomaly",
                anomaly_id=anomaly.id,
                metric=anomaly.metric_name,
            )
            return None

        return self._create_plan_from_playbook(anomaly, playbook, rca_result)

    def _create_plan_from_playbook(
        self,
        anomaly: Anomaly,
        playbook: Playbook,
        rca_result: Optional[RCAResult],
    ) -> ActionPlan:
        """Create plan from a playbook."""
        # Determine primary action for risk assessment
        primary_action = (
            playbook.steps[0].action if playbook.steps else ActionType.POD_RESTART
        )

        # Assess risk
        risk_assessment = self._risk_assessor.assess(
            anomaly=anomaly,
            action_type=primary_action,
        )

        # Override risk if playbook specifies
        if playbook.risk_override is not None:
            risk_score = playbook.risk_override
            risk_level = self._determine_risk_level(risk_score)
        else:
            risk_score = risk_assessment.risk_score
            risk_level = risk_assessment.risk_level

        # Create steps from playbook
        steps = [
            ActionStep(
                action_type=step.action,
                target=step.target,
                parameters=step.parameters,
            )
            for step in playbook.steps
        ]

        # Determine approval requirements
        requires_approval = risk_level in (RiskLevel.SEMI_AUTO, RiskLevel.MANUAL)
        approvals_required = self._risk_assessor.get_required_approvals(risk_level)

        # Set status based on risk level
        if risk_level == RiskLevel.CRITICAL:
            status = ActionStatus.PENDING  # Will need manual intervention
        elif requires_approval:
            status = ActionStatus.WAITING_APPROVAL
        else:
            status = ActionStatus.APPROVED  # Auto-approved

        # Calculate approval timeout
        approval_timeout = None
        if requires_approval:
            approval_timeout = datetime.utcnow() + timedelta(
                minutes=self._approval_timeout_minutes
            )

        plan = ActionPlan(
            anomaly_id=anomaly.id,
            anomaly_metric=anomaly.metric_name,
            root_cause=rca_result.root_causes[0] if rca_result and rca_result.root_causes else "",
            risk_score=risk_score,
            risk_level=risk_level,
            steps=steps,
            requires_approval=requires_approval,
            approvals_required=approvals_required,
            approval_timeout=approval_timeout,
            status=status,
        )

        self._history.add_plan(plan)

        logger.info(
            "Created action plan from playbook",
            plan_id=plan.id,
            playbook=playbook.id,
            risk_level=risk_level.value,
            steps=len(steps),
            requires_approval=requires_approval,
        )

        return plan

    def _create_plan_from_rca(
        self,
        anomaly: Anomaly,
        rca_result: RCAResult,
    ) -> Optional[ActionPlan]:
        """Create plan from RCA suggested actions."""
        if not rca_result.suggested_actions:
            return None

        steps: List[ActionStep] = []
        primary_action: Optional[ActionType] = None

        for action_def in rca_result.suggested_actions:
            try:
                action_type = ActionType(action_def.get("action", ""))
                if primary_action is None:
                    primary_action = action_type

                steps.append(
                    ActionStep(
                        action_type=action_type,
                        target=action_def.get("target", ""),
                    )
                )
            except ValueError:
                logger.debug(
                    "Skipping unknown action type",
                    action=action_def.get("action"),
                )

        if not steps or primary_action is None:
            return None

        # Assess risk
        risk_assessment = self._risk_assessor.assess(
            anomaly=anomaly,
            action_type=primary_action,
        )

        risk_level = risk_assessment.risk_level
        requires_approval = risk_level in (RiskLevel.SEMI_AUTO, RiskLevel.MANUAL)
        approvals_required = self._risk_assessor.get_required_approvals(risk_level)

        if risk_level == RiskLevel.CRITICAL:
            status = ActionStatus.PENDING
        elif requires_approval:
            status = ActionStatus.WAITING_APPROVAL
        else:
            status = ActionStatus.APPROVED

        approval_timeout = None
        if requires_approval:
            approval_timeout = datetime.utcnow() + timedelta(
                minutes=self._approval_timeout_minutes
            )

        plan = ActionPlan(
            anomaly_id=anomaly.id,
            anomaly_metric=anomaly.metric_name,
            root_cause=rca_result.root_causes[0] if rca_result.root_causes else "",
            risk_score=risk_assessment.risk_score,
            risk_level=risk_level,
            steps=steps,
            requires_approval=requires_approval,
            approvals_required=approvals_required,
            approval_timeout=approval_timeout,
            status=status,
        )

        self._history.add_plan(plan)

        logger.info(
            "Created action plan from RCA",
            plan_id=plan.id,
            risk_level=risk_level.value,
            steps=len(steps),
        )

        return plan

    def _determine_risk_level(self, score: float) -> RiskLevel:
        """Determine risk level from score."""
        settings = get_settings()
        thresholds = settings.risk_assessment.thresholds

        if score >= thresholds.manual:
            return RiskLevel.CRITICAL
        elif score >= thresholds.semi_auto:
            return RiskLevel.MANUAL
        elif score >= thresholds.auto:
            return RiskLevel.SEMI_AUTO
        else:
            return RiskLevel.AUTO

    def approve_plan(self, plan_id: str, approver: str) -> Optional[ActionPlan]:
        """
        Approve an action plan.

        Args:
            plan_id: Plan ID
            approver: Person approving

        Returns:
            Updated plan or None if not found
        """
        plan = self._find_plan(plan_id)
        if not plan:
            return None

        if plan.status != ActionStatus.WAITING_APPROVAL:
            logger.warning(
                "Cannot approve plan not waiting for approval",
                plan_id=plan_id,
                status=plan.status.value,
            )
            return plan

        if plan.is_expired:
            plan.status = ActionStatus.REJECTED
            plan.error_message = "Approval timeout expired"
            return plan

        is_complete = plan.add_approval(approver)
        if is_complete:
            plan.status = ActionStatus.APPROVED

        logger.info(
            "Plan approval added",
            plan_id=plan_id,
            approver=approver,
            approvals=f"{len(plan.approvals_received)}/{plan.approvals_required}",
            approved=is_complete,
        )

        return plan

    def reject_plan(
        self, plan_id: str, rejector: str, reason: str
    ) -> Optional[ActionPlan]:
        """Reject an action plan."""
        plan = self._find_plan(plan_id)
        if not plan:
            return None

        plan.reject(rejector, reason)

        logger.info(
            "Plan rejected",
            plan_id=plan_id,
            rejector=rejector,
            reason=reason,
        )

        return plan

    def get_pending_approvals(self) -> List[ActionPlan]:
        """Get all plans waiting for approval."""
        return self._history.get_by_status(ActionStatus.WAITING_APPROVAL)

    def get_approved_plans(self) -> List[ActionPlan]:
        """Get all approved plans ready for execution."""
        return self._history.get_by_status(ActionStatus.APPROVED)

    def _find_plan(self, plan_id: str) -> Optional[ActionPlan]:
        """Find a plan by ID."""
        for plan in self._history.plans:
            if plan.id == plan_id:
                return plan
        return None

    def get_plan(self, plan_id: str) -> Optional[ActionPlan]:
        """Get a plan by ID (public method)."""
        return self._find_plan(plan_id)
