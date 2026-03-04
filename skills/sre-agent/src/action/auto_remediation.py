"""
Auto-remediation engine for executing action plans.

Executes approved remediation actions with safety checks and rollback.
"""

from datetime import datetime
from typing import Any

import structlog

from src.action.audit_logger import AuditLogger
from src.action.executors.http_executor import HTTPExecutor
from src.action.executors.k8s_executor import KubernetesExecutor
from src.config.constants import ActionStatus, ActionType
from src.config.settings import get_settings
from src.models.action_plan import ActionPlan, ActionStep

logger = structlog.get_logger()


class AutoRemediation:
    """
    Auto-remediation execution engine.

    Features:
    - Pre-execution validation
    - Step-by-step execution
    - Automatic rollback on failure
    - Audit logging
    - Rate limiting
    """

    def __init__(self):
        settings = get_settings()
        self._enabled = settings.auto_remediation.enabled
        self._dry_run = settings.auto_remediation.dry_run
        self._max_concurrent = settings.auto_remediation.max_concurrent_actions
        self._cooldown_minutes = settings.auto_remediation.cooldown_minutes
        self._blacklist = settings.auto_remediation.blacklist

        # Executors
        self._k8s_executor = KubernetesExecutor()
        self._http_executor = HTTPExecutor()
        self._audit_logger = AuditLogger()

        # State tracking
        self._active_executions: dict[str, ActionPlan] = {}
        self._recent_targets: dict[str, datetime] = {}  # For cooldown

    @property
    def is_enabled(self) -> bool:
        """Check if remediation is enabled."""
        return self._enabled

    async def execute_plan(self, plan: ActionPlan) -> ActionPlan:
        """
        Execute an action plan.

        Args:
            plan: Approved action plan

        Returns:
            Updated plan with execution results
        """
        if not self._enabled:
            plan.error_message = "Auto-remediation is disabled"
            return plan

        if plan.status != ActionStatus.APPROVED:
            plan.error_message = f"Plan not approved, status: {plan.status.value}"
            return plan

        # Check concurrent executions
        if len(self._active_executions) >= self._max_concurrent:
            plan.error_message = "Max concurrent executions reached"
            return plan

        # Start execution
        plan.mark_started()
        self._active_executions[plan.id] = plan

        logger.info(
            "Starting plan execution",
            plan_id=plan.id,
            steps=len(plan.steps),
            dry_run=self._dry_run,
        )

        try:
            # Execute steps
            success = True
            for step in plan.steps:
                step_success = await self._execute_step(plan, step)
                if not step_success:
                    success = False
                    # Check if we should continue or rollback
                    if step.status == ActionStatus.FAILED:
                        await self._rollback_plan(plan)
                        break

            # Complete plan
            summary = self._generate_summary(plan)
            plan.mark_completed(success, summary)

        except Exception as e:
            logger.error(
                "Plan execution failed",
                plan_id=plan.id,
                error=str(e),
            )
            plan.mark_completed(False, f"Execution error: {str(e)}")
            await self._rollback_plan(plan)

        finally:
            self._active_executions.pop(plan.id, None)

        return plan

    async def _execute_step(self, plan: ActionPlan, step: ActionStep) -> bool:
        """Execute a single step."""
        # Check blacklist
        if self._is_blacklisted(step):
            step.status = ActionStatus.REJECTED
            step.error_message = "Target is blacklisted"
            self._audit_logger.log_action(
                action_type=step.action_type.value,
                target=step.target,
                status="rejected",
                plan_id=plan.id,
                step_id=step.id,
                error_message="Target is blacklisted",
            )
            return False

        # Check cooldown
        if self._is_in_cooldown(step.target):
            step.status = ActionStatus.REJECTED
            step.error_message = "Target is in cooldown period"
            return False

        # Log start
        self._audit_logger.log_action(
            action_type=step.action_type.value,
            target=step.target,
            status="started",
            plan_id=plan.id,
            step_id=step.id,
            actor_id="system",
        )

        step.mark_started()

        if self._dry_run:
            logger.info(
                "DRY RUN: Would execute step",
                step_id=step.id,
                action=step.action_type.value,
                target=step.target,
            )
            step.mark_completed(True)
            return True

        try:
            # Execute based on action type
            result = await self._dispatch_action(step)

            if result.get("success"):
                step.mark_completed(True)
                step.rollback_data = result.get("rollback_data", {})
                self._recent_targets[step.target] = datetime.utcnow()

                self._audit_logger.log_action(
                    action_type=step.action_type.value,
                    target=step.target,
                    status="success",
                    plan_id=plan.id,
                    step_id=step.id,
                    duration_seconds=step.duration_seconds,
                    state_after=result.get("state_after", {}),
                )
                return True
            else:
                step.mark_completed(False, result.get("error", "Unknown error"))
                self._audit_logger.log_action(
                    action_type=step.action_type.value,
                    target=step.target,
                    status="failed",
                    plan_id=plan.id,
                    step_id=step.id,
                    error_message=step.error_message,
                )
                return False

        except Exception as e:
            step.mark_completed(False, str(e))
            self._audit_logger.log_action(
                action_type=step.action_type.value,
                target=step.target,
                status="failed",
                plan_id=plan.id,
                step_id=step.id,
                error_message=str(e),
            )
            return False

    async def _dispatch_action(self, step: ActionStep) -> dict[str, Any]:
        """Dispatch action to appropriate executor."""
        action_handlers = {
            ActionType.POD_RESTART: self._k8s_executor.restart_pod,
            ActionType.HPA_SCALE: self._k8s_executor.scale_hpa,
            ActionType.DEPLOYMENT_ROLLBACK: self._k8s_executor.rollback_deployment,
            ActionType.CONFIG_ROLLBACK: self._k8s_executor.rollback_configmap,
            ActionType.CUSTOM_WEBHOOK: self._http_executor.call_webhook,
        }

        handler = action_handlers.get(step.action_type)
        if not handler:
            return {
                "success": False,
                "error": f"No handler for action type: {step.action_type.value}",
            }

        return await handler(step.target, step.namespace, step.parameters)

    async def _rollback_plan(self, plan: ActionPlan) -> None:
        """Rollback completed steps in reverse order."""
        logger.info("Rolling back plan", plan_id=plan.id)

        completed_steps = plan.get_completed_steps()
        for step in reversed(completed_steps):
            if step.status == ActionStatus.SUCCESS and step.can_rollback:
                await self._rollback_step(plan, step)

    async def _rollback_step(self, plan: ActionPlan, step: ActionStep) -> None:
        """Rollback a single step."""
        logger.info(
            "Rolling back step",
            step_id=step.id,
            action=step.action_type.value,
        )

        self._audit_logger.log_action(
            action_type=f"{step.action_type.value}_rollback",
            target=step.target,
            status="started",
            plan_id=plan.id,
            step_id=step.id,
        )

        if self._dry_run:
            step.mark_rolled_back()
            return

        try:
            result = await self._dispatch_rollback(step)
            if result.get("success"):
                step.mark_rolled_back()
                self._audit_logger.log_action(
                    action_type=f"{step.action_type.value}_rollback",
                    target=step.target,
                    status="success",
                    plan_id=plan.id,
                    step_id=step.id,
                )
            else:
                logger.error(
                    "Rollback failed",
                    step_id=step.id,
                    error=result.get("error"),
                )
        except Exception as e:
            logger.error("Rollback error", step_id=step.id, error=str(e))

    async def _dispatch_rollback(self, step: ActionStep) -> dict[str, Any]:
        """Dispatch rollback action."""
        if step.action_type == ActionType.DEPLOYMENT_ROLLBACK:
            # Rollback the rollback (go back to previous version)
            if "previous_revision" in step.rollback_data:
                return await self._k8s_executor.rollback_deployment(
                    step.target,
                    step.namespace,
                    {"revision": step.rollback_data["previous_revision"]},
                )

        # Most actions don't have automatic rollback
        return {"success": True}

    def _is_blacklisted(self, step: ActionStep) -> bool:
        """Check if target is blacklisted."""
        # Check namespace
        if step.namespace in self._blacklist.namespaces:
            return True

        # Check labels (would need to fetch from K8s)
        # For now, just check target name patterns
        for label in self._blacklist.labels:
            if label.split("=")[0] in step.target.lower():
                return True

        return False

    def _is_in_cooldown(self, target: str) -> bool:
        """Check if target is in cooldown period."""
        last_action = self._recent_targets.get(target)
        if not last_action:
            return False

        elapsed = (datetime.utcnow() - last_action).total_seconds() / 60
        return elapsed < self._cooldown_minutes

    def _generate_summary(self, plan: ActionPlan) -> str:
        """Generate execution summary."""
        total = len(plan.steps)
        successful = sum(1 for s in plan.steps if s.status == ActionStatus.SUCCESS)
        failed = sum(1 for s in plan.steps if s.status == ActionStatus.FAILED)
        rolled_back = sum(1 for s in plan.steps if s.status == ActionStatus.ROLLED_BACK)

        return (
            f"Executed {successful}/{total} steps successfully. "
            f"Failed: {failed}. Rolled back: {rolled_back}."
        )

    def get_active_executions(self) -> list[ActionPlan]:
        """Get currently executing plans."""
        return list(self._active_executions.values())
