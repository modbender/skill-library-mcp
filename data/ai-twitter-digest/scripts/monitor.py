#!/usr/bin/env python3
"""
AI Twitter Digest — OpenClaw Skill
Fetches tweets from AI/tech influencers, summarizes with available LLM, posts to a chat channel.

Configuration (environment variables or .env file next to this script):
  Required:
    AISA_API_KEY          - AISA API key (aisa.one)
    DELIVERY_CHANNEL      - Channel to post to: discord | whatsapp | telegram | slack | ...
    DELIVERY_TARGET       - Channel-specific target (see below)

  DELIVERY_TARGET format per channel:
    discord               - channel:<channel_id>   e.g. channel:1234567890
    whatsapp              - phone number in E.164   e.g. +1234567890
                            or group:<group_id>
    telegram              - @username, chat_id, or group:<group_id>
    slack                 - #channel-name or channel:<channel_id>

  LLM (at least one required, tried in order):
    ANTHROPIC_API_KEY     - Claude API key
    OPENAI_API_KEY        - OpenAI API key
    GEMINI_API_KEY        - Google Gemini API key

  Optional:
    STATE_FILE            - Path to dedup state file (default: ~/.ai-twitter-sent.json)
    MAX_STORED_IDS        - Max tweet IDs to remember (default: 500)
    CARD_PREVIEWS         - Show link card previews (true/false, default: true)
                            Note: only supported on Discord; auto-disabled on other channels
    SUMMARY_LANGUAGE      - Language for the digest (default: Chinese)
                            Examples: Chinese, English, Japanese, Spanish, French, German, Korean
"""

import os
import json
import subprocess
import re
from datetime import datetime, timezone
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────

def load_env():
    """Load .env file from same directory as this script (if present)."""
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

load_env()

def require_env(key):
    val = os.environ.get(key, "").strip()
    if not val:
        raise SystemExit(f"❌ Missing required env var: {key}\n"
                         f"   Set it in your environment or create a .env file next to monitor.py")
    return val

AISA_API_KEY       = require_env("AISA_API_KEY")
DELIVERY_CHANNEL   = require_env("DELIVERY_CHANNEL")   # discord | whatsapp | telegram | slack | ...
DELIVERY_TARGET    = require_env("DELIVERY_TARGET")    # channel-specific target string
STATE_FILE         = os.environ.get("STATE_FILE",
                         str(Path.home() / ".ai-twitter-sent.json"))
MAX_STORED_IDS     = int(os.environ.get("MAX_STORED_IDS", "500"))
# Card previews only make sense on Discord (inline link embeds)
CARD_PREVIEWS      = os.environ.get("CARD_PREVIEWS", "true").lower() == "true" \
                     and DELIVERY_CHANNEL == "discord"
SUMMARY_LANGUAGE   = os.environ.get("SUMMARY_LANGUAGE", "Chinese").strip()

# ── Monitored accounts ────────────────────────────────────────────────────────

ACCOUNTS = [
    {"username": "karpathy",      "name": "Andrej Karpathy"},
    {"username": "ilyasut",       "name": "Ilya Sutskever"},
    {"username": "AndrewYNg",     "name": "Andrew Ng"},
    {"username": "lilianweng",    "name": "Lilian Weng"},
    {"username": "DrJimFan",      "name": "Jim Fan"},
    {"username": "jeremyphoward", "name": "Jeremy Howard"},
    {"username": "natolambert",   "name": "Nathan Lambert"},
    {"username": "hwchase17",     "name": "Harrison Chase"},
    {"username": "rauchg",        "name": "Guillermo Rauch"},
    {"username": "levelsio",      "name": "Pieter Levels"},
    {"username": "swyx",          "name": "swyx"},
    {"username": "sama",          "name": "Sam Altman"},
    {"username": "demishassabis", "name": "Demis Hassabis"},
    {"username": "elonmusk",      "name": "Elon Musk"},
    {"username": "jensenhuang",   "name": "Jensen Huang"},
    {"username": "JeffDean",      "name": "Jeff Dean"},
    {"username": "sundarpichai",  "name": "Sundar Pichai"},
    {"username": "satyanadella",  "name": "Satya Nadella"},
]

# ── Deduplication ─────────────────────────────────────────────────────────────

