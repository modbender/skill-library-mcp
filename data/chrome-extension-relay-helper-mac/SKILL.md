---
name: OpenClaw Chrome Relay Helper - Mac
description: Attach the OpenClaw Browser Relay Chrome extension to a live tab so the browser tool (profile="chrome") works. Use this skill before any browser automation that requires Chrome extension relay access on macOS. Handles kill/launch/maximize/attach and verifies state via Peekaboo accessibility — no hardcoded coordinates, works at any screen size.
---

# OpenClaw Chrome Relay Helper - Mac

Automates attaching the **OpenClaw Browser Relay** Chrome extension to a live tab on macOS. Once attached, the `browser(profile="chrome")` tool works — you can navigate, snapshot, click, and scrape using your real Chrome session.

**macOS only.** Requires Peekaboo (macOS UI automation CLI).

## Quickstart

```bash
bash <skill-dir>/scripts/attach.sh
```

Outputs one of:
- `ALREADY_ATTACHED` — already connected, nothing to do
- `ATTACHED` — freshly connected, ready to use
- `FAILED: <reason>` — check `~/.openclaw/media/relay-attach-fail.png` for a debug screenshot

Then navigate and automate:
```python
browser(action="navigate", profile="chrome", targetUrl="https://example.com")
browser(action="snapshot", profile="chrome", compact=True)  # read page content
```

**Typical wall time: ~29s on a clean launch.**

## Prerequisites

### 1. Peekaboo (macOS UI automation CLI)

```bash
brew install steipete/tap/peekaboo
```

Peekaboo reads Chrome's accessibility tree to find the extension icon by description — no pixel coordinates needed.

### 2. Accessibility permission for `node`

Go to **System Settings → Privacy & Security → Accessibility** and add your `node` binary. Without this, Peekaboo cannot send click events.

Find your node path with: `which node`

### 3. openclaw.json browser profile

Add this to your `~/.openclaw/openclaw.json`:

```json
"browser": {
  "profiles": {
    "chrome": {
      "cdpUrl": "http://127.0.0.1:18792",
      "driver": "extension",
      "color": "#FF5A36"
    }
  }
}
```

Restart the gateway after editing: `openclaw gateway restart`

### 4. Extension loaded and pinned in Chrome

The OpenClaw Browser Relay extension must be loaded as an unpacked extension in Chrome. It's included with OpenClaw at:
```
~/.openclaw/browser/chrome-extension
```

Load it via `chrome://extensions` → **Developer mode ON** → **Load unpacked**.

**The extension must also be pinned to the toolbar.** The script finds the icon via Chrome's accessibility tree, which only exposes toolbar-pinned extensions — not icons hidden inside the Extensions panel. To pin: click the puzzle-piece icon → click the pin icon next to "OpenClaw Browser Relay".

## How it works

The script finds the extension icon using Chrome's **accessibility tree** — not pixel coordinates. The icon's description changes based on state:

- **Detached:** `"OpenClaw Browser Relay (click to attach/detach)"`
- **Attached:** `"OpenClaw Browser Relay: attached (click to detach)"`

Peekaboo scans for a `pop-up button` element whose description starts with `"OpenClaw Browser Relay"`, determines state, and clicks to attach if needed. Retries up to 8× (every 2s) to handle slow Chrome startup.

Window maximize is required before scanning — Chrome's toolbar icons are not visible in the accessibility tree on a small or default-sized window.

## What the script does (step by step)

1. **Fast path** — if Chrome is running and badge already shows "attached", exits immediately (~2s)
2. Kill any running Chrome instance
3. Patch `~/Library/Application Support/Google/Chrome/Default/Preferences` to suppress the "Restore Pages?" dialog on relaunch
4. Open Chrome to `https://info.cern.ch/` — the world's first website, a 428-byte static HTML file with zero anti-bot tech, JS, cookies, or Cloudflare
5. Maximize the window via Peekaboo (required for toolbar visibility)
6. Scan accessibility tree for the extension icon (retries up to 8×, 2s apart)
7. Click the icon to attach
8. Verify state changed to "attached" before returning

## Known pitfalls

| Approach | Why it doesn't work |
|---|---|
| Hardcoded pixel coordinates | Breaks at any screen size other than what they were measured on |
| AppleScript `keystroke` with Ctrl+Shift | Modifier keys are silently dropped — only the bare key fires |
| Chrome extension keyboard shortcut | The extension manifest has no `commands` — shortcuts don't trigger attach |
| Vision model to locate icon | Not reliable enough for toolbar UI at any resolution |
| Skipping window maximize | Toolbar icons don't appear in the accessibility tree on a small window |
| Extension not pinned to toolbar | Unpinned extensions are hidden inside the Extensions panel — not visible in the accessibility tree |
| Wrong profile name or port in config | `browser(profile="chrome")` requires the profile named exactly `chrome` pointing to port `18792` |

## Token efficiency tips

```python
# ✅ Use snapshot for reading page content (~3k tokens)
browser(action="snapshot", profile="chrome", compact=True)

# ❌ Avoid screenshot + vision for UI element detection
# → Unreliable for toolbar/coordinate identification
# → 10–50x more expensive than snapshot
```

## Integration pattern

Any skill that needs Chrome relay should call this first:

```bash
# 1. Attach
bash <path-to-chrome-relay>/scripts/attach.sh

# 2. Navigate
browser(action="navigate", profile="chrome", targetUrl="https://target.com")

# 3. Automate
browser(action="snapshot", profile="chrome", compact=True)
browser(action="act", profile="chrome", request={kind: "click", ref: "..."})
```
