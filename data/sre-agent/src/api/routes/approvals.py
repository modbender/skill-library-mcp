"""
Approval management API endpoints.
"""

from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from src.config.constants import ActionStatus
from src.decision.action_planner import ActionPlanner

router = APIRouter()

# Global action planner instance (will be set by main.py)
_action_planner: Optional[ActionPlanner] = None


def set_action_planner(planner: ActionPlanner) -> None:
    """Set the action planner instance."""
    global _action_planner
    _action_planner = planner


def get_planner() -> ActionPlanner:
    """Get the action planner instance."""
    if _action_planner is None:
        raise HTTPException(status_code=503, detail="Action planner not initialized")
    return _action_planner


class ApprovalRequest(BaseModel):
    """Request body for approval."""

    approver: str
    comment: Optional[str] = None


class RejectionRequest(BaseModel):
    """Request body for rejection."""

    rejector: str
    reason: str


@router.get("/approvals")
async def list_pending_approvals() -> Dict[str, Any]:
    """List all plans waiting for approval."""
    planner = get_planner()
    pending = planner.get_pending_approvals()

    return {
        "count": len(pending),
        "plans": [
            {
                "id": p.id,
                "anomaly_id": p.anomaly_id,
                "anomaly_metric": p.anomaly_metric,
                "root_cause": p.root_cause,
                "risk_score": p.risk_score,
                "risk_level": p.risk_level.value,
                "steps": len(p.steps),
                "approvals_required": p.approvals_required,
                "approvals_received": len(p.approvals_received),
                "approval_timeout": p.approval_timeout.isoformat() if p.approval_timeout else None,
                "created_at": p.created_at.isoformat(),
            }
            for p in pending
        ],
    }


@router.get("/approvals/{plan_id}")
async def get_plan_details(plan_id: str) -> Dict[str, Any]:
    """Get detailed information about a plan."""
    planner = get_planner()
    plan = planner.get_plan(plan_id)

    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    return {
        "id": plan.id,
        "anomaly_id": plan.anomaly_id,
        "anomaly_metric": plan.anomaly_metric,
        "root_cause": plan.root_cause,
        "risk_score": plan.risk_score,
        "risk_level": plan.risk_level.value,
        "status": plan.status.value,
        "requires_approval": plan.requires_approval,
        "approvals_required": plan.approvals_required,
        "approvals_received": plan.approvals_received,
        "approval_timeout": plan.approval_timeout.isoformat() if plan.approval_timeout else None,
        "is_approved": plan.is_approved,
        "is_expired": plan.is_expired,
        "created_at": plan.created_at.isoformat(),
        "started_at": plan.started_at.isoformat() if plan.started_at else None,
        "completed_at": plan.completed_at.isoformat() if plan.completed_at else None,
        "success": plan.success,
        "summary": plan.summary,
        "error_message": plan.error_message,
        "steps": [
            {
                "id": s.id,
                "action_type": s.action_type.value,
                "target": s.target,
                "namespace": s.namespace,
                "status": s.status.value,
                "error_message": s.error_message,
            }
            for s in plan.steps
        ],
    }


@router.post("/approvals/{plan_id}/approve")
async def approve_plan(plan_id: str, request: ApprovalRequest) -> Dict[str, Any]:
    """Approve a plan."""
    planner = get_planner()

    plan = planner.approve_plan(plan_id, request.approver)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    return {
        "status": "approved" if plan.is_approved else "approval_added",
        "plan_id": plan_id,
        "approver": request.approver,
        "approvals_received": len(plan.approvals_received),
        "approvals_required": plan.approvals_required,
        "is_fully_approved": plan.is_approved,
    }


@router.post("/approvals/{plan_id}/reject")
async def reject_plan(plan_id: str, request: RejectionRequest) -> Dict[str, Any]:
    """Reject a plan."""
    planner = get_planner()

    plan = planner.reject_plan(plan_id, request.rejector, request.reason)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    return {
        "status": "rejected",
        "plan_id": plan_id,
        "rejector": request.rejector,
        "reason": request.reason,
    }


@router.get("/plans")
async def list_plans(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(20, description="Maximum number of plans to return"),
) -> Dict[str, Any]:
    """List action plans."""
    planner = get_planner()

    plans = planner.history.plans
    if status:
        try:
            status_enum = ActionStatus(status)
            plans = [p for p in plans if p.status == status_enum]
        except ValueError:
            pass

    # Sort by creation time descending
    plans = sorted(plans, key=lambda p: p.created_at, reverse=True)[:limit]

    return {
        "count": len(plans),
        "plans": [
            {
                "id": p.id,
                "anomaly_id": p.anomaly_id,
                "risk_level": p.risk_level.value,
                "status": p.status.value,
                "created_at": p.created_at.isoformat(),
                "success": p.success,
            }
            for p in plans
        ],
    }
