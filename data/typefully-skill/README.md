# Typefully Skill for OpenClaw

Create, schedule, and manage [Typefully](https://typefully.com) drafts from your AI agent. Supports single tweets, threads, and multi-platform posts (X, LinkedIn, Threads, Bluesky, Mastodon).

## Prerequisites

- **curl** — HTTP client
- **python3** — used for JSON escaping
- **pass** (optional) — [Unix password store](https://www.passwordstore.org/) for API key/config. Not needed if using environment variables.

## Setup

1. Get your Typefully API key from **Settings → API** in Typefully
2. Provide it via **one of**:
   - Environment variable: `export TYPEFULLY_API_KEY=your-key`
   - Password store: `pass insert typefully/api-key`
3. Install the skill:
   ```bash
   clawhub install typefully --dir ~/.openclaw/skills
   ```

## Usage

```bash
bash scripts/typefully.sh <command> [options]
```

See [SKILL.md](SKILL.md) for the full command reference and examples.

### Quick Examples

```bash
# Simple tweet
bash scripts/typefully.sh create-draft "Just shipped a new feature 🚀"

# Thread
bash scripts/typefully.sh create-draft "First tweet\n---\nSecond tweet" --thread

# Cross-platform
bash scripts/typefully.sh create-draft "Big announcement!" --platform x,linkedin

# Schedule
bash scripts/typefully.sh create-draft "Morning thoughts ☀️" --schedule "2026-03-01T09:00:00Z"

# List drafts
bash scripts/typefully.sh list-drafts draft 5
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `TYPEFULLY_API_KEY` | **(Required)** API key (fallback: `pass typefully/api-key`) |
| `TYPEFULLY_SOCIAL_SET_ID` | *(Optional)* Social set ID — auto-detected if you have one account (fallback: `pass typefully/social-set-id`) |

## License

MIT
