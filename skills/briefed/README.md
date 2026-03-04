# briefed

An AI newsletter intelligence skill for [OpenClaw](https://openclaw.ai).

Fetches your Gmail newsletters daily, uses Claude Haiku to summarise them, and serves a polished local web reader with voting, notes, and interest tracking.

![Briefed reader app](assets/reader/public/icon.svg)

## What it does

- Pulls newsletters from Gmail (filters out transactional email automatically)
- Summarises each one with Claude Haiku — real headlines and bullets, not just subject lines
- Serves a local web app at `localhost:3001` to read, vote, save, and annotate stories
- Sends a daily notification ping when your digest is ready
- Tracks your interests over time based on what you open and upvote

## Installation

1. Download `briefed.skill` from [Releases](../../releases)
2. In OpenClaw: install the skill file
3. Follow the setup steps in `SKILL.md`

## Requirements

- [OpenClaw](https://openclaw.ai)
- [gog (gogcli)](https://github.com/openclaw/gogcli) — Gmail OAuth CLI
- Node.js ≥ 18
- `claude-haiku-4-5` on your OpenClaw models allowlist
- A notification channel (Telegram, Discord, etc.)

## Setup overview

1. Authenticate Gmail with `gog auth login`
2. Deploy the reader app (`npm install`)
3. Set your Gmail account via `NEWSLETTER_ACCOUNT` env var
4. Configure your interest topics
5. Start the reader (or set up a LaunchAgent for auto-start on macOS)
6. Create a daily 7am cron job in OpenClaw

Full instructions in `SKILL.md`.

## License

MIT
