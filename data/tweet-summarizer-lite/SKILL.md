---
name: tweet-summarizer-lite
description: Fetch and summarize single tweets from Twitter/X. Basic search and single tweet fetching. Lightweight version perfect for quick tweet lookups.
requiredEnv:
  - AUTH_TOKEN
  - CT0
requiredBins:
  - bird
permissions:
  - network: Contact X/Twitter API via bird CLI (uses session cookies)
  - filesystem: Write tweets to ~/.openclaw/workspace/data/tweets/
---

# Tweet Summarizer Lite

Use this skill when the user asks to fetch, read, save, or summarize a single tweet from Twitter/X.

## When to Use

✅ **USE this skill when the user:**

- Pastes a Twitter/X URL and wants to read or save it
- Asks to "fetch", "grab", "get", "read", or "summarize" a tweet
- Wants to search their saved tweets by text, author, or date
- Asks what they've saved so far

❌ **DON'T use when:**
- The user wants threads, user timelines, collections, or tags → use **tweet-summarizer-pro**
- Posting or replying to tweets (this skill is read-only)

## How to Use

You run the scripts internally — the user never types `python3`. Respond naturally, then exec the appropriate script and present the output conversationally.

The skill root is at: `~/.openclaw/workspace/skills/tweet-summarizer-lite/`
Run scripts with: `python3 <skill-root>/scripts/<script>.py <args>`

---

## Fetching a Tweet

**Triggers:** "fetch this tweet", "what does this say", "grab this", paste of x.com/*/status/* URL

```bash
python3 scripts/tweet.py <url>
# Skip summary: python3 scripts/tweet.py <url> -ns
```

Auto-detects tweet URLs in the user's message. Shows the tweet text and a short summary.

---

## Searching Saved Tweets

**Triggers:** "search my saved tweets for...", "find tweets about...", "do I have anything saved about..."

```bash
# By text content
python3 scripts/search_tweets.py --text "artificial intelligence"

# By author
python3 scripts/search_tweets.py --source elonmusk

# By date
python3 scripts/search_tweets.py --since 2026-02-01

# List all saved authors
python3 scripts/search_tweets.py --list-sources

# Storage stats
python3 scripts/search_tweets.py --stats
```

---

## Summarizing a Saved Tweet

**Triggers:** "summarize tweet [id]", "give me a summary of that"

```bash
python3 scripts/summarize.py <tweet-id>
```

---

## Troubleshooting

If bird CLI fails or credentials are missing:
```bash
python3 scripts/config.py --check-credentials
```

Tell the user:
> Set `AUTH_TOKEN` and `CT0` from your browser cookies (Twitter → DevTools → Application → Cookies). See `SECURITY.md` for details.

---

## Upgrading

Need threads, collections, tags, or user timelines? This lite version only handles single tweets. Suggest **tweet-summarizer-pro** for those features.
