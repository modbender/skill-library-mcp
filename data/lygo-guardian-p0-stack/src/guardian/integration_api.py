"""Integration API for LYGO Guardian P0 Stack (base skill).

This is intentionally lightweight: other agents can import these
functions to run their own content/actions through the Guardian.
"""

from .p0_kernel_core import validate_with_understanding


def validate_decision(context: dict, candidate: dict) -> dict:
    """Validate a candidate action or message.

    context: info about where/how this is being used, e.g.:
      {
        "channel": "moltx|clawchat|internal",
        "task": "post|reply|tool_call|memory_write",
        "user_intent": "string description",
        "risk_tolerance": "low|medium|high"
      }

    candidate: {
      "content": "text of reply or description of action",
      "metadata": {... optional ...}
    }
    """

    content = candidate.get("content", "")
    verdict = validate_with_understanding(content, context)
    return verdict


def guardian_wrap(fn):
    """Decorator to wrap a generation function with Guardian checks.

    Example:

    @guardian_wrap
    def generate_reply(context, *args, **kwargs):
        return llm_call(...)
    """

    def wrapped(context, *args, **kwargs):
        raw = fn(context, *args, **kwargs)
        verdict = validate_decision(context, {"content": raw})

        action = verdict.get("action", "allow")

        if action == "allow":
            return raw
        if action == "flag":
            note = verdict.get("understanding") or "Guardian flagged this content as risky."
            return f"{raw}\n\n[LYGO Guardian Note]: {note}"
        if action == "isolate":
            return "[BLOCKED BY LYGO GUARDIAN: content failed Nano-Kernel validation]"
        # escalate / default
        return "[LYGO GUARDIAN REQUESTS REVIEW BEFORE SENDING THIS]"

    return wrapped