def load_sent_tweets():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                return set(json.load(f).get("tweet_ids", []))
        except Exception:
            pass
    return set()

def save_sent_tweets(ids):
    ids_list = sorted(ids)[-MAX_STORED_IDS:]
    with open(STATE_FILE, "w") as f:
        json.dump({"tweet_ids": ids_list,
                   "updated": datetime.now(timezone.utc).isoformat()}, f)

def filter_new(tweets, sent):
    new, new_ids = [], set()
    for t in tweets:
        tid = t.get("id", "")
        if tid and tid not in sent:
            new.append(t)
            new_ids.add(tid)
    return new, new_ids

# ── Twitter fetch ─────────────────────────────────────────────────────────────

def fetch_tweets(username, limit=20):
    import requests
    headers = {"Authorization": f"Bearer {AISA_API_KEY}"}
    base = "https://api.aisa.one/apis/v1/twitter/tweet/advanced_search"

    for query in [
        f"from:{username} AI OR LLM OR GPT OR model OR agent",
        f"from:{username}",
    ]:
        try:
            r = requests.get(base, params={"query": query, "queryType": "Latest"},
                             headers=headers, timeout=15)
            tweets = r.json().get("tweets", [])
            if tweets:
                return tweets[:limit]
        except Exception as e:
            print(f"  fetch error @{username}: {e}")
    return []

# ── LLM summarization (provider auto-detection) ───────────────────────────────

SUMMARIZE_PROMPT = """\
You are an AI industry analyst. Analyze the following tweets and summarize the most important AI/tech developments of the day.

Requirements:
1. Write the summary in {language}
2. Each item format: <content> | [Original Link](<url>)
   - Use the phrase for "Original Link" in {language} (e.g. "原文链接" in Chinese, "Source" in English, "元のリンク" in Japanese)
3. Leave one blank line between each item
4. Include AI/tech-related content: technical posts, product launches, industry opinions, company news, etc.
5. Sort by importance, max 12 items, cover at least 5 different authors
6. Output directly without any introduction or preamble

Example format:
- Karpathy shared new neural network training techniques | [Original Link](https://x.com/karpathy/status/123)

- Sam Altman says GPT-5 launching this year | [Original Link](https://x.com/sama/status/456)

Tweets:
{tweets_text}"""

def build_tweet_list(tweets):
    items = []
    for t in tweets:
        author = t.get("author", {}).get("userName", "?")
        text = t.get("text", "")
        tid = t.get("id", "")
        url = f"https://x.com/{author}/status/{tid}" if tid else ""
        if len(text) >= 20:
            items.append({"author": author, "content": text,
                          "url": url, "likes": t.get("likeCount", 0)})
    return items[:60]

def summarize(tweets):
    import requests

    items = build_tweet_list(tweets)
    if not items:
        return None

    tweets_text = "\n".join(
        f"@{t['author']}: {t['content'][:300]} | ❤️{t['likes']} | {t['url']}"
        for t in items
    )
    prompt = SUMMARIZE_PROMPT.format(tweets_text=tweets_text, language=SUMMARY_LANGUAGE)

    # Try providers in order of preference
    providers = [
        ("Anthropic Claude", _call_anthropic),
        ("OpenAI GPT-4o-mini", _call_openai),
        ("Google Gemini", _call_gemini),
    ]

    for name, fn in providers:
        result = fn(prompt)
        if result:
            print(f"  Summarized with {name}")
            return result

    print("  All LLM providers failed — using raw fallback")
    return "\n\n".join(
        f"- @{t['author']}: {t['content'][:200]} | 原文链接 {t['url']}"
        for t in items[:10]
    )

def _call_anthropic(prompt):
    import requests
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not key:
        return None
    try:
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": key, "anthropic-version": "2023-06-01",
                     "content-type": "application/json"},
            json={"model": "claude-haiku-4-5", "max_tokens": 1500,
                  "messages": [{"role": "user", "content": prompt}]},
            timeout=60,
        )
        if r.status_code == 200:
            return r.json()["content"][0]["text"].strip()
        print(f"  Anthropic error {r.status_code}")
    except Exception as e:
        print(f"  Anthropic exception: {e}")
    return None

