# GuavaMemory — Episodic Memory System for OpenClaw

Structured episodic memory with Q-value scoring. Remember what worked, forget what didn't.

## What It Does

- Records task episodes with success/failure patterns and Q-values
- Searches past episodes via `memory_search` (Voyage AI compatible)
- Promotes repeated successes into reusable skill procedures
- Tracks anti-patterns to avoid repeating mistakes

## Quick Start

### 1. Set Up Memory Directories

```bash
mkdir -p memory/episodes memory/skills memory/meta
```

### 2. Initialize Index

```bash
cat > memory/episodes/index.json << 'EOF'
{
  "version": "1.0.0",
  "name": "GuavaMemory",
  "episodes": [],
  "stats": { "total": 0, "avg_q_value": 0, "promotions": 0 },
  "config": {
    "promotion_threshold": 0.85,
    "promotion_min_count": 3,
    "max_episodes_per_search": 3,
    "learning_rate": 0.3
  }
}
EOF
```

### 3. Add to AGENTS.md

Paste the following rules into your AGENTS.md:

```markdown
### Episodic Memory Rules
1. **Task start** → `memory_search` for related episodes. Use top 3 by Q-value
2. **Task complete** → Record episode in `memory/episodes/ep_YYYYMMDD_NNN.md`
3. **Record content** → Intent, Context, Success pattern, Failure pattern, Q-value, feel
4. **Skill promotion** → 3 successes with same intent & Q≥0.85 → promote to `memory/skills/`
5. **Anti-patterns** → Record failures in `memory/episodes/anti_patterns.md`
6. **No loops** → Record once per task at completion. No mid-task rewrites
7. **Update index** → Keep `memory/episodes/index.json` in sync
```

## Episode Format

Create files like `memory/episodes/ep_20260211_001.md`:

```markdown
# EP-20260211-001: Short description

## Intent
What you were trying to do

## Context
- domain: what area
- tools: what tools used

## Experience

### ✅ Success Pattern
1. Step one
2. Step two
3. Step three

### ❌ Failure Pattern
- What didn't work and why

## Utility
- reward: 0.0-1.0 (1.0 = one-shot success)
- q_value: 0.0-1.0 (updated over time)
- feel: flow | grind | frustration | eureka
```

## Q-Value Update

```
Q_new = Q_old + 0.3 * (reward - Q_old)
```

Reward scale:
- `1.0` → One-shot success
- `0.7` → Success with some trial and error
- `0.3` → Success but very roundabout
- `0.0` → Failed, solved differently
- `-0.5` → Failed, unresolved

## Skill Promotion

When the same intent succeeds 3+ times with Q ≥ 0.85:
1. Merge episodes into `memory/skills/skill-name.md`
2. Extract the optimal procedure
3. Mark source episodes as `status: "graduated"`

## Search Script

Copy `scripts/ep-search.sh` to your workspace:

```bash
#!/bin/bash
EPISODES_DIR="${HOME}/.openclaw/workspace/memory/episodes"
INDEX="${EPISODES_DIR}/index.json"
echo "🔍 Searching episodes for: $1"
cat "$INDEX" | jq -r '.episodes | sort_by(-.q_value) | .[] | select(.status == "active") | "Q:\(.q_value) | \(.feel) | \(.intent) → \(.file)"'
```

## Requirements

- OpenClaw (any version)
- `jq` (for search script)
- No other dependencies

## How It Works With memory_search

Episodes are plain Markdown files in `memory/`. OpenClaw's `memory_search` (Voyage AI) indexes them automatically. When you search for a task, episodes rank by semantic similarity. Then filter by Q-value to find what actually worked.
