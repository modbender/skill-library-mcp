# Composio - Tool Execution Platform for AI Agents

Composio connects your AI agent to 500+ apps — Gmail, Slack, GitHub, Notion, Google Workspace, Microsoft (Outlook, Teams), X/Twitter, Figma, Web Search, Browser automation, Meta apps, TikTok, and more — for seamless cross-app automation.

Use this guide to discover tools, manage connections, and execute actions across any supported app.

**API Base:** `https://backend.composio.dev/api/v3`
**Auth:** All requests require `x-api-key: YOUR_API_KEY`

---

## Setup (One-Time)

### 1. Get Your API Key

Go to [platform.composio.dev](https://platform.composio.dev) and sign in with Google or another account. Navigate to your project settings and copy your API key.

```bash
export COMPOSIO_API_KEY="your_api_key_here"
export COMPOSIO_BASE="https://backend.composio.dev/api/v3"
```

That's it. You can now call any Composio tool.

---

## Core Operations

Every tool is called through one endpoint — the tool slug goes in the URL:

```
POST /api/v3/tools/execute/{TOOL_SLUG}
```

```bash
curl -X POST "$COMPOSIO_BASE/tools/execute/TOOL_SLUG_HERE" \
  -H "x-api-key: $COMPOSIO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "arguments": { ... }
  }'
```

Optional fields on every request:

| Field | Description |
|-------|-------------|
| `arguments` | Tool-specific input parameters (see each tool below) |
| `user_id` | Your end-user's identifier (for multi-user connected accounts) |
| `connected_account_id` | Override which connected account to use |

---

### COMPOSIO_SEARCH_TOOLS — Discover Tools

**Always call this first.** Searches 500+ apps to find the right tools for your task. Returns tool schemas, execution plans, connection status, and pitfalls.

```bash
curl -X POST "$COMPOSIO_BASE/tools/execute/COMPOSIO_SEARCH_TOOLS" \
  -H "x-api-key: $COMPOSIO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "arguments": {
      "queries": [
        {
          "use_case": "send an email to someone",
          "known_fields": "recipient_name: John"
        },
        {
          "use_case": "create a meeting invite",
          "known_fields": "meeting_date: tomorrow"
        }
      ],
      "session": {
        "generate_id": true
      }
    }
  }'
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `queries` | Yes | Array of search queries (1-7 items) |
| `queries[].use_case` | Yes | Normalized English description of the task. Include app name if known. No personal identifiers here. |
| `queries[].known_fields` | No | Comma-separated key:value pairs of known inputs (e.g., `"channel_name: general, timezone: UTC"`) |
| `session.generate_id` | Yes (first call) | Set `true` for new workflows to get a session ID |
| `session.id` | Yes (subsequent) | Reuse the session ID returned from first call |
| `model` | No | Your LLM model name (e.g., `"claude-4.5-sonnet"`) for optimized planning |

**Response:**

```json
{
  "data": {
    "results": [
      {
        "index": 1,
        "use_case": "send an email to someone",
        "primary_tool_slugs": ["GMAIL_SEND_EMAIL"],
        "related_tool_slugs": ["GMAIL_CREATE_EMAIL_DRAFT"],
        "toolkits": ["gmail"],
        "recommended_plan_steps": ["Step 1: ...", "Step 2: ..."],
        "known_pitfalls": ["Always set user_id to 'me'"],
        "reference_workbench_snippets": [...]
      }
    ],
    "tool_schemas": {
      "GMAIL_SEND_EMAIL": {
        "toolkit": "gmail",
        "tool_slug": "GMAIL_SEND_EMAIL",
        "description": "Send an email",
        "input_schema": { ... }
      }
    },
    "toolkit_connection_statuses": [
      {
        "toolkit": "gmail",
        "has_active_connection": false,
        "status_message": "No active connection. Initiate via COMPOSIO_MANAGE_CONNECTIONS."
      }
    ],
    "time_info": {
      "current_time_utc": "2025-01-15T10:30:00Z",
      "current_time_utc_epoch_seconds": 1736935800
    },
    "session": {
      "id": "abcd",
      "instructions": "Pass this session ID in all subsequent calls"
    }
  },
  "successful": true
}
```

**Splitting guidelines:**
- 1 query = 1 tool action. Include hidden prerequisites (e.g., "get issue" before "update issue").
- Include app names in every sub-query if the user specified one.
- Translate non-English prompts to English while preserving identifiers.

**After searching:**
- Review the `recommended_plan_steps` and `known_pitfalls` before executing.
- If a tool has `schemaRef` instead of `input_schema`, call `COMPOSIO_GET_TOOL_SCHEMAS` first.
- If `has_active_connection` is `false` for a toolkit, call `COMPOSIO_MANAGE_CONNECTIONS` before executing its tools.

---

### COMPOSIO_MANAGE_CONNECTIONS — Connect to Apps

Creates or checks OAuth/API connections for toolkits. Returns auth links for user authentication.

```bash
curl -X POST "$COMPOSIO_BASE/tools/execute/COMPOSIO_MANAGE_CONNECTIONS" \
  -H "x-api-key: $COMPOSIO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "arguments": {
      "toolkits": ["gmail", "slack"],
      "session_id": "abcd"
    }
  }'
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `toolkits` | Yes | Toolkit names from SEARCH_TOOLS response (e.g., `["gmail", "github"]`). Never invent names. |
| `reinitiate_all` | No | Force reconnection even if already active (default: `false`) |
| `session_id` | No | Session ID from SEARCH_TOOLS |

