---
name: x-actionbook-recap
description: Collect, scroll, extract, and summarize recent X (Twitter) posts for any handle (optionally filtered by keyword search) using the Actionbook Rust CLI (actionbook-rs) workflow (open → snapshot/accessibility tree → extract `article` text). Use when asked to analyze a handle over a time window (e.g., last 7 days), produce Chinese working notes, and publish a neutral English recap (single post or thread) from a specified account.
---

# X recap via actionbook-rs

## What this skill is for

Produce a **repeatable** “collect → extract → summarize → publish” workflow for **any X handle** (optionally with a keyword) using the **actionbook-rs** approach:

1) `actionbook browser open` the profile/search page
2) `actionbook browser snapshot` to get the accessibility tree (incl. `article` nodes)
3) (optional) `actionbook browser eval` to scroll
4) extract post text from `article` blocks
5) analyze + draft output (Chinese internal notes; English publish)
6) publish on X (neutral tone; optionally attach an image)

## Guardrails

- Infinite scroll is not exhaustive; be explicit about coverage limits.
- Don’t quote “recent interviews” unless the user provides exact links/timestamps.
- Publishing is external action: confirm the target account + final copy before posting.

## Workflow

### 1) Collect posts (Actionbook)

Pick one entry point:
- Profile: `https://x.com/<handle>`
- Search (keyword + optional recency): `https://x.com/search?q=from%3A<handle>%20<keyword>&src=typed_query&f=live`

Commands (example):

```bash
# open (profile)
actionbook browser open "https://x.com/<handle>"

# snapshot (repeat after each scroll)
actionbook browser snapshot --refs aria --depth 18 --max-chars 12000

# scroll a bit
actionbook browser eval "window.scrollBy(0, 2200)"
```

Extraction heuristic:
- In snapshots, locate `article` nodes that contain the post text.
- Record for each post:
  - text (verbatim)
  - timestamp shown (relative or absolute)
  - URL if present
  - whether it’s a repost/quote (note it)

Stop condition:
- You have enough coverage for the user’s time window (e.g., 7 days) OR diminishing returns.

### 2) Summarize (Chinese notes)

Write a compact Chinese working summary:
- themes (3–6 bullets)
- representative posts (links)
- what’s missing / uncertainty

### 3) Draft publish copy (English, neutral)

Choose output type:
- **Single post** (≤280 chars) OR
- **Thread** (6–10 parts) if needed

Use neutral framing:
- “Observation from public posts …”
- avoid mind-reading; separate “what he said” from interpretation

Use templates in `references/templates.md`.

### 4) Image (optional but recommended)

Preferred options (no Python required):
- Clean crop of the relevant post (browser screenshot at 1280×720 + zoom)
- A simple HTML/SVG card rendered in browser and screenshotted (see `references/image-card.md`)

### 5) Publish on X

If using OpenClaw browser automation:
- open compose
- paste final English copy
- upload image (if any)
- post / thread

Confirm before posting:
- target handle (e.g., @gblwll)
- final text
- image choice

## Bundled references

- `references/templates.md` — recap + thread templates (English)
- `references/checklist.md` — extraction checklist + caveats
- `references/image-card.md` — HTML/SVG card approach (no Pillow)
