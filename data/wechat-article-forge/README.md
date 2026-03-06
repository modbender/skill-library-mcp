# wechat-article-writer

> 从选题到发布的公众号一体化写作工作流

An OpenClaw skill that automates the full lifecycle of a WeChat Official Account (微信公众号) article: topic research, multi-agent writing with quality gates, scrapbook-style illustrations, formatting, and publishing to the draft box.

**v2.4.0** · Three publishing paths: Official Account API (recommended), browser tool, or direct CDP · Bundled baoyu renderer (no external dependencies)

---

## What It Does

```
forge write 关于AI编程工具的深度评测
```

That single command runs a **9-step pipeline**:

1. **Research + Prep** — topic angles, verified `sources.json` bank, voice profile, outline
2. **Write** via Writer subagent (Chinese-first, constrained to source bank)
3. **Review** via Reviewer subagent (blind 8-dimension craft scoring)
4. **Revise** — 4a: up to 2 automated cycles; 4b: human-in-the-loop if needed
5. **Fact-check** via Fact-Checker subagent (verify every claim, generate reference list)
6. **Format** to WeChat HTML via bundled baoyu renderer (`scripts/format.sh`, default classic theme)
7. **Preview** on persistent HTTP server at port 8898 for human approval
8. **Illustrate + Embed** — scrapbook images via article-illustrator, upload to WeChat CDN
9. **Publish** to WeChat draft box — via API (preferred) or browser automation (fallback)

---

## Architecture

```
Orchestrator (Main Agent) — routes, tracks, enforces gates
    ├── Writer Subagent — drafts + revises (Opus model)
    ├── Reviewer Subagent — blind craft scoring (Sonnet model)
    ├── Fact-Checker Subagent — verifies claims via web search (Sonnet model)
    └── article-illustrator — scrapbook images (after text passes)
```

- **Writer never self-reviews.** Constrained to verified source bank — must mark `[UNVERIFIED]` for anything outside it.
- **Reviewer is blind.** Never sees outline or brief — judges craft as a reader would.
- **Fact-Checker is independent.** Verifies every claim via web search, generates reference list.
- **Illustrations are gated.** No images until text is human-approved (~$0.06/article via Z.AI).

---

## Setup

```bash
bash <skill-dir>/scripts/setup.sh <workspace-dir>
```

Installs: bun runtime, bundled baoyu renderer deps, persistent preview server (`wechat-preview.service`, port 8898, auto-restart), writes `config.json`, appends rules to `AGENTS.md`.

### API Keys

| Key | Purpose | Required? |
|-----|---------|-----------|
| `ZAI_API_KEY` | Image generation via Z.AI ($0.015/image, 97.9% Chinese accuracy) | Preferred |
| `GLM_API_KEY` | Image generation via BigModel China | Alternative |
| `OPENROUTER_API_KEY` | Image generation fallback | Alternative |

At least one image key is required for illustrations.

### Publishing Credentials

**Path C (API — recommended):** Store appid + appsecret in a credentials file (default: `~/.wechat-article-writer/secrets.json`):
```json
{ "appid": "wx...", "appsecret": "..." }
```
No browser needed. Works for unverified subscription accounts.

**Path A/B (browser fallback):** If no API credentials, the skill automates `mp.weixin.qq.com` via Chrome CDP. See `references/browser-automation.md`.

---

## Commands

| Command | Description |
|---------|-------------|
| `forge topic <subject>` | Research + propose 3 topic angles |
| `forge write <subject>` | Full pipeline: research → write → review → illustrate → publish |
| `forge draft <subject>` | Write + format only, stop before illustrations |
| `forge publish <draft-id>` | Push existing draft to WeChat |
| `forge preview <draft-id>` | Format check + preview |
| `forge voice train` | Build voice profile from past articles |
| `forge status` | Show all drafts and their pipeline status |

---

## Publishing (Step 9)

The skill checks for publishing credentials in order and uses the first available method:

### Path C — WeChat Official Account API (recommended)

```bash
python3 scripts/publish_via_api.py \
  --draft-dir ~/.wechat-article-writer/drafts/<slug> \
  --title "草稿标题（≤18字）" \
  --author "作者" \
  --source-url "https://..."
```

**⚠️ Undocumented WeChat API field limits** (confirmed empirically, February 2026):

| Field | Documented | Actual Limit |
|-------|-----------|--------------|
| `title` | 64 chars | **≤18 chars** (36 bytes) |
| `author` | 8 chars | **≤8 bytes** (= 2 Chinese chars) |
| `digest` | 120 chars | **~28 Chinese chars** |
| `content` | 20,000 bytes | **~18KB UTF-8** |

