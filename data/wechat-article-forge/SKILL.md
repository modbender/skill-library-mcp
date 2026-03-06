---
name: wechat-article-writer
description: 'End-to-end 微信公众号 (WeChat Official Account) article writing and
  publishing pipeline. 9-step multi-agent workflow: topic research →
  Chinese-first writing → blind quality review → fact-check → formatting → human
  preview → scrapbook illustrations → draft box publish. Use when user asks to
  write, draft, or publish a WeChat article, or says "forge
  write/draft/publish/topic/voice/status".'
---


# wechat-article-writer

> 从选题到发布的公众号一体化写作工作流

Multi-agent pipeline: Orchestrator delegates writing and reviewing to independent subagents. The orchestrator never writes or reviews — it routes, tracks versions, and enforces quality gates.

## Setup

```bash
bash <skill-dir>/scripts/setup.sh <workspace-dir>
```

Installs: bun runtime, bundled baoyu renderer deps, and a persistent preview server (`wechat-preview.service`, port 8898, auto-restart).

## Scope

**Handles:** Topic research → Chinese-first writing → quality review → scrapbook illustrations → WeChat formatting → publishing to WeChat draft box (via Official Account API or CDP browser automation).

**Does NOT handle:** Git/version control, non-WeChat platforms, post-publish analytics, WeChat messaging/customer service.

**Ends at:** Article saved to WeChat draft box. User publishes manually.

---

## Commands

Trigger any command below, or see `skill.yml` for the full trigger pattern list.

| Command | What it does |
|---------|-------------|
| `forge topic X` | Research trending angles, propose 3 options with hooks |
| `forge write X` | Full pipeline: research → publish (9 steps) |
| `forge draft X` | Write + format only, stop before illustrations/publish (steps 1-7) |
| `forge publish <slug>` | Publish an existing draft to WeChat |
| `forge preview <slug>` | Render preview, run format quality checks |
| `forge voice train` | Analyze past articles to extract voice profile |
| `forge status` | Show pipeline status and pending drafts |

If no subject given, loads from `session.json` (set by `forge topic`). See `references/data-layout.md`.

---

## Pipeline (9 Steps)

State persists to `pipeline-state.json` — survives compaction. See `references/pipeline-state.md`.

| # | Step | Who | Details |
|---|------|-----|---------|
| 1 | **Research + Prep** | Orchestrator | (a) `web_search` for topic angles + 5-8 sources. (b) Verify each source exists (fetch title/authors/venue). Save as `sources.json`. (c) Load voice profile. (d) Generate outline (6-8 sections), save `outline.md`. |
| 2 | **Write** | Writer subagent | Chinese-first draft. Writer MUST cite only from `sources.json` or mark `[UNVERIFIED]`. See `references/writer-prompt.md` |
| 3 | **Review** | Reviewer subagent | Blind 8-dimension craft scoring. See `references/reviewer-rubric.md` |
| 4a | **Revise (auto)** | Writer subagent | Max 2 automated cycles. Loop back to Step 3 if score < threshold. |
| 4b | **Revise (human)** | Human-in-the-loop | If still below threshold after 2 auto cycles, user provides direction. Pauses pipeline. |
| 5 | **Fact-check** | Fact-Checker subagent | Verify every claim via web search. Produces corrections + reference list. Max 2 fact-check cycles (corrections → re-verify). See `references/fact-checker-prompt.md` |
| 6 | **Format** | Script | `bash scripts/format.sh <draft-dir> [draft-file] [theme]` — baoyu renderer (default theme: classic WeChat style). Themes: default/grace/simple. If fact-check required >3 text changes, Orchestrator does a **spot re-review** (Reviewer scores only changed paragraphs, not full article). |
| 7 | **Preview** | Human | Open `http://<host>:8898/formatted.html` (persistent preview server, systemd `wechat-preview.service`), await text approval |
| 8 | **Illustrate + Embed** | article-illustrator + script | Generate scrapbook images (AFTER text approval). ~$0.06/article via Z.AI (preferred, ~$0.015/image) or ~$0.50 via OpenRouter. |
| 9 | **Publish** | Orchestrator | **Three paths** — check in order: (C) WeChat Official Account API via appid+appsecret (credentials at `wechat_secrets_path` in config.json) — **preferred, most reliable**; (A) OpenClaw browser tool with base64 chunking for macOS/Titan; or (B) direct CDP WebSocket for Linux/remote. Paths A+B use two-phase injection (text first, then images via clipboard blob paste). See `references/browser-automation.md` |

### Key Rules

