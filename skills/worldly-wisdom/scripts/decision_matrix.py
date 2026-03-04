#!/usr/bin/env python3
"""Weighted decision matrix with criterion-by-criterion normalisation.

Input JSON format:
{
  "weights": {"criterion": 0.4, "other": 0.6},
  "direction": {"criterion": "higher", "other": "lower"},
  "options": [
    {"name": "Option A", "scores": {"criterion": 7, "other": 2}},
    {"name": "Option B", "scores": {"criterion": 5, "other": 4}}
  ]
}

Examples:
  python3 scripts/decision_matrix.py --input assets/sample-decision-matrix.json
  python3 scripts/decision_matrix.py --input my-matrix.json --format markdown
""" 
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Iterable, List


class InputError(ValueError):
    """Raised when the input file or arguments are invalid."""


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


def _coerce_number(value: object, label: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise InputError(f"Error: {label} must be numeric. Received: {value!r}") from exc


def validate(data: dict) -> None:
    if "weights" not in data or "options" not in data:
        raise InputError("Error: input JSON must contain 'weights' and 'options'.")

    weights = data["weights"]
    options = data["options"]
    direction = data.get("direction", {})

    if not isinstance(weights, dict) or not weights:
        raise InputError("Error: 'weights' must be a non-empty object.")
    if not isinstance(options, list) or len(options) < 2:
        raise InputError("Error: 'options' must contain at least two options.")
    if not isinstance(direction, dict):
        raise InputError("Error: 'direction' must be an object if provided.")

    criteria = list(weights.keys())
    names: set[str] = set()
    weight_total = 0.0
    for criterion in criteria:
        weight_total += _coerce_number(weights[criterion], f"weight for '{criterion}'")
        if criterion in direction and direction[criterion] not in {"higher", "lower"}:
            raise InputError(
                f"Error: direction for '{criterion}' must be 'higher' or 'lower'. Received: {direction[criterion]!r}"
            )
    if weight_total <= 0:
        raise InputError("Error: weights must sum to a positive number.")

    criteria_set = set(criteria)
    for index, option in enumerate(options, start=1):
        if not isinstance(option, dict):
            raise InputError(f"Error: option #{index} must be an object.")
        if "name" not in option or "scores" not in option:
            raise InputError("Error: each option must contain 'name' and 'scores'.")
        name = str(option["name"])
        if name in names:
            raise InputError(f"Error: option names must be unique. Duplicate: {name!r}")
        names.add(name)
        scores = option["scores"]
        if not isinstance(scores, dict):
            raise InputError(f"Error: scores for option {name!r} must be an object.")
        missing = criteria_set - set(scores.keys())
        extra = set(scores.keys()) - criteria_set
        if missing:
            raise InputError(
                f"Error: option {name!r} is missing criteria: {sorted(missing)}"
            )
        if extra:
            raise InputError(
                f"Error: option {name!r} has unexpected criteria not present in weights: {sorted(extra)}"
            )
        for criterion in criteria:
            _coerce_number(scores[criterion], f"score for option {name!r}, criterion '{criterion}'")


def normalise_weights(weights: Dict[str, float]) -> Dict[str, float]:
    total = sum(float(v) for v in weights.values())
    return {k: float(v) / total for k, v in weights.items()}


def criterion_values(options: Iterable[dict], criterion: str) -> List[float]:
    return [float(option["scores"][criterion]) for option in options]


def normalised_score(value: float, values: List[float], direction: str) -> float:
    low = min(values)
    high = max(values)
    if high == low:
        return 0.5
    if direction == "lower":
        return (high - value) / (high - low)
    return (value - low) / (high - low)


def compute(data: dict) -> dict:
    weights = normalise_weights(data["weights"])
    direction = data.get("direction", {})
    options = data["options"]
    criteria = list(weights.keys())
    value_map = {criterion: criterion_values(options, criterion) for criterion in criteria}

    ranking = []
    for option in options:
        contributions = {}
        total = 0.0
        for criterion in criteria:
            norm = normalised_score(
                float(option["scores"][criterion]),
                value_map[criterion],
                direction.get(criterion, "higher"),
            )
            contribution = weights[criterion] * norm
            contributions[criterion] = {
                "raw": float(option["scores"][criterion]),
                "normalised": norm,
                "weighted_contribution": contribution,
            }
            total += contribution
        ranking.append(
            {
                "name": str(option["name"]),
                "total": total,
                "contributions": contributions,
            }
        )

    ranking.sort(key=lambda row: row["total"], reverse=True)
    top_gap = None
    if len(ranking) >= 2:
        top_gap = ranking[0]["total"] - ranking[1]["total"]

    return {
        "weights_normalized": weights,
        "direction": {criterion: direction.get(criterion, "higher") for criterion in criteria},
        "ranking": ranking,
        "top_gap": top_gap,
        "note": "The matrix is a thinking aid. If the ranking conflicts with common sense, inspect the weights, criteria, and score ranges.",
    }


def render_markdown(result: dict) -> str:
    lines = []
    lines.append("# Decision Matrix Results")
    lines.append("")
    lines.append("## Ranking")
    lines.append("")
    lines.append("| Rank | Option | Weighted score |")
    lines.append("|---|---|---:|")
    for idx, row in enumerate(result["ranking"], start=1):
        lines.append(f"| {idx} | {row['name']} | {row['total']:.3f} |")
    lines.append("")
    lines.append("## Criteria weights")
    lines.append("")
    for criterion, weight in result["weights_normalized"].items():
        direction = result["direction"].get(criterion, "higher")
        lines.append(f"- {criterion}: {weight:.2%} ({direction} is better)")
    lines.append("")
    lines.append("## Detail by option")
    lines.append("")
    for row in result["ranking"]:
        lines.append(f"### {row['name']}")
        for criterion, detail in row["contributions"].items():
            lines.append(
                f"- {criterion}: raw={detail['raw']}, normalised={detail['normalised']:.3f}, weighted contribution={detail['weighted_contribution']:.3f}"
            )
        lines.append(f"- total: {row['total']:.3f}")
        lines.append("")
    if result["top_gap"] is not None:
        lines.append(f"Top-gap between first and second place: {result['top_gap']:.3f}")
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
        description="Run a weighted decision matrix from JSON input.",
        epilog=(
            "Examples:\n"
            "  python3 scripts/decision_matrix.py --input assets/sample-decision-matrix.json\n"
            "  python3 scripts/decision_matrix.py --input my-matrix.json --format markdown"
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
