---
name: browser-playwright-bridge
description: "Run Playwright scripts that share OpenClaw browser's login state
  via CDP, with automatic conflict avoidance. Use when: (1) recording browser
  tool operations as reusable Playwright scripts, (2) running headless
  automation that needs existing cookies/sessions, (3) scheduling browser tasks
  in cron without CDP conflicts, (4) converting exploratory browser tool
  workflows into zero-token repeatable scripts."
---


# Browser ↔ Playwright Bridge

OpenClaw's browser tool and external Playwright scripts cannot share the same CDP connection simultaneously. This skill provides a lock-based bridge: stop OpenClaw browser → run Playwright with the same Chrome profile (cookies/login intact) → release for OpenClaw to reconnect.

## Architecture

```
Chrome (CDP port)  ←  shared user-data-dir (~/.openclaw/browser/openclaw/user-data)
       ↕ mutually exclusive
┌──────────────┐    ┌──────────────────┐
│ OpenClaw     │ OR │ Playwright script │
│ browser tool │    │ (zero token cost) │
└──────────────┘    └──────────────────┘
       ↕ managed by browser-lock.sh
```

## Setup

1. Install Playwright in the workspace (once):

```bash
cd <workspace> && npm install playwright
```

> **Note:** `npx playwright install` is NOT needed. Playwright connects to the existing Chrome via CDP — no local browser download required.

2. Copy `scripts/browser-lock.sh` to your workspace `scripts/` directory:

```bash
chmod +x scripts/browser-lock.sh
```

## Discovering the CDP Port

The CDP port is dynamically assigned. **Never hardcode it.** Use `discoverCdpUrl()` (see below) or the shell equivalent in `browser-lock.sh`.

Shell one-liner:

```bash
ps aux | grep 'remote-debugging-port=' | grep -v grep | grep -o 'remote-debugging-port=[0-9]*' | head -1 | cut -d= -f2
```

Verify CDP is responding:

```bash
curl -s --max-time 1 http://127.0.0.1:<port>/json/version
```

## Usage

### Run a Playwright script (recommended)

```bash
./scripts/browser-lock.sh run scripts/my-task.js [args...]
./scripts/browser-lock.sh run --timeout 120 scripts/my-task.js  # custom timeout
```

Default timeout: 300s. If the script exceeds it, the watchdog kills it and releases the lock.

This automatically: checks lock → stops OpenClaw browser → starts Chrome with CDP → runs script → cleans up → releases lock.

### Manual acquire/release

```bash
./scripts/browser-lock.sh acquire    # stop OpenClaw browser, start Chrome
node scripts/my-task.js              # run script(s)
./scripts/browser-lock.sh release    # kill Chrome, release lock
```

### Check status

```bash
./scripts/browser-lock.sh status
```

## Writing Playwright Scripts

Use `scripts/playwright-template.js` as starting point.

### CDP Discovery Helper

All scripts should use `discoverCdpUrl()` instead of hardcoding a port:

```javascript
const { execSync } = require('child_process');

/**
 * Discover the CDP URL by inspecting Chrome process args.
 * Falls back to CDP_PORT env var, then probes common ports.
 */
function discoverCdpUrl() {
  // Method 1: extract from running Chrome process
  try {
    const ps = execSync(
      "ps aux | grep 'remote-debugging-port=' | grep -v grep",
      { encoding: 'utf8', timeout: 3000 }
    );
    const match = ps.match(/remote-debugging-port=(\d+)/);
    if (match) return `http://127.0.0.1:${match[1]}`;
  } catch {}

  // Method 2: CDP_PORT env var
  if (process.env.CDP_PORT) {
    return `http://127.0.0.1:${process.env.CDP_PORT}`;
  }

  // Method 3: probe common ports
  // 18800 is the typical OpenClaw default; others are common CDP conventions
  const { execSync: probe } = require('child_process');
  for (const port of [18800, 9222, 9229]) {
    try {
      probe(`curl -s --max-time 1 http://127.0.0.1:${port}/json/version`, {
        encoding: 'utf8', timeout: 2000
      });
      return `http://127.0.0.1:${port}`;
    } catch {}
  }

  throw new Error('CDP port not found. Is Chrome running with --remote-debugging-port?');
}
```

### Script Pattern

```javascript
const { chromium } = require('playwright');

async function main() {
  let browser;
  try {
    browser = await chromium.connectOverCDP(discoverCdpUrl());
  } catch (e) {
    console.error('❌ Cannot connect to Chrome CDP:', e.message);
    console.error('   Ensure browser-lock.sh acquire was called, or Chrome is running with --remote-debugging-port');
    process.exit(1);
  }

  const context = browser.contexts()[0]; // reuse existing context (cookies!)
  const page = await context.newPage();

  try {
    // ====== Your automation here ======
    await page.goto('https://example.com');
    console.log('Title:', await page.title());
    // ==================================
  } catch (e) {
    console.error('❌ Script error:', e.message);
    throw e;
  } finally {
    await page.close();     // close only your tab
    // NEVER call browser.close() — it kills the entire Chrome
  }
}

main().then(() => process.exit(0)).catch(e => {
  console.error('❌', e.message);
  process.exit(1);
});
```

**Critical rules:**
- `browser.contexts()[0]` — reuse the existing context to inherit cookies/login
- `page.close()` only — **never `browser.close()`**
- Always `process.exit(0)` on success — Playwright keeps event loops alive otherwise
- Wrap `connectOverCDP` in try-catch — fail fast with a clear message

## Workflow: Explore → Record → Replay

1. **Explore** — Use OpenClaw browser tool (snapshot/act) to figure out a new workflow
2. **Record** — Ask the agent to convert the steps into a Playwright script
3. **Replay** — Run via `browser-lock.sh run` — zero token cost, deterministic

## Cron / Scheduled Tasks

In cron tasks, call browser-lock.sh directly:

```bash
cd /path/to/workspace && ./scripts/browser-lock.sh run scripts/publish-task.js
```

The lock file (`/tmp/openclaw-browser.lock`) prevents concurrent browser access. If a lock is stale (owner process dead), it auto-recovers.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `Lock held by PID xxx` | `./scripts/browser-lock.sh release` to force-release |
| Playwright connectOverCDP timeout | Ensure OpenClaw browser is stopped first (`acquire` does this) |
| `CDP port not found` | Chrome isn't running; call `browser-lock.sh acquire` first |
| `openclaw browser stop` doesn't kill Chrome | Known issue; browser-lock.sh kills the process directly |
| Script hangs after completion | Add `process.exit(0)` at the end |
| Login expired | Use OpenClaw browser tool to re-login, then run scripts again |

## Environment Variables

| Var | Default | Description |
|-----|---------|-------------|
| `CDP_PORT` | auto-discover | Override CDP port (skips process detection) |
| `CHROME_BIN` | auto-detect | Path to Chrome/Chromium binary |
| `HEADLESS` | auto | Set `true`/`1` to force headless; `false`/`0` to force headed. Auto-detects on Linux without DISPLAY |
