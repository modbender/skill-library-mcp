#!/usr/bin/env python3
"""
AI Exposure Index — Composite Score Calculator

Usage:
    python calculate_scores.py --d1 4 --d2 5 --d3 3.5 --d4 4 --d5 2 --d6 1 --d7 5 --d8 2.5

Outputs the vulnerability score, adaptive capacity score, classification, and a summary.
"""

import argparse
import math
import json
import sys


def calculate_vulnerability(d1, d2, d4, d6, d7):
    """Weighted geometric mean of vulnerability dimensions."""
    log_sum = (
        0.08 * math.log(d1)
        + 0.18 * math.log(d2)
        + 0.16 * math.log(d4)
        + 0.03 * math.log(d6)
        + 0.17 * math.log(d7)
    )
    return math.exp(log_sum / 0.62)


def calculate_adaptive_capacity(d3, d5, d8):
    """Weighted average of capability dimensions, normalized to 1-5 scale."""
    return (d3 * 0.10 + d5 * 0.12 + d8 * 0.16) / 0.38


def classify(vulnerability, adaptive_capacity):
    """Classify into the 2x2 matrix."""
    high_vuln = vulnerability > 2.5
    high_adapt = adaptive_capacity >= 3.5

    if high_adapt and not high_vuln:
        return "AI FORTIFIED"
    elif high_adapt and high_vuln:
        return "AI TRANSFORMER"
    elif not high_adapt and not high_vuln:
        return "AI BYSTANDER"
    else:
        return "AI ENDANGERED"


def vulnerability_level(score):
    if score <= 2.0:
        return "Low"
    elif score <= 3.0:
        return "Moderate"
    elif score <= 4.0:
        return "High"
    else:
        return "Very High"


def capacity_level(score):
    if score <= 2.0:
        return "Low"
    elif score <= 3.0:
        return "Low-to-Moderate"
    elif score <= 3.5:
        return "Moderate"
    elif score <= 4.0:
        return "Moderate-to-High"
    else:
        return "High"


def borderline_check(vulnerability, adaptive_capacity):
    """Check if scores are near classification boundaries."""
    notes = []
    if abs(vulnerability - 2.5) < 0.3:
        notes.append(f"Vulnerability score ({vulnerability:.2f}) is borderline — near the 2.5 threshold")
    if abs(adaptive_capacity - 3.5) < 0.3:
        notes.append(f"Adaptive Capacity ({adaptive_capacity:.2f}) is borderline — near the 3.5 threshold")
    return notes


def main():
    parser = argparse.ArgumentParser(description="AI Exposure Index Composite Score Calculator")
    parser.add_argument("--d1", type=float, required=True, help="Dimension 1: Labor Automation Vulnerability (1-5)")
    parser.add_argument("--d2", type=float, required=True, help="Dimension 2: Revenue Model Disruption (1-5)")
    parser.add_argument("--d3", type=float, required=True, help="Dimension 3: AI Adoption Maturity (1-5, positive)")
    parser.add_argument("--d4", type=float, required=True, help="Dimension 4: Moat Durability (1-5, 5=weakest)")
    parser.add_argument("--d5", type=float, required=True, help="Dimension 5: Operational AI Leverage (1-5, positive)")
    parser.add_argument("--d6", type=float, required=True, help="Dimension 6: Regulatory Risk (1-5)")
    parser.add_argument("--d7", type=float, required=True, help="Dimension 7: Industry Transformation Velocity (1-5)")
    parser.add_argument("--d8", type=float, required=True, help="Dimension 8: Data & Ecosystem Strength (1-5, positive)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    # Validate scores
    for name, val in [("d1", args.d1), ("d2", args.d2), ("d3", args.d3), ("d4", args.d4),
                       ("d5", args.d5), ("d6", args.d6), ("d7", args.d7), ("d8", args.d8)]:
        if not (1 <= val <= 5):
            print(f"Error: {name} must be between 1 and 5, got {val}", file=sys.stderr)
            sys.exit(1)

    vuln = calculate_vulnerability(args.d1, args.d2, args.d4, args.d6, args.d7)
    adapt = calculate_adaptive_capacity(args.d3, args.d5, args.d8)
    classification = classify(vuln, adapt)
    borderline = borderline_check(vuln, adapt)

    result = {
        "dimensions": {
            "d1_labor_automation": args.d1,
            "d2_revenue_disruption": args.d2,
            "d3_ai_adoption": args.d3,
            "d4_moat_durability": args.d4,
            "d5_operational_leverage": args.d5,
            "d6_regulatory_risk": args.d6,
            "d7_industry_velocity": args.d7,
            "d8_data_ecosystem": args.d8,
        },
        "vulnerability_score": round(vuln, 2),
        "vulnerability_level": vulnerability_level(vuln),
        "adaptive_capacity_score": round(adapt, 2),
        "adaptive_capacity_level": capacity_level(adapt),
        "classification": classification,
        "borderline_notes": borderline,
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("=" * 60)
        print("AI EXPOSURE INDEX — COMPOSITE SCORES")
        print("=" * 60)
        print()
        print("Dimension Scores:")
        print(f"  D1 Labor Automation Vulnerability:  {args.d1}")
        print(f"  D2 Revenue Model Disruption:        {args.d2}")
        print(f"  D3 AI Adoption & Implementation ↑:  {args.d3}")
        print(f"  D4 Competitive Moat Durability:      {args.d4}")
        print(f"  D5 Operational AI Leverage ↑:        {args.d5}")
        print(f"  D6 Regulatory & Ethical Risk:         {args.d6}")
        print(f"  D7 Industry Transformation Velocity: {args.d7}")
        print(f"  D8 Data & Ecosystem Strength ↑:      {args.d8}")
        print()
        print(f"AI Vulnerability Score:      {vuln:.2f} ({vulnerability_level(vuln)})")
        print(f"AI Adaptive Capacity Score:  {adapt:.2f} ({capacity_level(adapt)})")
        print()
        print(f"Classification: *** {classification} ***")
        print()
        if borderline:
            print("Borderline Notes:")
            for note in borderline:
                print(f"  ⚠ {note}")
            print()
        print("=" * 60)


if __name__ == "__main__":
    main()
