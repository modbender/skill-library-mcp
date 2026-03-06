---
name: browser-automation-ultra
description: "Zero-token browser automation via Playwright scripts with CDP lock management and human-like interaction. Use when: (1) automating any browser-based workflow (publish, login, scrape, fill forms), (2) reducing token cost by converting browser-tool explorations into replayable scripts, (3) avoiding CDP port conflicts between OpenClaw browser and Playwright, (4) needing anti-detection/human-like mouse/keyboard behavior for platforms with bot detection. NOT for: simple URL fetches (use web_fetch instead), tasks that don't need a real browser session."
---

# Browser Automation Ultra

Explore → Record → Replay → Fix. Convert expensive browser-tool interactions into zero-token Playwright scripts that reuse OpenClaw's Chrome session (cookies/login intact).

## Prerequisites

Install Playwright (once per machine):

```bash
npm install -g playwright
# or in workspace: npm init -y && npm install playwright
```

No browser download needed — scripts connect to OpenClaw's existing Chrome via CDP.

## Architecture

```
Chrome user-data: ~/.openclaw/browser/openclaw/user-data
       ↕ shared cookies/login (mutually exclusive CDP)
┌──────────────┐    ┌──────────────────┐
│ browser tool │ OR │ Playwright script │
│ (explore)    │    │ (zero token)      │
└──────────────┘    └──────────────────┘
       ↕ managed by browser-lock.sh
```

Only one CDP client can connect at a time. `browser-lock.sh` handles the mutex.

## Setup

1. Copy `scripts/browser-lock.sh` to your workspace `scripts/` directory
2. Copy `scripts/utils/human-like.js` to your workspace `scripts/browser/utils/`
3. `chmod +x scripts/browser-lock.sh`
4. Create `scripts/browser/` for your automation scripts

## Core Workflow

### 1. Explore (browser tool, costs tokens)

Use the OpenClaw `browser` tool (snapshot/act) to figure out a workflow. Note selectors, page flow, key waits.

### 2. Record (write a Playwright script)

Convert steps into a script. Save to `scripts/browser/<verb>-<target>.js`. Use the template pattern:

```javascript
const { chromium } = require('playwright');
const { humanDelay, humanClick, humanType, humanThink, humanBrowse } = require('./utils/human-like');

function discoverCdpUrl() {
  try {
    const { execSync } = require('child_process');
    const ps = execSync("ps aux | grep 'remote-debugging-port' | grep -v grep", { encoding: 'utf8' });
    const match = ps.match(/remote-debugging-port=(\d+)/);
    return `http://127.0.0.1:${match ? match[1] : '18800'}`;
  } catch { return 'http://127.0.0.1:18800'; }
}

