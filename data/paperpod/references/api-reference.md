# PaperPod API Reference

Complete reference for HTTP endpoints. For CLI commands:
- `ppod help` — show all commands
- `ppod <cmd> --help` — per-command help (e.g., `ppod browser:screenshot --help`)

## Authentication

All requests require a PaperPod token (`pp_sess_...`).

### Getting a Token

```bash
# 1. Request magic link
curl -X POST https://paperpod.dev/login \
  -H "Content-Type: application/json" \
  -d '{"email":"you@email.com"}'

# 2. Click link in email → get token
```

### Using the Token

| Method | Example |
|--------|---------|
| **Header** | `Authorization: Bearer pp_sess_...` |
| **Env var** | `export PAPERPOD_TOKEN=pp_sess_...` |
| **CLI** | `ppod login pp_sess_...` |

Tokens expire in **15 days**. Refresh before expiry:

```bash
curl -X POST https://paperpod.dev/auth/refresh \
  -d '{"token":"pp_sess_..."}'
```

---

## Code Execution

### POST /execute

Run Python, JavaScript, or shell code.

```bash
curl -X POST https://paperpod.dev/execute \
  -H "Authorization: Bearer $PAPERPOD_TOKEN" \
  -d '{
    "code": "print(\"Hello!\")",
    "language": "python"
  }'
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `code` | string | Yes | Code to execute |
| `language` | string | Yes | `python`, `javascript`, or `shell` |
| `timeout` | number | No | Max execution time in ms (default: 30000) |
| `env` | object | No | Environment variables |

### POST /execute/stream

Same as `/execute` but returns Server-Sent Events for streaming output.

### POST /interpret

Execute code with rich output (charts, images, data frames).

---

## File Operations

### POST /files/write

```bash
curl -X POST https://paperpod.dev/files/write \
  -H "Authorization: Bearer $PAPERPOD_TOKEN" \
  -d '{"path": "/workspace/app.py", "content": "print(\"hello\")"}'
```

### POST /files/read

```bash
curl -X POST https://paperpod.dev/files/read \
  -H "Authorization: Bearer $PAPERPOD_TOKEN" \
  -d '{"path": "/workspace/app.py"}'
```

### POST /files/list

```bash
curl -X POST https://paperpod.dev/files/list \
  -H "Authorization: Bearer $PAPERPOD_TOKEN" \
  -d '{"path": "/workspace"}'
```

---

## Process Management

### POST /process/start

Start a background process.

```bash
curl -X POST https://paperpod.dev/process/start \
  -H "Authorization: Bearer $PAPERPOD_TOKEN" \
  -d '{"command": "python -m http.server 8080", "processId": "web"}'
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `command` | string | Yes | Command to run |
| `processId` | string | No | Custom ID for the process |
| `env` | object | No | Environment variables |

### POST /process/list

List running processes.

### POST /process/get

Get process status by ID.

### POST /process/stop

Stop a running process.

---

## Port Exposure

### POST /expose

Expose a port and get a public URL.

```bash
curl -X POST https://paperpod.dev/expose \
  -H "Authorization: Bearer $PAPERPOD_TOKEN" \
  -d '{"port": 8080}'
```

**Response:**
```json
{
  "url": "https://8080-abc123-p8080_v1.paperpod.work",
  "port": 8080
}
```

**Important:**
- Server must bind to `0.0.0.0`, not `localhost`
- Ports 3000-3010 are reserved (use 8080, 5000, 4000, etc.)

---

## Agent Memory

Persistent storage that survives sandbox resets (10MB per user).

### POST /memory/write

```bash
curl -X POST https://paperpod.dev/memory/write \
  -H "Authorization: Bearer $PAPERPOD_TOKEN" \
  -d '{"path": "state.json", "content": "{\"step\": 3}"}'
```

### POST /memory/read

```bash
curl -X POST https://paperpod.dev/memory/read \
  -H "Authorization: Bearer $PAPERPOD_TOKEN" \
  -d '{"path": "state.json"}'
```

### POST /memory/list

List all files in memory.

### POST /memory/delete

Delete a file from memory.

### POST /memory/usage

Check quota usage.

---

## Browser Automation

All browser endpoints use Playwright and support:

| Parameter | Type | Description |
|-----------|------|-------------|
| `url` | string | URL to render |
| `waitForSelector` | string | CSS selector to wait for |
| `waitForTimeout` | number | Time to wait in ms (max 30000) |

### POST /browser/screenshot

