#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "nova-act",
#     "pydantic>=2.0",
#     "fire",
# ]
# ///
"""
Run browser automation tasks using Amazon Nova Act.

Usage:
    uv run nova_act_runner.py --url "https://google.com/flights" --task "Find flights from SFO to NYC and return the options"
"""

import json
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

from pydantic import BaseModel


class TaskResult(BaseModel):
    """Generic result schema for any browser task."""
    summary: str
    details: list[str]


ALLOWED_SCHEMES = {"http", "https"}

MATERIAL_IMPACT_KEYWORDS = [
    # Monetary
    "buy", "purchase", "checkout", "pay", "subscribe", "donate", "order",
    # Communication
    "post", "publish", "share", "send", "email", "message", "tweet",
    # Account creation
    "sign up", "register", "create account", "join",
    # Submissions
    "submit", "apply", "enroll", "book", "reserve",
    # Destructive
    "delete", "remove", "cancel",
]

SAFETY_SUFFIX = (
    " IMPORTANT: Do NOT complete any final action that would cause monetary impact, "
    "external communication, account creation, or data modification. "
    "Stop before clicking any purchase, submit, post, or sign-up button. "
    "Instead, report what you found and confirm the final action button is accessible."
)


def load_cookbook() -> str:
    """Load the Nova Act cookbook for safety guidance and best practices."""
    skill_dir = Path(__file__).resolve().parent.parent
    cookbook_path = skill_dir / "references" / "nova-act-cookbook.md"
    try:
        content = cookbook_path.read_text()
        print(f"Loaded Nova Act cookbook ({len(content)} chars)", file=sys.stderr)
        return content
    except Exception as e:
        print(f"Could not load cookbook: {e}", file=sys.stderr)
        return ""


def validate_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in ALLOWED_SCHEMES:
        print(f"Error: URL scheme must be http or https, got: {parsed.scheme!r}", file=sys.stderr)
        sys.exit(1)
    if not parsed.netloc:
        print(f"Error: URL must include a hostname: {url}", file=sys.stderr)
        sys.exit(1)
    return url


def validate_task(task: str) -> str:
    if not task or not task.strip():
        print("Error: Task description cannot be empty", file=sys.stderr)
        sys.exit(1)
    if len(task) > 2000:
        print(f"Error: Task too long ({len(task)} chars, max 2000)", file=sys.stderr)
        sys.exit(1)
    return task.strip()


def check_material_impact(task: str) -> list[str]:
    """Check if task involves material-impact actions. Returns triggered keywords."""
    task_lower = task.lower()
    triggered = [kw for kw in MATERIAL_IMPACT_KEYWORDS if kw in task_lower]
    if triggered:
        print(f"Safety: Material-impact keywords detected ({', '.join(triggered)}). "
              f"Will stop before completing irreversible actions.", file=sys.stderr)
    return triggered


def apply_safety_guardrails(task: str, triggered_keywords: list[str]) -> str:
    """Append safety instructions to task prompt when material-impact keywords detected."""
    if triggered_keywords:
        return task + SAFETY_SUFFIX
    return task


def run(url: str, task: str) -> None:
    """
    Run a browser automation task with Nova Act.

    Safety: If the task description contains material-impact keywords
    (buy, purchase, submit, etc.), the runner automatically appends
    safety instructions to prevent Nova Act from completing irreversible
    actions.

    Args:
        url: Starting URL to navigate to
        task: Task to perform and return results
    """
    url = validate_url(url)
    task = validate_task(task)
    triggered = check_material_impact(task)
    safe_task = apply_safety_guardrails(task, triggered)

    cookbook = load_cookbook()  # Load safety guidelines at runtime

    api_key = os.environ.get("NOVA_ACT_API_KEY")
    if not api_key:
        print("Error: NOVA_ACT_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    from nova_act import NovaAct

    try:
        with NovaAct(starting_page=url) as nova:
            # act_get performs the task AND extracts results in one call
            result = nova.act_get(safe_task, schema=TaskResult.model_json_schema())

            # Parse and output
            task_result = TaskResult.model_validate(result.parsed_response)

            # If safety guardrails were applied, note it in the output
            if triggered:
                task_result.details.append(
                    f"[Safety] Material-impact keywords detected ({', '.join(triggered)}). "
                    f"Stopped before completing irreversible actions."
                )

            print(json.dumps(task_result.model_dump(), indent=2))

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    import fire
    fire.Fire(run)


if __name__ == "__main__":
    main()
