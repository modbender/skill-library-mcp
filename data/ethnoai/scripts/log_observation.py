#!/usr/bin/env python3
"""
UXR Observer v2.0 - Observation & Survey Logger
Appends structured observation and survey records to the daily JSONL logs.
Includes cost tracking, use-case fields, and PII redaction metadata.
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path.home() / ".uxr-observer"
SESSIONS_DIR = BASE_DIR / "sessions"
CONFIG_PATH = BASE_DIR / "config.json"

# PII detection patterns (simplified - the LLM agent does deeper redaction)
PII_PATTERNS = {
    "EMAIL": re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
    "PHONE": re.compile(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b"),
    "SSN": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "CREDIT_CARD": re.compile(r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b"),
    "API_KEY": re.compile(r"\b(sk-[a-zA-Z0-9]{20,}|Bearer\s+[a-zA-Z0-9._-]{20,})\b"),
}


def detect_pii(text: str) -> dict:
    """Detect PII categories present in text. Returns category counts."""
    if not text:
        return {"categories": [], "count": 0}

    categories = []
    total = 0
    for category, pattern in PII_PATTERNS.items():
        matches = pattern.findall(text)
        if matches:
            categories.append(category)
            total += len(matches)

    return {"categories": categories, "count": total}


def estimate_cost(tokens_input: int, tokens_output: int, model: str = "default") -> float:
    """Estimate cost from token counts using config pricing."""
    try:
        config = json.loads(CONFIG_PATH.read_text())
        pricing = config.get("cost_tracking", {}).get("model_pricing", {})
    except (FileNotFoundError, json.JSONDecodeError):
        pricing = {
            "default": {"input_per_mtok": 3.00, "output_per_mtok": 15.00}
        }

    model_pricing = pricing.get(model, pricing.get("default", {}))
    input_cost = (tokens_input / 1_000_000) * model_pricing.get("input_per_mtok", 3.00)
    output_cost = (tokens_output / 1_000_000) * model_pricing.get("output_per_mtok", 15.00)
    return round(input_cost + output_cost, 6)


def get_today_dir() -> Path:
    """Get or create today's session directory."""
    today = datetime.now().strftime("%Y-%m-%d")
    today_dir = SESSIONS_DIR / today
    today_dir.mkdir(parents=True, exist_ok=True)
    (today_dir / "supersummary").mkdir(exist_ok=True)
    return today_dir


def log_observation(observation: dict):
    """Append an observation to today's log file."""
    today_dir = get_today_dir()
    obs_path = today_dir / "observations.jsonl"

    # Ensure required fields
    observation.setdefault("timestamp", datetime.now().isoformat())
    observation.setdefault("observation_type", "interaction")

    # Auto-detect PII if not already set
    if "pii_redacted" not in observation:
        all_text = " ".join(
            str(v)
            for v in [
                observation.get("user_request_verbatim", ""),
                observation.get("task_context_summary", ""),
                observation.get("notes", ""),
            ]
        )
        for v in observation.get("verbatims", []):
            all_text += " " + v.get("quote", "")
        observation["pii_redacted"] = detect_pii(all_text)

    # Auto-estimate cost if not set and tokens are available
    cost = observation.get("cost", {})
    if cost and cost.get("tokens_input") and not cost.get("actual_cost_usd") and not cost.get("estimated_cost_usd"):
        cost["estimated_cost_usd"] = estimate_cost(
            cost["tokens_input"],
            cost.get("tokens_output", 0),
            cost.get("model_used", "default"),
        )
        cost["cost_source"] = "estimated"
        observation["cost"] = cost

    with open(obs_path, "a") as f:
        f.write(json.dumps(observation) + "\n")

    print(f"[UXR Observer] Logged observation to {obs_path}")


def log_survey(survey: dict):
    """Append a survey response to today's log file."""
    today_dir = get_today_dir()
    survey_path = today_dir / "surveys.jsonl"

    survey.setdefault("timestamp", datetime.now().isoformat())

    # Auto-detect PII in survey responses
    if "pii_redacted" not in survey:
        responses = survey.get("responses", {})
        all_text = " ".join(str(v) for v in responses.values())
        survey["pii_redacted"] = detect_pii(all_text)

    with open(survey_path, "a") as f:
        f.write(json.dumps(survey) + "\n")

    print(f"[UXR Observer] Logged survey response to {survey_path}")


if __name__ == "__main__":
    # Accept JSON from stdin or command line arg
    if len(sys.argv) > 1:
        data = json.loads(sys.argv[1])
    else:
        data = json.loads(sys.stdin.read())

    record_type = data.pop("_type", "observation")
    if record_type == "survey":
        log_survey(data)
    else:
        log_observation(data)
