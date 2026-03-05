---
name: limitless_lifelogs
description: Search, summarize, and extract insights from your Limitless AI pendant life logs. Supports keyword and semantic search, date range queries, memory recall, and action item extraction for named agents.
user-invocable: true
metadata: {"openclaw":{"emoji":"🎙️","primaryEnv":"LIMITLESS_API_KEY","requires":{"bins":["curl","jq"],"env":["LIMITLESS_API_KEY"]}}}
---

# Limitless Life Logs Skill

You have access to the user's Limitless AI pendant recordings via the Limitless REST API.
Use the tools below to retrieve, search, and analyze life log transcriptions.

## Configuration

Read these values from the environment before any API call:

| Variable | Required | Description |
|---|---|---|
| `LIMITLESS_API_KEY` | Yes | API key from Limitless Developer settings |
| `LIMITLESS_TIMEZONE` | No | IANA timezone (e.g. `America/Los_Angeles`). Defaults to `UTC` |

If `LIMITLESS_API_KEY` is not set, stop and tell the user:
> "Please set your API key first: `export LIMITLESS_API_KEY=your_key_here`"

If `LIMITLESS_TIMEZONE` is not set, proceed with `UTC` and note it in your response.

---

## API Reference

Base URL: `https://api.limitless.ai`
Auth header: `X-API-Key: $LIMITLESS_API_KEY`
This skill is **READ-ONLY** — never call DELETE endpoints.

### List / Search Lifelogs

```bash
curl -s -H "X-API-Key: $LIMITLESS_API_KEY" \
  "https://api.limitless.ai/v1/lifelogs?timezone=$LIMITLESS_TIMEZONE&PARAMS"
```

Query parameters (append as `&key=value`):

| Param | Type | Description |
|---|---|---|
| `q` | string | Hybrid semantic + keyword search query |
| `date` | ISO-8601 date | Filter to a specific day (`YYYY-MM-DD`) |
| `start` | ISO-8601 datetime | Range start |
| `end` | ISO-8601 datetime | Range end |
| `limit` | integer | Results per page (default 10, max 50) |
| `cursor` | string | Pagination cursor from previous `nextCursor` |
| `direction` | `asc`\|`desc` | Sort order (default `desc`) |
| `includeMarkdown` | boolean | Include formatted markdown content |
| `includeHeadings` | boolean | Include section headings |

### Get a Specific Lifelog

```bash
curl -s -H "X-API-Key: $LIMITLESS_API_KEY" \
  "https://api.limitless.ai/v1/lifelogs/LOG_ID"
```

### Paginate

If the response includes `"nextCursor"` in the `meta` object, fetch the next page by
appending `&cursor=NEXT_CURSOR` to the same request. Continue until `nextCursor` is null
or you have enough data.

---

## Capabilities

### 1. Search by Topic or Keyword

Trigger phrases: "search my logs for...", "find mentions of...", "did anyone say..."

1. Extract the search term from the user's message.
2. Call the lifelogs endpoint with `q=<term>` and `limit=10`.
3. Present results as a numbered list: timestamp, a short excerpt, and the log ID.
4. Offer to fetch more pages or open a specific log.

### 2. Summarize Recent Activity

Trigger phrases: "what happened today", "summarize this week", "recap yesterday"

1. Determine the date or range from the user's intent.
   - "today" → `date=<today's date>`
   - "this week" → `start=<Monday>&end=<today>`
   - "yesterday" → `date=<yesterday>`
2. Fetch up to 50 logs for the range (paginate if needed).
3. Synthesize a structured summary:
   - **Key topics and conversations**
   - **Decisions made**
   - **People mentioned**
   - **Notable moments**

### 3. Memory Recall

Trigger phrases: "what did we decide about...", "who mentioned...", "remind me about..."

1. Identify the topic or entity from the user's question.
2. Search with `q=<topic>`, fetching enough results to answer.
3. Synthesize a direct answer citing the relevant log entries (include date and time).

### 4. Browse by Date / Time Range

Trigger phrases: "show me logs from...", "what was recorded on...", "logs between X and Y"

1. Parse the date or range from the user's message.
2. Fetch logs with `date=` or `start=`/`end=`.
3. Present a chronological list with titles, timestamps, and brief summaries.

### 5. Action Item Extraction

Trigger phrases: "extract tasks", "what did I ask [agent] to do", "find action items for...", or
automatically after fetching logs when the user asks for a recap.

**Agent Roster**

Load the configured agents from the roster file and extract the list of known agent names:

```bash
cat ~/.openclaw/workspace/skills/limitless/agents.json | jq '[.agents[].name]'
```

Use these names as the detection vocabulary. Never hardcode agent names in logic — always derive them from `agents.json` at runtime.

**Detection Rules**

Scan the lifelog transcription text for directives to any agent in the roster. An action item is present when:

- A known agent name (from the roster) appears as a direct address at the start of a phrase or sentence
  - Examples: `"<AgentName>, send..."`, `"Hey <AgentName> can you..."`, `"@<AgentName> please..."`, `"<AgentName> — I need you to..."`
- A task verb follows: send, schedule, remind, book, find, create, draft, write, check, follow up, research, compile, etc.
- The phrase contains a clear deliverable or target

**Extraction Format**

For each detected action item, output:

```
Agent:    <agent name>
Trigger:  "<exact quote from transcript>"
Task:     <one-sentence plain-English summary of what was asked>
From log: <log ID> — <timestamp>
```

**Dispatch Prompt**

After presenting each extracted action item, ask the user:
> "Should I dispatch this task to [Agent Name]?"

If the user says yes, read the agent's `dispatch` config from `agents.json` and use the
appropriate method:

- **webhook**: POST to `dispatch.url` with JSON body:
  ```json
  {
    "agent": "<name>",
    "task": "<task summary>",
    "source_quote": "<exact quote>",
    "log_id": "<log ID>",
    "timestamp": "<ISO timestamp>"
  }
  ```
  ```bash
  curl -s -X POST -H "Content-Type: application/json" \
    -d '{"agent":"NAME","task":"TASK","source_quote":"QUOTE","log_id":"ID","timestamp":"TS"}' \
    "DISPATCH_URL"
  ```

- **email**: Inform the user what the email should contain and ask them to send it, or
  use the system `mail` command if available:
  ```bash
  echo "Task for AGENT_NAME:\nTASK_SUMMARY\n\nSource: QUOTE\nLog: LOG_ID" | \
    mail -s "Task from Limitless" AGENT_EMAIL
  ```

If the agent name is not in the roster, flag it:
> "I found a task directed at '[Name]' but they're not in your agents.json roster. Add them
> to `~/.openclaw/workspace/skills/limitless/agents.json` to enable dispatch."

---

## Error Handling

| Situation | Response |
|---|---|
| `LIMITLESS_API_KEY` not set | Stop and prompt user to export it |
| HTTP 401 | "Your API key appears invalid. Check it in Limitless Developer settings." |
| HTTP 429 | "Rate limit hit (180 req/min). Wait 60 seconds and try again." |
| HTTP 404 | "That log ID wasn't found. It may have been deleted or the ID is incorrect." |
| Empty results | "No logs found matching that query. Try a broader search term or different date range." |
| `agents.json` missing | "agents.json not found. Create it at `~/.openclaw/workspace/skills/limitless/agents.json` using the template in the skill repo." |
