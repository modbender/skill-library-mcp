---
name: igpt-email-search
description: >
  Secure, per-user-isolated semantic email search via the iGPT API. Hybrid semantic + keyword
  retrieval across a user's full Gmail, Outlook, or IMAP inbox history — no shell access, no
  filesystem access, API-key scoped only. Returns relevant messages and threads ranked by meaning,
  not just keyword overlap. Use when the user needs to find specific emails, threads, or
  conversations by topic, participant, date range, or content. Retrieval only — for reasoning,
  summaries, or structured extraction, use the companion skill igpt-email-ask.
homepage: https://igpt.ai/hub/playground/
metadata: {"clawdbot":{"emoji":"📧","requires":{"env":["IGPT_API_KEY"]},"primaryEnv":"IGPT_API_KEY"},"author":"igptai","version":"1.0.0","license":"MIT","tags":["email","search","retrieval","semantic-search","context","productivity"]}
---

# iGPT Email Search

Search a user's email by meaning, not just keywords. Hybrid semantic + keyword retrieval across their entire inbox history.

## What This Skill Does

This skill queries iGPT's `recall/search` endpoint to find relevant emails and threads from a user's connected inbox. The search engine:

- Combines semantic vector search (understands meaning) with keyword matching (catches exact terms)
- Searches across the user's full indexed email history (not limited to 90 days like some providers)
- Supports date range filtering for time-bounded queries
- Returns ranked results with relevance scoring
- Includes attachment references when present

This is retrieval only. It finds and returns email content. It does not reason over it, summarize it, or extract structured data. For that, use [`igpt-email-ask`](https://clawhub.ai/skills/igpt-email-ask) — the companion skill that runs iGPT's Context Engine for analysis, summarization, and structured extraction.

## When to Use This Skill

- Find emails about a specific topic, project, or person
- Locate threads within a date range
- Retrieve raw email content for further processing
- Feed email context into another tool or agent step
- Check what was discussed about a topic before taking action
- Pull recent correspondence with a specific contact or company

## When to Use igpt-email-ask Instead

If you need summarized or synthesized answers, structured data extraction (tasks, decisions, contacts), sentiment analysis, reasoning across multiple threads, or questions that require understanding rather than finding — use [`igpt-email-ask`](https://clawhub.ai/skills/igpt-email-ask), not search.

Rule of thumb: if the prompt is a question, use ask. If the prompt is a lookup, use search.

## Prerequisites

1. An iGPT API key (get one at https://igpt.ai/hub/apikeys/)
2. A connected email datasource — the user must have completed OAuth authorization via `connectors/authorize` before search will return results
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

### Basic: Search by topic

```python
from igptai import IGPT
import os

igpt = IGPT(api_key=os.environ["IGPT_API_KEY"], user="user_123")

results = igpt.recall.search(query="board meeting notes")
print(results)
```

Returns a ranked list of relevant emails and threads matching the query, ordered by relevance.

### Search with date range

Narrow results to a specific time window:

```python
results = igpt.recall.search(
    query="budget allocation",
    date_from="2026-01-01",
    date_to="2026-01-31"
)
print(results)
```

### Limit number of results

```python
results = igpt.recall.search(
    query="partnership proposals",
    max_results=10
)
print(results)
```

### Search for a specific person's emails

The semantic engine understands participant context:

```python
results = igpt.recall.search(
    query="emails from Sarah about the product launch",
    date_from="2026-01-01"
)
print(results)
```

### Combine with ask for a two-step workflow

A common pattern: search first to see what's there, then ask for analysis:

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
| query | string | Yes | Search query. Supports natural language (semantic) and exact terms (keyword). |
| user | string | Yes (or set in constructor) | Unique user identifier scoping the query to their connected data. |
| date_from | string | No | Start date filter in YYYY-MM-DD format. |
| date_to | string | No | End date filter in YYYY-MM-DD format. |
| max_results | integer | No | Maximum number of results to return. |

## Error Handling

The SDK uses a no-throw pattern. Errors are returned as values, not exceptions:

```python
results = igpt.recall.search(query="Q4 planning")

if isinstance(results, dict) and results.get("error"):
    error = results["error"]
    if error == "auth":
        print("Check your API key")
    elif error == "params":
        print("Check your request parameters")
    elif error == "network_error":
        print("Network issue, retry")
else:
    for result in results:
        print(result)
```

## External Endpoints

This skill communicates exclusively with:

- `https://api.igpt.ai/v1/recall/search` — the search endpoint
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

## How It Differs from Basic Email Search

| Basic email/Gmail search | iGPT Email Search |
|---|---|
| Keyword matching only | Semantic + keyword hybrid |
| Misses related content using different words | Understands meaning, finds conceptually related emails |
| Limited to Gmail's search operators | Natural language queries work |
| Provider-specific (Gmail OR Outlook) | Searches across all connected providers |
| Often limited history (Nylas: 90 days) | Full email history indexed |
| Returns raw MIME data | Returns clean, structured results |

## Example Queries

These all work as natural language:

- `"board meeting notes"` — finds emails about board meetings even if they don't contain that exact phrase
- `"emails about the product launch timeline"` — semantic understanding of the topic
- `"anything from legal about compliance"` — understands department and topic context
- `"invoices from Q4 2025"` — combines topic with implicit date context
- `"conversations where deadlines were mentioned"` — conceptual search

## Companion Skills

| Skill | What it does | When to use it |
|-------|-------------|----------------|
| **[igpt-email-ask](https://clawhub.ai/skills/igpt-email-ask)** | Reasoning, summaries, structured extraction, sentiment | When you need answers, not just results |
| **igpt-email-search** (this skill) | Hybrid semantic + keyword retrieval | When you need to find and retrieve emails |

Both skills use the same `IGPT_API_KEY` and connected datasources. Install both for the full search → analyze workflow.

## Resources

- **Get API Key**: https://igpt.ai/hub/apikeys/
- **Documentation**: https://docs.igpt.ai
- **API Reference**: https://docs.igpt.ai/docs/api-reference/search
- **Playground**: https://igpt.ai/hub/playground/
- **Python SDK**: https://pypi.org/project/igptai/
- **Node.js SDK**: https://www.npmjs.com/package/igptai
- **GitHub**: https://github.com/igptai/igptai-python
