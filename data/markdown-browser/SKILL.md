---
name: markdown-browser
description: "Wrapper skill for OpenClaw web_fetch results. Use when you need MECE post-processing on fetched pages: policy decision from Content-Signal, privacy redaction, optional markdown normalization fallback, and stable output schema without re-implementing network fetch."
---

# Markdown Browser Skills

This skill is an orchestration layer, not a replacement fetcher. It always keeps official `web_fetch` as the fetch source of truth.

## MECE Architecture

1. Fetch layer (official, exclusive)
- Use OpenClaw `web_fetch` to retrieve the page.
- Do not call direct HTTP fetch inside this skill for normal operation.

2. Policy layer (these skills)
- Parse `Content-Signal` and compute `policy_action`.
- Current action focuses on `ai-input` semantics: `allow_input`, `block_input`, `needs_review`.

3. Privacy layer (these skills)
- Redact path/fragment/query values in output URL fields.
- Keep URL shape useful for debugging without leaking sensitive values.

4. Normalization layer (these skills)
- If `contentType=text/markdown`, keep content as-is.
- If `contentType=text/html`, convert with `turndown` as fallback enhancement.
- For other content types, pass through text.

## Execution Order

1. Call official `web_fetch`.
2. Pass the result JSON into this wrapper.
3. Optionally pass `Content-Signal` and `x-markdown-tokens` header values if available.
4. Use the returned normalized object for downstream agent logic.

## Wrapper Tool

`process_web_fetch_result({ web_fetch_result, content_signal_header, markdown_tokens_header })`

Input:
- `web_fetch_result` (required): JSON payload returned by OpenClaw `web_fetch`.
- `content_signal_header` (optional): raw `Content-Signal` header string.
- `markdown_tokens_header` (optional): raw `x-markdown-tokens` header value.

Output:
- `content`
- `format` (`markdown` | `html-fallback` | `text`)
- `token_estimate` (`number | null`)
- `content_signal`
- `policy_action`
- `source_url` (redacted)
- `status_code`
- `fallback_used`

## CLI Usage

```bash
# Install runtime dependency once inside the skill directory
npm install --omit=dev

# 1) Obtain a web_fetch payload first (from OpenClaw runtime)
# 2) Save it as /tmp/web_fetch.json
# 3) Run wrapper post-processing
node browser.js \
  --input /tmp/web_fetch.json \
  --content-signal "ai-input=yes, search=yes, ai-train=no" \
  --markdown-tokens "1820"
```
