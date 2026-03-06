from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SessionHealth:
    key: str
    session_id: str
    model: str
    total_tokens: int
    context_tokens: int
    utilization: float
    age_minutes: float
    aborted_last_run: bool
    status: str
    reason: str


def session_utilization(total_tokens: int, context_tokens: int) -> float:
    if context_tokens <= 0:
        return 0.0
    return float(total_tokens) / float(context_tokens)


def evaluate_session(session: dict, warn_at: float, urgent_at: float, max_idle_minutes: int) -> SessionHealth:
    total = int(session.get("totalTokens") or 0)
    ctx = int(session.get("contextTokens") or 0)
    util = session_utilization(total, ctx)
    age_ms = int(session.get("ageMs") or 0)
    age_min = age_ms / 60000.0
    aborted = bool(session.get("abortedLastRun"))

    status = "healthy"
    reason = "within thresholds"

    if util >= urgent_at:
        status = "urgent"
        reason = f"context utilization {util:.0%}"
    elif util >= warn_at:
        status = "warning"
        reason = f"context utilization {util:.0%}"

    if aborted and util >= 0.9:
        status = "stuck"
        reason = "aborted run near context limit"
    elif age_min > max_idle_minutes and util >= warn_at:
        if status == "healthy":
            status = "warning"
        reason = f"idle {age_min:.0f}m with high token usage"

    return SessionHealth(
        key=str(session.get("key") or ""),
        session_id=str(session.get("sessionId") or ""),
        model=str(session.get("model") or "unknown"),
        total_tokens=total,
        context_tokens=ctx,
        utilization=util,
        age_minutes=age_min,
        aborted_last_run=aborted,
        status=status,
        reason=reason,
    )
