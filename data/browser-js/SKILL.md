---
name: browser-js
description: Lightweight CDP browser control for AI agents. Token-efficient alternative to the built-in browser tool — 3-10x fewer tokens per interaction. Use when browsing websites, clicking elements, filling forms, uploading files, or extracting page content. Requires a Chrome/Chromium browser running with --remote-debugging-port (OpenClaw browser works out of the box). Signed-in sessions carry over automatically.
---

# browser-js

Lightweight CLI that talks to Chrome via CDP (Chrome DevTools Protocol). Returns minimal, indexed output that agents can act on immediately — no accessibility tree parsing, no ref hunting.

## Setup

```bash
# Install dependency (one-time, in the skill scripts/ dir)
cd scripts && npm install

# Ensure browser is running with CDP enabled.
# With OpenClaw:
#   browser start profile=openclaw
# Or manually:
#   google-chrome --remote-debugging-port=18800 --user-data-dir=~/.browser-data
```

The tool connects to `http://127.0.0.1:18800` by default. Override with `CDP_URL` env var.

## Alias setup (optional)

```bash
mkdir -p ~/.local/bin
cat > ~/.local/bin/bjs << 'WRAPPER'
#!/bin/bash
exec node /path/to/scripts/browser.js "$@"
WRAPPER
chmod +x ~/.local/bin/bjs
```

## Commands

```
bjs tabs                    List open tabs
bjs open <url>              Navigate to URL
bjs tab <index>             Switch to tab
bjs newtab [url]            Open new tab
bjs close [index]           Close tab
bjs elements [selector]     List interactive elements (indexed)
bjs click <index>           Click element by index
bjs type <index> <text>     Type into element
bjs upload <path> [selector] Upload file to input (bypasses OS dialog)
bjs text [selector]         Extract visible page text
bjs html <selector>         Get element HTML
bjs eval <js>               Run JavaScript in page
bjs screenshot [path]       Save screenshot
bjs scroll <up|down|top|bottom> [px]
bjs url                     Current URL
bjs back / forward / refresh
bjs wait <ms>

Coordinate commands (cross-origin iframes, captchas, overlays):
bjs click-xy <x> <y>       Click at page coordinates via CDP Input
bjs click-xy <x> <y> --double   Double-click at coordinates
bjs click-xy <x> <y> --right    Right-click at coordinates
bjs hover-xy <x> <y>       Hover at page coordinates
bjs drag-xy <x1> <y1> <x2> <y2>   Drag between coordinates
bjs iframe-rect <selector> Get iframe bounding box (for click-xy targeting)
```

## How it works

`elements` scans the page for all interactive elements (links, buttons, inputs, selects, etc.) — **including those inside shadow DOM** (web components). This means sites like Reddit, GitHub, and other modern SPAs that use shadow DOM are fully supported. The scan recursively pierces all shadow roots.

Returns a compact numbered list:

```
[0] (link) Hacker News → https://news.ycombinator.com/news
[1] (link) new → https://news.ycombinator.com/newest
[2] (input:text) q
[3] (button) Submit
```

Then `click 3` or `type 2 search query` — immediately actionable, no interpretation needed.

**Auto-indexing:** `click` and `type` auto-index elements if not already indexed. You can skip calling `elements` first and go straight to `click`/`type` after `open`. Call `elements` explicitly when you need to see what's on the page.

**After navigation or AJAX changes:** Elements get re-indexed automatically on next `click`/`type` if stamps are stale. For manual re-index, call `elements` again.

**Real mouse events:** `click` uses CDP `Input.dispatchMouseEvent` (mousePressed + mouseReleased) instead of JS `.click()`. This triggers React/Vue/Angular synthetic event handlers that ignore plain `.click()` calls. Works reliably on SPAs like Instagram, GitHub, LinkedIn.

## File uploads

`upload` uses CDP's `DOM.setFileInputFiles` to inject files directly into hidden `<input type="file">` elements — no OS file picker dialog. Works with Instagram, Twitter, any site with file uploads.

```bash
bjs upload ~/photos/image.jpg                    # auto-finds input[type=file]
bjs upload ~/docs/resume.pdf "input.file-drop"   # specific selector
```

## Token efficiency

| Approach | Tokens per interaction | Notes |
|----------|----------------------|-------|
| **bjs** | ~50-200 | Indexed list, 1-line responses |
| browser tool (snapshot) | ~2,000-5,000 | Full accessibility tree |
| browser tool + thinking | ~3,000-8,000 | Plus reasoning to find refs |

Over a 10-step flow: **~1,500 tokens (bjs) vs ~30,000-80,000 (browser tool)**.

## Typical flow

```bash
bjs open https://example.com       # Navigate
bjs elements                        # See what's clickable
bjs click 5                         # Click element [5]
bjs type 12 "hello world"          # Type into element [12]
bjs text                            # Read page content
bjs screenshot /tmp/result.png      # Verify visually
```

## Shadow DOM support

bjs automatically pierces shadow DOM boundaries. Sites built with web components (Reddit, GitHub, etc.) work out of the box — `elements`, `click`, `type`, and `text` all recurse into shadow roots. No special flags needed.

## Coordinate commands (iframes, captchas, overlays)

When you can't use `click` by index — e.g. the target is inside a **cross-origin iframe** (captcha checkbox, payment form, OAuth widget) — use coordinate-based commands that dispatch real CDP Input events at the OS level. These bypass all DOM boundaries.

**Workflow for clicking inside an iframe:**
```bash
bjs iframe-rect 'iframe[title*="hCaptcha"]'    # Get bounding box
# Output: x=95 y=440 w=302 h=76 center=(246, 478)

bjs click-xy 125 458                            # Click checkbox position
```

`iframe-rect` returns the iframe's position on the page. Add offsets to target specific elements inside it (e.g. a checkbox is typically near the left side).

**Other uses:**
- `hover-xy` — trigger hover menus, tooltips that need mouse position
- `drag-xy` — slider controls, drag-and-drop, canvas interactions
- `click-xy --double` — double-click to select text, expand items
- `click-xy --right` — context menus

**When to use coordinate commands vs `click`:**
- `click <index>` — always preferred when the element shows up in `elements`
- `click-xy` — only when the target is inside a cross-origin iframe or otherwise unreachable by DOM indexing

## Tips

- `elements` with a CSS selector narrows scope: `bjs elements ".modal"`
- `eval` runs arbitrary JS and returns the result — use for custom extraction
- `text` caps at 8KB — enough for most pages, won't blow up context
- `html <selector>` caps at 10KB — for inspecting specific elements
- Pipe through `grep` to filter: `bjs elements | grep -i "submit\|login"`