> **Title workaround:** The API title is only for draft box listing. Edit it to the full version in the WeChat editor UI before publishing — the UI has no 18-char limit.

> **Chinese encoding:** Always use `data=json.dumps(..., ensure_ascii=False).encode("utf-8")` — never `requests(..., json=payload)` which escapes Chinese as `\uXXXX`.

### Path A — OpenClaw Browser Tool (macOS)

Uses the `browser` tool to drive `mp.weixin.qq.com` via Playwright. Injects via base64 chunking + clipboard paste. See `references/browser-automation.md` → Path A.

### Path B — Direct CDP WebSocket (Linux)

Connects to Chrome CDP directly from Python. Requires `--remote-debugging-port=18800 --remote-allow-origins='*'`. See `references/browser-automation.md` → Path B.

---

## Quality Gates

### Reviewer Scoring (8 dimensions)

| Dimension | Weight | What it measures |
|-----------|--------|-----------------|
| Insight Density (洞察密度) | 20% | Non-obvious ideas per section |
| Originality (新鲜感) | 15% | Genuinely new framing |
| Emotional Resonance (情感共鸣) | 15% | Earned emotional arc |
| Completion Power (完读力) | 15% | Every section earns the next scroll |
| Voice (语感) | 10% | Natural Chinese, sounds like a person |
| Evidence (论据) | 10% | Named researchers, institutions, venues |
| Content Timeliness (内容时效性) | 10% | Argument rests on principles, not news |
| Title (标题) | 5% | Clear, specific, ≤26 chars |

**Pass:** weighted_total ≥ 9.0, no dimension below 7, Originality ≥ 8.

**Hard blockers (instant FAIL):** 教材腔, 翻译腔, 鸡汤腔, 灌水, 模板化, 标题党.

---

## Formatting (Step 6)

`scripts/format.sh` renders markdown to WeChat-compatible HTML using the bundled baoyu renderer:

```bash
bash scripts/format.sh <draft-dir> <draft-file> [theme]
# Themes: default (recommended), grace, simple
```

The preview is served by a persistent systemd service (`wechat-preview.service`) on port 8898 — no manual server restarts needed.

---

## Illustrations

Uses **article-illustrator** skill's scrapbook pipeline:
- Style: hand-crafted mixed-media collages — torn paper, washi tape, cork boards, hand-drawn markers
- Cost: ~$0.06/article (4 images × $0.015 via Z.AI)
- Z.AI CDN note: URL may return 404 immediately after generation — script retries with 4s delay (up to 5 attempts)

---

## Configuration

`~/.wechat-article-writer/config.json`:

```json
{
  "default_article_type": "教程",
  "chrome_debug_port": 18800,
  "wechat_author": "你的公众号名称",
  "wechat_secrets_path": "~/.wechat-article-writer/secrets.json",
  "word_count_targets": {
    "资讯": [800, 1500],
    "教程": [1500, 3000],
    "观点": [1200, 2500],
    "科普": [1500, 3000]
  }
}
```

---

## Data Layout

```
~/.wechat-article-writer/
├── config.json
├── voice-profile.json
├── preview_server.py          # Persistent preview server (systemd)
└── drafts/
    └── <slug-YYYYMMDD>/
        ├── pipeline-state.json
        ├── outline.md
        ├── sources.json
        ├── draft.md / draft-v2.md / ...
        ├── review-v1.json / ...
        ├── fact-check.json
        ├── formatted.html
        └── images/
            ├── illustration-plan.json
            └── img*.png
```

---

## Scripts

| Script | Description |
|--------|-------------|
| `scripts/setup.sh` | One-click setup: bun, renderer deps, systemd preview service |
| `scripts/format.sh` | Markdown → WeChat HTML (baoyu renderer, default theme) |
| `scripts/publish_via_api.py` | API-based publisher (Path C) |
| `scripts/renderer/` | Bundled baoyu-markdown-to-html renderer |

---

## References

| File | When to load |
|------|-------------|
| `references/writer-prompt.md` | Step 2 (writing) and Step 4 (revision) |
| `references/reviewer-rubric.md` | Step 3 — full 8-dimension scoring criteria |
| `references/fact-checker-prompt.md` | Step 5 — claim verification protocol |
| `references/browser-automation.md` | Step 9 — all three publishing paths |
| `references/pipeline-state.md` | On resume — state machine schema |
| `references/wechat-html-rules.md` | Step 6 — what HTML/CSS works in WeChat |
| `references/LESSONS_LEARNED.md` | Hard-won lessons from production publishing sessions |

---

## License

MIT
