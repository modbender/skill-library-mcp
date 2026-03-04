"""
Data models for action plans and remediation steps.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from src.config.constants import ActionStatus, ActionType, RiskLevel


class ActionStep(BaseModel):
    """A single step in an action plan."""

    id: str = Field(default_factory=lambda: f"STEP-{uuid4().hex[:6]}")
    action_type: ActionType
    target: str  # e.g., "deployment/trading-engine", "pod/xyz-123"
    namespace: str = "default"
    parameters: Dict[str, Any] = Field(default_factory=dict)

    # Execution state
    status: ActionStatus = ActionStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    error_message: Optional[str] = None

    # Validation
    pre_check_passed: bool = False
    post_check_passed: bool = False

    # Rollback info
    rollback_data: Dict[str, Any] = Field(default_factory=dict)
    can_rollback: bool = True

    def mark_started(self) -> None:
        """Mark step as started."""
        self.status = ActionStatus.EXECUTING
        self.started_at = datetime.utcnow()

    def mark_completed(self, success: bool, error: Optional[str] = None) -> None:
        """Mark step as completed."""
        self.completed_at = datetime.utcnow()
        if self.started_at:
            self.duration_seconds = int(
                (self.completed_at - self.started_at).total_seconds()
            )
        self.status = ActionStatus.SUCCESS if success else ActionStatus.FAILED
        self.error_message = error

    def mark_rolled_back(self) -> None:
        """Mark step as rolled back."""
        self.status = ActionStatus.ROLLED_BACK


class ActionPlan(BaseModel):
    """Complete action plan for remediation."""

    id: str = Field(default_factory=lambda: f"PLAN-{uuid4().hex[:8]}")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Trigger information
    anomaly_id: str
    anomaly_metric: str
    root_cause: str = ""

    # Risk assessment
    risk_score: float
    risk_level: RiskLevel

    # Steps
    steps: List[ActionStep] = Field(default_factory=list)

    # Approval
    requires_approval: bool = False
    approvals_required: int = 0
    approvals_received: List[str] = Field(default_factory=list)
    approval_timeout: Optional[datetime] = None

    # Execution state
    status: ActionStatus = ActionStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    current_step_index: int = 0

    # Results
    success: bool = False
    error_message: Optional[str] = None
    summary: str = ""

    @property
    def is_approved(self) -> bool:
        """Check if plan has required approvals."""
        if not self.requires_approval:
            return True
        return len(self.approvals_received) >= self.approvals_required

    @property
    def is_expired(self) -> bool:
        """Check if approval timeout has passed."""
        if not self.approval_timeout:
            return False
        return datetime.utcnow() > self.approval_timeout

    def add_approval(self, approver: str) -> bool:
        """
        Add an approval.

        Returns True if this approval completes the requirements.
        """
        if approver not in self.approvals_received:
            self.approvals_received.append(approver)
        return self.is_approved

    def reject(self, rejector: str, reason: str) -> None:
        """Reject the plan."""
        self.status = ActionStatus.REJECTED
        self.error_message = f"Rejected by {rejector}: {reason}"

    def mark_started(self) -> None:
        """Mark plan as started."""
        self.status = ActionStatus.EXECUTING
        self.started_at = datetime.utcnow()

    def mark_completed(self, success: bool, summary: str = "") -> None:
        """Mark plan as completed."""
        self.completed_at = datetime.utcnow()
        self.success = success
        self.status = ActionStatus.SUCCESS if success else ActionStatus.FAILED
        self.summary = summary

    def get_current_step(self) -> Optional[ActionStep]:
        """Get the current step to execute."""
        if 0 <= self.current_step_index < len(self.steps):
            return self.steps[self.current_step_index]
        return None

    def advance_step(self) -> Optional[ActionStep]:
        """Advance to next step."""
        self.current_step_index += 1
        return self.get_current_step()

    def get_completed_steps(self) -> List[ActionStep]:
        """Get all completed steps."""
        return [
            s for s in self.steps
            if s.status in (ActionStatus.SUCCESS, ActionStatus.FAILED, ActionStatus.ROLLED_BACK)
        ]

    def get_failed_steps(self) -> List[ActionStep]:
        """Get all failed steps."""
        return [s for s in self.steps if s.status == ActionStatus.FAILED]

    def to_summary(self) -> str:
        """Generate human-readable summary."""
        lines = [
            f"Plan ID: {self.id}",
            f"Risk Level: {self.risk_level.value} (score: {self.risk_score:.2f})",
            f"Status: {self.status.value}",
            f"Steps: {len(self.steps)}",
            "",
            "Steps:",
        ]

        for i, step in enumerate(self.steps, 1):
            status_icon = {
                ActionStatus.PENDING: "⏳",
                ActionStatus.EXECUTING: "🔄",
                ActionStatus.SUCCESS: "✅",
                ActionStatus.FAILED: "❌",
                ActionStatus.ROLLED_BACK: "↩️",
            }.get(step.status, "?")

            lines.append(
                f"  {i}. {status_icon} {step.action_type.value} on {step.target}"
            )
            if step.error_message:
                lines.append(f"      Error: {step.error_message}")

        return "\n".join(lines)


class PlanHistory(BaseModel):
    """History of action plans for audit."""

    plans: List[ActionPlan] = Field(default_factory=list)

    def add_plan(self, plan: ActionPlan) -> None:
        """Add a plan to history."""
        self.plans.append(plan)

    def get_recent(self, limit: int = 10) -> List[ActionPlan]:
        """Get recent plans."""
        return sorted(
            self.plans, key=lambda p: p.created_at, reverse=True
        )[:limit]

    def get_by_status(self, status: ActionStatus) -> List[ActionPlan]:
        """Get plans by status."""
        return [p for p in self.plans if p.status == status]

    def get_success_rate(self, days: int = 7) -> float:
        """Calculate success rate over recent period."""
        cutoff = datetime.utcnow().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        recent = [
            p for p in self.plans
            if p.completed_at and p.completed_at >= cutoff
        ]

        if not recent:
            return 0.0

        successful = sum(1 for p in recent if p.success)
        return successful / len(recent)
