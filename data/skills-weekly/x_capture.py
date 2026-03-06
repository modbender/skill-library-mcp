"""
x_capture.py — Automated X/Twitter signal capture for weekly report

Runs the x-search skill with OpenClaw-related queries, parses tweet URLs
from Grok's prose output, and uses a fast LLM to structure each signal
into the weekly_signals.json format.

Usage:
    python x_capture.py                          # Last 7 days
    python x_capture.py --from 2026-02-22 --to 2026-03-01
    python x_capture.py --dry-run                # Print signals, don't write
    python x_capture.py --append                 # Append to existing signals (default: overwrite)

Requires:
    - x-search skill at ~/.claude/skills/x-search/scripts/x_search.py
    - XAI_API_KEY in env or .env file
    - ANTHROPIC_API_KEY in .env (for LLM structuring step)
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

X_SEARCH_SCRIPT = os.getenv(
    "X_SEARCH_SCRIPT",
    str(Path.home() / ".claude/skills/x-search/scripts/x_search.py"),
)
SIGNALS_PATH = Path(__file__).parent / "data" / "weekly_signals.json"

QUERIES = [
    "openclaw skills trending",
    "clawhub skill",
    "openclaw custom skill",
]

CATEGORY_KEYWORDS = {
    "security": ["malicious", "vulnerability", "security", "malware", "trust", "verification", "supply chain"],
    "tutorial": ["tutorial", "guide", "how to", "walkthrough", "learn", "course", "beginner"],
    "showcase": ["demo", "built", "shipped", "launched", "introducing", "check out", "created"],
    "market": ["funding", "valuation", "market", "competitor", "chinese", "enterprise", "startup"],
    "ecosystem": ["integration", "plugin", "mcp", "multi-agent", "framework", "platform"],
}


def _run_x_search(query: str, date_from: str, date_to: str) -> str:
    """Run the x-search script and return stdout."""
    cmd = [
        sys.executable,
        X_SEARCH_SCRIPT,
        query,
        "--from", date_from,
        "--to", date_to,
        "--max-tokens", "4096",
    ]
    print(f"[X-CAPTURE] Running: {query} ({date_from} to {date_to})")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=90, encoding="utf-8", errors="replace")
        if result.returncode != 0:
            print(f"  [WARN] x-search returned code {result.returncode}")
            if result.stderr:
                print(f"  stderr: {result.stderr[:200]}")
        return result.stdout
    except subprocess.TimeoutExpired:
        print(f"  [WARN] x-search timed out for query: {query}")
        return ""
    except FileNotFoundError:
        print(f"  [ERROR] x-search script not found at {X_SEARCH_SCRIPT}")
        return ""


def _extract_tweet_urls(text: str) -> list[str]:
    """Extract unique tweet URLs from prose text."""
    urls = re.findall(r'https://(?:x\.com|twitter\.com)/\w+/status/\d+', text)
    seen = set()
    unique = []
    for url in urls:
        # Normalise to x.com
        url = url.replace("twitter.com", "x.com")
        if url not in seen:
            seen.add(url)
            unique.append(url)
    return unique


def _extract_handle_from_url(url: str) -> str:
    """Extract @handle from tweet URL."""
    match = re.search(r'x\.com/(\w+)/status/', url)
    return f"@{match.group(1)}" if match else ""


def _guess_category(text: str) -> str:
    """Guess signal category from surrounding text."""
    text_lower = text.lower()
    for cat, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            return cat
    return "discussion"


def _extract_context_around_url(text: str, url: str, chars: int = 300) -> str:
    """Extract the paragraph/context surrounding a tweet URL."""
    idx = text.find(url)
    if idx == -1:
        return ""
    start = max(0, idx - chars)
    end = min(len(text), idx + len(url) + chars)
    snippet = text[start:end].strip()
    # Try to start at a sentence boundary
    first_period = snippet.find(". ")
    if first_period > 0 and first_period < chars // 2:
        snippet = snippet[first_period + 2:]
    return snippet


def _structure_with_llm(raw_text: str, tweet_urls: list[str], api_key: str) -> list[dict]:
    """Use Haiku to structure the raw prose into signal entries."""
    if not api_key or not tweet_urls:
        return _structure_heuristic(raw_text, tweet_urls)

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
    except Exception:
        return _structure_heuristic(raw_text, tweet_urls)

    prompt = f"""Extract structured signals from this X/Twitter search summary about OpenClaw skills.

For each tweet URL below, create a JSON object with:
- "url": the tweet URL
- "title": a short descriptive title (5-10 words)
- "summary": one sentence describing what's notable about this thread
- "category": one of: tutorial, security, ecosystem, showcase, discussion, market
- "tags": 2-4 lowercase keyword tags

Tweet URLs found:
{chr(10).join(f'- {u}' for u in tweet_urls[:15])}

