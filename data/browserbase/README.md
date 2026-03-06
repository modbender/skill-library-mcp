# Browserbase Sessions — OpenClaw Skill

A production-ready OpenClaw skill for creating and managing persistent Browserbase
cloud browser sessions with authentication persistence, automatic captcha solving,
session recording, and screenshot capture.

## What it does

This skill gives the OpenClaw agent the ability to:

- **Create cloud browser sessions** via Browserbase's infrastructure
- **Persist authentication** across sessions using Contexts (cookies, local storage,
  session storage are saved and restored automatically)
- **Solve CAPTCHAs automatically** — login flows and protected pages work without
  manual intervention (enabled by default)
- **Record sessions as video** — every session is recorded for later download and
  sharing (enabled by default)
- **Take screenshots** — viewport or full-page, during navigation or on demand
- **Reconnect to keep-alive sessions** that survive disconnections
- **Automate browsing** — navigate, execute JavaScript, extract page content, read cookies
- **Manage session lifecycle** — list, inspect, and terminate sessions

## Requirements

- Python 3.9+
- `browserbase` Python package
- `playwright` Python package + Chromium browser
- A Browserbase account with API key and project ID

## Quick Start

### 1. Copy the skill to your OpenClaw skills directory

```bash
cp -r browserbase-sessions/ ~/.openclaw/workspace/skills/browserbase-sessions/
```

### 2. Install dependencies

```bash
cd ~/.openclaw/workspace/skills/browserbase-sessions/scripts
pip install -r requirements.txt
playwright install chromium
```

### 3. Set credentials

```bash
export BROWSERBASE_API_KEY="bb_live_your_key_here"
export BROWSERBASE_PROJECT_ID="your-project-uuid-here"
```

### 4. Run the setup test

```bash
python3 ~/.openclaw/workspace/skills/browserbase-sessions/scripts/browserbase_manager.py setup
```

This validates everything end-to-end: credentials, SDK, Playwright, API connection, and runs a live smoke test (creates a session, navigates to example.com, terminates).

## Available Commands

| Command | Description |
|---|---|
| `setup` | Validate credentials and run full smoke test |
| `create-context` | Create a persistent context (with optional `--name`) |
| `delete-context` | Delete a context |
| `list-contexts` | List saved named contexts |
| `create-session` | Create a browser session (captchas + recording ON by default) |
| `list-sessions` | List all sessions |
| `get-session` | Get session details |
| `terminate-session` | Terminate a running session |
| `navigate` | Navigate to a URL (with optional screenshot and text extraction) |
| `screenshot` | Take a screenshot of the current page |
| `execute-js` | Execute JavaScript in a session |
| `get-cookies` | Get cookies from a session |
| `get-recording` | Download session recording video |
| `get-logs` | Get session logs |
| `live-url` | Get live debug URL for a running session |

## Key Design Decisions

**Captcha solving ON by default.** Browserbase's captcha solver handles reCAPTCHA,
hCaptcha, and other challenges automatically. This means login flows and protected
pages work without manual intervention. Disable with `--no-solve-captchas`.

**Recording ON by default.** Every session is recorded as a video. After terminating
a session, download the recording with `get-recording` to review or share. Disable
with `--no-record`.

**Named contexts.** Instead of remembering UUIDs, name your contexts (`--name github`,
`--name slack`) and reference them by name anywhere a context ID is expected.

**Keep-alive for research.** Set `--keep-alive` for long research sessions. The browser
survives network disconnections and persists until explicitly terminated — up to 6 hours.

## Architecture

This skill follows the AgentSkills open standard (agentskills.io):

- `SKILL.md` — Instructions the agent reads on-demand
- `scripts/browserbase_manager.py` — CLI tool the agent executes via bash
- `references/api-quick-ref.md` — API reference for deeper details

## License

MIT
