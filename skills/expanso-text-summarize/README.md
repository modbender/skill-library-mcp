# text-summarize

> Summarize any text into 3-5 bullet points while keeping your API keys local.

This is the "Hello World" of Expanso + OpenClaw skills. It demonstrates the core value proposition:

- **Your API keys stay local** - `${OPENAI_API_KEY}` is resolved on your machine
- **Validated pipelines** - This skill passes `expanso-cli job validate`
- **Full audit trail** - Every invocation is logged with input hash and trace ID
- **Backend flexibility** - Use OpenAI or Ollama without code changes

## Quick Start

### CLI Mode (for shell scripting)

```bash
# Set your API key
export OPENAI_API_KEY=sk-...

# Summarize text from stdin
echo "Your long article or document text here..." | \
  expanso-edge run pipeline-cli.yaml

# Or pipe a file
cat my-article.txt | expanso-edge run pipeline-cli.yaml
```

### MCP Mode (for OpenClaw integration)

```bash
# Start the skill server
PORT=8080 expanso-edge run pipeline-mcp.yaml &

# Call from curl (or OpenClaw MCP)
curl -X POST http://localhost:8080/summarize \
  -H "Content-Type: application/json" \
  -d '{"text": "Your long article or document text here..."}'
```

## Configuration

| Environment Variable | Required | Description |
|---------------------|----------|-------------|
| `OPENAI_API_KEY` | Yes* | OpenAI API key |
| `PORT` | No | HTTP port for MCP mode (default: 8080) |

*Not required if using Ollama backend locally.

## Example Output

```json
{
  "summary": "• Key insight from the text\n• Another important point\n• Action item or recommendation\n• Supporting detail\n• Conclusion or next steps",
  "metadata": {
    "skill": "text-summarize",
    "mode": "cli",
    "model": "gpt-4o-mini",
    "input_hash": "a1b2c3d4e5f6...",
    "input_length": 2847,
    "trace_id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2026-01-31T12:00:00Z"
  }
}
```

## Using with Ollama (Local, No API Key)

For complete privacy, you can use Ollama instead of OpenAI. Edit the pipeline to replace `openai_chat_completion` with `ollama_chat`:

```yaml
# In pipeline-cli.yaml, replace:
- openai_chat_completion:
    api_key: "${OPENAI_API_KEY}"
    model: gpt-4o-mini

# With:
- ollama_chat:
    server_address: "http://localhost:11434"
    model: llama3.2
```

Make sure Ollama is running:

```bash
ollama run llama3.2
```

## How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                     YOUR MACHINE                                 │
│                                                                 │
│  ┌───────────┐     ┌─────────────────┐     ┌───────────────┐   │
│  │ Input     │────▶│ Expanso Edge    │────▶│ Output        │   │
│  │ (stdin or │     │                 │     │ (stdout or    │   │
│  │  HTTP)    │     │ ${OPENAI_API_KEY}│     │  HTTP resp)   │   │
│  └───────────┘     │ resolved HERE   │     └───────────────┘   │
│                    └────────┬────────┘                         │
│                             │                                   │
│                    ┌────────▼────────┐                         │
│                    │ Local Vault     │                         │
│                    │ (env vars)      │                         │
│                    └─────────────────┘                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ API call with key
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     OPENAI API                                   │
│                                                                 │
│  Receives: text to summarize                                    │
│  Does NOT receive: who you are, where the key came from        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

The key insight: OpenAI only sees the text. Your identity and credential source are protected by the local execution model.

## Troubleshooting

### "OPENAI_API_KEY not set"

Make sure you've exported the environment variable:

```bash
export OPENAI_API_KEY=sk-your-key-here
```

### "text field is required"

For MCP mode, make sure you're sending JSON with a `text` field:

```bash
curl -X POST http://localhost:8080/summarize \
  -H "Content-Type: application/json" \
  -d '{"text": "Your text here"}'
```

### Validation Errors

Run the validation script:

```bash
uv run -s scripts/validate-skills.py text-summarize
```

## Cost Estimate

Using OpenAI GPT-4o-mini:
- ~$0.15 per 1M input tokens
- ~$0.60 per 1M output tokens
- Typical summary: ~$0.001 (less than a penny)

Using Ollama: **Free** (runs locally)

## Related Skills

- [json-extract](../json-extract/) - Extract structured JSON from text
- [pii-detect](../pii-detect/) - Detect PII in text

---

*Built with [Expanso Edge](https://expanso.io) - Your keys, your machine.*
