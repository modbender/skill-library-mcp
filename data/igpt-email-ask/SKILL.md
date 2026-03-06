---
name: igpt-email-ask
description: >
  Secure, per-user-isolated email reasoning and analysis via the iGPT Context Engine API.
  Summarizes threads, extracts tasks and decisions, detects sentiment, and reasons across multiple
  conversations -- no shell access, no filesystem access, API-key scoped only. Supports structured
  JSON output with schema validation and streaming (SSE). Use when the user needs analysis,
  summaries, structured data extraction, or answers that require understanding email context.
  For retrieval/lookup only, use the companion skill igpt-email-search.
homepage: https://igpt.ai/hub/playground/
metadata: {"clawdbot":{"emoji":"🧠","requires":{"env":["IGPT_API_KEY"]},"primaryEnv":"IGPT_API_KEY"},"author":"igptai","version":"1.0.0","license":"MIT","tags":["email","analysis","reasoning","summarization","context-engine","productivity"]}
---

# iGPT Email Ask

Ask questions about a user's email and get reasoned, structured answers. Powered by iGPT's Context Engine, which reconstructs conversations, decisions, ownership, and intent across time.

## What This Skill Does

This skill queries iGPT's `recall/ask` endpoint to generate answers grounded in a user's connected email data. Unlike basic retrieval, the Context Engine:

- Reconstructs full conversation threads across replies, forwards, and CCs
- Identifies who decided what, who owns what, and what's still open
- Extracts structured data (tasks, deadlines, contacts, risks) from unstructured email
- Supports multiple quality tiers for different complexity levels
- Returns text, JSON, or schema-validated structured output
- Supports streaming (SSE) for real-time responses

## When to Use This Skill

- Summarize what happened in a thread or across threads
- Extract action items, decisions, or open questions
- Analyze sentiment or risk in deal/customer threads
- Answer questions that require understanding context across multiple emails
- Generate structured data from email content (JSON, schema-validated)
- Prepare briefings before meetings based on recent correspondence

## Prerequisites

