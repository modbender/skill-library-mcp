---
name: agorahub
version: "1.0.0"
description: "AgoraHub agent registry — discover and use 14+ verified AI agents for dev tasks like hashing, encoding, formatting, and more. No signup needed for demo agents."
metadata:
  openclaw:
    emoji: "🌐"
    requires:
      bins: ["curl", "jq"]
      env: ["AGORAHUB_API_KEY"]
    primaryEnv: "AGORAHUB_API_KEY"
---

# AgoraHub — AI Agent Registry

AgoraHub is an open agent registry with 14+ verified demo agents you can use instantly — no signup required. For community agents, get an API key at https://agorahub.dev/dashboard/api-keys.

**Base URL:** `https://agorahub.dev`

---

## 1. Discover Available Agents

List all agents exposed as MCP tools:

```bash
curl -s https://agorahub.dev/api/mcp/tools | jq '.tools[] | {name, description}'
```

### Filter by Tags

```bash
curl -s "https://agorahub.dev/api/mcp/tools?tags=crypto" | jq '.tools[] | {name, description}'
```

### Search by Name/Description

```bash
curl -s "https://agorahub.dev/api/mcp/tools?q=hash" | jq '.tools[] | {name, description}'
```

---

## 2. Call an Agent

All 14 demo agents work without an API key. For community agents, add `-H "Authorization: Bearer $AGORAHUB_API_KEY"`.

### General Call Format

```bash
curl -s -X POST https://agorahub.dev/api/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{"name":"agora_<agent-slug>_<skill-id>","arguments":{...}}' | jq
```

---

## 3. Agent Quick Reference

### Echo Agent
Echo back a message with a timestamp.
```bash
curl -s -X POST https://agorahub.dev/api/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{"name":"agora_echo-agent_echo","arguments":{"message":"hello world"}}' | jq
```

### Hash Generator
Generate cryptographic hashes (md5, sha1, sha256, sha512).
```bash
curl -s -X POST https://agorahub.dev/api/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{"name":"agora_hash-generator_hash","arguments":{"text":"hello","algorithm":"sha256"}}' | jq
```

Hash with all algorithms at once:
```bash
curl -s -X POST https://agorahub.dev/api/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{"name":"agora_hash-generator_hash-all","arguments":{"text":"hello"}}' | jq
```

### Password Generator
Generate secure passwords with customizable options.
```bash
curl -s -X POST https://agorahub.dev/api/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{"name":"agora_password-generator_generate","arguments":{"length":20,"count":3,"symbols":true}}' | jq
```

### JSON Formatter
Validate, pretty-print, or minify JSON.
```bash
curl -s -X POST https://agorahub.dev/api/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{"name":"agora_json-formatter_format","arguments":{"json":"{\"key\":\"value\",\"num\":42}"}}' | jq
```

### Base64 Codec
Encode text to Base64:
```bash
curl -s -X POST https://agorahub.dev/api/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{"name":"agora_base64-codec_encode","arguments":{"text":"hello world"}}' | jq
```

Decode Base64 back to text:
```bash
curl -s -X POST https://agorahub.dev/api/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{"name":"agora_base64-codec_decode","arguments":{"text":"aGVsbG8gd29ybGQ="}}' | jq
```

### UUID Generator
Generate UUIDs in v4 or v7 format.
```bash
curl -s -X POST https://agorahub.dev/api/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{"name":"agora_uuid-generator_generate","arguments":{"version":"v4","count":5}}' | jq
```

### Regex Tester
Test regex patterns against text.
```bash
curl -s -X POST https://agorahub.dev/api/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{"name":"agora_regex-tester_test","arguments":{"pattern":"\\d+","text":"abc 123 def 456"}}' | jq
```

### JWT Decoder
Decode a JWT token (without verification).
```bash
curl -s -X POST https://agorahub.dev/api/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{"name":"agora_jwt-decoder_decode","arguments":{"token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"}}' | jq
```

### Markdown to HTML
Convert Markdown text to HTML.
```bash
curl -s -X POST https://agorahub.dev/api/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{"name":"agora_markdown-to-html_convert","arguments":{"markdown":"# Hello\n\n**Bold** and *italic*"}}' | jq
```

### Text Stats
Analyze text for word count, reading time, and more.
```bash
curl -s -X POST https://agorahub.dev/api/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{"name":"agora_text-stats_analyze","arguments":{"text":"The quick brown fox jumps over the lazy dog. This is a sample text for analysis."}}' | jq
```

### Lorem Ipsum Generator
Generate placeholder text.
```bash
curl -s -X POST https://agorahub.dev/api/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{"name":"agora_lorem-ipsum_generate","arguments":{"format":"paragraphs","count":2}}' | jq
```

### CSV/JSON Converter
Convert CSV to JSON:
```bash
curl -s -X POST https://agorahub.dev/api/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{"name":"agora_csv-json-converter_csv-to-json","arguments":{"csv":"name,age\nAlice,30\nBob,25"}}' | jq
```

Convert JSON to CSV:
```bash
curl -s -X POST https://agorahub.dev/api/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{"name":"agora_csv-json-converter_json-to-csv","arguments":{"data":[{"name":"Alice","age":30},{"name":"Bob","age":25}]}}' | jq
```

### Color Converter
Convert between Hex, RGB, and HSL.
```bash
curl -s -X POST https://agorahub.dev/api/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{"name":"agora_color-converter_convert","arguments":{"color":"#ff6600"}}' | jq
```

### Timestamp Converter
Convert between Unix timestamps, ISO 8601, and human-readable dates.
```bash
curl -s -X POST https://agorahub.dev/api/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{"name":"agora_timestamp-converter_convert","arguments":{"timestamp":"now"}}' | jq
```

---

## 4. Error Handling

Check the HTTP status code and `isError` field in the response:

- **200** — Success. Parse `content[0].text` for the result.
- **400** — Bad request. Check `error` field for details (missing tool name, invalid format).
- **401** — Authentication required. Only for non-demo agents. Set `AGORAHUB_API_KEY`.
- **404** — Agent or skill not found. Use the discover endpoint to list available tools.
- **429** — Rate limited. Check `Retry-After` header.
- **500** — Internal error. Retry or report at https://github.com/Codevena/AgoraHub/issues.

```bash
# Example: check for errors
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST https://agorahub.dev/api/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{"name":"agora_echo-agent_echo","arguments":{"message":"test"}}')
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | head -n -1)

if [ "$HTTP_CODE" -ne 200 ]; then
  echo "Error ($HTTP_CODE): $(echo "$BODY" | jq -r '.error // .content[0].text')"
else
  echo "$BODY" | jq '.content[0].text | fromjson'
fi
```

---

## 5. Using with API Key (Community Agents)

For non-demo agents, authenticate with your API key:

```bash
export AGORAHUB_API_KEY="agora_your_key_here"

curl -s -X POST https://agorahub.dev/api/mcp/tools/call \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $AGORAHUB_API_KEY" \
  -d '{"name":"agora_some-community-agent_skill","arguments":{...}}' | jq
```

Get your API key at: https://agorahub.dev/dashboard/api-keys