```bash
curl -X POST https://paperpod.dev/browser/screenshot \
  -H "Authorization: Bearer $PAPERPOD_TOKEN" \
  -d '{"url": "https://example.com"}' \
  --output screenshot.png
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `width` | number | Viewport width (max 3840) |
| `height` | number | Viewport height (max 2160) |
| `fullPage` | boolean | Capture full scrollable page |
| `deviceScaleFactor` | number | Pixel density (max 3) |

### POST /browser/pdf

```bash
curl -X POST https://paperpod.dev/browser/pdf \
  -H "Authorization: Bearer $PAPERPOD_TOKEN" \
  -d '{"url": "https://example.com", "format": "A4"}' \
  --output page.pdf
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `format` | string | `A4`, `Letter`, `Legal` |
| `landscape` | boolean | Landscape orientation |
| `printBackground` | boolean | Include background graphics |

### POST /browser/markdown

Extract page content as markdown.

### POST /browser/scrape

Scrape elements by CSS selector.

```bash
curl -X POST https://paperpod.dev/browser/scrape \
  -H "Authorization: Bearer $PAPERPOD_TOKEN" \
  -d '{"url": "https://example.com", "selector": "h1, h2, p"}'
```

### POST /browser/content

Get rendered HTML content.

### POST /browser/trace

Run with Playwright tracing enabled.

### POST /browser/test

Run QA assertions against a page.

### GET /browser/sessions

List active browser sessions.

---

## AI Models

### POST /ai/generate

Text generation with LLMs.

```bash
# Simple prompt
curl -X POST https://paperpod.dev/ai/generate \
  -H "Authorization: Bearer $PAPERPOD_TOKEN" \
  -d '{"prompt": "Explain quantum computing briefly"}'

# Chat messages
curl -X POST https://paperpod.dev/ai/generate \
  -H "Authorization: Bearer $PAPERPOD_TOKEN" \
  -d '{
    "messages": [{"role": "user", "content": "Hello!"}],
    "model": "@cf/meta/llama-3.2-3b-instruct"
  }'
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `prompt` | string | Simple text prompt |
| `messages` | array | Chat format `[{role, content}]` |
| `model` | string | Model ID (default: llama-3.2-3b-instruct) |
| `maxTokens` | number | Max output tokens (default: 1024, max: 4096) |
| `temperature` | number | Sampling temperature |
| `lora` | string | Public LoRA adapter |

### POST /ai/embed

Generate text embeddings.

```bash
curl -X POST https://paperpod.dev/ai/embed \
  -H "Authorization: Bearer $PAPERPOD_TOKEN" \
  -d '{"text": "Hello world"}'
```

### POST /ai/image

Generate images.

```bash
curl -X POST https://paperpod.dev/ai/image \
  -H "Authorization: Bearer $PAPERPOD_TOKEN" \
  -d '{"prompt": "A sunset over mountains"}' \
  --output image.png
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `prompt` | string | Image description |
| `width` | number | Image width (max 2048) |
| `height` | number | Image height (max 2048) |
| `steps` | number | Inference steps (max 50) |

### POST /ai/transcribe

Transcribe audio to text.

```bash
curl -X POST https://paperpod.dev/ai/transcribe \
  -H "Authorization: Bearer $PAPERPOD_TOKEN" \
  -d '{"audio": "<base64-encoded-audio>"}'
```

### GET /ai/models

List available AI models by category.

---

## Error Handling

### Error Response Format

```json
{
  "error": true,
  "code": "ERROR_CODE",
  "message": "Description of what went wrong"
}
```

### Common Error Codes

| Code | HTTP | Description | Action |
|------|------|-------------|--------|
| `INVALID_JSON` | 400 | Malformed JSON body | Fix request body |
| `MISSING_FIELD` | 400 | Required field missing | Add the field |
| `INVALID_FIELD` | 400 | Field has wrong value | Check field value |
| `EXPIRED_TOKEN` | 401 | Token expired | `POST /login` |
| `INVALID_TOKEN` | 401 | Token invalid | `POST /login` |
| `INSUFFICIENT_CREDITS` | 402 | No credits remaining | Top up credits |
| `RATE_LIMITED` | 429 | Too many requests | Wait and retry |

---

## Billing

| Service | Price |
|---------|-------|
| Compute | $0.0001/second |
| Browser | $0.0001/second |
| AI | $0.02/1,000 neurons |

### Top-up Tiers

| Tier | Amount | Bonus |
|------|--------|-------|
| `micro` | $1 | - |
| `starter` | $5 | - |
| `pro` | $20 | +10% |
| `scale` | $100 | +20% |

New accounts get **$5 free credits**.
