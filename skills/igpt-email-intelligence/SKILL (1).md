---
name: igpt-email-ask
description: >
  Secure, per-user-isolated email reasoning and analysis via the iGPT Context Engine API.
  Summarizes threads, extracts tasks and decisions, detects sentiment, and reasons across multiple
  conversations — no shell access, no filesystem access, API-key scoped only. Supports structured
  JSON output with schema validation and streaming (SSE). Use when the user needs analysis,
  summaries, structured data extraction, or answers that require understanding email context.
  For retrieval/lookup only, use the companion skill igpt-email-search.
metadata:
  clawdbot:
    config:
      requiredEnv:
        - IGPT_API_KEY
      primaryCredential: IGPT_API_KEY
      example: |
        config = {
          env = {
            IGPT_API_KEY = "<your-api-key-from-igpt.ai/hub/apikeys>";
          };
        };
  author: igptai
  homepage: https://igpt.ai/hub/playground/
  version: "1.0.0"
  license: MIT
  tags:
    - email
    - analysis
    - reasoning
    - summarization
    - context-engine
    - productivity
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

This is the reasoning layer. It understands and analyzes email content. For finding and retrieving raw emails, use [`igpt-email-search`](https://clawhub.ai/skills/igpt-email-search) — the companion skill for hybrid semantic + keyword retrieval.

## When to Use This Skill

- Summarize what happened in a thread or across threads
- Extract action items, decisions, or open questions
- Analyze sentiment or risk in deal/customer threads
- Answer questions that require understanding context across multiple emails
- Generate structured data from email content (JSON, schema-validated)
- Prepare briefings before meetings based on recent correspondence

## When to Use igpt-email-search Instead

If you only need to find and retrieve emails without analysis — use [`igpt-email-search`](https://clawhub.ai/skills/igpt-email-search). Search returns raw results. Ask returns reasoned answers.

Rule of thumb: if the prompt is a question, use ask. If the prompt is a lookup, use search.

## Prerequisites

1. An iGPT API key (get one at https://igpt.ai/hub/apikeys/)
2. A connected email datasource — the user must have completed OAuth authorization via `connectors/authorize`
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

response = igpt.recall.ask(
    input="Summarize key risks, decisions, and next steps from this week's meetings."
)
print(response)
```

### Get structured JSON output

```python
response = igpt.recall.ask(
    input="Open action items from this week",
    quality="cef-1-normal",
    output_format={
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "action_items": {
                    "type": "array",
                    "items": {
                        "type": "object",
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
print(response)
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

iGPT's Context Engine has multiple quality tiers for different complexity levels:

```python
# Normal: fast, good for straightforward questions
response = igpt.recall.ask(
    input="When is my next meeting with Acme Corp?",
    quality="cef-1-normal"
)

# High: deeper reasoning, better for complex multi-thread analysis
response = igpt.recall.ask(
    input="What is the current negotiation status with Acme Corp and what leverage do we have?",
    quality="cef-1-high"
)
```

### Stream responses

For real-time output in interactive contexts:

```python
stream = igpt.recall.ask(
    input="Walk me through the timeline of the Acme deal from first contact to now.",
    stream=True
)

for chunk in stream:
    if isinstance(chunk, dict) and chunk.get("error"):
        print("Stream error:", chunk)
        break
    print(chunk, end="", flush=True)
```

Streaming is resilient: if the connection breaks, the iterator yields an error chunk and finishes rather than throwing.

### Two-step workflow with search

Search first to scope what's available, then ask for analysis:

```python
# Step 1: Find relevant threads
results = igpt.recall.search(
    query="Acme Corp contract negotiation",
    max_results=20
)
print(f"Found {len(results)} relevant threads")

# Step 2: Ask for structured analysis
analysis = igpt.recall.ask(
    input="Summarize the current status of the Acme Corp contract negotiation. What are the open issues and who owns them?",
    output_format="json"
)
print(analysis)
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| input | string | Yes | The prompt or question to ask. |
| user | string | Yes (or set in constructor) | Unique user identifier scoping the query to their connected data. |
| stream | boolean | No (default: false) | If true, returns an SSE stream of response chunks. |
| quality | string | No | Context Engine quality tier: `"cef-1-normal"` or `"cef-1-high"`. |
| output_format | string or object | No | `"text"` (default), `"json"`, or `{ "schema": <JSON Schema> }` for validated structured output. |

## Error Handling

The SDK uses a no-throw pattern. Errors are returned as values, not exceptions:

```python
response = igpt.recall.ask(input="What happened in yesterday's board meeting?")

if isinstance(response, dict) and response.get("error"):
    error = response["error"]
    if error == "auth":
        print("Check your API key")
    elif error == "params":
        print("Check your request parameters")
    elif error == "network_error":
        print("Network issue, retry")
else:
    print(response)
```

## External Endpoints

This skill communicates exclusively with:

- `https://api.igpt.ai/v1/recall/ask` — the reasoning endpoint
- `https://api.igpt.ai/v1/connectors/authorize` — only during initial datasource connection setup

No other external endpoints are contacted. No data is sent to any third-party service. The `igptai` PyPI package source is available at https://github.com/igptai/igptai-python.

## Security & Privacy

- **API-key scoped**: All requests authenticate via `IGPT_API_KEY` sent as a Bearer token over HTTPS. No shell access, no filesystem access, no system commands.
- **Per-user isolation**: Every query is scoped to a specific `user` identifier. User A cannot access User B's email data. Isolation is enforced at the index and execution level, not as a filter layer.
- **OAuth read-only**: The email datasource connection uses OAuth with read-only scopes. The skill does not send, modify, or delete emails.
- **No data retention**: Prompts are discarded after execution. Memory is reconstructed on-demand, not stored.
- **Transport encryption**: All communication occurs over HTTPS. No plaintext endpoints.
- **No local persistence**: This skill does not write to disk, modify environment files, or create persistent configuration outside of the standard `IGPT_API_KEY` environment variable.

For the full security model, see https://docs.igpt.ai/docs/security/model.

## What This Skill Does NOT Do

- Does not send, modify, forward, or delete emails
- Does not access the filesystem or execute shell commands
- Does not install persistent services or scheduled tasks
- Does not contact endpoints other than `api.igpt.ai`
- Does not store API keys or OAuth tokens outside the environment variable

## Example Questions

These all work as natural language prompts:

- `"Summarize key risks from this week's email threads"` — cross-thread analysis
- `"What are the open action items from yesterday's board meeting?"` — task extraction
- `"What's the current status of the Acme deal?"` — deal intelligence
- `"Who owns the budget approval and when is it due?"` — ownership and deadline extraction
- `"Are there any threads where tone has shifted negatively in the last 7 days?"` — sentiment analysis
- `"Generate a briefing for my meeting with Sarah tomorrow"` — meeting prep

## Companion Skills

| Skill | What it does | When to use it |
|-------|-------------|----------------|
| **igpt-email-ask** (this skill) | Reasoning, summaries, structured extraction, sentiment | When you need answers and analysis |
| **[igpt-email-search](https://clawhub.ai/skills/igpt-email-search)** | Hybrid semantic + keyword retrieval | When you need to find and retrieve emails |

Both skills use the same `IGPT_API_KEY` and connected datasources. Install both for the full search → analyze workflow.

## Resources

- **Get API Key**: https://igpt.ai/hub/apikeys/
- **Documentation**: https://docs.igpt.ai
- **API Reference**: https://docs.igpt.ai/docs/api-reference/ask
- **Playground**: https://igpt.ai/hub/playground/
- **Python SDK**: https://pypi.org/project/igptai/
- **Node.js SDK**: https://www.npmjs.com/package/igptai
- **GitHub**: https://github.com/igptai/igptai-python
