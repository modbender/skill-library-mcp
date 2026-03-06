---
name: xhs-auto-publish
description: Automate publishing image+text posts (图文笔记) on Xiaohongshu (小红书) creator platform. Use when the user wants to publish a Xiaohongshu post, create XHS content, auto-post to 小红书, or schedule social media posts for the Chinese market. Supports multi-image upload, title, body text, and hashtags. Requires a browser with CDP (Chrome DevTools Protocol) already logged in to creator.xiaohongshu.com.
---

# 小红书自动发布 (Xiaohongshu Auto-Publish)

Publish image+text posts to Xiaohongshu via browser automation. No API key needed — uses CDP to control an already-logged-in browser.

## Prerequisites

1. **playwright-core** installed: `npm install -g playwright-core`
2. **A Chromium browser** running with CDP (remote debugging) enabled
3. **Logged in** to `creator.xiaohongshu.com` in that browser

For **OpenClaw** users: the managed browser (`profile="openclaw"`) provides CDP automatically at `http://127.0.0.1:18800`.

## Quick Start

```bash
node scripts/publish.js \
  --title "你的标题（20字以内）" \
  --body "正文内容（1000字以内）" \
  --images cover.png,slide2.png,slide3.png \
  --hashtags "AI绘画,独立开发" \
  --cdp-url http://127.0.0.1:18800
```

This auto-publishes the post. Add `--dry-run` to preview without publishing.

## Options

| Flag | Description | Required |
|------|-------------|----------|
| `--title <text>` | Post title, max 20 Chinese chars | ✅ |
| `--body <text>` | Post body, max 1000 chars | ✅* |
| `--body-file <path>` | Read body from a text file | ✅* |
| `--images <paths>` | Comma-separated image paths (1-18) | ✅ |
| `--hashtags <tags>` | Comma-separated hashtags (auto-prefixed with #) | Optional |
| `--cdp-url <url>` | CDP endpoint (default: `http://127.0.0.1:9222`, or `XHS_CDP_URL` env) | Optional |
| `--dry-run` | Preview only, skip publish (default: auto-publish) | Optional |
| `--screenshot <path>` | Save preview screenshot path | Optional |

*One of `--body` or `--body-file` is required (unless using `--hashtags` alone).

## Workflow

1. Connects to browser via CDP
2. Navigates to `creator.xiaohongshu.com/publish/publish`
3. Clicks "上传图文" (upload images) tab
4. Uploads all images via file input
5. Sets title (native input value setter for React compatibility)
6. Sets body (innerHTML on TipTap/ProseMirror editor)
7. Takes preview screenshot
8. Optionally clicks "发布" (publish) button

## Tips

- **Title**: Keep under 20 chars. Hook-style titles work best (e.g. "用AI画塔罗牌也太好看了吧")
- **Body**: Short paragraphs with emoji. 小红书 is scroll-heavy — hooks > long text
- **Images**: First image is the cover. Use 3:4 ratio (1242×1660) for best display
- **Hashtags**: Add 3-5 relevant tags for discoverability
- **Preview first**: Always run without `--publish` first to verify via screenshot

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Cannot connect to CDP" | Ensure browser is running with remote debugging. For OpenClaw: check `openclaw browser status` |
| "Redirected" / not logged in | Open the browser manually and log in to creator.xiaohongshu.com |
| Title input not found | Page may not have loaded. Increase wait time or check network |
| Images fail to upload | Ensure images are PNG/JPG/WebP and under 20MB each |

## XHS Content Best Practices

- **Short hook titles** > descriptive titles (20 char limit forces creativity)
- **3-6 images** per post is the sweet spot
- **First image = cover** — make it eye-catching
- **Short punchy paragraphs** with emoji — not walls of text
- **End with a question** to drive comments
- **3-5 hashtags** for discovery, more feels spammy