**Response:**

```json
{
  "data": {
    "message": "1 active, 1 initiated",
    "results": {
      "gmail": {
        "toolkit": "gmail",
        "status": "initiated",
        "redirect_url": "https://accounts.google.com/o/oauth2/...",
        "instruction": "Click the link to authenticate"
      },
      "slack": {
        "toolkit": "slack",
        "status": "active",
        "has_active_connection": true,
        "connected_account_id": "ca_xxx",
        "current_user_info": { "email": "user@example.com" }
      }
    },
    "summary": {
      "total_toolkits": 2,
      "active_connections": 1,
      "initiated_connections": 1,
      "failed_connections": 0
    }
  },
  "successful": true
}
```

**Connection workflow:**
1. Call SEARCH_TOOLS — check `toolkit_connection_statuses`
2. If `has_active_connection` is false, call MANAGE_CONNECTIONS
3. If status is `"initiated"`, present the `redirect_url` to the user for authentication
4. Once the user completes auth, the connection becomes active
5. Only execute tools after the connection is confirmed active

---

### COMPOSIO_GET_TOOL_SCHEMAS — Get Full Input Schemas

Retrieves complete input schemas for tools. Call this when SEARCH_TOOLS returns `schemaRef` instead of a full `input_schema`.

```bash
curl -X POST "$COMPOSIO_BASE/tools/execute/COMPOSIO_GET_TOOL_SCHEMAS" \
  -H "x-api-key: $COMPOSIO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "arguments": {
      "tool_slugs": ["GMAIL_SEND_EMAIL", "SLACK_SEND_MESSAGE"],
      "session_id": "abcd"
    }
  }'
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `tool_slugs` | Yes | Array of tool slugs from SEARCH_TOOLS |
| `session_id` | No | Session ID |

**Response:**

```json
{
  "data": {
    "success": true,
    "tool_schemas": {
      "GMAIL_SEND_EMAIL": {
        "toolkit": "gmail",
        "tool_slug": "GMAIL_SEND_EMAIL",
        "description": "Send an email via Gmail",
        "input_schema": {
          "properties": {
            "to": { "type": "string", "description": "Recipient email" },
            "subject": { "type": "string" },
            "body": { "type": "string" }
          },
          "required": ["to", "subject", "body"]
        }
      }
    },
    "not_found": []
  },
  "successful": true
}
```

---

### COMPOSIO_MULTI_EXECUTE_TOOL — Execute Tools

Executes one or more tools in parallel. This is how you run the tools discovered through SEARCH_TOOLS.

```bash
curl -X POST "$COMPOSIO_BASE/tools/execute/COMPOSIO_MULTI_EXECUTE_TOOL" \
  -H "x-api-key: $COMPOSIO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "arguments": {
      "tools": [
        {
          "tool_slug": "GMAIL_SEND_EMAIL",
          "arguments": {
            "to": "john@example.com",
            "subject": "Hello",
            "body": "Welcome to the team!"
          }
        },
        {
          "tool_slug": "SLACK_SEND_MESSAGE",
          "arguments": {
            "channel": "#general",
            "text": "New member joined!"
          }
        }
      ],
      "sync_response_to_workbench": false,
      "session_id": "abcd"
    }
  }'
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `tools` | Yes | Array of tool executions (1-50 items) |
| `tools[].tool_slug` | Yes | Valid slug from SEARCH_TOOLS |
| `tools[].arguments` | Yes | Arguments matching the tool's input schema exactly |
| `sync_response_to_workbench` | Yes | Set `true` if response may be large or needed for later scripting |
| `session_id` | No | Session ID |

