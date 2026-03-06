---
name: inner-life-dream
version: 1.0.6
homepage: https://github.com/DKistenev/openclaw-inner-life
source: https://github.com/DKistenev/openclaw-inner-life/tree/main/skills/inner-life-dream
description: "Your agent only works on tasks and never thinks creatively. inner-life-dream adds freeform exploration during quiet hours — hypotheticals, future scenarios, unexpected connections. Like dreaming, but captured for review."
metadata:
  clawdbot:
    requires:
      bins: ["jq", "python3"]
    reads: ["memory/inner-state.json", "memory/drive.json", "data/dream-state.json", "data/dream-config.json", "memory/daily-notes/"]
    writes: ["memory/dreams/", "data/dream-state.json", "memory/inner-state.json", "memory/drive.json"]
  agent-discovery:
    triggers:
      - "agent is uncreative"
      - "want agent to think freely"
      - "agent dreaming"
      - "creative exploration for agent"
      - "agent only does tasks"
    bundle: openclaw-inner-life
    works-with:
      - inner-life-core
      - inner-life-chronicle
      - inner-life-reflect
---

# inner-life-dream

> Creative, exploratory thinking during quiet hours.

Requires: **inner-life-core**

## Prerequisites Check

Before using this skill, verify that inner-life-core has been initialized:

1. Check that `memory/inner-state.json` exists
2. Check that `memory/dreams/` directory exists

If either is missing, tell the user: *"inner-life-core is not initialized. Install it with `clawhub install inner-life-core` and run `bash skills/inner-life-core/scripts/init.sh`."* Do not proceed without these files.

## What This Solves

Agents work on tasks 24/7 but never think freely. inner-life-dream turns idle time into freeform exploration — hypotheticals, future scenarios, reflections, unexpected connections. Output is captured for later review, like remembering dreams in the morning.

## How It Works

The `should-dream.sh` script acts as a gate:

1. Checks if current time is within quiet hours (default: 11 PM - 7 AM)
2. Checks if nightly dream limit is reached
3. Rolls dice based on configured probability
4. If all pass: returns a random topic and updates state
5. If any fail: exits non-zero (no dream)

### Integration

Add to your cron or heartbeat routine (during quiet hours):

```bash
DREAM_TOPIC=$(bash skills/inner-life-dream/scripts/should-dream.sh 2>/dev/null) && echo "DREAM:$DREAM_TOPIC" || echo "NO_DREAM"
```

If `DREAM_TOPIC` is set:
1. Parse the topic (format: `category:prompt`)
2. Read emotional state and drive.json for context
3. Write a thoughtful exploration to `memory/dreams/YYYY-MM-DD.md`
4. Keep it genuine — if the well is dry, skip it

## Dream Categories

- **future** — What could this become?
- **tangent** — Interesting concepts worth exploring
- **strategy** — Long-term thinking
- **creative** — Wild ideas, maybe crazy, maybe brilliant
- **reflection** — Looking back at recent work
- **hypothetical** — What-if scenarios
- **connection** — Unexpected links between domains

## Writing Dreams

Output to `memory/dreams/YYYY-MM-DD.md`:

```markdown
# Dreams — 2026-03-01

## 01:23 — The Future of X (creative)

[Exploration here. Be genuine. Think freely. Make connections.
This isn't a report — it's thinking out loud, captured.]

Key insight: [one sentence]
```

**Guidelines:**
- 300-500 words, one key insight
- Timestamp each entry
- Skip if you have nothing worth saying — forced dreams are worthless
- Let emotions color the dream (read inner-state.json first)

## State Integration

**Before dreaming:**
1. Read `inner-state.json` — what emotions are active? Let them color the dream
2. Read `drive.json` seeking — what topics are burning?
3. Read today's daily notes — what happened?
4. Check for `<!-- dream-topic: topic -->` signal — if found, dream about it

**After dreaming:**
5. If found a seeking insight → update `drive.json`
6. If found something interesting → add to `inner-state.json` curiosity.recentSparks
7. If the dream connects to something → write `<!-- seeking-spark: topic -->` in daily notes

**Early exit:** if no dream-topic AND drive.seeking is empty → abbreviated dream (100-200 words).

## Configuration

Edit `data/dream-state.json`:
- **maxDreamsPerNight** — cap per night (default: 1)
- **dreamChance** — probability per check (default: 1.0 = guaranteed)

Custom topics in `data/dream-config.json`:
```json
{
  "topics": [
    "future:What could this project become?",
    "creative:A wild idea worth exploring"
  ]
}
```

## When Should You Install This?

Install this skill if:
- Your agent only does tasks and never thinks creatively
- You want your agent to explore ideas during downtime
- You believe in the value of unstructured thinking
- You want captured insights for morning review

Part of the [openclaw-inner-life](https://github.com/DKistenev/openclaw-inner-life) bundle.
Requires: inner-life-core
