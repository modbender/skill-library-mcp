# cdp-browser

CDP browser control skill for OpenClaw. CLI for Chrome/Chromium at localhost:9222.

**Repo:** https://github.com/gostlightai/cdp-browser

## Install

```bash
cd skills/cdp-browser
npm install
```

## Prerequisites

Chromium running with `--remote-debugging-port=9222` (Docker Compose or local Chrome).

## Usage

See [SKILL.md](SKILL.md) for commands and usage. Run `bin/` scripts from the skill dir.

## Config (Telegram confirm button)

To enable the "Confirm Post" inline button in Telegram, copy the example config:

```bash
cp ~/.openclaw/workspace/skills/cdp-browser/.cdp-browser.json.example ~/.openclaw/workspace/.cdp-browser.json
```

Without it, tweet-draft works but the agent sends plain text only; user confirms via "go ahead" in chat.

## Tweet flow

- **tweet-draft** — fills compose only (safe default)
- **tweet-post** — requires `--confirm` as second arg; posts only when user approves

## Security

See [SECURITY.md](SECURITY.md) for security considerations and mitigations.