**Response:**

```json
{
  "data": {
    "results": [
      {
        "tool_slug": "GMAIL_SEND_EMAIL",
        "index": 0,
        "response": {
          "data": { "id": "msg_123", "threadId": "thread_456" },
          "successful": true
        },
        "error": null
      },
      {
        "tool_slug": "SLACK_SEND_MESSAGE",
        "index": 1,
        "response": {
          "data": { "ok": true, "ts": "1234567890.123456" },
          "successful": true
        },
        "error": null
      }
    ],
    "total_count": 2,
    "success_count": 2,
    "error_count": 0,
    "remote_file_info": null
  },
  "successful": true
}
```

**Rules:**
- Only batch tools that are logically independent (no ordering dependencies).
- Never invent tool slugs or argument fields — always use what SEARCH_TOOLS returned.
- Ensure active connections exist before executing.
- If response is large, it may be saved to a remote file — use `remote_file_info.file_path` with the Remote Workbench or Bash tools to process it.

---

### COMPOSIO_REMOTE_WORKBENCH — Run Python Code

Executes Python code in a persistent remote Jupyter sandbox. Use for processing large tool outputs, bulk operations, and scripting multi-tool chains.

```bash
curl -X POST "$COMPOSIO_BASE/tools/execute/COMPOSIO_REMOTE_WORKBENCH" \
  -H "x-api-key: $COMPOSIO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "arguments": {
      "code_to_execute": "result, error = run_composio_tool(\"GMAIL_FETCH_EMAILS\", {\"max_results\": 5, \"user_id\": \"me\"})\nif error:\n    print(\"Error:\", error)\nelse:\n    emails = result.get(\"data\", {})\n    print(\"Fetched:\", len(emails.get(\"messages\", [])))",
      "thought": "Fetching recent emails for bulk processing",
      "session_id": "abcd"
    }
  }'
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `code_to_execute` | Yes | Python code to run in the sandbox |
| `thought` | No | One-sentence objective description |
| `timeout` | No | Execution timeout in seconds (1-780, default: 600) |
| `session_id` | No | Session ID |

**Response:**

```json
{
  "data": {
    "results": "Fetched: 5",
    "stdout": "Fetched: 5\n",
    "stderr": "",
    "error": "",
    "sandbox_id_suffix": "a1b2"
  },
  "successful": true
}
```

If output exceeds 40,000 characters, it is saved to a file and `results_file_path` / `stdout_file_path` is returned instead.

**Pre-loaded helper functions** (do NOT import or redeclare these):

| Function | Signature | Description |
|----------|-----------|-------------|
| `run_composio_tool` | `(tool_slug: str, arguments: dict) -> tuple[dict, str]` | Execute a Composio app tool. Returns `(response, error)`. |
| `invoke_llm` | `(query: str) -> tuple[str, str]` | Call an LLM for analysis, summarization, extraction. Max 200k chars input. Returns `(response, error)`. |
| `proxy_execute` | `(method, endpoint, toolkit, query_params?, body?, headers?) -> tuple[any, str]` | Direct API call to a connected toolkit when no Composio tool exists. Returns `(response, error)`. |
| `web_search` | `(query: str) -> tuple[str, str]` | Search the web via Exa AI. Returns `(results, error)`. |
| `upload_local_file` | `(*file_paths) -> tuple[dict, str]` | Upload sandbox files to cloud storage. Returns `({"s3_url": ...}, error)`. |
| `smart_file_extract` | `(sandbox_file_path: str) -> tuple[str, str]` | Extract text from PDF, images, etc. Returns `(text, error)`. |

**All helpers return `(result, error)` — always check error before using result.**

**Coding rules:**
1. Split work into small steps; save intermediate results to `/tmp/` files.
2. State persists across executions (variables, imports, files).
3. Hard timeout of 4 minutes — use `ThreadPoolExecutor` for bulk operations.
4. Always check error from helper functions before using results.
5. Use `invoke_llm` for summarization and analysis — it gives better results than ad-hoc filtering.
6. Do NOT call `COMPOSIO_*` meta tools via `run_composio_tool` — only use it for app tools (e.g., `GMAIL_SEND_EMAIL`).

**Example — bulk email processing:**

```python
import concurrent.futures

