---
name: ai-picture-book
description: Generate static or dynamic picture book videos using Baidu AI
metadata: { "openclaw": { "emoji": "📔", "requires": { "bins": ["python3"], "env":["BAIDU_API_KEY"]},"primaryEnv":"BAIDU_API_KEY" } }
---

# AI Picture Book

Generate picture book videos from stories or descriptions.

## Workflow

1. **Create Task**: Submit story + type → get task ID
2. **Poll Status**: Query every 5-10s until completion
3. **Get Results**: Retrieve video URLs when status = 2

## Book Types

| Type | Method | Description |
|------|--------|-------------|
| Static | 9 | Static picture book |
| Dynamic | 10 | Dynamic picture book |

**Required**: User must specify type (static/9 or dynamic/10). If not provided, ask them to choose.

## Status Codes

| Code | Status | Action |
|-------|---------|---------|
| 0, 1, 3 | In Progress | Continue polling |
| 2 | Completed | Return results |
| Other | Failed | Show error |

## APIs

### Create Task

**Endpoint**: `POST /v2/tools/ai_picture_book/task_create`

**Parameters**:
- `method` (required): `9` for static, `10` for dynamic
- `content` (required): Story or description

**Example**:
```bash
python3 scripts/ai_picture_book_task_create.py 9 "A brave cat explores the world."
```

**Response**:
```json
{ "task_id": "uuid-string" }
```

### Query Task

**Endpoint**: `GET /v2/tools/ai_picture_book/query`

**Parameters**:
- `task_id` (required): Task ID from create endpoint

**Example**:
```bash
python3 scripts/ai_picture_book_task_query.py "task-id-here"
```

**Response** (Completed):
```json
{
  "status": 2,
  "video_bos_url": "https://...",
}
```

## Polling Strategy

### Auto Polling (Recommended)
```bash
python3 scripts/ai_picture_book_poll.py <task_id> [max_attempts] [interval_seconds]
```

**Examples**:
```bash
# Default: 20 attempts, 5s intervals
python3 scripts/ai_picture_book_poll.py "task-id-here"

# Custom: 30 attempts, 10s intervals
python3 scripts/ai_picture_book_poll.py "task-id-here" 30 10
```

### Manual Polling
1. Create task → store `task_id`
2. Query every 5-10s until status = 2
3. Timeout after 2-3 minutes

## Error Handling

- Invalid content: "Content cannot be empty"
- Invalid type: "Invalid type. Use 9 (static) or 10 (dynamic)"
- Processing error: "Failed to generate picture book"
- Timeout: "Task timed out. Try again later"
