from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any

from _runtime import read_input_payload, write_json


CRITERION_DIRECTION_MAP = {
    "cost": "cost",
    "price": "cost",
    "budget": "cost",
    "expense": "cost",
    "time": "cost",
    "duration": "cost",
    "latency": "cost",
    "delay": "cost",
    "walk": "cost",
    "walking": "cost",
    "transfer": "cost",
    "transfers": "cost",
    "risk": "cost",
    "quality": "benefit",
    "reliability": "benefit",
    "support": "benefit",
    "accuracy": "benefit",
    "fit": "benefit",
    "coverage": "benefit",
    "speed": "benefit",
    "performance": "benefit",
    "interpretability": "benefit",
    "extensibility": "benefit",
}


def _guess_direction(name: str) -> str | None:
    lowered = name.strip().lower()
    for token, direction in CRITERION_DIRECTION_MAP.items():
        if token in lowered:
            return direction
    return None


def _normalize_criterion(item: Any) -> tuple[dict[str, Any] | None, str | None]:
    if isinstance(item, str):
        direction = _guess_direction(item)
        if direction is None:
            return None, f"criterion '{item}' is missing an explicit direction"
        return {"name": item, "direction": direction}, None

    if not isinstance(item, dict):
        return None, f"criterion entry of type {type(item).__name__} is unsupported"

    name = str(item.get("name", "")).strip()
    if not name:
        return None, "criterion is missing a name"

    direction = item.get("direction")
    if direction is None:
        direction = _guess_direction(name)
    if direction not in {"benefit", "cost"}:
        return None, f"criterion '{name}' requires direction 'benefit' or 'cost'"

    normalized = {"name": name, "direction": direction}
    if "weight" in item:
        normalized["weight"] = item["weight"]
    if item.get("description"):
        normalized["description"] = item["description"]
    return normalized, None


def _normalize_option(item: Any) -> tuple[dict[str, Any] | None, str | None]:
    if isinstance(item, str):
        name = item.strip()
        if not name:
            return None, "option name cannot be empty"
        return {"name": name, "values": []}, None

    if not isinstance(item, dict):
        return None, f"option entry of type {type(item).__name__} is unsupported"

    name = str(item.get("name", "")).strip()
    if not name:
        return None, "option is missing a name"

    values = item.get("values", [])
    if values is None:
        values = []
    return {"name": name, "values": values}, None


def _extract_text_options(text: str) -> list[str]:
    options: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(("-", "*")):
            value = stripped[1:].strip()
            if value:
                options.append(value)
    return options


def build_request_skeleton(payload: Any) -> dict[str, Any]:
    if isinstance(payload, str):
        text = payload.strip()
        extracted_options = _extract_text_options(text)
        request: dict[str, Any] = {
            "context": text,
            "policy_name": "balanced",
        }
        missing = ["criteria"]
        if extracted_options:
            request["options"] = [{"name": item, "values": []} for item in extracted_options]
            missing.append("option criterion values")
        else:
            request["options"] = []
            missing.extend(["options", "option criterion values"])

        return {
            "mode": "freeform",
            "ready_to_run": False,
            "request": request,
            "missing_fields": missing,
            "guidance": [
                "Provide 2 or more options.",
                "Provide explicit criteria with benefit/cost direction.",
                "Provide per-option numeric values for each criterion.",
            ],
        }

    if not isinstance(payload, dict):
        return {
            "mode": "freeform",
            "ready_to_run": False,
            "request": {"policy_name": "balanced"},
            "missing_fields": ["options", "criteria"],
            "guidance": ["Provide a JSON object or plain-text decision brief."],
        }

    request: dict[str, Any] = {}
    if payload.get("policy_name"):
        request["policy_name"] = payload["policy_name"]
    else:
        request["policy_name"] = "balanced"
    if payload.get("context"):
        request["context"] = payload["context"]
    if payload.get("problem"):
        request["context"] = payload["problem"]

    missing: list[str] = []
    warnings: list[str] = []

    raw_options = payload.get("options", [])
    normalized_options = []
    for item in raw_options:
        option, error = _normalize_option(item)
        if error:
            warnings.append(error)
            continue
        normalized_options.append(option)
    request["options"] = normalized_options
    if not normalized_options:
        missing.append("options")

    raw_criteria = payload.get("criteria", [])
    normalized_criteria = []
    all_have_weights = True
    for item in raw_criteria:
        criterion, error = _normalize_criterion(item)
        if error:
            warnings.append(error)
            continue
        assert criterion is not None
        if "weight" not in criterion:
            all_have_weights = False
        normalized_criteria.append(criterion)
    request["criteria"] = normalized_criteria
    if not normalized_criteria:
        missing.append("criteria")
    elif not all_have_weights:
        missing.append("criterion weights")

    constraints = payload.get("constraints")
    if isinstance(constraints, list) and constraints:
        request["constraints"] = constraints

    preferences = payload.get("preferences")
    if isinstance(preferences, dict) and preferences:
        request["preferences"] = preferences

    if normalized_options and normalized_criteria:
        options_without_values = [
            option["name"] for option in normalized_options if not option.get("values")
        ]
        if options_without_values:
            missing.append("option criterion values")
            warnings.append(
                "The following options have no criterion values yet: "
                + ", ".join(options_without_values)
            )

    ready_to_run = not missing and not warnings
    return {
        "mode": "structured" if payload.get("options") or payload.get("criteria") else "freeform",
        "ready_to_run": ready_to_run,
        "request": request,
        "missing_fields": sorted(set(missing)),
        "warnings": warnings,
        "guidance": [
            "Use explicit numeric values for each option/criterion pair.",
            "Use benefit or cost direction for every criterion.",
            "Only run ADI after the request is complete and validated.",
        ],
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Normalize a plain-language decision brief or partial JSON object into an ADI request skeleton."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to a JSON file or '-' to read plain text / JSON from stdin.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        _source, payload = read_input_payload(args.input)
        normalized = build_request_skeleton(payload)
        write_json(normalized)
        return 0
    except Exception as exc:
        print(f"error: unexpected failure: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
