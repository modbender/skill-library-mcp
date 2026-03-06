---
name: zentable
description: "Render structured table data as high-quality PNG images using Headless Chrome. Use when: need to visualize tabular data for chat interfaces, reports, or social media. NOT for: simple text tables that don't need visualization."
homepage: https://github.com/con2000us/zenTable
metadata:
  openclaw:
    emoji: "📊"
    requires:
      bins: ["python3", "google-chrome"]
allowed-tools: ["exec", "read", "write"]
---

# ZenTable Skill

Render structured table data into high-quality PNG images.

## TL;DR

ZenTable turns messy table-like content into readable, decision-ready table outputs for both mobile (Discord-first) and desktop.

**Accepted inputs**
- text-based content (raw text tables, long agent responses)
- structured JSON
- screenshots / real-world photos (via OCR-assisted extraction when needed)

**Core capabilities**
- CSS + PIL rendering
- sorting / filtering / pagination
- threshold-based highlighting
- optional PNG + TXT dual output (`--both`)

## Runtime & security note

This skill runs local scripts and depends on local runtime binaries (`python3`, `google-chrome`).
Review code and dependencies before running in sensitive environments.

## Naming convention

- Canonical code name: `zentable` (lowercase)
- UI / brand label: `ZenTable`
- `zeble*` / `zenble*` are legacy compatibility aliases
- Reference: `NAMING_MIGRATION.md` (repository document)

## When to use

✅ Use this skill when:
- You need a visual table image instead of plain text
- You need polished output for chat/report/social sharing
- The dataset is large enough that plain text is hard to read
- You need a specific visual theme (iOS-like, dark, compact, etc.)

❌ Do not use this skill when:
- The table is tiny and plain text is enough
- The user explicitly asks for no image output
- The user needs an editable spreadsheet format (CSV/Excel)

## Capability matrix (SkillHub release)

| Capability | Status | Notes |
|---|---|---|
| CSS output | ✅ Stable | Primary release path; default `minimal_ios_mobile + width=450` |
| PIL output | ✅ Stable | Safe fallback when Chrome is unavailable |
| ASCII output | ⚠️ Beta / Experimental | Works, but alignment can drift cross-platform due to font and whitespace behavior |

## Known limitations

- ASCII output is sensitive to platform font fallback and whitespace handling.
- Create separate calibration profiles per platform; do not share blindly.
- `--both` already includes text-theme fallback to `default` when no text theme exists.
- Discord plain text collapses repeated normal spaces; Unicode spacing characters may be required for spacing preservation.
- This beta was validated primarily on Discord; other chat platforms may require agent-side output adaptation (image/message formatting differences).

## Zx shorthand policy (project rule)

When user input is `Zx`, treat it as a strong render intent:

1. Execute rendering directly by default (no preliminary Q&A).
2. Default path: CSS + `minimal_ios_mobile` + `width=450`.
3. Ask follow-up only under high uncertainty:
   - no usable source data in current/previous context,
   - intent does not look like table rendering,
   - critical fields are missing and output would likely be wrong.
4. If platform supports images, return the image directly (not link-only).

Data source priority for `Zx`:
1) current message image OCR
2) current message text-to-table
3) previous message image OCR
4) previous message text-to-table

## Syntax sugar → canonical mapping

| Sugar | Canonical key | Normalization | Final renderer args |
|---|---|---|---|
| `--width N` / `--w N` | `width` | positive int | `--width N` |
| `--transpose` / `--cc` | `transpose` | boolean | `--transpose` |
| `--tt` | `keep_theme_alpha` | boolean | `--tt` |
| `--per-page N` / `--pp N` | `per_page` | positive int | `--per-page N` |
| `--page ...` / `--p ...` | `page_spec` | `N` / `A-B` / `A-` / `all` | expanded by `table_renderer.py` |
| `--all` | `page_spec` | equivalent to `all` | expanded by `table_renderer.py` |
| `--text-scale V` / `--ts V` | `text_scale` | enum/ratio | `--text-scale V` |
| `--sort SPEC` | `sort_spec` | single/multi-key | `--sort SPEC` |
| `--asc` / `--desc` | `sort_default_dir` | default direction | `--asc` / `--desc` |
| `--f SPEC` / `--filter SPEC` | `filters` | repeatable filter | `--f SPEC` |
| `--smart-wrap` | `smart_wrap` | true | `--smart-wrap` |
| `--no-smart-wrap` / `--nosw` | `smart_wrap` | false | `--no-smart-wrap` |
| `--theme NAME` / `-t NAME` | `theme` | theme id | `--theme NAME` |
| `--both` / `--bo` | `output_both` | boolean | `--both` |
| `--pin KEYS` | `pin_keys` | persist defaults | `--pin` |
| `--pin-reset` | `pin_reset` | reset pinned defaults | `--pin-reset` |

Pinned default baseline:
- `theme=minimal_ios_mobile`
- `width=450`
- `smart_wrap=true`
- `per_page=15`

## `page_spec` rules

- `N`: page N only
- `A-B`: inclusive range A..B
- `A-`: from A to last page
- `all`: all pages
- if omitted: default preview pages `1-3`

## Canonical payload example

```json
{
  "theme": "minimal_ios_mobile",
  "width": 900,
  "transpose": false,
  "keep_theme_alpha": false,
  "per_page": 15,
  "page_spec": "2-",
  "sort_spec": "score:desc,name:asc",
  "sort_default_dir": "asc",
  "filters": ["col:!note,attachment", "row:status!=disabled;score>=60"],
  "text_scale": "auto",
  "smart_wrap": true,
  "output_both": false
}
```

## Command examples

```bash
# run from repository root

# basic CSS output
python3 skills/zentable/table_renderer.py - /tmp/out.png --theme minimal_ios_mobile --width 900 --text-scale large --page 1

# transpose + disable smart wrap
python3 skills/zentable/table_renderer.py - /tmp/out.png --theme compact_clean --transpose --no-smart-wrap --page 1

# page range expansion (2-4)
python3 skills/zentable/table_renderer.py - /tmp/out.p2.png --per-page 12 --page 2
python3 skills/zentable/table_renderer.py - /tmp/out.p3.png --per-page 12 --page 3
python3 skills/zentable/table_renderer.py - /tmp/out.p4.png --per-page 12 --page 4

# PNG + ASCII side output
python3 skills/zentable/table_renderer.py - /tmp/out.png --theme mobile_chat --both
```

## Validation checklist (minimum)

- `python3 -m py_compile scripts/zentable_render.py`
- CSS smoke output succeeds
- PIL smoke output succeeds
- `--pin`, `--pin-reset`, `--both` verified
- Golden tests pass when relevant

## Release positioning

Current channel: **beta**.
ASCII remains **beta/experimental** for SkillHub release.

## Support / Contact

- GitHub Issues: https://github.com/con2000us/zenTable/issues
- Maintainer: @con2000us (Discord)
- Bug report checklist:
  - input type (text / screenshot / photo / json)
  - expected vs actual output
  - platform (Discord/mobile/desktop)
  - command/options used
