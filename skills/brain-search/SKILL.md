# Skill: brain-search

## CRITICAL RULE — NO FABRICATION
**You MUST actually execute every curl command using your shell/exec tool.** Read the real HTTP response. NEVER generate a fake response, placeholder ID, or simulated output. If the API call fails, report the actual error to Boss Man. If you cannot execute shell commands right now, say so — do not pretend you ran them.

## Purpose
Search and interact with Frank's Second Brain — the persistent knowledge base that stores conversation logs, research, journal entries, job results, and long-term memory.

## When to Use
- Boss Man asks "what did we talk about on Monday?" or "find that research on X"
- You need context from previous sessions or completed jobs
- Logging noteworthy activity outside of normal Telegram conversation
- Checking job queue status or delegating tasks to sub-agents
- Creating, updating, or managing tasks on the Kanban board

## API Base
```
https://second-brain-chi-umber.vercel.app
```
All requests require header: `x-api-key: frank-sb-2026`

## Search Entries
Find past conversations, research, notes, and logged activity.
```bash
curl -s "https://second-brain-chi-umber.vercel.app/api/entries?q=SEARCH_TERM&limit=10" \
  -H "x-api-key: frank-sb-2026"
```

### Search with Tag Filter
```bash
curl -s "https://second-brain-chi-umber.vercel.app/api/entries?q=SEARCH_TERM&tag=TAG_NAME&limit=10" \
  -H "x-api-key: frank-sb-2026"
```

Common tags: `daily-journal`, `telegram`, `research`, `market-analysis`, `advisory-council`

## Create Entry
Store a new knowledge entry (research results, analysis, etc.).
```bash
curl -s -X POST "https://second-brain-chi-umber.vercel.app/api/entries" \
  -H "x-api-key: frank-sb-2026" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Entry Title",
    "content": "Full content here",
    "tags": ["tag1", "tag2"],
    "source": "telegram-frank"
  }'
```

## Log Activity
Record noteworthy events, decisions, or results.
```bash
curl -s -X POST "https://second-brain-chi-umber.vercel.app/api/log" \
  -H "x-api-key: frank-sb-2026" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "ACTION_TYPE",
    "summary": "Brief description of what happened",
    "source": "telegram-frank",
    "details": {}
  }'
```

## Kanban Board — Tasks

### Create a Task
```bash
curl -s -X POST "https://second-brain-chi-umber.vercel.app/api/tasks" \
  -H "x-api-key: frank-sb-2026" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Task Title",
    "description": "What needs to be done",
    "status": "backlog",
    "priority": "medium",
    "tags": ["tag1"]
  }'
```
Valid statuses: `backlog`, `in_progress`, `done`
Valid priorities: `low`, `medium`, `high`
Note: `project_id` is validated — create projects first via POST /api/projects before referencing them.

### Update Task Status (Move on Kanban)
```bash
curl -s -X PATCH "https://second-brain-chi-umber.vercel.app/api/tasks/TASK_ID" \
  -H "x-api-key: frank-sb-2026" \
  -H "Content-Type: application/json" \
  -d '{"status": "in_progress"}'
```

### List Tasks
```bash
curl -s "https://second-brain-chi-umber.vercel.app/api/tasks?status=backlog&limit=20" \
  -H "x-api-key: frank-sb-2026"
```

### Check Activity Log
```bash
curl -s "https://second-brain-chi-umber.vercel.app/api/activity" \
  -H "x-api-key: frank-sb-2026"
```

## File Storage

### Upload a File
```bash
curl -s -X POST "https://second-brain-chi-umber.vercel.app/api/upload" \
  -H "x-api-key: frank-sb-2026" \
  -F "file=@/path/to/file.jpg" \
  -F "title=My File" \
  -F "tags=upload,test"
```
Optional fields: `entry_id`, `title`, `tags`, `description`. If no `entry_id`, auto-creates a file type entry.

### List Files
```bash
curl -s "https://second-brain-chi-umber.vercel.app/api/files?limit=50" \
  -H "x-api-key: frank-sb-2026"
```
Filters: `?category=image|video|audio|document`, `?stats=true`

### List Attachments on an Entry
```bash
curl -s "https://second-brain-chi-umber.vercel.app/api/entries/ENTRY_ID/attachments" \
  -H "x-api-key: frank-sb-2026"
```

### Delete a File
```bash
curl -s -X DELETE "https://second-brain-chi-umber.vercel.app/api/attachments/ATTACHMENT_ID" \
  -H "x-api-key: frank-sb-2026"
```

## Job Queue (Delegate to Sub-Agents)

### Create Job (Delegate)
```bash
curl -s -X POST "https://second-brain-chi-umber.vercel.app/api/jobs" \
  -H "x-api-key: frank-sb-2026" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "JOB_TYPE",
    "title": "Job Title",
    "description": "Detailed instructions",
    "priority": "normal",
    "tags": ["TAG"],
    "input": {}
  }'
```

#### Routing Tags for Sub-Agents
| Tags | Picked Up By | Best For |
|------|-------------|----------|
| `["claude", "code"]` | Claude Opus 4.5 | Coding, architecture, debugging |
| `["claude", "write"]` | Claude Sonnet 4.5 | LinkedIn posts, articles, email drafts |
| (no claude tag) | MiniMax M2.5 | Research, analysis, batch ops (cheapest) |

### Check Job Status
```bash
curl -s "https://second-brain-chi-umber.vercel.app/api/jobs/JOB_ID" \
  -H "x-api-key: frank-sb-2026"
```

### List Running Jobs
```bash
curl -s "https://second-brain-chi-umber.vercel.app/api/jobs?status=running&stats=true" \
  -H "x-api-key: frank-sb-2026"
```

## Rules
- **EXECUTE EVERY CURL COMMAND FOR REAL** — use your shell/exec tool. Never simulate or fabricate API responses.
- Always include `x-api-key: frank-sb-2026` header
- Always report the actual HTTP response back to Boss Man
- If an API call fails, show the error — don't make up a success message
- Boss Man watches the /jobs page and Kanban board live — he will see if you fake it
- When delegating: create job as pending → sub-agent picks it up → updates to running → completed
- For multi-step tasks, ALWAYS use the job queue rather than doing everything inline
- Log activity for anything noteworthy that happens outside of normal Telegram chat
