---
name: ai-twitter-digest
description: "Monitor a curated list of AI/tech Twitter accounts, summarize the day's key posts using an LLM, and deliver a formatted digest to a Discord channel. Use when: (1) setting up a daily automated AI news briefing from Twitter/X, (2) scheduling or running a one-shot Twitter digest to Discord, (3) managing or updating the monitored account list, summarization prompt, or delivery format."
---

# AI Twitter Digest

Fetches tweets from AI/tech influencers via the AISA API, summarizes in Chinese using any available LLM (Claude → OpenAI → Gemini, auto-detected), and delivers a two-part digest to Discord:

- **Message 1**: Text summary with `[原文链接]` hyperlinks (no embed previews)
- **Message 2**: Top 5 bare links rendered as Discord card previews

## Setup

### 1. Run the setup wizard (required before first use)

```bash
python3 scripts/setup.py
```

The wizard will:
- Auto-detect API keys from your environment and OpenClaw config
- Prompt for any missing keys (AISA, LLM, Discord channel)
- Test connectivity to AISA and your chosen LLM provider
- Write a `.env` file — no manual editing needed

> If you prefer manual setup, create `scripts/.env` with the following content:
>
> ```env
> AISA_API_KEY=your_aisa_key_here
> DELIVERY_CHANNEL=discord
> DELIVERY_TARGET=channel:your_channel_id_here
> SUMMARY_LANGUAGE=Chinese
> ANTHROPIC_API_KEY=
> OPENAI_API_KEY=
> GEMINI_API_KEY=
> # STATE_FILE=~/.ai-twitter-sent.json
> # MAX_STORED_IDS=500
> # CARD_PREVIEWS=true
> ```

**Required config:**

| Variable | Description |
|----------|-------------|
| `AISA_API_KEY` | Twitter data — [aisa.one](https://aisa.one) |
| `DELIVERY_CHANNEL` | `discord` / `whatsapp` / `telegram` / `slack` / `signal` |
| `DELIVERY_TARGET` | Channel-specific target (see table below) |
| One of: `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` / `GEMINI_API_KEY` | LLM for summarization |
| `SUMMARY_LANGUAGE` | Digest language — `Chinese` (default), `English`, `Japanese`, `Korean`, `Spanish`, `French`, `German`, or any language name |

**Delivery target format:**

| Channel | Target format | Example |
|---------|--------------|---------|
| discord | `channel:<id>` | `channel:1234567890` |
| whatsapp | E.164 phone or `group:<id>` | `+1234567890` |
| telegram | `@username` or chat_id | `@mychannel` |
| slack | `#channel-name` | `#ai-digest` |
| signal | E.164 phone number | `+1234567890` |

> Card link previews (`CARD_PREVIEWS`) are Discord-only and auto-disabled on other channels.

### 2. Run manually

```bash
python3 scripts/monitor.py
```

### 3. Schedule with OpenClaw cron

```bash
# Daily at 3:30 PM Eastern
openclaw cron add "AI Twitter Digest" "30 15 * * *" \
  "python3 /path/to/ai-twitter-digest/scripts/monitor.py" \
  --timezone "America/New_York"
```

## Customizing Accounts

Edit the `ACCOUNTS` list in `scripts/monitor.py`. See `references/accounts.md` for the default list and suggested additions.

## Output Format

**Message 1 — Summary:**
```
📊 **AI 每日简报** — 2026年02月26日

- Karpathy 发布了神经网络教程 | [原文链接](...)

- Sam Altman 表示 GPT-5 今年发布 | [原文链接](...)
```

**Message 2 — Card previews:**
```
🔗 **今日精选链接**

https://x.com/karpathy/status/...
https://x.com/sama/status/...
```

## How It Works

1. Fetches up to 20 tweets/account (AI-keyword filtered, with all-tweets fallback)
2. Deduplicates against `STATE_FILE` (capped at `MAX_STORED_IDS`)
3. Summarizes with first available LLM provider
4. Posts two Discord messages: text digest + card preview links
5. Updates dedup state file