def process_email(email_id):
    result, error = run_composio_tool("GMAIL_GET_EMAIL", {
        "message_id": email_id, "user_id": "me"
    })
    if error:
        return {"id": email_id, "error": error}
    subject = result.get("data", {}).get("subject", "")
    return {"id": email_id, "subject": subject}

# Fetch email list
emails, err = run_composio_tool("GMAIL_FETCH_EMAILS", {
    "max_results": 50, "user_id": "me"
})
if not err:
    ids = [m["id"] for m in emails.get("data", {}).get("messages", [])]
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
        results = list(ex.map(process_email, ids))
    print(f"Processed {len(results)} emails")
```

---

### COMPOSIO_REMOTE_BASH_TOOL — Run Bash Commands

Executes bash commands in the same persistent sandbox as the workbench.

```bash
curl -X POST "$COMPOSIO_BASE/tools/execute/COMPOSIO_REMOTE_BASH_TOOL" \
  -H "x-api-key: $COMPOSIO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "arguments": {
      "command": "cat /home/user/.code_out/response.json | jq \".results[] | .tool_slug\"",
      "session_id": "abcd"
    }
  }'
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `command` | Yes | Bash command to execute |
| `session_id` | No | Session ID |

**Response:**

```json
{
  "data": {
    "stdout": "\"GMAIL_SEND_EMAIL\"\n\"SLACK_SEND_MESSAGE\"\n",
    "stdoutLines": 2,
    "stderr": "",
    "stderrLines": 0,
    "sandbox_id_suffix": "a1b2"
  },
  "successful": true
}
```

**Use cases:**
- Process large tool responses saved to remote files (via `jq`, `awk`, `sed`, `grep`)
- File system operations in the sandbox
- Commands run from `/home/user` by default
- 5-minute timeout, max 40,000 chars output per stream

---

## Typical Workflow

```
1. COMPOSIO_SEARCH_TOOLS
   | Find tools for your task
   | Check connection statuses
   | Review execution plan and pitfalls

2. COMPOSIO_GET_TOOL_SCHEMAS (if needed)
   | Get full input schemas for tools with schemaRef

3. COMPOSIO_MANAGE_CONNECTIONS (if needed)
   | Initiate connections for toolkits without active connections
   | Present auth URL to user -> user completes OAuth

4. COMPOSIO_MULTI_EXECUTE_TOOL
   | Execute tools with schema-compliant arguments
   | Process inline results or note remote file paths

5. COMPOSIO_REMOTE_WORKBENCH / COMPOSIO_REMOTE_BASH_TOOL (if needed)
   | Process large outputs saved to remote files
   | Run bulk operations or multi-tool scripts
   | Upload artifacts via upload_local_file
```

**Example — complete "send email" workflow:**

