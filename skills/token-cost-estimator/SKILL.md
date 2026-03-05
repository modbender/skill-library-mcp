---
name: token-cost-estimator
description: Estimate API token costs from OpenClaw session transcripts. Analyzes all agent sessions to calculate what you'd pay on per-token pricing vs subscription plans. Use when asked about API costs, token usage, billing estimates, or comparing Max/Pro plans to pay-per-use.
---

# Token Cost Estimator

Estimate real API costs from OpenClaw session transcript data.

## How It Works

OpenClaw stores session transcripts as JSONL files in `~/.openclaw/agents/<agent>/sessions/*.jsonl`. Each line is a turn with role, content, and sometimes usage data.

## Estimation Script

Run this Python script to analyze all agents:

```python
import json, glob, os

AGENTS_DIR = os.path.expanduser('~/.openclaw/agents')
# Pricing per million tokens (update as needed)
PRICING = {
    'opus': {'input': 15, 'output': 75, 'cache_read': 1.875},
    'sonnet': {'input': 3, 'output': 15, 'cache_read': 0.375},
}

agent_dirs = [d for d in os.listdir(AGENTS_DIR) if os.path.isdir(os.path.join(AGENTS_DIR, d))]
grand_in, grand_out = 0, 0

for agent in sorted(agent_dirs):
    sess_dir = os.path.join(AGENTS_DIR, agent, 'sessions')
    if not os.path.isdir(sess_dir):
        continue
    total_in, total_out, sessions = 0, 0, 0
    for f in glob.glob(os.path.join(sess_dir, '*.jsonl')):
        sessions += 1
        turns = []
        for line in open(f):
            try:
                obj = json.loads(line)
                msg = obj.get('message', {})
                if not isinstance(msg, dict): continue
                role = msg.get('role', '')
                raw = json.dumps(msg)
                turns.append((role, len(raw)))
            except: pass
        # Account for context re-sending
        cumulative = 0
        for role, chars in turns:
            if role in ('user', 'system', 'tool'):
                cumulative += chars
            elif role == 'assistant':
                total_in += cumulative // 4
                total_out += chars // 4
    print(f'{agent}: {sessions} sessions, ~{total_in:,} input, ~{total_out:,} output tokens')
    grand_in += total_in
    grand_out += total_out

print(f'\nTotal input: ~{grand_in:,}, output: ~{grand_out:,}')
for tier, rates in PRICING.items():
    for cache_pct in [0.6, 0.9]:
        cached = int(grand_in * cache_pct)
        uncached = grand_in - cached
        cost = (uncached/1e6)*rates['input'] + (cached/1e6)*rates['cache_read'] + (grand_out/1e6)*rates['output']
        print(f'{tier} ({int(cache_pct*100)}% cache): ${cost:,.2f}')
```

## Key Concepts

**Context re-sending:** Every API call sends the full conversation history as input. A 50-turn conversation re-sends all prior turns on each new message. This is the #1 cost driver.

**Cache hits:** OpenClaw caches prompt prefixes. Typical cache hit rates: 60-90%. Cache reads cost 87.5% less than fresh input.

**What transcripts miss:** System prompts, tool definitions, and internal retries aren't always logged. Real cost is typically 1.5-2x the transcript estimate.

## Comparing Plans

| Plan | Monthly Cost | Best For |
|------|-------------|----------|
| API (Opus) | Variable | Heavy agentic use (>$200/mo equivalent) |
| API (Sonnet) | Variable | Most agent tasks, 5x cheaper than Opus |
| Claude Max ($100) | $100 flat | Light-medium use via OAuth (if allowed) |
| Claude Max ($200) | $200 flat | Heavy use via OAuth (if allowed) |

**Break-even:** If your estimated API cost exceeds your subscription price, the subscription saves money. Note: Anthropic has restricted OAuth token use in third-party tools.
