---
name: feishu-comments
description: |
  Read comments from Feishu documents. Use when: user asks to check/read/fetch comments on a Feishu doc, review feedback on a document, or collaborate on document revisions via comments.
---

# Feishu Document Comments

Fetch comments from Feishu docx documents via the Drive Comment API.

## Requirements

- **Feishu app credentials** configured in `~/.openclaw/openclaw.json` (reads `appId` and `appSecret` from `channels.feishu`)
- **System dependencies**: `curl`, `python3` (must be available on PATH)
- **Feishu app permission**: `docs:document.comment:read` or `drive:drive`

## Usage

Run the bundled script to get all comments on a document:

```bash
bash skills/feishu-comments/scripts/get_comments.sh <doc_token>
```

To fetch specific comments by ID:

```bash
bash skills/feishu-comments/scripts/get_comments.sh <doc_token> "id1,id2,id3"
```

Resolve `skills/` paths relative to the workspace directory.

## When to Use

- After `feishu_doc` `list_blocks` shows `comment_ids` on blocks
- When user asks to review or check comments on a document
- During document collaboration review cycles

## Output Format

Each comment shows:
- Comment ID, status (Open/Resolved), scope (Global/Local)
- Quoted text (for local/inline comments)
- All replies with user ID and text content

## Extracting doc_token

From URL `https://xxx.feishu.cn/docx/ABC123def` → doc_token = `ABC123def`

For wiki pages, first use `feishu_wiki` to get `obj_token`, then use that as the doc_token.

## How It Works

The bundled shell script:
1. Reads Feishu app credentials (`appId`, `appSecret`) from `~/.openclaw/openclaw.json`
2. Obtains a `tenant_access_token` via the Feishu auth API
3. Calls the Drive Comment API to list and batch-query comments
4. Formats and outputs comment content to stdout

No data is sent to any third party beyond the Feishu/Lark API endpoints.

## Limitations

- Read-only (cannot create or reply to comments)
- API error responses are printed to stderr (may contain request IDs but no sensitive data)
