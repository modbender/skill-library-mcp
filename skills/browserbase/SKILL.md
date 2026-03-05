---
name: browserbase-sessions
description: Create and manage persistent Browserbase cloud browser sessions with authentication persistence. Use when the user needs to automate browsers, maintain logged-in sessions across interactions, scrape authenticated pages, or manage cloud browser instances. Handles session creation, context-based auth persistence, keep-alive reconnection, captcha solving, session recording, screenshots, and session cleanup.
license: MIT
metadata:
  author: custom
  version: "2.0.0"
  openclaw:
    emoji: "🌐"
    requires:
      bins: ["python3"]
      anyBins: ["uv", "pip"]
      env: ["BROWSERBASE_API_KEY", "BROWSERBASE_PROJECT_ID"]
    primaryEnv: "BROWSERBASE_API_KEY"
---

# Browserbase Sessions Skill

Manage persistent cloud browser sessions via Browserbase. This skill creates browser sessions that preserve authentication (cookies, local storage) across interactions, automatically solve CAPTCHAs, and record sessions for later review.

## First-Time Setup

### Step 1 — Get your Browserbase credentials

1. Sign up at [browserbase.com](https://www.browserbase.com/) if you haven't already.
2. Go to **Settings → API Keys** and copy your API key (starts with `bb_live_`).
3. Go to **Settings → Project** and copy your Project ID (a UUID).

### Step 2 — Install dependencies

```bash
cd {baseDir}/scripts && pip install -r requirements.txt
playwright install chromium
```

Or with uv:

```bash
cd {baseDir}/scripts && uv pip install -r requirements.txt
uv run playwright install chromium
```

### Step 3 — Set environment variables

```bash
export BROWSERBASE_API_KEY="bb_live_your_key_here"
export BROWSERBASE_PROJECT_ID="your-project-uuid-here"
```

Or configure via OpenClaw's `skills.entries.browserbase-sessions.env` in `~/.openclaw/openclaw.json`.

### Step 4 — Run the setup test

This validates everything end-to-end (credentials, SDK, Playwright, API connection, and a live smoke test):

```bash
python3 {baseDir}/scripts/browserbase_manager.py setup
```

You should see `"status": "success"` with all steps passing. If any step fails, the error message tells you exactly what to fix.

## Defaults

Every session is created with these defaults to support research workflows:

- **Captcha solving: ON** — Browserbase automatically solves CAPTCHAs so login flows and protected pages work without manual intervention. Disable with `--no-solve-captchas`.
- **Session recording: ON** — Every session is recorded as a video you can download later for review or sharing. Disable with `--no-record`.
- **Auth persistence** — Use contexts with `--persist` to stay logged in across sessions.

## Available Commands

All commands are run via the manager script:

```bash
python3 {baseDir}/scripts/browserbase_manager.py <command> [options]
```

### Setup & Validation

Run the full setup test:
```bash
python3 {baseDir}/scripts/browserbase_manager.py setup
```

### Context Management (for authentication persistence)

Create a named context to store login state:
```bash
python3 {baseDir}/scripts/browserbase_manager.py create-context --name github
```

List all saved contexts:
```bash
python3 {baseDir}/scripts/browserbase_manager.py list-contexts
```

Delete a context (by name or ID):
```bash
python3 {baseDir}/scripts/browserbase_manager.py delete-context --context-id github
```

### Session Lifecycle

Create a new session (captcha solving and recording enabled by default):
```bash
# Basic session
python3 {baseDir}/scripts/browserbase_manager.py create-session

# Session with saved context (persist=true saves cookies on close)
python3 {baseDir}/scripts/browserbase_manager.py create-session --context-id github --persist

# Keep-alive session for long research (survives disconnections)
python3 {baseDir}/scripts/browserbase_manager.py create-session --context-id github --persist --keep-alive --timeout 3600

# Full options
python3 {baseDir}/scripts/browserbase_manager.py create-session \
  --context-id github \
  --persist \
  --keep-alive \
  --timeout 3600 \
  --region us-west-2 \
  --proxy \
  --block-ads \
  --viewport-width 1280 \
  --viewport-height 720
```

List all sessions:
```bash
python3 {baseDir}/scripts/browserbase_manager.py list-sessions
python3 {baseDir}/scripts/browserbase_manager.py list-sessions --status RUNNING
```

Get session details:
```bash
python3 {baseDir}/scripts/browserbase_manager.py get-session --session-id <id>
```

Terminate a session:
```bash
python3 {baseDir}/scripts/browserbase_manager.py terminate-session --session-id <id>
```

### Browser Automation

Navigate to a URL:
```bash
# Navigate and get page title
python3 {baseDir}/scripts/browserbase_manager.py navigate --session-id <id> --url "https://example.com"

# Navigate and extract text
python3 {baseDir}/scripts/browserbase_manager.py navigate --session-id <id> --url "https://example.com" --extract-text

# Navigate and save screenshot
python3 {baseDir}/scripts/browserbase_manager.py navigate --session-id <id> --url "https://example.com" --screenshot /tmp/page.png

# Navigate and take full-page screenshot
python3 {baseDir}/scripts/browserbase_manager.py navigate --session-id <id> --url "https://example.com" --screenshot /tmp/full.png --full-page
```

Take a screenshot of the current page (without navigating):
```bash
python3 {baseDir}/scripts/browserbase_manager.py screenshot --session-id <id> --output /tmp/current.png
python3 {baseDir}/scripts/browserbase_manager.py screenshot --session-id <id> --output /tmp/full.png --full-page
```

Execute JavaScript:
```bash
python3 {baseDir}/scripts/browserbase_manager.py execute-js --session-id <id> --code "document.title"
```

Get cookies:
```bash
python3 {baseDir}/scripts/browserbase_manager.py get-cookies --session-id <id>
```

### Recordings, Logs & Debug

Download a session recording video (session must be terminated first):
```bash
python3 {baseDir}/scripts/browserbase_manager.py get-recording --session-id <id> --output /tmp/session.webm
```

Get session logs:
```bash
python3 {baseDir}/scripts/browserbase_manager.py get-logs --session-id <id>
```

Get the live debug URL (for visual inspection of a running session):
```bash
python3 {baseDir}/scripts/browserbase_manager.py live-url --session-id <id>
```

## Common Workflows

### Workflow 1: Multi-session research with persistent login

```bash
# 1. One-time: create a named context for the site
python3 {baseDir}/scripts/browserbase_manager.py create-context --name myapp

# 2. Start a research session (captchas auto-solved, recording on)
python3 {baseDir}/scripts/browserbase_manager.py create-session --context-id myapp --persist --keep-alive --timeout 3600

# 3. Navigate to login — captchas solved automatically
python3 {baseDir}/scripts/browserbase_manager.py navigate --session-id <id> --url "https://myapp.com/login"
# Use execute-js to fill forms and submit

# 4. Do research, take screenshots
python3 {baseDir}/scripts/browserbase_manager.py navigate --session-id <id> --url "https://myapp.com/dashboard" --extract-text
python3 {baseDir}/scripts/browserbase_manager.py screenshot --session-id <id> --output /tmp/dashboard.png

# 5. Terminate (cookies saved to context)
python3 {baseDir}/scripts/browserbase_manager.py terminate-session --session-id <id>

# 6. Download recording to share
python3 {baseDir}/scripts/browserbase_manager.py get-recording --session-id <id> --output /tmp/research.webm

# 7. Next day: new session, already logged in!
python3 {baseDir}/scripts/browserbase_manager.py create-session --context-id myapp --persist --keep-alive --timeout 3600
```

### Workflow 2: Screenshot documentation

```bash
python3 {baseDir}/scripts/browserbase_manager.py create-session
python3 {baseDir}/scripts/browserbase_manager.py navigate --session-id <id> --url "https://docs.example.com" --screenshot /tmp/docs_home.png
python3 {baseDir}/scripts/browserbase_manager.py navigate --session-id <id> --url "https://docs.example.com/api" --screenshot /tmp/docs_api.png --full-page
python3 {baseDir}/scripts/browserbase_manager.py terminate-session --session-id <id>
```

### Workflow 3: Record and share a walkthrough

```bash
# Session recording is ON by default
python3 {baseDir}/scripts/browserbase_manager.py create-session --context-id myapp --persist
# ... do your walkthrough (navigate, click, etc.) ...
python3 {baseDir}/scripts/browserbase_manager.py terminate-session --session-id <id>
# Download the video
python3 {baseDir}/scripts/browserbase_manager.py get-recording --session-id <id> --output /tmp/walkthrough.webm
```

## Important Notes

- **Captcha solving is ON by default.** Browserbase handles CAPTCHAs automatically during login flows and page loads. Use `--no-solve-captchas` to disable.
- **Recording is ON by default.** Every session is recorded. Download with `get-recording` after termination. Use `--no-record` to disable.
- **Connection timeout**: 5 minutes to connect after creation before auto-termination.
- **Keep-alive sessions** survive disconnections and must be explicitly terminated.
- **Context persistence**: Wait a few seconds after `terminate-session --persist` before creating a new session with the same context.
- **Named contexts**: Use `--name` with `create-context` to save friendly names (e.g. `github`, `slack`). Use the name anywhere a context ID is expected.
- **One context per site**: Use separate contexts for different authenticated sites.
- **Avoid concurrent sessions on the same context**.
- **Regions**: us-west-2 (default), us-east-1, eu-central-1, ap-southeast-1.
- **Session timeout**: 60–21600 seconds (max 6 hours).

## Error Handling

All commands return JSON output. On error, the output includes an `"error"` key. Common errors:
- `APIConnectionError`: Browserbase API unreachable
- `RateLimitError`: Too many concurrent sessions for your plan
- `APIStatusError`: Invalid parameters or authentication failure
- Missing env vars: Set `BROWSERBASE_API_KEY` and `BROWSERBASE_PROJECT_ID`

## Reference

For full API details, read `{baseDir}/references/api-quick-ref.md`.
