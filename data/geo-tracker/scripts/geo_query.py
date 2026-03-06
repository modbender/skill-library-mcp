#!/usr/bin/env python3
"""GEO Query — Check brand visibility across AI search engines."""

import argparse
import json
import os
import re
import sys
from datetime import datetime

try:
    import openai
except ImportError:
    openai = None

try:
    import anthropic
except ImportError:
    anthropic = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None


def query_chatgpt(prompt: str, brand: str) -> dict:
    if not openai:
        return {"engine": "chatgpt", "error": "openai package not installed"}
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        return {"engine": "chatgpt", "error": "OPENAI_API_KEY not set"}
    client = openai.OpenAI(api_key=key)
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024,
    )
    text = resp.choices[0].message.content or ""
    return analyze_response("chatgpt", text, brand)


def query_perplexity(prompt: str, brand: str) -> dict:
    key = os.environ.get("PERPLEXITY_API_KEY")
    if not key:
        return {"engine": "perplexity", "error": "PERPLEXITY_API_KEY not set"}
    import urllib.request
    data = json.dumps({
        "model": "sonar",
        "messages": [{"role": "user", "content": prompt}],
    }).encode()
    req = urllib.request.Request(
        "https://api.perplexity.ai/chat/completions",
        data=data,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        body = json.loads(r.read())
    text = body["choices"][0]["message"]["content"]
    return analyze_response("perplexity", text, brand)


def query_gemini(prompt: str, brand: str) -> dict:
    if not genai:
        return {"engine": "gemini", "error": "google-generativeai package not installed"}
    key = os.environ.get("GOOGLE_API_KEY")
    if not key:
        return {"engine": "gemini", "error": "GOOGLE_API_KEY not set"}
    genai.configure(api_key=key)
    model = genai.GenerativeModel("gemini-2.0-flash")
    resp = model.generate_content(prompt)
    text = resp.text or ""
    return analyze_response("gemini", text, brand)


def query_claude(prompt: str, brand: str) -> dict:
    if not anthropic:
        return {"engine": "claude", "error": "anthropic package not installed"}
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return {"engine": "claude", "error": "ANTHROPIC_API_KEY not set"}
    client = anthropic.Anthropic(api_key=key)
    resp = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    text = resp.content[0].text if resp.content else ""
    return analyze_response("claude", text, brand)


ENGINE_MAP = {
    "chatgpt": query_chatgpt,
    "perplexity": query_perplexity,
    "gemini": query_gemini,
    "claude": query_claude,
}


def analyze_response(engine: str, text: str, brand: str) -> dict:
    brand_lower = brand.lower()
    text_lower = text.lower()
    # Count mentions
    mentions = len(re.findall(re.escape(brand_lower), text_lower))
    # Check if recommended (appears in top portion or with positive framing)
    first_mention_pos = text_lower.find(brand_lower)
    is_recommended = False
    if first_mention_pos >= 0:
        # Check surrounding context for recommendation signals
        window = text_lower[max(0, first_mention_pos - 100):first_mention_pos + len(brand_lower) + 100]
        rec_signals = ["recommend", "best", "top", "leading", "popular", "great", "excellent", "#1", "first choice"]
        is_recommended = any(s in window for s in rec_signals)
    # Position score: earlier mention = higher score
    if mentions == 0:
        position_score = 0
    elif first_mention_pos < len(text) * 0.2:
        position_score = 100
    elif first_mention_pos < len(text) * 0.5:
        position_score = 60
    else:
        position_score = 30
    # Visibility score
    visibility = min(100, (mentions * 20) + position_score * 0.5 + (30 if is_recommended else 0))
    return {
        "engine": engine,
        "mentions": mentions,
        "first_mention_position": first_mention_pos if first_mention_pos >= 0 else None,
        "is_recommended": is_recommended,
        "visibility_score": round(visibility),
        "response_length": len(text),
        "snippet": text[:500],
    }


def score_label(score: int) -> str:
    if score <= 20: return "Invisible"
    if score <= 40: return "Low"
    if score <= 60: return "Moderate"
    if score <= 80: return "Strong"
    return "Dominant"


def run_query(brand: str, query: str, engines: list, competitors: list = None):
    print(f"\n🔍 GEO Query: \"{query}\"")
    print(f"   Brand: {brand}")
    if competitors:
        print(f"   Competitors: {', '.join(competitors)}")
    print(f"   Engines: {', '.join(engines)}")
    print("=" * 60)

    all_brands = [brand] + (competitors or [])
    results = {}

    for b in all_brands:
        results[b] = []
        for eng in engines:
            fn = ENGINE_MAP.get(eng)
            if not fn:
                print(f"   ⚠️  Unknown engine: {eng}")
                continue
            print(f"   Querying {eng} for '{b}'...")
            try:
                result = fn(query, b)
                results[b].append(result)
            except Exception as e:
                results[b].append({"engine": eng, "error": str(e)})

    # Print results
    print("\n" + "=" * 60)
    print("📊 RESULTS")
    print("=" * 60)

    for b in all_brands:
        marker = "🎯" if b == brand else "⚔️"
        print(f"\n{marker} {b}")
        for r in results[b]:
            if "error" in r:
                print(f"   {r['engine']}: ❌ {r['error']}")
            else:
                label = score_label(r["visibility_score"])
                rec = " ⭐ RECOMMENDED" if r["is_recommended"] else ""
                print(f"   {r['engine']}: Score {r['visibility_score']}/100 ({label}) | Mentions: {r['mentions']}{rec}")

    # Overall score for primary brand
    brand_results = [r for r in results[brand] if "error" not in r]
    if brand_results:
        avg = round(sum(r["visibility_score"] for r in brand_results) / len(brand_results))
        print(f"\n{'=' * 60}")
        print(f"🏆 Overall Visibility Score for {brand}: {avg}/100 ({score_label(avg)})")

    return results


def main():
    parser = argparse.ArgumentParser(description="GEO Query — Check brand visibility in AI engines")
    parser.add_argument("--brand", required=True, help="Brand name to track")
    parser.add_argument("--query", required=True, help="Search query to send to AI engines")
    parser.add_argument("--engines", default="chatgpt,perplexity,gemini,claude",
                        help="Comma-separated engines (chatgpt,perplexity,gemini,claude)")
    parser.add_argument("--competitors", default=None, help="Comma-separated competitor names")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    engines = [e.strip() for e in args.engines.split(",")]
    competitors = [c.strip() for c in args.competitors.split(",")] if args.competitors else None

    results = run_query(args.brand, args.query, engines, competitors)

    if args.json:
        print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