1. An iGPT API key (get one at https://igpt.ai/hub/apikeys/)
2. A connected email datasource -- the user must have completed OAuth authorization via `connectors/authorize` before ask will return results. You can check connection status with `datasources.list()`.
3. Python >= 3.8 with the `igptai` package installed

## Setup

```bash
pip install igptai
```

Set your API key as an environment variable:

```bash
export IGPT_API_KEY="your-api-key-here"
```

## Usage

### Basic: Ask a question

```python
from igptai import IGPT
import os

igpt = IGPT(api_key=os.environ["IGPT_API_KEY"], user="user_123")

res = igpt.recall.ask(input="Summarize key risks, decisions, and next steps from this week's meetings.")
if res is not None and res.get("error"):
    print("iGPT error:", res)
else:
    print(res)
```

### Get JSON output

Pass `output_format="json"` for unstructured JSON, or provide a schema for validated structured output:

```python
# Simple JSON output
res = igpt.recall.ask(
    input="What are the open action items from this week?",
    output_format="json"
)

# Schema-validated structured output
res = igpt.recall.ask(
    input="Open action items from this week",
    quality="cef-1-normal",
    output_format={
        "strict": True,
        "schema": {
            "type": "object",
            "required": ["action_items"],
            "additionalProperties": False,
            "properties": {
                "action_items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["title", "owner", "due_date"],
                        "properties": {
                            "title": {"type": "string"},
                            "owner": {"type": "string"},
                            "due_date": {"type": "string"}
                        }
                    }
                }
            }
        }
    }
)
print(res)
```

Example response:

```json
{
    "action_items": [
        {
            "title": "Approve revised Q1 budget allocation",
            "owner": "Dvir Ben-Aroya",
            "due_date": "2026-01-15"
        },
        {
            "title": "Approve final FY2026 strategic priorities",
            "owner": "Board of Directors",
            "due_date": "2026-01-31"
        }
    ]
}
```

### Use quality tiers

iGPT's Context Engine has three quality tiers:

```python
# Normal: fast, good for straightforward questions
res = igpt.recall.ask(
    input="When is my next meeting with Acme Corp?",
    quality="cef-1-normal"
)

# High: deeper reasoning, better for complex multi-thread analysis
res = igpt.recall.ask(
    input="What is the current negotiation status with Acme Corp and what leverage do we have?",
    quality="cef-1-high"
)

# Reasoning: maximum depth, for complex cross-thread synthesis
res = igpt.recall.ask(
    input="Across all communication with Acme over the past quarter, what patterns suggest risk and what should we do about it?",
    quality="cef-1-reasoning"
)
```

### Stream responses

Streaming returns parsed JSON chunks (dicts), not raw text. Extract content from each chunk:

```python
stream = igpt.recall.ask(
    input="Walk me through the timeline of the Acme deal from first contact to now.",
    stream=True
)

for chunk in stream:
    if isinstance(chunk, dict) and chunk.get("error"):
        print("Stream error:", chunk)
        break
    # Each chunk is a parsed JSON dict
    print(chunk)
```

Streaming is resilient: if the connection breaks, the iterator yields an error chunk and finishes rather than throwing.

### Check datasource connection before asking

```python
# Verify user has a connected datasource
status = igpt.datasources.list()
if status is not None and not status.get("error"):
    print("Connected datasources:", status)
else:
    # Connect a datasource first
    auth = igpt.connectors.authorize(service="spike", scope="messages")
    print("Open this URL to authorize:", auth.get("url"))
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| input | string | Yes | The prompt or question to ask. |
| user | string | Yes (or set in constructor) | Unique user identifier scoping the query to their connected data. Per-call value overrides constructor default. |
| stream | boolean | No (default: false) | If true, returns a generator yielding parsed JSON dicts via SSE. |
| quality | string | No | Context Engine quality tier: `"cef-1-normal"`, `"cef-1-high"`, or `"cef-1-reasoning"`. |
| output_format | string or object | No | `"text"` (default), `"json"`, or `{"strict": true, "schema": <JSON Schema>}` for validated structured output. |

## Error Handling

The SDK does not throw exceptions. It returns normalized error objects:

```python
res = igpt.recall.ask(input="What happened in yesterday's board meeting?")

if res is not None and res.get("error"):
    error = res["error"]
    if error == "auth":
        print("Check your API key")
    elif error == "params":
        print("Check your request parameters")
    elif error == "network_error":
        print("Network issue -- the SDK retries with exponential backoff (3 attempts by default) before returning this")
else:
    print(res)
```

## External Endpoints

This skill communicates exclusively with:

- `https://api.igpt.ai/v1/recall/ask/` -- the reasoning endpoint
- `https://api.igpt.ai/v1/connectors/authorize/` -- only during initial datasource connection setup
- `https://api.igpt.ai/v1/datasources/list/` -- to check connection status

No other external endpoints are contacted. No data is sent to any third-party service. The `igptai` PyPI package source is available at https://github.com/igptai/igpt-python.

## Security & Privacy

- **API-key scoped**: All requests authenticate via `IGPT_API_KEY` sent as a Bearer token over HTTPS. No shell access, no filesystem access, no system commands.
- **Per-user isolation**: Every query is scoped to a specific `user` identifier. User A cannot access User B's email data. Isolation is enforced at the index and execution level, not as a filter layer.
- **OAuth read-only**: The email datasource connection uses OAuth with read-only scopes. The skill does not send, modify, or delete emails.
- **No data retention**: Prompts are discarded after execution. Memory is reconstructed on-demand, not stored.
- **Transport encryption**: All communication occurs over HTTPS. No plaintext endpoints.
- **No local persistence**: This skill does not write to disk, modify environment files, or create persistent configuration outside of the standard `IGPT_API_KEY` environment variable.
- **Built-in retries**: The SDK retries failed requests with exponential backoff (default: 3 attempts, 100ms base, 2x factor) before returning a `network_error`.

For the full security model, see https://docs.igpt.ai/docs/security/model.

## What This Skill Does NOT Do

- Does not send, modify, forward, or delete emails
- Does not access the filesystem or execute shell commands
- Does not install persistent services or scheduled tasks
- Does not contact endpoints other than `api.igpt.ai`
- Does not store API keys or OAuth tokens outside the environment variable

## Example Questions

These all work as natural language prompts:

- `"Summarize key risks from this week's email threads"` -- cross-thread analysis
- `"What are the open action items from yesterday's board meeting?"` -- task extraction
- `"What's the current status of the Acme deal?"` -- deal intelligence
- `"Who owns the budget approval and when is it due?"` -- ownership and deadline extraction
- `"Are there any threads where tone has shifted negatively in the last 7 days?"` -- sentiment analysis
- `"Generate a briefing for my meeting with Sarah tomorrow"` -- meeting prep

## Resources

- **Get API Key**: https://igpt.ai/hub/apikeys/
- **Documentation**: https://docs.igpt.ai
- **API Reference**: https://docs.igpt.ai/docs/api-reference/ask
- **Playground**: https://igpt.ai/hub/playground/
- **Python SDK**: https://pypi.org/project/igptai/
- **Node.js SDK**: https://www.npmjs.com/package/igptai
- **GitHub**: https://github.com/igptai/igpt-python
