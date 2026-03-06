---
name: hn-daily
description: Generate and deliver a Hacker News daily report (Top-N) with article summaries and multi-view comment synthesis, in user-selected language, with optional file persistence and index update.
---

# HN Daily

## Release Notes
- v0.7.0: Add concurrent retry profile for schedule reliability (primary run + immediate retry + delayed retry) with idempotent completion checks to avoid timeout-caused misses.
- v0.6.0: Brand rename for distribution as "HN Daily Brief" + full copy cleanup to English-only wording.
- v0.5.1: Language cleanup for public distribution (English-first docs; localized markers still supported).
- v0.5.0: First public release.

## Parameters
- `language`: output language (default: current user conversation language)
- `topN`: number of items (default: 10)
- `style`: `strict | lite` (default: strict)
- `outputDir`: output directory (default: `/home/ubuntu/.openclaw/workspace/output/hn-daily/`)
- `persist`: whether to save file + update index (default: true)
- `reminderTime`: cron time in user timezone, or `off`

## First-load behavior
- On first load (or when user changes params), show effective params once and confirm.
- Otherwise, reuse last confirmed params.

## Mandatory execution order
1. Retry preflight check (required for retry jobs):
   - If this run is a retry/compensation run, first check whether today's report already exists and is complete (at minimum includes `## Top 10`).
   - If already complete, return `NO_REPLY` and stop (idempotent exit).
2. Always fetch fresh inputs for this run (required):
   - Re-pull current HN Top-N items, article snippets, and comments at run time.
   - Do not reuse previous report body as source input.
3. Collect materials via script (data collection only, never user-facing):
   - `scripts/generate_hn_daily.py --style <style> --top <topN> --language <language> --outdir /tmp/hn-daily-draft --materials /tmp/hn-daily-draft/HN-materials.json`
   - Script must only output `HN-materials.json` (no user-facing report body).
   - Use `HN-materials.json` as the only source for final writing.
4. LLM generation (required, prompt-driven quality):
   - Use a single strict prompt template to generate final report in selected `language`.
   - All content quality constraints (summary depth, comment synthesis style, anti-template wording) must be enforced by prompt, not by script templates.
   - No “summarize then translate”; generate directly in target language.
5. Re-check completion before send (required for retry jobs):
   - If another concurrent run has already persisted a complete report, do not send duplicate content; return `NO_REPLY`.
6. Send full final report body to current chat.
7. If `persist=true`, write final report to `<outputDir>/HN-daily-YYYY-MM-DD.md` and update `<outputDir>/HN_DAILY_INDEX.md`.

## Success criteria (strict)
- `persist=false`: success = full report body delivered in chat.
- `persist=true`: success = chat delivery + file write + index update.
- Under concurrent retry profile: success can be achieved by primary run or any retry run; retries must skip if the report is already complete.
- If any required condition fails, treat run as failed (do not claim completion).

## Output rules
- Send only report body to user (no receipts/status metadata).
- Never send script draft markdown directly; user-facing report must come from LLM rewrite over materials JSON.
- Output must use one language only: the selected `language` for the run (no bilingual/mixed-language output).
- Real markdown newlines only; never output literal `\n` in user-visible content.
- Top-N structure per item:
  - Title
  - Link
  - HN link
  - Heat
  - Source summary
  - Comment viewpoint synthesis

## Length rules (by selected language)
- Default hard rule: source summary must be >=300 chars in zh (>=200 words in en; equivalent depth for others).
- Elastic exception: only when source content is genuinely short/information-limited, summary may be shorter than default target.
- Comment viewpoint summary target: zh>=80 chars (equivalent depth for others), with the same short-source exception.
- When exception is used, explicitly mark "source is short / info limited" (or equivalent in selected language), prioritize verifiable facts + discussion context + actionable implications, and keep concise but information-dense output.
- Never inflate length with generic filler text.

## Comment synthesis rules
- Must be in selected `language`.
- Multi-perspective (not binary pro/con).
- Per item, output 5 comment viewpoints when available.
- If username exists in source comment, it must be preserved in output.
- Only use "insufficient comments" when no usable comments are available.
- Summarize viewpoints; do not paste long raw quotes.

## Scheduling rules (concurrent retry profile)
- If `reminderTime != off`, create/update a **3-job retry ladder** automatically (no duplicates):
  1) Primary run at `reminderTime` (e.g. `HN Daily 06:50`)
  2) Immediate retry at `reminderTime + 1m` (e.g. `HN Daily 06:51 Retry`)
  3) Delayed retry at `reminderTime + 15m` (e.g. `HN Daily 07:05 Retry`)
- All retry jobs must be idempotent via completion checks (see Mandatory execution order step 1 and step 5).
- Keep job names aligned with schedule and retry role.
- Cron payload must be execution-oriented (not passive reminder).
- Rationale: cron has no built-in on-failure callback; this retry ladder is the required equivalent for timeout/failure recovery.

## Prompt template requirements (must include)
- Generate directly in selected `language`.
- Source summary length must meet selected-language threshold.
- Each comment viewpoint summary must meet selected-language threshold.
- Summaries must be article-specific and fact-based; avoid reusable boilerplate.
- Comment section must synthesize viewpoints (not raw quote dumping), with usernames when available.

## Pre-send quality gate (mandatory)
- Validate final report before sending:
  - zh summary default >=300 chars per item;
  - zh comment viewpoint default >=80 chars per viewpoint.
- Recommended command:
  - `scripts/validate_report.py --report <final_report_path> --language <language>`
- If an item/viewpoint is below default threshold, it must explicitly include a short-source marker (e.g. `source is short / info limited`).
- If gate fails, rewrite and re-check; do not send failing report.

## Guardrail
- If prompt-driven LLM generation path is not available/validated, keep cron disabled until fixed.
- If primary + both retries all fail on the same day, send a concise failure alert to the current chat with the first actionable error cause (do not silently drop the run).
