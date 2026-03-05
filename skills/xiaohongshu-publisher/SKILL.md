---
name: xiaohongshu-publisher
description: Draft and publish posts to 小红书 (Xiaohongshu/RED). Use when creating content for 小红书, drafting posts, generating cover images, or publishing via browser automation. Covers the full workflow from content creation to browser-based publishing, including cover image generation with Pillow.
---

# 小红书 Publisher

Create, format, and publish posts to 小红书 (Xiaohongshu/RED) through browser automation.

## Requirements

- **Python 3** with **Pillow** (`pip install Pillow` or `apt install python3-pil`)
- **CJK fonts** — `fonts-noto-cjk` on Linux (`apt install fonts-noto-cjk`), or Noto Sans CJK via Homebrew on macOS
- **OpenClaw browser tool** — access to a browser with the user logged into 小红书 creator portal
- A connected **OpenClaw node** (or sandbox browser) with Chrome/Chromium for browser automation

## Overview

This skill handles the complete 小红书 publishing pipeline:
1. **Draft** — Write post content in 小红书 style
2. **Cover** — Generate a cover image (1080×1440)
3. **Review** — Send draft to user for approval via messaging channel
4. **Publish** — Use browser automation to post (or deliver for manual posting)

## Workflow

### Step 1: Draft Content

Create post content following 小红书 style. See [references/content-guide.md](references/content-guide.md) for formatting rules, structure, and examples.

Key rules:
- Title ≤20 chars, with emoji hook
- Use `---` section breaks, emoji bullets, short paragraphs
- End with question CTA + hashtags (8-12 tags)
- Save draft to `memory/xiaohongshu-draft.md`

### Step 2: Generate Cover Image

Run the cover generation script:

```bash
python3 <skill-dir>/scripts/gen_cover.py --title "主标题" --subtitle "副标题" --tags "标签1,标签2,标签3" --output /path/to/cover.png
```

Options:
- `--title` — Main title (large text, required)
- `--subtitle` — Subtitle line (medium text, optional)
- `--tags` — Comma-separated feature tags shown as pills (optional)
- `--badge` — Top-right badge text (default: "OpenClaw")
- `--output` — Output path (default: `cover.png`)
- `--gradient` — Color scheme: `purple` (default), `blue`, `green`, `orange`, `dark`

Output: 1080×1440 PNG with gradient background, decorative elements, CJK text.

### Step 3: Send for Review

Send the draft content + cover image to the user's messaging channel for review. Format:

```
📝 小红书草稿 — [主题]

标题：[标题]

[正文内容]

封面图已生成：[path]

请确认：
✅ 可以发布
✏️ 需要修改
❌ 不发
```

**Never auto-publish.** Always wait for explicit user approval.

### Step 4: Publish via Browser

After user approval, publish using browser automation on the configured node.

See [references/browser-publish.md](references/browser-publish.md) for the complete browser automation steps.

Summary:
1. Navigate to `https://creator.xiaohongshu.com/publish/publish`
2. Enter title and body text
3. Upload cover image via browser `upload` action
4. Click publish

### Fallback: Manual Publishing

If browser automation is unavailable (CDP issues, node offline, etc.), send the complete post to the user's channel with all content formatted for easy copy-paste:

```
📋 小红书发帖内容（请手动发布）

【标题】[标题]

【正文】
[正文内容]

【标签】[hashtags]

封面图：[path to cover image]
```

## Known Limitations

- **Mac Chrome CDP**: Chrome launched via SSH/node may fail to bind `--remote-debugging-port` on macOS (GUI session required). If `browser start` fails, fall back to manual publishing.
- **Login state**: 小红书 creator portal requires login. If the session has expired, ask the user to re-login in their browser before proceeding.
- **Pillow emoji**: Pillow cannot render color emoji (NotoColorEmoji.ttf) — use text/icon alternatives in cover images.

## Cron Integration

This skill works with cron jobs for scheduled daily posting. Typical cron setup:

```
Schedule: 0 8 * * * (Asia/Shanghai)
Session: isolated agentTurn
Delivery: announce to user's channel
```

The cron job message should reference this skill and include the content plan/topic for the day.
