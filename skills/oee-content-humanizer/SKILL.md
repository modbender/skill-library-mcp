# 🐾 Humanizer — AI Content De-Robotifier

> by Odin's Eye Enterprises — Ancient Wisdom. Modern Intelligence.

Strip the AI out of AI-generated text. Makes content sound like a human wrote it.

## What It Does

1. **Detects** AI tells (buzzwords, tone inflation, repetitive structure)
2. **Rewrites** with natural cadence, contractions, varied rhythm
3. **Tunes** output for specific platforms (Twitter, LinkedIn, Blog, Email, Telegram)

## Trigger Phrases

- "humanize this text"
- "make this sound human"
- "de-robotify this"
- "rewrite this naturally"
- "strip the AI from this"

## Usage

```bash
# Direct argument
python humanize.py "Your AI-sounding text here" --channel twitter

# Pipe from stdin
echo "In today's rapidly evolving landscape..." | python humanize.py --channel linkedin

# Detection only (no rewrite)
python humanize.py -d "Let's delve into this transformative tapestry"

# General rewrite (no specific channel)
python humanize.py "text here"
```

## Channels

| Channel    | Style                              |
|------------|-------------------------------------|
| `twitter`  | Punchy, <280 chars, direct          |
| `linkedin` | Professional but conversational     |
| `blog`     | Longer form, personal voice         |
| `email`    | Brief, clear, action-oriented       |
| `telegram` | Casual, concise                     |
| `general`  | Natural prose (default)             |

## Requirements

- Python 3.10+ (stdlib only — no pip installs)
- `ANTHROPIC_API_KEY` environment variable
- Uses Claude Haiku for cost efficiency

## For Agents

When asked to humanize text, run from the skill directory:

```bash
python humanize.py "TEXT" --channel CHANNEL
```

Stdout = clean rewritten text. Stderr = detection info.

<!-- 🐾 a raven left paw prints in the snow -->
