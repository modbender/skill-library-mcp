#!/usr/bin/env python3
"""
quality-score.py — Parse a skill rubric audit markdown file and compute quality scores.

Usage:
    python3 scripts/quality-score.py audits/{skill}-rubric.md
    python3 scripts/quality-score.py audits/{skill}-rubric.md --pretty

Output (JSON to stdout):
    {
        "skill": "skill-engineer",
        "total": 72,
        "max": 90,
        "percentage": 80.0,
        "rating": "Deploy",
        "sections": {
            "SQ-A": {"score": 19, "max": 24, "percentage": 79.2},
            ...
        },
        "criteria": [
            {"id": "A1", "score": 3, "evidence": "..."},
            ...
        ]
    }

Rubric file format expected:
    | A1 | criterion | **N** | evidence |
    where N is the integer score (0–3).

Section totals are auto-detected from headings like "SQ-A", "SQ-B", "SQ-C", "SQ-D", "AS".
"""

import re
import sys
import json
import os

# ---------------------------------------------------------------------------
# Scoring thresholds (as percentages)
# ---------------------------------------------------------------------------
RATING_THRESHOLDS = [
    (80.0, "Deploy"),
    (60.0, "Revise"),
    (40.0, "Redesign"),
    (0.0,  "Reject"),
]

# ---------------------------------------------------------------------------
# Section heading patterns
# ---------------------------------------------------------------------------
SECTION_PATTERNS = [
    (re.compile(r"##\s+SQ-A", re.IGNORECASE), "SQ-A"),
    (re.compile(r"##\s+SQ-B", re.IGNORECASE), "SQ-B"),
    (re.compile(r"##\s+SQ-C", re.IGNORECASE), "SQ-C"),
    (re.compile(r"##\s+SQ-D", re.IGNORECASE), "SQ-D"),
    (re.compile(r"##\s+AS[:\s]", re.IGNORECASE), "AS"),
    (re.compile(r"##\s+AS$", re.IGNORECASE), "AS"),
]

# Criterion ID patterns: A1–A9, B1–B9, C1–C9, D1–D9, AS-1–AS-9
CRITERION_PATTERN = re.compile(
    r"^\|\s*([A-D]\d+|AS-?\d+)\s*\|[^|]*\|\s*\*\*(\d+)\*\*\s*\|([^|]*)\|?",
    re.IGNORECASE
)

# Grand total pattern: | **TOTAL** | **N** | max |  or similar
TOTAL_PATTERNS = [
    re.compile(r"\|\s*\*\*TOTAL\*\*\s*\|\s*\*\*(\d+)\*\*", re.IGNORECASE),
    re.compile(r"\|\s*TOTAL\s*\|\s*(\d+)\s*\|", re.IGNORECASE),
    re.compile(r"Score:\s*(\d+)/(\d+)"),
]

# Section total patterns: | SQ-A Total | N / M | or **SQ-A Total: N / M**
SECTION_TOTAL_PATTERN = re.compile(
    r"(?:SQ-([A-D])|AS)\s+Total[:\s]*(\d+)\s*/\s*(\d+)",
    re.IGNORECASE
)


def extract_skill_name(path: str) -> str:
    """Derive skill name from file path."""
    basename = os.path.basename(path)
    # Try {skill}-rubric.md pattern
    m = re.match(r"(.+?)-rubric\.md$", basename, re.IGNORECASE)
    if m:
        return m.group(1)
    return re.sub(r"\.md$", "", basename, flags=re.IGNORECASE)


