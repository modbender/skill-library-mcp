---
name: notebooklm-cli
description: Search and answer questions over documents already uploaded to NotebookLM using the nlm CLI. Use when users ask to find information, summarize sources, or query a specific NotebookLM notebook.
metadata: {"openclaw":{"requires":{"bins":["nlm"],"env":["NOTEBOOKLM_MCP_CLI_PATH"]}}}
user-invocable: true
---

# NotebookLM CLI

## Purpose

Use this skill when the user wants to search or ask questions over content that already exists in NotebookLM notebooks.

This skill assumes:
- `nlm` is installed (`notebooklm-mcp-cli` package).
- Auth was pre-injected for headless runtime.
- `NOTEBOOKLM_MCP_CLI_PATH` points to the auth storage directory.

## Hard Rules (avoid wrong tool choices)

When the user mentions any of the following, treat it as a strict request to query NotebookLM:
- "NotebookLM", "notebooklm"
- "notebook alias", "alias"
- a known alias name (for example: `tai_lieu_dien`, `nlm_tai_lieu_dien`)

In these cases:
- Always run `nlm` via Exec to answer. Do not answer from memory.
- Do not switch to web search unless the user explicitly asks for web sources.
- If the answer is not in the notebook, say so (based on the `nlm` output).

Slash command:
- If the user invokes this skill via `/nlm ...` in Telegram, treat the raw text after `/nlm` as the `nlm` arguments.
- Always execute exactly: `nlm <args>` via Exec, and return the relevant stdout.

## Runtime Checks

Before running queries:

1. Verify auth path is configured:
```bash
echo "$NOTEBOOKLM_MCP_CLI_PATH"
```
2. Verify login status:
```bash
nlm login --check
```

If auth check fails, stop and ask for auth refresh workflow (do not run browser login in AWS runtime).

## Query Workflow

1. List notebooks:
```bash
nlm notebook list --json
```
2. Select notebook:
- If user provided notebook id, use it directly.
- If user provided title, resolve it to `notebook_id` from the list output (do not pass raw title into `nlm notebook get/source list/query`).
- If user provided alias, use the alias.
- If ambiguous, ask user to choose one notebook.
3. Query notebook:
```bash
nlm notebook query "<notebook_id_or_alias>" "<user_question>"
```
4. Return answer and include which notebook was queried.

Notes:
- `nlm notebook list` returns titles for display, but many other commands expect a notebook id (UUID) or an alias. Passing a title like `"tài liệu điện"` may return null/empty results.
- If the user will query the same notebook often, create an alias and use it consistently (for example: `tai_lieu_dien`).

## Telegram Prompt Templates (copy/paste)

Prefer one of these formats to reliably trigger this skill:

1) Force CLI query:
```text
Chạy lệnh: nlm notebook query tai_lieu_dien "giá của A9N61500 là bao nhiêu? Nếu notebook không có thông tin giá thì trả lời: không thấy trong NotebookLM."
```

2) Natural language but explicit:
```text
Trong NotebookLM notebook alias tai_lieu_dien: trả lời câu hỏi "giá của A9N61500 là bao nhiêu?". Bắt buộc dùng nlm để truy vấn, không tìm web, không đọc file local.
```

## Output Guidelines

- Be explicit about notebook identity (title + id when available).
- If query result is empty or vague, suggest a refined follow-up query.
- Prefer concise, factual answers grounded in NotebookLM response.

## Common Errors

- `Authentication expired` / `401` / `403`:
  - Check `NOTEBOOKLM_MCP_CLI_PATH`.
  - Ensure `profiles/default/cookies.json` and `profiles/default/metadata.json` exist.
  - Refresh cookies outside AWS (machine with browser), then redeploy secret.
- `nlm: command not found`:
  - Install package: `pipx install notebooklm-mcp-cli` (recommended), or `uv tool install notebooklm-mcp-cli`.

## Command Reference

```bash
# List notebooks
nlm notebook list --json

# Query notebook by id or alias
nlm notebook query "<notebook_id_or_alias>" "<question>"

# Check auth status
nlm login --check
```
