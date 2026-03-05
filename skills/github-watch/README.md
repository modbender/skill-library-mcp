# 🐙 openclaw-skill-github-watch

> OpenClaw skill - Weekly GitHub digest for sysops/DevOps engineers

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-skill-blue)](https://openclaw.ai)
[![ClawHub](https://img.shields.io/badge/ClawHub-github--watch-green)](https://clawhub.com/skills/github-watch)

Automated weekly GitHub digest tailored for sysops/DevOps engineers. Fetches GitHub Trending repos and `topic:sysops` / `topic:devops` repos, scores them via LLM against a sysops/DevOps relevance profile, deduplicates across weeks, and dispatches a formatted HTML email + Markdown to Nextcloud. Uses `requests` and `beautifulsoup4` for fetching; dispatch delegates to [mail-client](https://github.com/Rwx-G/openclaw-skill-mail-client) and [nextcloud-files](https://github.com/Rwx-G/openclaw-skill-nextcloud) skills.

## Install

```bash
clawhub install github-watch
```

Or manually:

```bash
git clone https://github.com/Rwx-G/openclaw-skill-github-watch \
  ~/.openclaw/workspace/skills/github-watch
pip3 install requests beautifulsoup4
```

## Setup

```bash
python3 scripts/setup.py    # configure token path, recipient, outputs
```

You'll need a GitHub **Personal Access Token** (read-only public repos) to raise rate limits. Create one at GitHub → Settings → Developer settings → Personal access tokens → Fine-grained (no scopes needed for public repos).

## What it does

Each week the agent:

| Step | Description |
|------|-------------|
| Fetch | GitHub Trending (weekly) + `topic:sysops` + `topic:devops` via API |
| Filter | Excludes repos already seen in previous digests |
| Score | LLM scoring against sysops/DevOps profile (see `references/scoring_guide.md`) |
| Select | Up to 6 trending + 6 sysops/devops + 3 highlights |
| Dispatch | HTML email via mail-client skill + Markdown to Nextcloud + Telegram notification |

### Scoring profile

Kept: infra, containers, k8s, monitoring, CI/CD, system security, networking, IaC, shell, automation.
Discarded: front-end, mobile, gaming, pure data science, generic LLM wrappers.

External content is wrapped in untrusted blocks before LLM scoring to prevent prompt injection from malicious repo descriptions.

## Configuration

Config is stored at `~/.openclaw/config/github-watch/config.json` and survives `clawhub update`.

```json
{
  "token_path": "~/.openclaw/secrets/github_token",
  "recipient": "you@example.com",
  "nc_path": "/Jarvis/github-watch.md",
  "outputs": ["email", "nextcloud"],
  "since": "weekly"
}
```

| Field | Default | Description |
|-------|---------|-------------|
| `token_path` | `~/.openclaw/secrets/github_token` | Path to GitHub PAT (plain text file) |
| `recipient` | — | Email address for the digest |
| `nc_path` | `/Jarvis/github-watch.md` | Nextcloud path for Markdown output |
| `outputs` | `["email", "nextcloud"]` | Active outputs — remove any you don't use |
| `since` | `weekly` | Trending window: `daily`, `weekly`, `monthly` |

A `config.example.json` with safe defaults is included as reference.

## Storage

- Config: `~/.openclaw/config/github-watch/config.json`
- Seen repos: `~/.openclaw/data/github-watch/seen.json`

No credentials stored — GitHub token read from `token_path` at runtime.

## Requirements

- Python 3.10+
- `requests`, `beautifulsoup4` (`pip3 install requests beautifulsoup4`)
- GitHub PAT (optional, recommended)
- [mail-client](https://github.com/Rwx-G/openclaw-skill-mail-client) skill for email output
- [nextcloud-files](https://github.com/Rwx-G/openclaw-skill-nextcloud) skill for Nextcloud output

## Documentation

- [SKILL.md](SKILL.md) - full skill instructions, pipeline, CLI reference
- [references/scoring_guide.md](references/scoring_guide.md) - LLM scoring criteria and output format

## License

[MIT](LICENSE)
