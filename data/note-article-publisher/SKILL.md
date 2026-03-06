---
name: note-article-publisher
description: Publish markdown articles to note.com with image upload, tags, and
  browser automation.
---


# Note Article Publisher

Publish articles to note.com from markdown files via browser automation.

**Use when** publishing to note.com, managing drafts, or automating content pipeline.

**Triggers**: "publish to note", "note.com article", "create note draft", "note記事"

## Requirements

- Node.js 18+
- Playwright with Chromium (`npx playwright install chromium`)
- note.com account credentials
- No external API keys needed

## Instructions

1. **Prepare markdown** with frontmatter:
   ```markdown
   ---
   title: 記事タイトル
   tags: [AI, テクノロジー]
   cover: ./cover.png
   ---

   # 見出し
   本文テキスト...

   ## セクション
   - リスト項目
   ![画像の説明](./image.png)
   ```

2. **Run the pipeline**:
   ```bash
   cd {skill_dir}
   npm install

   # Create draft from markdown
   node dist/cli.js draft --input ./article.md --title "記事タイトル"

   # Preview draft
   node dist/cli.js preview --draft-id <id>

   # Publish
   node dist/cli.js publish --draft-id <id> --tags "AI,テクノロジー"

   # Full pipeline (markdown → published)
   node dist/cli.js pipeline \
     --input ./article.md \
     --title "AIエージェントの作り方" \
     --tags "AI,プログラミング,自動化" \
     --cover-image ./cover.png
   ```

3. **Pipeline flow**:
   ```
   Markdown → Parse & Format → Upload images → Create draft → Review → Publish
   ```

## Configuration

Set credentials via environment variables:

```bash
# Option A: Session cookie (preferred — safer)
export NOTE_SESSION="your_session_cookie"

# Option B: Login credentials (less safe)
export NOTE_EMAIL="your@email.com"
export NOTE_PASSWORD="your_password"
```

## Security Considerations

- **⚠️ Prefer `NOTE_SESSION`** over email/password — session cookies are safer than plaintext passwords.
- Store credentials in `~/.openclaw/secrets.env` with `chmod 600`.
- **Never commit credentials to git** — add `.env` to `.gitignore`.
- Playwright navigation **must stay on `https://note.com/*`** — reject external redirects.
- Never log or display credential values in output.
- Session cookies expire — rotate periodically.
- Clear Playwright browser data after use on shared systems.

## Edge Cases

- **Session expired**: Re-login or refresh `NOTE_SESSION` cookie.
- **Image upload fails**: Check file size (note.com has limits), try compressing first.
- **Draft preview differs from publish**: note.com may reformat some HTML. Preview before publishing.
- **Rate limiting**: Don't publish many articles in rapid succession.
- **Playwright not installed**: Run `npx playwright install chromium` first.
- **Headless mode issues**: Some note.com pages may need `--headed` mode for debugging.

## Troubleshooting

- **Login fails**: Clear browser data and try fresh session.
- **Missing dependencies**: Run `npm install` in skill directory.
- **Chromium not found**: Run `npx playwright install chromium`.