def _call_openai(prompt):
    import requests
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        return None
    try:
        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}",
                     "Content-Type": "application/json"},
            json={"model": "gpt-4o-mini", "max_tokens": 1500,
                  "messages": [{"role": "user", "content": prompt}]},
            timeout=60,
        )
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"].strip()
        print(f"  OpenAI error {r.status_code}")
    except Exception as e:
        print(f"  OpenAI exception: {e}")
    return None

def _call_gemini(prompt):
    import requests
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key:
        return None
    try:
        r = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={key}",
            headers={"Content-Type": "application/json"},
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=60,
        )
        if r.status_code == 200:
            return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        print(f"  Gemini error {r.status_code}")
    except Exception as e:
        print(f"  Gemini exception: {e}")
    return None

# ── Channel delivery ──────────────────────────────────────────────────────────

def send_message(message):
    """Send a message via OpenClaw to the configured channel and target."""
    subprocess.run([
        "openclaw", "message", "send",
        "--channel", DELIVERY_CHANNEL,
        "--target", DELIVERY_TARGET,
        "--message", message,
    ])

# ── Format output ─────────────────────────────────────────────────────────────

def format_messages(summary, date_str, failed_accounts):
    """Returns (text_msg, cards_msg) tuple."""

    # Extract bare links before transformation (for card message)
    raw_links = re.findall(r'https://\S+', summary)
    raw_links = [re.sub(r'[)\].,>]+$', '', l) for l in raw_links]
    seen, top_links = set(), []
    for l in raw_links:
        if l not in seen:
            seen.add(l)
            top_links.append(l)
        if len(top_links) == 5:
            break

    # Convert "原文链接 https://..." → "[原文链接](<url>)"
    formatted = re.sub(
        r'原文链接\s+(https://\S+)',
        lambda m: f"[原文链接](<{re.sub(r'[)\\].,>]+$', '', m.group(1))}>)",
        summary,
    )
    # Suppress remaining bare links
    formatted = re.sub(r'(?<!<)(https://\S+)(?!>)', r'<\1>', formatted)

    if len(formatted) > 1800:
        formatted = formatted[:1800] + "\n\n...(截断)"

    text_msg = f"📊 **AI 每日简报** — {date_str}\n\n{formatted}"
    if failed_accounts:
        text_msg += f"\n\n⚠️ 未获取到数据: {', '.join('@' + a for a in failed_accounts)}"

    # Card preview message only for Discord
    cards_msg = None
    if CARD_PREVIEWS and top_links:
        cards_msg = "🔗 **今日精选链接**\n\n" + "\n".join(top_links)

    return text_msg, cards_msg

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print(f"🤖 AI Twitter Digest — {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    sent_ids = load_sent_tweets()
    print(f"Loaded {len(sent_ids)} previously sent tweet IDs")

    all_tweets, failed = [], []
    for acc in ACCOUNTS:
        username = acc["username"].strip()
        print(f"Fetching @{username}...")
        tweets = fetch_tweets(username)
        if tweets:
            all_tweets.extend(tweets)
            print(f"  -> {len(tweets)} tweets")
        else:
            failed.append(username)
            print(f"  -> no tweets (skipped)")

    print(f"\nTotal: {len(all_tweets)} tweets | Failed: {len(failed)}")

    new_tweets, new_ids = filter_new(all_tweets, sent_ids)
    print(f"New after dedup: {len(new_tweets)}")

    if not new_tweets:
        send_to_discord("📊 **AI Twitter Update** — No new tweets today.")
        return

    print("\nSummarizing...")
    summary = summarize(new_tweets)

    if not summary:
        summary = "今日暂无重要AI动态。"

    lang = SUMMARY_LANGUAGE.lower()
    if "chinese" in lang or "中文" in lang:
        date_str = datetime.now().strftime('%Y年%m月%d日')
    elif "japanese" in lang or "日本語" in lang:
        date_str = datetime.now().strftime('%Y年%m月%d日')
    else:
        date_str = datetime.now().strftime('%B %d, %Y')
    text_msg, cards_msg = format_messages(summary, date_str, failed)

    send_message(text_msg)

    if cards_msg:
        import time
        time.sleep(1)
        send_message(cards_msg)

    save_sent_tweets(sent_ids | new_ids)
    print(f"✅ Done. Tracked IDs: {min(len(sent_ids | new_ids), MAX_STORED_IDS)}")

if __name__ == "__main__":
    main()
