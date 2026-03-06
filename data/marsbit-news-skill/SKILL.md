---
name: marsbit-opennews
description: Fetch MarsBit news and flash data through the hosted MCP route in marsbit-co. Use this for latest news, channel lookup, keyword search, detail, related news, and flash updates.
metadata: {"openclaw":{"emoji":"📰","requires":{"bins":["curl"]},"install":[{"id":"curl","kind":"brew","formula":"curl","label":"curl (HTTP client)"}],"os":["darwin","linux","win32"]},"version":"1.3.1"}
---

# MarsBit OpenNews Skill (Directly Usable)

This skill is designed to work immediately after installation using the hosted
MCP endpoint.

MCP endpoint:
- `https://www.marsbit.co/api/mcp`

Use this endpoint in all commands:

```bash
MCP_URL="https://www.marsbit.co/api/mcp"
```

## Runtime rules

When user asks for MarsBit news/flash info, call MCP tools via `curl` directly.

Required headers for every MCP POST:
- `Content-Type: application/json`
- `Accept: application/json, text/event-stream`
- `mcp-protocol-version: 2025-11-25`

Response parsing:
- MCP wraps tool output in `result.content[0].text`
- `text` is a JSON string; parse it before answering
- If `success` is `false`, surface the error and ask user whether to retry with different params

## Tool calls

### 1) List tools (quick connectivity check)

```bash
curl -sS -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-protocol-version: 2025-11-25" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

### 2) Get news channels

```bash
curl -sS -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-protocol-version: 2025-11-25" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"get_news_channels","arguments":{}}}'
```

### 3) Get latest news

```bash
curl -sS -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-protocol-version: 2025-11-25" \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"get_latest_news","arguments":{"limit":10}}}'
```

### 4) Search news by keyword

```bash
curl -sS -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-protocol-version: 2025-11-25" \
  -d '{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"search_news","arguments":{"keyword":"bitcoin","limit":10}}}'
```

### 5) Get one news detail by id

```bash
curl -sS -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-protocol-version: 2025-11-25" \
  -d '{"jsonrpc":"2.0","id":5,"method":"tools/call","params":{"name":"get_news_detail","arguments":{"news_id":"20260304151610694513"}}}'
```

### 6) Get related news by id

```bash
curl -sS -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-protocol-version: 2025-11-25" \
  -d '{"jsonrpc":"2.0","id":6,"method":"tools/call","params":{"name":"get_related_news","arguments":{"news_id":"20260304151610694513","limit":6}}}'
```

### 7) Get latest flash

```bash
curl -sS -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-protocol-version: 2025-11-25" \
  -d '{"jsonrpc":"2.0","id":7,"method":"tools/call","params":{"name":"get_latest_flash","arguments":{"limit":10}}}'
```

### 8) Search flash by keyword

```bash
curl -sS -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-protocol-version: 2025-11-25" \
  -d '{"jsonrpc":"2.0","id":8,"method":"tools/call","params":{"name":"search_flash","arguments":{"keyword":"ETF","limit":10}}}'
```

## Intent -> tool routing

- Latest news -> `get_latest_news`
- News channels -> `get_news_channels`
- Keyword news search -> `search_news`
- One news detail -> `get_news_detail`
- Related by news id -> `get_related_news`
- Latest flash -> `get_latest_flash`
- Keyword flash search -> `search_flash`

## Backend architecture alignment

This skill relies on the current `marsbit-co` hosted MCP implementation (`/api/mcp`), which internally uses:
- `fetcher(..., { marsBit: true })` in `src/lib/utils.ts`
- News APIs: `/info/news/channels`, `/info/news/shownews`, `/info/news/getbyid`, `/info/news/v2/relatednews`
- Flash API: `/info/lives/showlives`
- Search API: `/info/assist/querySimilarityInfo` (via `src/lib/db-marsbit/agent`)

## ClawHub upload path

Upload this folder directly:

`marsbit-co/skills/opennews`

Do not upload its parent directory.
