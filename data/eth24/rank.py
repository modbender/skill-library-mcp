#!/usr/bin/env python3
"""Rank top tweets and generate commentary using Claude or Grok."""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

import httpx

SCRIPT_DIR = Path(__file__).parent
CONFIG = json.loads((SCRIPT_DIR / "config.json").read_text())


def call_anthropic(prompt):
    """Call Anthropic Claude API."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    resp = httpx.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        },
        json={
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 3000,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=90,
    )
    resp.raise_for_status()
    data = resp.json()
    return "".join(
        b["text"] for b in data.get("content", []) if b.get("type") == "text"
    )


def call_xai(prompt):
    """Call xAI Grok API."""
    api_key = os.environ.get("XAI_API_KEY")
    if not api_key:
        return None
    resp = httpx.post(
        "https://api.x.ai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": "grok-3-mini-fast",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 3000,
            "temperature": 0.3,
        },
        timeout=90,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


PROVIDERS = {
    "anthropic": ("Anthropic", call_anthropic),
    "xai": ("xAI", call_xai),
}


def rank(crawl_data):
    """Rank tweets by ecosystem importance and generate commentary."""
    tweets = crawl_data.get("tweets", [])
    rss = crawl_data.get("rss", [])

    # Build context with actual tweet text and metrics
    parts = []
    for i, t in enumerate(tweets):
        parts.append(
            f"TWEET {i + 1}: @{t['handle']} ({t.get('author_name', '')})\n"
            f"URL: {t['url']}\n"
            f"Text: {t['text'][:500]}\n"
            f"Engagement: {t.get('likes', 0)} likes, "
            f"{t.get('retweets', 0)} RTs, "
            f"{t.get('replies', 0)} replies "
            f"(score: {t.get('engagement_score', 0):.0f})"
        )
    for a in rss:
        parts.append(
            f"RSS [{a['feed']}]: {a['title']} - {a.get('summary', '')[:300]}\n"
            f"{a.get('link', '')}"
        )

    context = "\n\n---\n\n".join(parts)
    today_label = datetime.now().strftime("%B %d, %Y")
    short_label = datetime.now().strftime("%-m/%d/%y")
    voice = CONFIG["rank"].get("voice", "Concise and informed.")
    brand = CONFIG.get("brand", {})
    max_tweets = CONFIG["crawl"].get("max_tweets", 10)

    prompt = f"""You are curating {brand.get('name', 'ETH24')}, a daily {CONFIG.get('topic', 'Ethereum')} digest for {brand.get('account', '@ethcforg')} on X.

Today is {today_label}. Below are the top Ethereum tweets from the last 24 hours (sorted by engagement) plus RSS context.

Select up to {max_tweets} tweets by ecosystem importance. Only include stories that are genuinely important. If it's a quiet day, include fewer. If nothing clears the bar, return 0 stories. Write one-line commentary for each selected story.

Voice: {voice}

Examples of good commentary:
- "Stripe just enabled AI-to-AI payments in USDC on Base. First major fintech going native on an Ethereum L2."
- "$0.10 per mainnet tx vs $25 round-trip to bridge to an L2. The cost comparison is getting hard to ignore."
- "$61K and a two-month wait to run a validator. $7.84B in the queue."
- "Vitalik commits $45M to Ethereum privacy projects. a16z and Barry Silbert also flagging privacy as a priority."

Rules:
- Commentary: 1-2 short sentences MAX. Tell the reader why this matters. Don't restate the tweet.
- Be accurate. Don't claim "first" or "biggest" unless you're certain. Stick to what the tweet actually says.
- NEVER use emojis or emdashes. Use hyphens (-) not emdashes.
- Keep the tweet_url exactly as provided. Do not modify URLs.
- Write "highlights": a comma-separated list of the day's biggest stories (used as a preview in the first tweet). Keep it under 200 characters.
- Use the RSS articles as background context for better commentary, but only select from the tweets.

Return ONLY valid JSON (no markdown fences, no extra text):
{{"stories":[{{"commentary":"One sentence.","tweet_url":"https://x.com/handle/status/ID","handle":"handle"}}],"highlights":"Story A, Story B, Story C","date_label":"{short_label}"}}

RAW DATA:
{context[:12000]}"""

    print("> Ranking with AI...", file=sys.stderr)

    order = CONFIG["rank"].get("ai_provider_order", ["anthropic", "xai"])
    text = None
    for key in order:
        entry = PROVIDERS.get(key)
        if not entry:
            continue
        name, fn = entry
        try:
            text = fn(prompt)
            if text:
                print(f"  Using {name}", file=sys.stderr)
                break
        except Exception as e:
            print(f"  {name} failed: {e}", file=sys.stderr)

    if not text:
        print("ERROR: No AI provider available", file=sys.stderr)
        sys.exit(1)

    # Parse JSON
    try:
        ranked = json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if m:
            ranked = json.loads(m.group())
        else:
            print(f"Failed to parse AI response:\n{text[:500]}", file=sys.stderr)
            sys.exit(1)

    return ranked


def main():
    today = datetime.now().strftime("%Y-%m-%d")
    crawled_path = SCRIPT_DIR / "output" / today / "crawled.json"

    if crawled_path.exists():
        crawl_data = json.loads(crawled_path.read_text())
    else:
        crawl_data = json.loads(sys.stdin.read())

    ranked = rank(crawl_data)

    out_dir = SCRIPT_DIR / "output" / today
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "ranked.json").write_text(
        json.dumps(ranked, indent=2, ensure_ascii=False)
    )
    print(f"> Saved to {out_dir / 'ranked.json'}", file=sys.stderr)
    print(json.dumps(ranked, ensure_ascii=False))


if __name__ == "__main__":
    main()