```bash
# Step 1: Search for email tools
curl -X POST "$COMPOSIO_BASE/tools/execute/COMPOSIO_SEARCH_TOOLS" \
  -H "x-api-key: $COMPOSIO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "arguments": {
      "queries": [{"use_case": "send an email via gmail", "known_fields": "recipient: john@example.com"}],
      "session": {"generate_id": true}
    }
  }'
# -> Returns GMAIL_SEND_EMAIL tool with schema
# -> Check toolkit_connection_statuses for gmail
# -> Save session.id from response (e.g., "abcd")

# Step 2: Connect gmail (if not active)
curl -X POST "$COMPOSIO_BASE/tools/execute/COMPOSIO_MANAGE_CONNECTIONS" \
  -H "x-api-key: $COMPOSIO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "arguments": {
      "toolkits": ["gmail"],
      "session_id": "abcd"
    }
  }'
# -> If status is "initiated", present redirect_url to user for OAuth

# Step 3: Execute the tool
curl -X POST "$COMPOSIO_BASE/tools/execute/COMPOSIO_MULTI_EXECUTE_TOOL" \
  -H "x-api-key: $COMPOSIO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "arguments": {
      "tools": [{
        "tool_slug": "GMAIL_SEND_EMAIL",
        "arguments": {
          "to": "john@example.com",
          "subject": "Welcome!",
          "body": "Welcome to the team, John!",
          "user_id": "me"
        }
      }],
      "sync_response_to_workbench": false,
      "session_id": "abcd"
    }
  }'
```

---

## Best Practices

### Session Management
- Pass `session: {generate_id: true}` on your first SEARCH_TOOLS call to get a session ID.
- Pass that `session_id` into all subsequent tool calls within the same workflow.
- Generate a new session when the user pivots to a different task.

### Tool Discovery
- Always call SEARCH_TOOLS first — never guess tool slugs or argument fields.
- Re-run SEARCH_TOOLS when you need additional tools due to errors or changed requirements.
- Review `recommended_plan_steps` and `known_pitfalls` before executing.

### Connections
- Never execute a toolkit tool without an active connection.
- Use exact toolkit names from SEARCH_TOOLS — never invent names.
- If a connection fails, present the auth URL to the user.

### Execution
- Use schema-compliant arguments only — check input_schema before every call.
- Batch independent tools into a single MULTI_EXECUTE call.
- For large responses, set `sync_response_to_workbench: true` and process in the workbench.

### Workbench
- Only use the workbench for remote file processing or bulk scripting — not for data already visible inline.
- Keep code concise; split long operations into multiple workbench calls.
- Use `ThreadPoolExecutor` for parallelism within the 4-minute timeout.

---

## Quick Reference

| Action | Tool Slug | Key Arguments |
|--------|-----------|---------------|
| Discover tools | `COMPOSIO_SEARCH_TOOLS` | `queries`, `session` |
| Get input schemas | `COMPOSIO_GET_TOOL_SCHEMAS` | `tool_slugs` |
| Connect to apps | `COMPOSIO_MANAGE_CONNECTIONS` | `toolkits`, `reinitiate_all` |
| Execute tools | `COMPOSIO_MULTI_EXECUTE_TOOL` | `tools`, `sync_response_to_workbench` |
| Run Python code | `COMPOSIO_REMOTE_WORKBENCH` | `code_to_execute`, `thought` |
| Run bash commands | `COMPOSIO_REMOTE_BASH_TOOL` | `command` |

**Endpoint for all tools:**

```
POST /api/v3/tools/execute/{TOOL_SLUG}
```

**Common errors:**

| Error | Meaning |
|-------|---------|
| 401 | Invalid or missing API key |
| 403 | Forbidden — insufficient permissions |
| 404 | Tool or resource not found |
| 422 | Invalid arguments (check input schema) |
| 429 | Rate limited — back off and retry |
| 500 | Internal server error |

**Rate limits:** Respect 429 responses with exponential backoff.

---

## Agent Notes

_Gotchas and non-obvious behavior discovered during testing._

- **Some tools return `schemaRef` instead of `input_schema`**. When you see `"hasFullSchema": false`, you MUST call `COMPOSIO_GET_TOOL_SCHEMAS` before executing that tool.
- **Response nesting**: Tool execution results live at `response.data.results[].response.data` — two levels of `data`. Parse carefully.
- **Workbench state persists** across calls. Variables, imports, and files in `/tmp/` survive between executions within the same sandbox session.
- **String formatting in workbench code**: Avoid f-strings with nested quotes when sending code via JSON. Use string concatenation instead to prevent quoting issues.
- **`invoke_llm`** works well for classification and analysis of tool output. Request explicit JSON format for structured results.
