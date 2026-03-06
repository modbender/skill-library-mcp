# Humanizer Integrations

Use humanizer with Claude, ChatGPT, and other LLMs via multiple integration methods.

## Quick Comparison

| Method | Platforms | Setup | Best For |
|--------|-----------|-------|----------|
| **MCP Server** | Claude, ChatGPT, VS Code | Medium | Cross-platform tool access |
| **OpenAI Custom GPT** | ChatGPT Plus | Easy | ChatGPT users |
| **HTTP API** | Any | Medium | Custom integrations |
| **SKILL.md** | OpenClaw | Easy | OpenClaw agents |

---

## MCP Server (Recommended)

Model Context Protocol works with Claude Desktop, ChatGPT, VS Code, and other MCP clients.

### Install

```bash
cd humanizer/mcp-server
npm install
```

### Configure Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "humanizer": {
      "command": "node",
      "args": ["/path/to/humanizer/mcp-server/index.js"]
    }
  }
}
```

### Configure VS Code

Add to `.vscode/settings.json`:

```json
{
  "mcp.servers": {
    "humanizer": {
      "command": "node",
      "args": ["${workspaceFolder}/humanizer/mcp-server/index.js"]
    }
  }
}
```

### Available Tools

| Tool | Description |
|------|-------------|
| `score` | Quick AI score (0-100) |
| `analyze` | Full analysis with patterns and stats |
| `humanize` | Get suggestions with optional auto-fix |
| `stats` | Statistical analysis only |

---

## OpenAI Custom GPT

Create a GPT that has humanizer capabilities built-in.

### Setup

1. Go to [chat.openai.com/gpts/editor](https://chat.openai.com/gpts/editor)
2. Click "Create a GPT"
3. Copy instructions from `openai-gpt/instructions.md`
4. Name it "Humanizer"
5. (Optional) Add Actions using `api-server/openapi.yaml`

### With Actions API

If you want the GPT to call the humanizer programmatically:

1. Deploy the API server (see below)
2. In GPT editor, click "Configure" → "Create new action"
3. Import schema from your deployed `/api/openapi` endpoint

---

## HTTP API Server

Simple HTTP API for OpenAI Actions and custom integrations.

### Run Locally

```bash
cd humanizer
node api-server/server.js
```

### Deploy (Cloudflare Workers example)

```bash
# Create wrangler.toml
npx wrangler deploy
```

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/score` | POST | Quick score (0-100) |
| `/api/analyze` | POST | Full analysis |
| `/api/humanize` | POST | Suggestions + autofix |
| `/api/stats` | POST | Statistical analysis |
| `/api/openapi` | GET | OpenAPI spec |

### Example

```bash
curl -X POST http://localhost:3000/api/score \
  -H "Content-Type: application/json" \
  -d '{"text": "This serves as a testament to innovation."}'
```

Response:
```json
{
  "score": 62,
  "badge": "🟠",
  "interpretation": "Moderately AI-influenced"
}
```

---

## OpenClaw Skill

Already included as `SKILL.md`. Install via ClawHub:

```bash
clawhub install ai-humanizer
```

Or copy manually:

```bash
cp SKILL.md ~/.config/openclaw/skills/humanizer.md
```

---

## Always-On Mode

For LLMs that should ALWAYS write like a human (not just when asked), add the core rules to the system prompt.

### Claude (Projects or System Prompt)

Add to your project instructions or custom system prompt:

```markdown
## Writing Rules (Always Active)

Never use these words: delve, tapestry, vibrant, crucial, comprehensive, meticulous, embark, robust, seamless, groundbreaking, leverage, synergy, transformative, paramount, multifaceted, myriad, cornerstone, reimagine, empower, catalyst, invaluable, bustling, nestled, realm

Replace filler phrases:
- "In order to" → "to"
- "Due to the fact that" → "because"  
- "It is important to note that" → (just say it)

Never write: "Great question!", "I hope this helps!", "Let me know if..."

Vary sentence length. Have opinions. Use concrete specifics.
```

### ChatGPT (Custom Instructions)

Add to "How would you like ChatGPT to respond?":

```
Write like a human, not an AI. Never use words like: delve, tapestry, vibrant, crucial, seamless, groundbreaking, leverage, synergy, transformative, paramount. Replace "in order to" with "to". Never say "Great question!" or "I hope this helps!" Vary your sentence length. Have opinions. Be specific.
```

---

## Troubleshooting

### MCP Server not connecting

1. Check the path in config is absolute
2. Run `node mcp-server/index.js` manually to test
3. Check Claude/VS Code logs for errors

### API returns 500

1. Check that `src/*.js` files are ES modules (`import`/`export`)
2. Add `"type": "module"` to package.json if needed
3. Check Node version >= 18

### Score seems wrong

The scoring is transparent — run `analyze` with `verbose: true` to see exactly which patterns matched.