def parse_rubric(path: str) -> dict:
    """Parse a rubric markdown file and return structured quality data."""
    with open(path, "r", encoding="utf-8") as fh:
        lines = fh.readlines()

    skill_name = extract_skill_name(path)
    current_section = "unknown"
    criteria = []
    sections_criteria: dict[str, list] = {}

    for line in lines:
        # Detect section headings
        for pattern, section_name in SECTION_PATTERNS:
            if pattern.search(line):
                current_section = section_name
                break

        # Detect criteria rows
        m = CRITERION_PATTERN.match(line.strip())
        if m:
            crit_id = m.group(1).upper().replace("AS-", "AS-")
            score = int(m.group(2))
            evidence = m.group(3).strip()
            entry = {"id": crit_id, "section": current_section, "score": score, "evidence": evidence}
            criteria.append(entry)
            sections_criteria.setdefault(current_section, []).append(entry)

    # Build section summaries
    sections: dict[str, dict] = {}
    for sec, crits in sections_criteria.items():
        sec_score = sum(c["score"] for c in crits)
        # Max per criterion is 3
        sec_max = len(crits) * 3
        sections[sec] = {
            "score": sec_score,
            "max": sec_max,
            "count": len(crits),
            "percentage": round(100.0 * sec_score / sec_max, 1) if sec_max else 0.0,
        }

    # Compute totals from parsed criteria
    total_score = sum(c["score"] for c in criteria)
    total_max = len(criteria) * 3

    # Try to find declared max in file (e.g., "Max score: 90")
    declared_max = None
    declared_total = None
    for line in lines:
        m = re.search(r"\*\*Max score[:\s*]+(\d+)", line, re.IGNORECASE)
        if m:
            declared_max = int(m.group(1))
        m2 = re.search(r"Score:\s*(\d+)/(\d+)", line, re.IGNORECASE)
        if m2:
            declared_total = int(m2.group(1))
            if not declared_max:
                declared_max = int(m2.group(2))

    # Use declared max if available and criteria parse looks low (subsets of tables may be parsed)
    effective_max = declared_max if declared_max else total_max
    effective_total = total_score

    percentage = round(100.0 * effective_total / effective_max, 1) if effective_max else 0.0

    # Determine rating
    rating = "Reject"
    for threshold, label in RATING_THRESHOLDS:
        if percentage >= threshold:
            rating = label
            break

    # Warn if parsed total diverges significantly from declared total
    warnings = []
    if declared_total is not None and abs(declared_total - total_score) > 2:
        warnings.append(
            f"Parsed total ({total_score}) differs from declared total ({declared_total}). "
            f"Check rubric table formatting."
        )

    result = {
        "skill": skill_name,
        "total": effective_total,
        "max": effective_max,
        "percentage": percentage,
        "rating": rating,
        "criteria_count": len(criteria),
        "sections": sections,
        "criteria": criteria,
    }
    if warnings:
        result["warnings"] = warnings
    if declared_total is not None:
        result["declared_total"] = declared_total

    return result


def rating_emoji(rating: str) -> str:
    return {"Deploy": "✅", "Revise": "🔄", "Redesign": "⚠️", "Reject": "❌"}.get(rating, "?")


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    pretty = "--pretty" in args
    paths = [a for a in args if not a.startswith("--")]

    if not paths:
        print("ERROR: No rubric file specified.", file=sys.stderr)
        sys.exit(1)

    results = []
    for path in paths:
        if not os.path.isfile(path):
            print(f"ERROR: File not found: {path}", file=sys.stderr)
            sys.exit(1)
        results.append(parse_rubric(path))

    output = results[0] if len(results) == 1 else results

    if pretty:
        # Human-readable summary to stderr, JSON to stdout
        r = results[0] if len(results) == 1 else results[0]
        print(f"\n{'='*50}", file=sys.stderr)
        print(f"  Skill: {r['skill']}", file=sys.stderr)
        print(f"  Score: {r['total']}/{r['max']} ({r['percentage']}%)", file=sys.stderr)
        print(f"  Rating: {rating_emoji(r['rating'])} {r['rating']}", file=sys.stderr)
        print(f"  Criteria parsed: {r['criteria_count']}", file=sys.stderr)
        print(f"\n  Sections:", file=sys.stderr)
        for sec, data in r["sections"].items():
            bar_filled = int(data["percentage"] / 5)
            bar = "█" * bar_filled + "░" * (20 - bar_filled)
            print(f"    {sec:6s}  {data['score']:3d}/{data['max']:3d}  [{bar}] {data['percentage']}%", file=sys.stderr)
        if "warnings" in r:
            print(f"\n  ⚠ Warnings:", file=sys.stderr)
            for w in r["warnings"]:
                print(f"    - {w}", file=sys.stderr)
        print(f"{'='*50}\n", file=sys.stderr)

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
