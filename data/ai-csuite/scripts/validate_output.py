from __future__ import annotations

import argparse
from pathlib import Path

REQUIRED_MARKERS = [
    "**DATA BRIEF (Pre-Round):**",
    "**CEO BRIEF**",
    "**CEO DECISION**",
    "**DECISION:**",
    "**RATIONALE:**",
    "**WHAT I WEIGHED:**",
    "**OVERRIDES:**",
    "**NEXT STEPS:**",
    "**REVIEW TRIGGER:**",
    "**CONFIDENCE:**",
    "**REVERSIBILITY:**",
]


def validate(text: str) -> list[str]:
    issues: list[str] = []
    for marker in REQUIRED_MARKERS:
        if marker not in text:
            issues.append(f"missing marker: {marker}")
    if "**REVERSIBILITY:**" in text:
        valid = ["easily_reversible", "costly_to_reverse", "irreversible"]
        if not any(v in text for v in valid):
            issues.append("invalid reversibility value")
    if "runway" in text.lower() and "less than 6" in text.lower() and "severity" not in text.lower():
        issues.append("runway under 6 months mentioned without severity")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True)
    args = parser.parse_args()
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"FAIL: file not found: {file_path}")
        return 1
    text = file_path.read_text(encoding="utf-8")
    issues = validate(text)
    if issues:
        print("FAIL")
        for issue in issues:
            print(f"- {issue}")
        return 10
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
