# Claude Usage

Calculate your [Claude Max](https://claude.ai) subscription usage from [OpenClaw](https://openclaw.ai) session data.

> **Built for OpenClaw** — This tool reads OpenClaw session JSONL transcripts to calculate Claude API credit consumption. It requires an [OpenClaw](https://openclaw.ai) installation with active sessions.

Track credits consumed, rate limits, and per-session breakdown based on the reverse-engineered credits system from [she-llac.com/claude-limits](https://she-llac.com/claude-limits).

## Features

- **Weekly overview** with progress bar and remaining budget
- **5-hour sliding window** rate limit warning (⚡ >50%, ⚠️ >80%)
- **Per-session breakdown** — see which sessions cost the most
- **Single session detail** — deep-dive into any session's usage
- **Saved config** — set reset time once, never type it again
- **JSON output** for programmatic use

## Install

```bash
# npm (global CLI)
npm install -g claude-usage

# Or as an OpenClaw skill via ClawHub
npx clawhub@latest install claude-usage
```

## Usage

```bash
# First time — save your reset time (from claude.ai Settings > Usage)
claude-usage "2026-02-09 14:00" --plan 5x --save

# After saving, just run:
claude-usage

# Top 5 sessions only
claude-usage --top 5

# Single session detail
claude-usage --session "main"

# JSON output
claude-usage --json
```

> You can also run the Python script directly: `python3 scripts/claude-usage.py [args]`

## Example Output

```
╔══════════════════════════════════════════════════════╗
║  Claude Max 5X Usage Report                  ║
╠══════════════════════════════════════════════════════╣
║  Reset:  2026-02-09 14:00                           ║
║  Budget:   41,666,700 credits/week                ║
║  Used:      1,819,685 credits (4.4%)             ║
║  Remain:   39,847,015 credits                     ║
║  Turns:           253                             ║
╠──────────────────────────────────────────────────────╣
║  5h window:  1,814,155 /  3,300,000 (55.0%)  ⚡ Watch it  ║
╚══════════════════════════════════════════════════════╝

  Weekly: [█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 4.4%
  5h:     [█████████████████████░░░░░░░░░░░░░░░░░░░] 55.0%
```

## Credits Formula

| Model  | Input rate | Output rate |
|--------|-----------|-------------|
| Haiku  | 2/15      | 10/15       |
| Sonnet | 6/15      | 30/15       |
| Opus   | 10/15     | 50/15       |

Cache reads are **free** on subscription plans. Non-Claude models don't consume Claude credits.

## Plans

| Plan | $/month | Credits/5h | Credits/week |
|------|---------|-----------|-------------|
| Pro  | $20     | 550,000   | 5,000,000   |
| 5×   | $100    | 3,300,000 | 41,666,700  |
| 20×  | $200    | 11,000,000| 83,333,300  |

## Requirements

- Python 3.9+
- OpenClaw with session JSONL transcripts

## License

MIT
