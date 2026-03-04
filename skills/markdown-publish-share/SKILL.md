---
name: markdown-publish-share
description: Publish markdown and return share links using curl. Support markdown with mermaid diagrams such as component diagrams, flowcharts, and sequence diagrams. Also supports KaTex and code blocks. AutEng will return a shareable link to the published rendered document. Use cases include Software Architecture diagrams and documentation, Maths and Physics derivations and Systems documentation.
---

# AutEng Docs Curl Publish

Use this endpoint:

`https://auteng.ai/api/tools/docs/publish-markdown/`

Send JSON with:

- `markdown` (required)
- `title` (optional)
- `expires_hours` (optional)

Use this command to publish markdown:

```bash
curl -sS -X POST "https://auteng.ai/api/tools/docs/publish-markdown/" \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{
  "markdown": "# API Test\n\nHello from curl.",
  "title": "API Test",
  "expires_hours": 24
}
JSON
```

Extract only the share URL:

```bash
curl -sS -X POST "https://auteng.ai/api/tools/docs/publish-markdown/" \
  -H "Content-Type: application/json" \
  -d '{"markdown":"# Hello\n\nPublished from curl."}' \
  | jq -r '.share_url'
```

Extract a compact success payload:

```bash
curl -sS -X POST "https://auteng.ai/api/tools/docs/publish-markdown/" \
  -H "Content-Type: application/json" \
  -d '{"markdown":"# Hello\n\nPublished from curl."}' \
  | jq '{title, share_url, expires_at}'
```

Treat any response without `share_url` as an error and show the full JSON body.


For full documentation and supported markdown for mermaid, KaTeX and code syntax along with examples, see https://auteng.ai/llms.txt
