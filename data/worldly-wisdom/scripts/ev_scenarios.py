#!/usr/bin/env python3
"""Expected value calculator for named scenarios.

Input JSON format:
{
  "unit": "GBP",
  "scenarios": [
    {"name": "Strong success", "probability": 0.2, "value": 250000},
    {"name": "Base case", "probability": 0.5, "value": 50000},
    {"name": "Bad miss", "probability": 0.3, "value": -80000}
  ]
}

Probabilities must be decimals that sum to 1.0.

Examples:
  python3 scripts/ev_scenarios.py --input assets/sample-ev-scenarios.json
  python3 scripts/ev_scenarios.py --input my-scenarios.json --format markdown
""" 
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


class InputError(ValueError):
    """Raised when the input file or arguments are invalid."""


def _coerce_number(value: object, label: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise InputError(f"Error: {label} must be numeric. Received: {value!r}") from exc


def load_input(path: Path) -> dict:
    if not path.exists():
        raise InputError(f"Error: input file not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise InputError(
            f"Error: input file is not valid JSON: {path} (line {exc.lineno}, column {exc.colno})"
        ) from exc
    if not isinstance(data, dict):
        raise InputError("Error: input JSON must be an object.")
    return data


def validate(data: dict) -> None:
    if "scenarios" not in data:
        raise InputError("Error: input JSON must contain 'scenarios'.")
    scenarios = data["scenarios"]
    if not isinstance(scenarios, list) or not scenarios:
        raise InputError("Error: 'scenarios' must be a non-empty list.")

    total_probability = 0.0
    for index, scenario in enumerate(scenarios, start=1):
        if not isinstance(scenario, dict):
            raise InputError(f"Error: scenario #{index} must be an object.")
        for key in ("name", "probability", "value"):
            if key not in scenario:
                raise InputError(f"Error: each scenario must include '{key}'.")
        probability = _coerce_number(scenario["probability"], f"probability for scenario #{index}")
        if probability < 0 or probability > 1:
            raise InputError(
                f"Error: scenario probabilities must be decimals between 0 and 1. Received: {probability!r} for {scenario['name']!r}"
            )
        _coerce_number(scenario["value"], f"value for scenario #{index}")
        total_probability += probability

    if abs(total_probability - 1.0) > 1e-6:
        raise InputError(
            f"Error: scenario probabilities must sum to 1.0. Received: {total_probability:.6f}."
        )


def expected_value(scenarios: list[dict]) -> float:
    return sum(float(s["probability"]) * float(s["value"]) for s in scenarios)


def compute(data: dict) -> dict:
    scenarios = data["scenarios"]
    contributions = []
    for scenario in scenarios:
        probability = float(scenario["probability"])
        value = float(scenario["value"])
        contributions.append(
            {
                "name": str(scenario["name"]),
                "probability": probability,
                "value": value,
                "contribution": probability * value,
            }
        )

    ev = expected_value(scenarios)
    downside_probability = sum(item["probability"] for item in contributions if item["value"] < 0)
    upside_probability = sum(item["probability"] for item in contributions if item["value"] > 0)
    worst_case = min(item["value"] for item in contributions)
    best_case = max(item["value"] for item in contributions)

    return {
        "unit": str(data.get("unit", "")),
        "expected_value": ev,
        "upside_probability": upside_probability,
        "downside_probability": downside_probability,
        "best_case": best_case,
        "worst_case": worst_case,
        "scenarios": contributions,
        "note": "Expected value is one lens. Pair it with reversibility, variance, leverage, and competence before deciding.",
    }


def render_markdown(result: dict) -> str:
    unit = result.get("unit", "")
    prefix = f"{unit} " if unit else ""
    lines = []
    lines.append("# Scenario Expected Value")
    lines.append("")
    lines.append("| Scenario | Probability | Value | Contribution |")
    lines.append("|---|---:|---:|---:|")
    for scenario in result["scenarios"]:
        lines.append(
            f"| {scenario['name']} | {scenario['probability']:.2%} | {prefix}{scenario['value']:,.2f} | {prefix}{scenario['contribution']:,.2f} |"
        )
    lines.append("")
    lines.append(f"- Expected value: {prefix}{result['expected_value']:,.2f}")
    lines.append(f"- Upside probability: {result['upside_probability']:.2%}")
    lines.append(f"- Downside probability: {result['downside_probability']:.2%}")
    lines.append(f"- Best case: {prefix}{result['best_case']:,.2f}")
    lines.append(f"- Worst case: {prefix}{result['worst_case']:,.2f}")
    lines.append("")
    lines.append(result["note"])
    return "\n".join(lines)


def write_output(text: str, output_path: str | None) -> None:
    if output_path:
        Path(output_path).write_text(text + ("" if text.endswith("\n") else "\n"), encoding="utf-8")
    else:
        sys.stdout.write(text)
        if not text.endswith("\n"):
            sys.stdout.write("\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Calculate expected value across named scenarios.",
        epilog=(
            "Examples:\n"
            "  python3 scripts/ev_scenarios.py --input assets/sample-ev-scenarios.json\n"
            "  python3 scripts/ev_scenarios.py --input my-scenarios.json --format markdown"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--input", required=True, help="Path to the input JSON file.")
    parser.add_argument(
        "--format",
        default="json",
        choices=["json", "markdown"],
        help="Output format. Defaults to json for machine-readable output.",
    )
    parser.add_argument("--output", help="Write output to this file instead of stdout.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        data = load_input(Path(args.input))
        validate(data)
        result = compute(data)
        if args.format == "json":
            rendered = json.dumps(result, indent=2, sort_keys=True)
        else:
            rendered = render_markdown(result)
        write_output(rendered, args.output)
        return 0
    except InputError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except Exception as exc:  # pragma: no cover - defensive fallback
        print(f"Error: unexpected failure: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
