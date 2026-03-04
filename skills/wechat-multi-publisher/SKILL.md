---
name: wechat-mp-publisher
description: "Publish one or multiple Markdown articles to WeChat Official Account (公众号) draft box in a single API call. Supports multi-article combined drafts (main article + sub-articles), smart cover image selection with Unsplash auto-match + 12-image fallback rotation, custom styling (gold quote highlights, && section dividers, accent headings), inline image auto-upload to WeChat CDN, digest auto-extraction, and optional immediate publish. Activate when user wants to push Markdown files to WeChat MP, publish to 公众号草稿箱, schedule WeChat articles, or automate public account content delivery."
---

# wechat-mp-publisher

Publish Markdown articles to WeChat Official Account draft box.

## Key features

- **Multi-article push** — main article + up to 7 sub-articles in one draft (unique vs single-article tools)
- **Smart cover images** — keyword-matched Unsplash + 12-image fallback pool, each article gets a different cover
- **Custom styling** — gold quote highlights, `&&` section dividers, accent-colored headings
- **Inline images** — local PNG/JPG auto-uploaded to WeChat CDN
- **Flexible credentials** — env vars or `~/.config/wechat-mp/credentials.json`

## Quick start

```bash
# Install dependency
npm install @wenyan-md/core

# Set credentials
export WECHAT_APP_ID=your_appid
export WECHAT_APP_SECRET=your_appsecret

# Push to draft box
node scripts/publish.mjs main-article.md [sub-article.md ...]
```

See `references/setup.md` for full credential setup, IP whitelist, and cron automation.

## Markdown conventions

**Section divider** (renders as gradient rule):
```
paragraph text

&&

next paragraph
```

**Section header** (renders as accented H2):
```
&& My Section Title
```

**Gold quotes** — automatically highlighted when text starts with:
- `真正的...` / `不是...而是...` / `底层逻辑是...` / `关键不是...`

## CLI reference

```
node scripts/publish.mjs <main.md> [sub1.md] [sub2.md] ...
  --dry-run        Render to /tmp/wechat-preview/ without uploading
  --publish        Also trigger freepublish after draft creation
  --media-id=xxx   Publish an existing draft by media_id
```

## Author field

Set `WECHAT_AUTHOR` env var to customize the author name shown in WeChat.