Full search output:
{raw_text[:6000]}

Return ONLY a JSON array of objects. No explanation."""

    try:
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )
        text = message.content[0].text.strip()
        # Extract JSON array from response
        match = re.search(r'\[.*\]', text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception as e:
        print(f"  [WARN] LLM structuring failed: {e}")

    return _structure_heuristic(raw_text, tweet_urls)


def _structure_heuristic(raw_text: str, tweet_urls: list[str]) -> list[dict]:
    """Fallback: build signals from heuristics when LLM unavailable."""
    signals = []
    for url in tweet_urls:
        handle = _extract_handle_from_url(url)
        context = _extract_context_around_url(raw_text, url)
        category = _guess_category(context)

        # Build title from first sentence of context
        first_sentence = context.split(". ")[0] if context else "OpenClaw discussion"
        if len(first_sentence) > 80:
            first_sentence = first_sentence[:77] + "..."

        signals.append({
            "url": url,
            "title": first_sentence,
            "summary": context[:200] if context else "",
            "category": category,
            "tags": ["openclaw"],
        })
    return signals


def capture(
    date_from: str = "",
    date_to: str = "",
    dry_run: bool = False,
    append: bool = False,
) -> list[dict]:
    """
    Run x-search queries, structure results, and optionally save to weekly_signals.json.

    Returns list of structured signal dicts.
    """
    now = datetime.now(timezone.utc)
    if not date_to:
        date_to = now.strftime("%Y-%m-%d")
    if not date_from:
        date_from = (now - timedelta(days=7)).strftime("%Y-%m-%d")

    print(f"[X-CAPTURE] Scanning X for OpenClaw signals: {date_from} to {date_to}")

    # Run all queries and collect raw output
    all_text = []
    all_urls = set()
    for query in QUERIES:
        output = _run_x_search(query, date_from, date_to)
        if output:
            all_text.append(output)
            urls = _extract_tweet_urls(output)
            print(f"  Found {len(urls)} tweet URLs for '{query}'")
            all_urls.update(urls)

    unique_urls = list(all_urls)
    print(f"[X-CAPTURE] Total unique tweet URLs: {len(unique_urls)}")

    if not unique_urls:
        print("[X-CAPTURE] No tweets found. Signals file unchanged.")
        return []

    # Structure using LLM or heuristics
    combined_text = "\n\n---\n\n".join(all_text)
    api_key = os.getenv("ANTHROPIC_API_KEY", "")

    if api_key:
        print("[X-CAPTURE] Structuring signals via LLM...")
        structured = _structure_with_llm(combined_text, unique_urls, api_key)
    else:
        print("[X-CAPTURE] No ANTHROPIC_API_KEY — using heuristic structuring")
        structured = _structure_heuristic(combined_text, unique_urls)

    # Build final signals
    signals = []
    seen_urls = set()
    for entry in structured:
        url = entry.get("url", "")
        if url in seen_urls:
            continue
        seen_urls.add(url)

        signals.append({
            "date": date_to,
            "category": entry.get("category", "discussion"),
            "title": entry.get("title", "OpenClaw discussion"),
            "url": url,
            "summary": entry.get("summary", ""),
            "tags": entry.get("tags", ["openclaw"]),
            "source": "x",
        })

    print(f"[X-CAPTURE] Structured {len(signals)} signals")

    if dry_run:
        print("\n[DRY RUN] Signals that would be saved:")
        for s in signals:
            print(f"  [{s['category']}] {s['title']}")
            print(f"    {s['url']}")
        return signals

    # Save to JSON
    SIGNALS_PATH.parent.mkdir(parents=True, exist_ok=True)
    existing = []
    if append and SIGNALS_PATH.exists():
        try:
            existing = json.loads(SIGNALS_PATH.read_text(encoding="utf-8"))
            existing_urls = {s.get("url") for s in existing}
            signals = [s for s in signals if s["url"] not in existing_urls]
            print(f"[X-CAPTURE] After dedup: {len(signals)} new signals to append")
        except (json.JSONDecodeError, OSError):
            existing = []

    final = existing + signals
    SIGNALS_PATH.write_text(json.dumps(final, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[X-CAPTURE] Saved {len(final)} total signals to {SIGNALS_PATH}")

    return signals


def main():
    parser = argparse.ArgumentParser(description="Capture X/Twitter OpenClaw signals")
    parser.add_argument("--from", dest="date_from", default="", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--to", dest="date_to", default="", help="End date (YYYY-MM-DD)")
    parser.add_argument("--dry-run", action="store_true", help="Print signals without saving")
    parser.add_argument("--append", action="store_true", help="Append to existing signals (default: overwrite)")
    args = parser.parse_args()

    capture(
        date_from=args.date_from,
        date_to=args.date_to,
        dry_run=args.dry_run,
        append=args.append,
    )


if __name__ == "__main__":
    main()
