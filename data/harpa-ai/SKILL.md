---
name: harpa-grid
description: Automate web browsers, scrape pages, search the web, and run AI prompts on live websites via HARPA AI Grid REST API
user-invocable: true
homepage: https://harpa.ai/grid/web-automation
metadata: {"openclaw":{"emoji":"🌐","requires":{"anyBins":["curl","wget"],"env":["HARPA_API_KEY"]},"primaryEnv":"HARPA_API_KEY","homepage":"https://harpa.ai/grid/web-automation","skillKey":"harpa-grid"}}
---

# HARPA Grid — Browser Automation API

HARPA Grid lets you orchestrate real web browsers remotely. You can scrape pages, search the web, run built-in or custom AI commands, and send AI prompts with full page context — all through a single REST endpoint.

## Prerequisites

The user **must** have:
1. **HARPA AI Chrome Extension** installed from https://harpa.ai
2. **At least one active Node** — a browser with HARPA running (configured in the extension's AUTOMATE tab)
3. **A HARPA API key** — obtained from the HARPA extension AUTOMATE tab. The key is provided as the `HARPA_API_KEY` environment variable.

If the user hasn't set up HARPA yet, direct them to: https://harpa.ai/grid/browser-automation-node-setup

## API Reference

**Endpoint:** `POST https://api.harpa.ai/api/v1/grid`
**Auth:** `Authorization: Bearer $HARPA_API_KEY`
**Content-Type:** `application/json`

Full reference: https://harpa.ai/grid/grid-rest-api-reference

---

## Actions

### 1. Scrape a Web Page

Extract full page content (as markdown) or specific elements via CSS/XPath/text selectors.

**Full page scrape:**

```bash
curl -s -X POST https://api.harpa.ai/api/v1/grid \
  -H "Authorization: Bearer $HARPA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "scrape",
    "url": "https://example.com",
    "timeout": 15000
  }'
```

**Targeted element scrape (grab):**

```bash
curl -s -X POST https://api.harpa.ai/api/v1/grid \
  -H "Authorization: Bearer $HARPA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "scrape",
    "url": "https://example.com/products",
    "grab": [
      {
        "selector": ".product-title",
        "selectorType": "css",
        "at": "all",
        "take": "innerText",
        "label": "titles"
      },
      {
        "selector": ".product-price",
        "selectorType": "css",
        "at": "all",
        "take": "innerText",
        "label": "prices"
      }
    ],
    "timeout": 15000
  }'
```

**Grab fields:**

| Field | Required | Default | Values |
|-------|----------|---------|--------|
| selector | yes | — | CSS (`.class`, `#id`), XPath (`//h2`), or text content |
| selectorType | no | auto | `auto`, `css`, `xpath`, `text` |
| at | no | first | `all`, `first`, `last`, or a number |
| take | no | innerText | `innerText`, `textContent`, `innerHTML`, `outerHTML`, `href`, `value`, `id`, `className`, `attributes`, `styles`, `[attrName]`, `(styleName)` |
| label | no | data | Custom label for extracted data |

### 2. Search the Web (SERP)

Perform a web search. Supports operators like `site:`, `intitle:`.

```bash
curl -s -X POST https://api.harpa.ai/api/v1/grid \
  -H "Authorization: Bearer $HARPA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "serp",
    "query": "OpenClaw AI agent framework",
    "timeout": 15000
  }'
```

### 3. Run an AI Command

Execute one of 100+ built-in HARPA commands or a custom automation on a target page.

```bash
curl -s -X POST https://api.harpa.ai/api/v1/grid \
  -H "Authorization: Bearer $HARPA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "command",
    "url": "https://example.com/article",
    "name": "Extract data",
    "inputs": "List all headings with their word counts",
    "connection": "HARPA AI",
    "resultParam": "message",
    "timeout": 30000
  }'
```

- `name` — command name (e.g. `"Summary"`, `"Extract data"`, or any custom command)
- `inputs` — pre-filled user inputs for multi-step commands
- `resultParam` — HARPA parameter to return as result (default: `"message"`)
- `connection` — AI model to use (e.g. `"HARPA AI"`, `"gpt-4o"`, `"claude-3.5-sonnet"`)

### 4. Run an AI Prompt

Send a custom AI prompt with page context. Use `{{page}}` to inject the page content.

```bash
curl -s -X POST https://api.harpa.ai/api/v1/grid \
  -H "Authorization: Bearer $HARPA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "prompt",
    "url": "https://example.com",
    "prompt": "Analyze the current page and extract all contact information. Webpage: {{page}}",
    "connection": "CHAT AUTO",
    "timeout": 30000
  }'
```

---

## Common Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| action | yes | — | `scrape`, `serp`, `command`, or `prompt` |
| url | no | — | Target page URL (ignored by `serp`) |
| node | no | — | Node ID (`"r2d2"`), multiple (`"r2d2 c3po"`), first N (`"5"`), or all (`"*"`) |
| timeout | no | 300000 | Max wait time in ms (max 5 minutes) |
| resultsWebhook | no | — | URL to POST results to asynchronously (retained 30 days) |
| connection | no | — | AI model for `command`/`prompt` actions |

## Node Targeting

- Omit `node` to use the default node
- `"node": "mynode"` — target a specific node by ID
- `"node": "node1 node2"` — target multiple nodes
- `"node": "3"` — use first 3 available nodes
- `"node": "*"` — broadcast to all nodes

## Async Results via Webhook

Set `resultsWebhook` to receive results asynchronously. The action stays alive for up to 30 days, useful when target nodes are temporarily offline.

```json
{
  "action": "scrape",
  "url": "https://example.com",
  "resultsWebhook": "https://your-server.com/webhook",
  "timeout": 15000
}
```

## Tips

- Scraping behind-login pages works because HARPA runs inside a real browser session with the user's cookies and auth state.
- Use the `grab` array with multiple selectors to extract structured data in a single request.
- For long-running AI commands, increase `timeout` (max 300000ms / 5 min) or use `resultsWebhook`.
- The `{{page}}` variable in prompts injects the full page content — use it to give AI context about the current page.
