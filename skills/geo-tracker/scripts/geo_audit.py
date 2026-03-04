#!/usr/bin/env python3
"""GEO Audit — Run batch audit across multiple prompts."""

import argparse
import json
import os
import sys
from datetime import datetime

# Import from geo_query
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geo_query import query_chatgpt, query_perplexity, query_gemini, query_claude, ENGINE_MAP, analyze_response, score_label


def load_prompts(path: str) -> list:
    with open(path, "r") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


def run_audit(brand: str, prompts: list, engines: list, competitors: list = None):
    print(f"\n🚀 Starting GEO Audit for: {brand}")
    print(f"   Prompts: {len(prompts)}")
    print(f"   Engines: {', '.join(engines)}")
    print(f"   Timestamp: {datetime.now().isoformat()}")
    print("=" * 60)

    all_results = []
    engine_scores = {eng: [] for eng in engines}
    engine_recommendations = {eng: 0 for eng in engines}

    for i, prompt in enumerate(prompts, 1):
        print(f"\n[{i}/{len(prompts)}] Query: \"{prompt}\"")

        # Query each engine for each brand
        for b in [brand] + (competitors or []):
            for eng in engines:
                fn = ENGINE_MAP.get(eng)
                if not fn:
                    continue
                try:
                    result = fn(prompt, b)
                    result["prompt"] = prompt
                    result["brand"] = b
                    all_results.append(result)

                    if "error" not in result:
                        engine_scores[eng].append(result["visibility_score"])
                        if result["is_recommended"]:
                            engine_recommendations[eng] += 1
                except Exception as e:
                    print(f"   ⚠️  {eng}/{b}: {e}")

    # Aggregate results
    print("\n" + "=" * 60)
    print("📊 AUDIT SUMMARY")
    print("=" * 60)

    print(f"\n🎯 Brand: {brand}")
    for eng in engines:
        scores = engine_scores[eng]
        if scores:
            avg = round(sum(scores) / len(scores))
            recs = engine_recommendations[eng]
            print(f"   {eng}: Avg Score {avg}/100 ({score_label(avg)}) | Recommended {recs}/{len(prompts)} times")
        else:
            print(f"   {eng}: No data")

    # Calculate overall score
    all_scores = [s for scores in engine_scores.values() for s in scores]
    if all_scores:
        overall = round(sum(all_scores) / len(all_scores))
        print(f"\n🏆 OVERALL VISIBILITY: {overall}/100 ({score_label(overall)})")

    # Top opportunities (prompts where brand scored poorly)
    print(f"\n📈 TOP OPTIMIZATION OPPORTUNITIES")
    brand_results = [r for r in all_results if r.get("brand") == brand and "error" not in r]
    low_score = sorted(brand_results, key=lambda x: x["visibility_score"])[:5]
    for r in low_score:
        print(f"   - \"{r['prompt']}\" → Score {r['visibility_score']}/100")

    return all_results


def main():
    parser = argparse.ArgumentParser(description="GEO Audit — Batch brand visibility check")
    parser.add_argument("--brand", required=True, help="Brand name")
    parser.add_argument("--prompts", required=True, help="Path to prompts file (one per line)")
    parser.add_argument("--engines", default="chatgpt,perplexity,gemini", help="Comma-separated engines")
    parser.add_argument("--competitors", default=None, help="Comma-separated competitors")
    parser.add_argument("--output", default=None, help="Output markdown report path")
    args = parser.parse_args()

    prompts = load_prompts(args.prompts)
    if not prompts:
        print("Error: No prompts loaded")
        sys.exit(1)

    engines = [e.strip() for e in args.engines.split(",")]
    competitors = [c.strip() for c in args.competitors.split(",")] if args.competitors else None

    results = run_audit(args.brand, prompts, engines, competitors)

    if args.output:
        report = f"""# GEO Audit Report: {args.brand}

Generated: {datetime.now().isoformat()}

## Summary

- **Brand:** {args.brand}
- **Prompts Audited:** {len(prompts)}
- **Engines:** {', '.join(engines)}
- **Competitors:** {', '.join(competitors) if competitors else 'None'}

## Results

{json.dumps(results, indent=2)}

## Recommendations

1. Focus on prompts with lowest visibility scores
2. Add brand to content in contexts where competitors are mentioned
3. Build authoritative content around high-volume search queries
"""
        with open(args.output, "w") as f:
            f.write(report)
        print(f"\n📄 Report saved to: {args.output}")


if __name__ == "__main__":
    main()
