# context-engineer

**Context Window Optimizer** — Analyze, audit, and optimize your agent's context utilization. Know exactly where your tokens go before they're sent.

Built by the Anvil AI open-source team.

## Features

- **Analyze** — Scan SKILL.md, SOUL.md, MEMORY.md, AGENTS.md, TOOLS.md, and other workspace files. Count tokens, identify bloat, score efficiency.
- **Audit Tools** — Parse tool definitions from OpenClaw config, identify redundant/overlapping tools, measure tool definition overhead.
- **Report** — Terminal-rendered report with token counts, efficiency scores, and specific recommendations.
- **Compare** — Before/after comparison showing projected token savings from recommendations.

## Quick Start

```bash
# Analyze your workspace
python3 context.py analyze --workspace ~/.openclaw/workspace

# Audit tool definitions
python3 context.py audit-tools --config ~/.openclaw/openclaw.json

# Full context report
python3 context.py report --workspace ~/.openclaw/workspace

# Save a snapshot, optimize, then compare
python3 context.py analyze --workspace ~/.openclaw/workspace --snapshot before.json
# ... make optimizations ...
python3 context.py analyze --workspace ~/.openclaw/workspace --snapshot after.json
python3 context.py compare --before before.json --after after.json
```

## Requirements

- Python 3.8+
- No external dependencies (stdlib only)

## Analysis Categories

| Category | What It Checks |
|----------|---------------|
| System prompt efficiency | Length, redundancy detection, compression potential |
| Tool definition overhead | Tool count, per-tool token cost, overlapping definitions |
| Memory file bloat | MEMORY.md size, stale entries, optimization suggestions |
| Skill overhead | Installed skills contributing to context, per-skill cost |
| Context budget | % of model context window consumed by static content |

## Token Counting

Token estimates use a character-based heuristic (~4 characters per token). This provides reasonable approximations for planning purposes. For precise counts, use a model-specific tokenizer like `tiktoken`.

## Install

```bash
clawhub install context-engineer
```

Or clone from [GitHub](https://github.com/cacheforge-ai/cacheforge-skills).

## License

MIT — see [LICENSE](./LICENSE).