- **Writer never self-reviews.** Reviewer is blind — never sees outline or brief.
- **Illustrations LAST.** Most expensive step. Only after user approves text.
- **article-illustrator is the ONLY image method.** Must follow full scrapbook pipeline: read `references/scrapbook-prompt.md` → generate JSON plan with 300-500 char descriptions → call `generate.py`. Never bare prompts. **Prefer Z.AI provider** (~$0.015/image, 97.9% Chinese text accuracy) over OpenRouter (~$0.12/image).
- **Two-phase image injection.** Base64 images are stripped on save. Inject text-only HTML first, then insert each image at the correct position via clipboard blob paste (WeChat auto-uploads to CDN). Verify image count + positions after insertion.
- **Browser tool vs direct CDP.** On macOS/Titan where OpenClaw manages the browser, you MUST use the browser tool (Path A). Playwright isolates page contexts — external CDP connections see zero targets. On Linux with standalone Chrome, use direct CDP (Path B). See `references/browser-automation.md`.
- **Base64 chunking for browser tool.** Raw HTML in the browser tool's `fn` parameter breaks due to escaping conflicts. Always base64-encode HTML, store in chunks via `window._b`, then `atob()` and inject. Track `chunks_stored` in pipeline state for compaction recovery.
- **Always save as draft.** User publishes manually.
- **Check for WeChat API credentials first.** If `wechat_secrets_path` credentials file (see `config.json`) exists, use Path C (API) — no browser required, more reliable. Fall back to Path A/B only if no credentials.
- **`ensure_ascii=False` is mandatory for WeChat API.** `requests(..., json=payload)` escapes Chinese as `\u5199\u4e66`. Always use `data=json.dumps(..., ensure_ascii=False).encode('utf-8')`.
- **Topic fidelity:** Every revision preserves the article's 初心 (purpose statement in pipeline-state.json). Drift = FAIL.

### Image Counts by Type

| Type | Min | Max |
|------|-----|-----|
| 科普 | 3 | 5 |
| 教程 | 3 | 6 |
| 观点 | 2 | 4 |
| 资讯 | 2 | 3 |

---

## Review Dimensions

Reviewer scores 0-10 on **craft-observable** dimensions (not outcome predictions):

| Dimension | Weight |
|-----------|--------|
| Insight Density (洞察密度) | 20% |
| Originality (新鲜感) | 15% |
| Emotional Resonance (情感共鸣) | 15% |
| Completion Power (完读力) | 15% |
| Voice (语感) | 10% |
| Evidence (论据) | 10% |
| Content Timeliness (内容时效性) | 10% |
| Title (标题) | 5% |

**Pass:** weighted_total ≥ 9.0, no dimension below 7, Originality ≥ 8.

**Hard blockers (instant FAIL):** 教材腔, 翻译腔, 鸡汤腔, 灌水, 模板化, 标题党.

Full rubric with scoring criteria: `references/reviewer-rubric.md`

---

## Architecture

```
Orchestrator (Main Agent) — routes, tracks, enforces gates
    ├── Writer Subagent — drafts + revises (Opus model)
    ├── Reviewer Subagent — blind scoring (Sonnet model)
    ├── Fact-Checker Subagent — verifies claims via web search (Sonnet model)
    └── article-illustrator — scrapbook images (after text passes)
```

---

## Configuration

Configure via `~/.wechat-article-writer/config.json` (generated by `scripts/setup.sh`):

| Field | Default | Description |
|-------|---------|-------------|
| `default_article_type` | `"教程"` | Default article type (科普/教程/观点/资讯) |
| `wechat_secrets_path` | `~/.wechat-article-writer/secrets.json` | Path to WeChat API credentials |
| `chrome_debug_port` | `18800` | Chrome CDP port for browser automation (Path B) |
| `wechat_author` | — | Author name shown in WeChat draft |
| `word_count_targets` | See defaults | Min/max word counts per article type |

See `references/data-layout.md` for full config schema.


---

## References

| File | When to load |
|------|-------------|
| `references/writer-prompt.md` | Step 2 (writing) and Step 4 (revision) |
| `references/reviewer-rubric.md` | Step 3 (review) — full 8-dimension scoring criteria |
| `references/fact-checker-prompt.md` | Step 5 — claim extraction, verification, correction protocol |
| `references/viral-article-traits.md` | Step 2 — Writer self-check list |
| `references/pipeline-state.md` | On resume or compaction — state machine schema + protocol |
| `references/browser-automation.md` | Step 9 — Two publishing paths: Path A (OpenClaw browser tool) and Path B (direct CDP). Includes base64 chunking, image insertion, save verification. |
| `references/LESSONS_LEARNED.md` | Hard-won lessons from production publishing sessions (escaping, selectors, mixed content, costs) |
| `references/data-layout.md` | Directory structure, slug generation, config/session schemas |
| `references/agent-config.md` | Setup — Gateway, AGENTS.md, environment config |
| `references/quality-checks.md` | Steps 3, 7 — content/format quality gates |
| `references/figure-generation-guide.md` | Step 8 — illustration placement heuristics |
| `references/wechat-html-rules.md` | Step 6 — what HTML/CSS works in WeChat |
| `references/templates.md` | Step 1 — starting templates by article type |
| `references/voice-profile-schema.json` | Step 1 — voice profile field definitions |
| `references/default-voice-profile.json` | Step 1 — fallback voice profile |