async function main() {
  const browser = await chromium.connectOverCDP(discoverCdpUrl());
  const context = browser.contexts()[0]; // reuse existing context (cookies/login)
  const page = await context.newPage();
  try {
    // automation here — use human-like functions
    await page.goto('https://example.com', { waitUntil: 'networkidle', timeout: 30000 });
    await humanBrowse(page); // simulate looking at the page
    await humanClick(page, 'button.submit');
    await humanType(page, 'input[name="title"]', 'Hello World');
  } finally {
    await page.close(); // NEVER browser.close() — kills entire Chrome
  }
}
main().then(() => process.exit(0)).catch(e => { console.error('❌', e.message); process.exit(1); });
```

### 3. Replay (zero tokens)

```bash
./scripts/browser-lock.sh run scripts/browser/my-task.js [args]
./scripts/browser-lock.sh run --timeout 120 scripts/browser/my-task.js
```

### 4. Fix (on error)

1. Read script error output
2. Re-explore the failing step with `browser` tool (snapshot) to check current UI
3. Update script with corrected selectors/logic
4. Retry

**Never guess fixes blindly. Always re-explore the actual page state.**

## browser-lock.sh

Manages CDP mutex between OpenClaw browser and Playwright scripts.

```bash
./scripts/browser-lock.sh run <script.js> [args]    # acquire → run → release (300s default)
./scripts/browser-lock.sh run --timeout 120 <script> # custom timeout
./scripts/browser-lock.sh acquire                    # manual: stop OpenClaw browser, start Chrome
./scripts/browser-lock.sh release                    # manual: kill Chrome, release lock
./scripts/browser-lock.sh status                     # show state
```

Lock file: `/tmp/openclaw-browser.lock`. Stale locks auto-recover.

## Anti-Detection Rules (MANDATORY)

All scripts **must** use `human-like.js`. See [references/anti-detection.md](references/anti-detection.md) for the full rule set.

Summary of critical rules:

| ❌ Banned | ✅ Required |
|-----------|------------|
| `waitForTimeout(3000)` fixed delays | `humanDelay(2000, 4000)` random range |
| `input.fill(text)` instant fill | `humanType(page, sel, text)` char-by-char with typos |
| `element.click()` teleport click | `humanClick(page, sel)` bezier mouse path + hover |
| Direct page operation after load | `humanBrowse(page)` simulate reading first |
| `nativeSetter.call()` DOM injection | `humanType()` or `humanFillContentEditable()` |
| Fixed cron schedule | `jitterWait(1, 10)` random offset |

**Exception:** `setInputFiles()` for file uploads is allowed (no human simulation possible), but add random delays before/after.

## human-like.js API

| Function | Purpose |
|----------|---------|
| `humanDelay(min, max)` | Random wait (ms) |
| `humanThink(min, max)` | Longer pause before form fills |
| `humanClick(page, sel)` | Bezier mouse move → hover → click with press/release jitter |
| `humanType(page, sel, text, opts)` | Char-by-char typing, normal distribution speed, 3% typo rate |
| `humanFillContentEditable(page, sel, text)` | For contenteditable divs (line-by-line Enter + humanType) |
| `humanBrowse(page, opts)` | Simulate page reading (scroll + mouse wander, 2-5s) |
| `humanScroll(page, opts)` | Random scroll with occasional reverse |
| `jitterWait(minMin, maxMin)` | Random delay in minutes for cron tasks |

## Script Naming Convention

`<verb>-<target>.js` — e.g. `publish-deviantart.js`, `read-inbox.js`, `reply-comment.js`

## Example Scripts

Production-tested scripts in `scripts/examples/`. Copy to your workspace `scripts/browser/` and adapt.

| Script | Platform | Function |
|--------|----------|----------|
| `publish-deviantart.js` | DeviantArt | Upload image, fill title/desc/tags, submit |
| `publish-xiaohongshu.js` | 小红书 | Publish image note with topic tag association via recommend list |
| `publish-pinterest.js` | Pinterest | Create pin with title/desc, select board |
| `publish-behance.js` | Behance | Upload project with title/desc/tags/categories |
| `read-proton-latest.js` | Proton Mail | Read inbox, output JSON list of emails |
| `read-xhs-comments.js` | 小红书 | Read notification comments, output JSON with reply button index |
| `reply-xhs-comment.js` | 小红书 | Reply to a specific comment by index |

Usage pattern:
```bash
# Copy examples to workspace
cp scripts/examples/*.js scripts/browser/
cp scripts/utils/human-like.js scripts/browser/utils/

# Run
./scripts/browser-lock.sh run scripts/browser/publish-deviantart.js image.png "Title" "Description" "tag1,tag2"
./scripts/browser-lock.sh run scripts/browser/read-xhs-comments.js --limit 10
./scripts/browser-lock.sh run scripts/browser/reply-xhs-comment.js 0 "回复文字"
```

All example scripts already use `human-like.js` for anti-detection.

## Cron Integration

```bash
cd /path/to/workspace && ./scripts/browser-lock.sh run scripts/browser/task.js
```

Add `jitterWait()` at script start to randomize execution time.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Lock held by PID xxx | `./scripts/browser-lock.sh release` |
| CDP connection timeout | Ensure `acquire` was called / Chrome is running |
| Login expired | Use browser tool to re-login, then run script |
| Selector not found | Re-explore with browser tool, update script |
| Script timeout | Increase with `--timeout` flag |

## Environment Variables

| Var | Default | Description |
|-----|---------|-------------|
| `CDP_PORT` | auto-discover | Override CDP port |
| `CHROME_BIN` | auto-detect | Chrome binary path |
| `HEADLESS` | auto | `true`/`false` to force headless |
