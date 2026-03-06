#!/usr/bin/env python3
"""Build a deterministic run-plan JSON for multi-model-critique orchestration.

Security notes:
- Validates and normalizes untrusted user inputs (`question`, `constraints`).
- Rejects known prompt-injection control phrases by default.
- Validates model mapping format (`name=agentId`) with conservative patterns.

This script does not call OpenClaw tools directly.
It prepares a reproducible artifact that an agent/operator can execute with
sessions_spawn / sessions_send / sessions_history.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

MAX_QUESTION_CHARS = 4000
MAX_CONSTRAINTS_CHARS = 2000
NAME_RE = re.compile(r"^[A-Za-z0-9._-]{1,64}$")
AGENT_ID_RE = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")

DISALLOWED_PATTERNS = [
    re.compile(p, re.IGNORECASE)
    for p in [
        r"ignore\s+previous\s+instructions",
        r"disregard\s+all\s+prior",
        r"you\s+are\s+now\s+(system|developer)",
        r"<\s*(system|developer)\s*>",
        r"\btool\s*call\b",
        r"\bsessions_spawn\b",
        r"\bexecute\s+shell\s+command\b",
    ]
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--question", required=True)
    p.add_argument("--models", required=True, help="name=agentId,name=agentId,...")
    p.add_argument("--constraints", default="(none)")
    p.add_argument("--complex", default="true", choices=["true", "false"])
    p.add_argument("--timeout-sec", type=int, default=180)
    p.add_argument("--max-retries", type=int, default=1)
    p.add_argument("--budget-usd", type=float, default=None)
    p.add_argument("--out", required=True)
    return p.parse_args()


def normalize_input(value: str, *, label: str, max_chars: int) -> str:
    cleaned = value.replace("\x00", "").strip()
    cleaned = re.sub(r"\r\n?", "\n", cleaned)

    if not cleaned:
        raise ValueError(f"{label} must not be empty")
    if len(cleaned) > max_chars:
        raise ValueError(f"{label} exceeds max length ({max_chars} chars)")

    for pat in DISALLOWED_PATTERNS:
        if pat.search(cleaned):
            raise ValueError(
                f"{label} contains disallowed control phrase matching: {pat.pattern}"
            )

    cleaned = cleaned.replace("```", "'''")
    return cleaned


def parse_models(raw: str) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for pair in raw.split(","):
        pair = pair.strip()
        if not pair:
            continue
        if "=" not in pair:
            raise ValueError(f"Invalid model mapping: {pair}. Expected name=agentId")

        name, agent_id = pair.split("=", 1)
        name = name.strip()
        agent_id = agent_id.strip()

        if not NAME_RE.fullmatch(name):
            raise ValueError(f"Invalid model name: {name}")
        if not AGENT_ID_RE.fullmatch(agent_id):
            raise ValueError(f"Invalid agentId: {agent_id}")

        items.append({"name": name, "agentId": agent_id})

    if not items:
        raise ValueError("No model mappings provided")
    return items


def main() -> int:
    args = parse_args()
    models = parse_models(args.models)
    question = normalize_input(args.question, label="question", max_chars=MAX_QUESTION_CHARS)
    constraints = normalize_input(
        args.constraints, label="constraints", max_chars=MAX_CONSTRAINTS_CHARS
    )
    now = datetime.now(timezone.utc).isoformat()

    if args.complex != "true":
        raise SystemExit("This workflow should run only when --complex true")
    if args.timeout_sec <= 0 or args.timeout_sec > 3600:
        raise SystemExit("--timeout-sec must be between 1 and 3600")
    if args.max_retries < 0 or args.max_retries > 5:
        raise SystemExit("--max-retries must be between 0 and 5")
    if args.budget_usd is not None and args.budget_usd <= 0:
        raise SystemExit("--budget-usd must be > 0 when provided")

    plan = {
        "schemaVersion": "1.0.1",
        "kind": "multi-model-critique-run-plan",
        "createdAt": now,
        "question": question,
        "constraints": constraints,
        "complex": True,
        "models": models,
        "ops": {
            "timeoutSec": args.timeout_sec,
            "maxRetries": args.max_retries,
            "maxRounds": 4,
            "budgetUsd": args.budget_usd,
        },
        "rounds": [
            {
                "name": "draft",
                "requiredSections": ["Plan", "Execute", "Review", "Improve", "Draft Answer"],
            },
            {
                "name": "cross-critique",
                "requiredSections": [
                    "Strengths",
                    "Weaknesses",
                    "Missing assumptions/data",
                    "Hallucination/confidence risks",
                    "Concrete fixes",
                    "Ranking",
                ],
            },
            {
                "name": "revision",
                "requiredSections": [
                    "Plan",
                    "Execute",
                    "Review",
                    "Improve",
                    "Changes from Critique",
                    "Revised Answer",
                ],
            },
            {
                "name": "synthesis",
                "requiredSections": [
                    "Final Answer",
                    "Key Improvements from Critique",
                    "Uncertainties",
                    "Next Steps",
                ],
            },
        ],
        "rubric": {
            "accuracy": 0.40,
            "coverage": 0.25,
            "evidence": 0.20,
            "actionability": 0.15,
            "scale": "1-5",
        },
        "security": {
            "inputValidated": True,
            "promptInjectionFilters": [p.pattern for p in DISALLOWED_PATTERNS],
        },
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote run plan: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
