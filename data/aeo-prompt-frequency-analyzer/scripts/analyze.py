#!/usr/bin/env python3
"""
Prompt Frequency Analyzer — Run a prompt N times against Gemini with Google Search
grounding and report search query frequencies.

Usage:
    python3 analyze.py "your prompt here" [--runs 10] [--model gemini-2.5-pro] [--concurrency 5] [--output json|text]

Requires: GEMINI_API_KEY env var
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed


def call_gemini(prompt: str, api_key: str, model: str) -> dict:
    """Call Gemini API with Google Search grounding. Returns parsed JSON response."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "tools": [{"google_search": {}}],
    }).encode()
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                return json.loads(resp.read())
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            if attempt < 2:
                time.sleep(2 ** attempt)
            else:
                return {"error": str(e)}


def extract_queries(response: dict) -> list[str]:
    """Extract web search queries from Gemini grounding metadata."""
    queries = []
    for cand in response.get("candidates", []):
        meta = cand.get("groundingMetadata", {})
        queries.extend(meta.get("webSearchQueries", []))
    return queries


def extract_sources(response: dict) -> list[dict]:
    """Extract grounding source URLs from Gemini response."""
    sources = []
    seen = set()
    for cand in response.get("candidates", []):
        meta = cand.get("groundingMetadata", {})
        for chunk in meta.get("groundingChunks", []):
            web = chunk.get("web", {})
            uri = web.get("uri", "")
            title = web.get("title", "")
            if uri and uri not in seen:
                seen.add(uri)
                sources.append({"title": title, "uri": uri})
    return sources


def run_analysis(prompt: str, runs: int, model: str, concurrency: int):
    """Run prompt N times and collect search query data."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable required", file=sys.stderr)
        sys.exit(1)

    all_run_queries = []  # list of lists
    all_sources = []
    errors = 0

    print(f"Running '{prompt}' x{runs} against {model}...", file=sys.stderr)

    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = {pool.submit(call_gemini, prompt, api_key, model): i for i in range(runs)}
        for future in as_completed(futures):
            run_idx = futures[future]
            try:
                resp = future.result()
                if "error" in resp:
                    errors += 1
                    print(f"  Run {run_idx + 1}: ERROR - {resp['error']}", file=sys.stderr)
                    continue
                queries = extract_queries(resp)
                sources = extract_sources(resp)
                all_run_queries.append(queries)
                all_sources.extend(sources)
                print(f"  Run {run_idx + 1}: {len(queries)} queries", file=sys.stderr)
            except Exception as e:
                errors += 1
                print(f"  Run {run_idx + 1}: EXCEPTION - {e}", file=sys.stderr)

    successful_runs = len(all_run_queries)

    # Exact frequency: how many runs included each query
    query_run_count = defaultdict(int)
    for run_queries in all_run_queries:
        seen_in_run = set()
        for q in run_queries:
            ql = q.strip().lower()
            if ql not in seen_in_run:
                query_run_count[ql] += 1
                seen_in_run.add(ql)

    # Sort by frequency desc
    sorted_queries = sorted(query_run_count.items(), key=lambda x: (-x[1], x[0]))

    # Source frequency
    source_count = defaultdict(int)
    for s in all_sources:
        # Extract domain from title (which is usually the domain in Gemini grounding)
        domain = s.get("title", s.get("uri", ""))
        source_count[domain] += 1
    sorted_sources = sorted(source_count.items(), key=lambda x: (-x[1], x[0]))

    return {
        "prompt": prompt,
        "model": model,
        "total_runs": runs,
        "successful_runs": successful_runs,
        "errors": errors,
        "unique_queries": len(sorted_queries),
        "queries": [
            {
                "query": q,
                "count": c,
                "frequency": round(c / successful_runs * 100) if successful_runs else 0,
            }
            for q, c in sorted_queries
        ],
        "sources": [
            {"domain": d, "count": c}
            for d, c in sorted_sources[:20]
        ],
    }


def format_text(result: dict) -> str:
    lines = []
    lines.append(f"Prompt: \"{result['prompt']}\"")
    lines.append(f"Model: {result['model']}")
    lines.append(f"Runs: {result['successful_runs']}/{result['total_runs']} successful")
    lines.append(f"Unique queries: {result['unique_queries']}")
    lines.append("")
    lines.append("Search Query Frequency:")
    lines.append("=" * 60)
    for q in result["queries"]:
        lines.append(f"  {q['frequency']}% ({q['count']}/{result['successful_runs']}) — {q['query']}")
    if result["sources"]:
        lines.append("")
        lines.append("Top Sources Referenced:")
        lines.append("=" * 60)
        for s in result["sources"]:
            lines.append(f"  {s['count']}x — {s['domain']}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Analyze Gemini search query frequency for a prompt")
    parser.add_argument("prompt", help="The prompt to analyze")
    parser.add_argument("--runs", type=int, default=10, help="Number of runs (default: 10)")
    parser.add_argument("--model", default="gemini-2.5-pro", help="Gemini model (default: gemini-2.5-pro)")
    parser.add_argument("--concurrency", type=int, default=5, help="Max concurrent requests (default: 5)")
    parser.add_argument("--output", choices=["json", "text"], default="text", help="Output format")
    args = parser.parse_args()

    result = run_analysis(args.prompt, args.runs, args.model, args.concurrency)

    if args.output == "json":
        print(json.dumps(result, indent=2))
    else:
        print(format_text(result))


if __name__ == "__main__":
    main()
