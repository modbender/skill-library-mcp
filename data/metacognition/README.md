# metacognition

A self-reflection engine for AI agents. Extracts patterns from session transcripts into a weighted insight graph with Hebbian learning and time decay, then compiles a token-budgeted lens of active self-knowledge.

An [OpenClaw](https://openclaw.app) skill.

## How It Works

1. **Extract** — Analyzes session transcripts for deeper patterns: recurring mistakes, relationship dynamics, confidence calibration, growth principles
2. **Categorize** — Stores insights as perceptions, overrides, protections, self-observations, decisions, or curiosities
3. **Reinforce** — Hebbian learning: repeated insights get stronger, unused ones decay over time (configurable half-life)
4. **Connect** — Builds a graph of relationships between insights, discovering clusters that may represent higher-level principles
5. **Compile** — Produces a token-budgeted "metacognition lens" — a compact summary of the agent's active self-knowledge

## Security

- **Localhost-only embeddings** — the optional embeddings endpoint is validated at startup to be `127.0.0.1`, `localhost`, or `::1`; remote URLs are rejected entirely
- **Python stdlib only** — uses `urllib` for the local embeddings call; no `curl`, no `subprocess`, no external dependencies
- **No network access** beyond the optional local embeddings server
- File reads capped at 1MB

## CLI Commands

```bash
python3 metacognition.py add <type> "<insight>"   # Add or merge an entry
python3 metacognition.py list [type]               # List entries
python3 metacognition.py feedback <id> <pos|neg>   # Reinforce or weaken
python3 metacognition.py decay                     # Apply time-based decay
python3 metacognition.py compile                   # Compile the lens
python3 metacognition.py extract <path>            # Extract from a daily note
python3 metacognition.py reweave                   # Build graph connections
python3 metacognition.py graph                     # Show graph stats
python3 metacognition.py integrate                 # Full cycle
```

## Configuration

| Constant | Default | Description |
|----------|---------|-------------|
| `HALF_LIFE_DAYS` | 7.0 | Decay rate for unreinforced entries |
| `STRENGTH_CAP` | 3.0 | Maximum entry strength |
| `LENS_TOKEN_BUDGET` | 500 | Token budget for compiled lens |
| `EMBEDDING_SIM_THRESHOLD` | 0.85 | Merge threshold (embeddings) |
| `FALLBACK_SIM_THRESHOLD` | 0.72 | Merge threshold (string matching) |

## Requirements

- Python 3 (stdlib only — no pip dependencies)
- [OpenClaw](https://openclaw.app) with cron support
- Optional: local embeddings server (falls back to string similarity)

## License

MIT
