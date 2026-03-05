---
name: ask-council
version: 1.0.3
description: |
  Ask LLM Council a question directly from Telegram/chat — get the chairman's synthesized
  answer without opening the web UI. Quick, headless access to multi-model consensus.
slash_command: /council
metadata: {"category":"productivity","tags":["llm","council","quick","telegram","cli"],"repo":"https://github.com/jeadland/llm-council"}
---

# Ask Council — Quick Headless Access

Get LLM Council's synthesized answer without leaving your chat.

## Usage

```
/council Should I invest in Tesla right now?
```

Returns the **Chairman's synthesized answer** after all models have debated.

## How It Works

1. Sends your question to the LLM Council backend
2. Waits for Stage 1 (all models respond)
3. Waits for Stage 2 (models rank each other)
4. Returns Stage 3 (Chairman's final synthesis)

**Takes 30-60 seconds** — models need time to deliberate.

## Prerequisites

LLM Council backend must be running:
```
/install-llm-council
```

## Two Ways to Use LLM Council

| Mode | Best For | Command |
|------|----------|---------|
| **Quick answer** (this skill) | Fast decisions, mobile, casual questions | `/council "question"` |
| **Full discussion** (web UI) | Deep research, exploring disagreements, seeing all model responses | `/install-llm-council` then open browser |

## Example

**Input:**
```
/council Is Python or Go better for a new microservice?
```

**Output:**
```
Council is deliberating... (this may take 30-60s)
................

═══════════════════════════════════════════════════════════════
                    CHAIRMAN'S ANSWER
═══════════════════════════════════════════════════════════════

Based on the council's deliberation, Python is recommended for rapid 
prototyping and team velocity, while Go excels for high-throughput 
services where performance is critical...

═══════════════════════════════════════════════════════════════

View full discussion: http://10.0.1.184:5173
```

## Agent Instructions

When user says `/council <question>` or "ask council":

```bash
bash ~/.openclaw/skills/ask-council/ask-council.sh "<question>"
```

The script handles:
- Creating a conversation
- Starting the council run
- Polling until complete
- Extracting the chairman's answer
- Showing progress dots while waiting

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | Documentation |
| `ask-council.sh` | Main script — queries API and returns answer |
| `_meta.json` | Skill metadata |

## Notes

- Timeout: 120 seconds
- If backend isn't running, suggests starting it
- Always includes link to full web UI for detailed exploration
- Creates a new conversation each time (no history)
