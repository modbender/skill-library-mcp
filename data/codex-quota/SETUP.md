# Codex Quota - Setup Instructions

## Prerequisites

### Required Software

- **Python 3** — For running the quota checker script
- **Codex CLI** — OpenAI Codex command-line client (required for `--fresh` and `--all` options)
  - Download from: https://codex.openai.com

No additional Python packages required. The skill uses only Python standard library modules.

### File Access

The skill reads from:
- `~/.codex/sessions/` — Codex session logs containing rate limit data
- `~/.codex/auth.json` — Current Codex authentication (for `--fresh` option)

⚠️ With `--all --yes`, the skill temporarily overwrites `~/.codex/auth.json` to switch between accounts (restored afterwards). Ensure you have saved accounts via the `codex-account-switcher` skill first.

## Configuration

No configuration file needed. The skill works out of the box by reading Codex session files.

### Installation (Optional)

For easier access, add the script to your PATH:

```bash
cp ~/Developer/Skills/codex-quota/codex-quota.py ~/bin/codex-quota
chmod +x ~/bin/codex-quota
```

Then you can run:
```bash
codex-quota
codex-quota --fresh
codex-quota --all --yes
```

## How It Works

Codex CLI logs rate limit information in every session file (`~/.codex/sessions/YYYY/MM/DD/*.jsonl`) as part of `token_count` events. This tool:

1. Finds the most recent session file
2. Extracts the last `rate_limits` object
3. Formats and displays it with:
   - **Primary Window** (5 hours) — Short-term rate limit
   - **Secondary Window** (7 days) — Weekly rate limit
   - Reset times in local timezone with countdown
   - Source session file and age

### Options

- **Default** — Show cached quota from latest session (instant, no API call)
- **`--fresh`** — Ping Codex API first for live data (requires `codex` CLI)
- **`--all --yes`** — Check quota for all saved accounts by temporarily switching between them
- **`--json`** — Output as JSON for programmatic use
