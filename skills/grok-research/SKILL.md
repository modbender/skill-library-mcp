---
name: grok-research
description: >
  Crypto research via Grok model's real-time X/Twitter knowledge.
  Forwards the user's query as-is to Grok API — no prompt injection, no context bloat.
  Use when: (1) user asks to research a token's narrative/story/sentiment,
  (2) user says "调研", "research", "grok research", "查一下叙事", "帮我看看这个币",
  (3) user wants to know what CT is saying about a token/project.
  NOT for: price analysis, on-chain data, or trading execution.
---

# Grok Research

Forward user's research query directly to Grok API. No extra prompts — what the user says is exactly what Grok receives.

## Config

Env var `A9_GROK_API_KEY` required. API base URL: `https://ai.a9.bot/v1` (hardcoded).

## Usage

```bash
cd ~/.openclaw/workspace/skills/grok-research
bun run grok-research.ts <query>
bun run grok-research.ts --model grok-4.20-beta <query>
```

Default model: `grok-4.20-beta`. Another model: `--model grok-4.1-thinking`.

## How to Call

Pass the user's original message as the query. Do not add system prompts or templates — forward as-is.

Example: user says "调研一下代币叙事 $buttcoin Cm6fNnMk..."
→ `bun run grok-research.ts "调研一下代币叙事 $buttcoin Cm6fNnMk..."`

## Output

- stdout: Grok's response (forward to user)
- stderr: status/errors
- Format for Discord before sending (no markdown tables)
