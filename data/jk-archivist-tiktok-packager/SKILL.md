---
name: jk-archivist-tiktok-skill
description: Generate deterministic 6-slide portrait PNG slideshow assets plus caption text for TikTok-style posting workflows, including reusable templates and a strict validation pipeline.
homepage: https://github.com/J-a-m-e-s-o-n/jk-archivist-tiktok-skill
metadata: {"openclaw":{"emoji":"🎬","requires":{"bins":["node","python3"]}}}
---

# JK Archivist TikTok Skill

Generate deterministic, text-driven 6-slide portrait slideshow assets for TikTok-style content.

## What This Skill Is For

Use this skill when you want:

- Repeatable 6-slide visual posts without external image generation
- Consistent dimensions and readable layout for short-form platforms
- A simple contract: input slide copy -> validated PNG outputs + caption text
- A base that can later plug into draft upload workflows (for example via Postiz)

Typical use cases:

- Brand or creator intro slides
- Educational mini explainers
- Product update snapshots
- Story-driven announcement sequences

## Quick Start

1. Install dependencies:
   - `python3 -m pip install -r requirements.txt`
2. Optional font override:
   - `export TIKTOK_FONT_PATH=/absolute/path/to/font.ttf`
3. Run:
   - `node scripts/tiktok-intro-draft.mjs`

Custom input modes:

- Use your own 6-slide copy file:
  - `node scripts/tiktok-intro-draft.mjs --spec /absolute/path/to/spec.json`
- Ask the agent to generate copy from a topic:
  - `node scripts/tiktok-intro-draft.mjs --topic "your topic"`
- Optional Postiz draft upload:
  - `node scripts/tiktok-intro-draft.mjs --postiz`

Advanced modes:

- `--template intro|educational|product-update|announcement`
- `--style default|high-contrast|clean|midnight`
- `--audience beginner|operator|expert`
- `--cta-pack follow-focused|link-focused|engagement-focused`
- `--hashtag-policy tcg-default|general`
- `--locale en|es|fr`
- `--ab-test caption-cta|style|template`
- `--dry-run` (write spec/review only, skip render/upload)
- `--postiz-only` (reuse existing rendered slides, upload only)
- `--no-upload` (force local-only even with `--postiz`)
- `--resume-upload` (resume partially uploaded runs)
- `--max-retries <n>`
- `--timeout-ms <n>`
- `--verbose`

Template options:

- `intro`
- `educational`
- `product-update`
- `announcement`

Style options:

- `default`
- `high-contrast`
- `clean`
- `midnight`

Audience options:

- `beginner`
- `operator`
- `expert`

CTA pack options:

- `follow-focused`
- `link-focused`
- `engagement-focused`

Hashtag policy options:

- `tcg-default`
- `general`

## Core Output Contract

- Exactly 6 slides
- 1024x1536 portrait
- PNG output format
- Large readable text with safe margins

Expected layout:

```text
outbox/tiktok/intro/YYYY-MM-DD/
  _slide_spec.json
  _render_metadata.json
  slides/slide_01.png ... slide_06.png
  caption.txt
  review/review.md
  review/contact_sheet.png
  run_log.json
  upload_state.json (optional)
  postiz_response.json (optional)
```

## What Can Be Customized

- Slide text (any 6-line narrative)
- Font via `TIKTOK_FONT_PATH`
- Caption behavior via template + CTA + hashtags
- Audience mode and localization
- A/B variant strategy
- Optional Postiz upload controls

To customize for your use case, change:

- The `slides` array content (via `--spec` JSON or topic mode)
- The caption template in `src/node/write-caption.mjs`
- Hashtag/CTA policy in `src/node/hashtags` and `src/node/cta`
- Audience adaptation in `src/node/audience`
- Optional Postiz env vars if enabling `--postiz`

Spec format:

```json
{
  "slides": [
    "Slide line 1",
    "Slide line 2",
    "Slide line 3",
    "Slide line 4",
    "Slide line 5",
    "Slide line 6"
  ],
  "caption": "Optional caption override",
  "template": "intro",
  "audience": "operator",
  "ctaPack": "follow-focused",
  "hashtagPolicy": "tcg-default",
  "hashtagOverrides": ["#customtag"],
  "locale": "en",
  "ab_test": {
    "strategy": "caption-cta"
  },
  "style": {
    "preset": "default"
  }
}
```

### Customization Matrix

| Need | Option |
|---|---|
| Use your own exact slide copy | `--spec /path/spec.json` |
| Generate deterministic copy from a topic | `--topic "your topic"` |
| Use a built-in narrative structure | `--template educational` (or others) |
| Change visual style | `--style high-contrast` |
| Adjust reading complexity for target viewers | `--audience beginner|operator|expert` |
| Change CTA behavior | `--cta-pack ...` |
| Apply hashtag policy | `--hashtag-policy ...` |
| Add custom hashtags | `--hashtag #customtag` (repeatable) |
| Localize CTA text | `--locale es` |
| Generate multiple candidates | `--ab-test caption-cta|style|template` |
| Keep local-only output | run without `--postiz` or add `--no-upload` |
| Upload optional draft via Postiz | `--postiz` with required env vars |
| Resume partial uploads | `--postiz --resume-upload` |
| Tune network/upload behavior | `--max-retries N --timeout-ms N` |
| Validate pipeline without rendering/upload | `--dry-run` |

## Preset: JK Archivist Intro (Exact Contract)

### Objective

Generate a deterministic 6-slide TikTok intro slideshow (PNG) + caption and (optionally) upload as a TikTok draft/private post using Postiz. Human publishes manually after selecting trending sound.

### Draft/Private Upload Rules (Optional)

- `privacy_level = SELF_ONLY`
- `content_posting_method = UPLOAD`

### Slide Copy (Exact)

1. The trading card market runs on messy data.
2. Prices fragment. Condition drifts. Signals lie.
3. Collectors make real decisions on incomplete info.
4. JK Index = market intelligence for TCGs.
5. Truth first. No guessing. Built in public.
6. Alpha today. Compounding weekly. Brick by brick. 👑🧱

### Caption Template (Exact)

TCG prices look certain — until you zoom in.
JK Index is building the truth layer: clean IDs, real comps, market signals.
Follow if you want collector-first market intelligence. 👑🧱

#pokemon #tcg #cardcollecting #marketdata #startup

## Safety / Never Do

- No token mentions
- No `$`
- No buy/sell language
- No predictions
- No copyrighted character art
- No unverified superlatives (e.g., "guaranteed", "most accurate")

## Required/Optional Environment Variables

Required for optional upload mode:

- `POSTIZ_API_KEY`
- `POSTIZ_TIKTOK_INTEGRATION_ID`

Optional:

- `POSTIZ_BASE_URL` (defaults to `https://api.postiz.com/public/v1`)
- `TIKTOK_FONT_PATH` (absolute `.ttf` path)

## References

- `references/setup.md`
- `references/spec-schema.md`
- `references/renderer-spec.md`
- `references/outputs-and-validation.md`
- `references/troubleshooting.md`
- `references/publish-checklist.md`
- `examples/sample-slide-spec.json`
