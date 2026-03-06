---
name: regex-visualizer
description: Render Regulex-style railroad diagrams for a JavaScript regular expression and export the exact same SVG/PNG as the Regulex-Plus web UI (docs/index.html) "Export Image" feature. Use when the user provides a regex and wants an image for documentation, sharing, debugging, or embedding; output should match the web UI rendering rather than a re-implemented diagram. Supports flags i/m/g.
---

# Regex Visualizer

## Overview

Export the Regulex-Plus web visualizer output to `*.svg` and/or `*.png` in a single command, using the built-in web UI export logic (no re-drawing).

## Quick Start

Render both SVG and PNG:

```powershell
cd "$env:USERPROFILE\.codex\skills\regex-visualizer"
node scripts/render.mjs `
  --re "hello\\s+world" `
  --flags "i" `
  --out "out/hello-world"
```

```bash
cd ~/.codex/skills/regex-visualizer
node scripts/render.mjs \
  --re 'hello\\s+world' \
  --flags 'i' \
  --out 'out/hello-world'
```

SVG only:

```powershell
cd ~/.codex/skills/regex-visualizer
node scripts/render.mjs `
  --re "^(a|b)*?$" `
  --out "out/re" `
  --svg-only
```

PNG only:

```powershell
cd ~/.codex/skills/regex-visualizer
node scripts/render.mjs `
  --re "^(a|b)*?$" `
  --out "out/re" `
  --png-only
```

## Install Dependencies

This skill uses `puppeteer-core` (does not bundle Chromium). Install once:

```bash
cd ~/.codex/skills/regex-visualizer
npm install
```

## Screenshot

An example export generated using the built-in web UI rendering:
- `assets/example.png`
- `assets/example.svg`

## Behavior

- Uses `assets/regulex.html` (a copy of the Regulex-Plus web UI) and loads it with `#!cmd=export&flags=...&re=...`.
- Waits for the page to produce the exported canvas (`canvas.exportCanvas`) and then writes:
  - `<out>.png` from the same canvas as the web UI "Export Image" button
  - `<out>.svg` from the same `<svg>` element used by the web UI

## Notes

- Flags are limited to what the web UI supports by default: `i`, `m`, `g`.
- If the regex fails to parse, the script surfaces the same error text shown in the UI.

## Resources

### scripts/
- `scripts/render.mjs`: Headless export to SVG/PNG via the built-in `cmd=export` mode.

### references/
None.

### assets/
- `assets/regulex.html`: Copy of `Regulex-Plus/docs/index.html` used for rendering/export.

---
