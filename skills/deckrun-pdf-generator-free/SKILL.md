---
name: deckrun-pdf-generator-free
version: 1.0.0
description: >
  Generate a presentation-quality PDF slide deck from Deckrun Markdown.
  No authentication required. Free. Returns a public URL valid for 90 days.
metadata:
  openclaw:
    requires:
      env: []
      bins: []
    homepage: https://agenticdecks.com
tags:
  - pdf
  - markdown
  - slides
  - presentations
  - export
  - ai-agents
  - documentation
---

# Deckrun Free PDF Generator

Converts Deckrun Markdown into a 16:9 PDF slide deck. No account or API key
required. Returns a public PDF URL valid for 90 days.

## Endpoint

```
POST https://free.agenticdecks.com/free/generate
Content-Type: application/json
```

## Request

```json
{
  "markdown": "<Deckrun Markdown>",
  "schema_version": "deckrun.v1"
}
```

## Response

```json
{
  "url": "https://storage.googleapis.com/.../deck.pdf",
  "slug": "abc123",
  "slides": 6,
  "warnings": [],
  "schema_version": "deckrun.v1"
}
```

## Slide format

Fetch the live format spec before writing Markdown:

```
GET https://agenticdecks.com/schemas/v1/deckrun-slide-format.schema.json
```

Key rules:
- Slides are separated by `---` on its own line
- First slide must use `<!-- <title-slide /> -->`
- All other slides use `<!-- <title-content-slide /> -->` or another layout tag
- Title slide heading is `#` (H1); all other slide headings are `##` (H2)
- Maximum 10 slides, 50 KB Markdown

## Example

```markdown
<!-- <title-slide /> -->
# Quantum Computing Today

Prepared by AI

---

<!-- <title-content-slide /> -->
## What is Quantum Computing?

- Uses quantum bits (qubits) instead of classical bits
- Exploits superposition and entanglement
- Exponential speedup for certain problem classes
```

## Constraints

| Limit | Value |
|-------|-------|
| Max slides | 10 |
| Max Markdown size | 50 KB |
| PDF expiry | 90 days |
| Watermark | Required (free tier) |
| Auth | None |

## Links

- OpenAPI spec: https://free.agenticdecks.com/.well-known/openapi.yaml
- Slide format schema: https://agenticdecks.com/schemas/v1/deckrun-slide-format.schema.json
- MCP server (Claude Desktop / Cursor): https://smithery.ai/servers/agenticdecks/deckrun-free
- Web UI: https://free.agenticdecks.com
