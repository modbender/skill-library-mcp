# 小雨 Bot 状态监测 API 规范

## GET /api/status

### 响应格式
```json
{
  "recent_work": [
    {
      "id": "string",
      "title": "string",
      "description": "string", 
      "timestamp": "ISO-8601 timestamp",
      "status": "completed|in_progress|failed",
      "type": "string",
      "completion": "number (0-100)"
    }
  ],
  "scheduled_tasks": [
    {
      "id": "string",
      "name": "string",
      "schedule": "cron expression",
      "next_run": "ISO-8601 timestamp", 
      "status": "active|disabled"
    }
  ],
  "health_status": {
    "status": "healthy|warning|error",
    "uptime": "string (e.g. '12 天 1 小时 23 分钟')",
    "cpu_load": "string (e.g. '33.5%')",
    "memory_available": "string (e.g. '1.77 GB')",
    "openclaw_connected": "boolean",
    "model_status": "string",
    "last_check": "ISO-8601 timestamp"
  },
  "last_updated": "ISO-8601 timestamp"
}
```

## POST /api/chat

### 请求格式
```json
{
  "message": "string",
  "sessionId": "string",
  "unlocked": "boolean (optional)"
}
```

### 响应格式
```json
{
  "sessionId": "string",
  "activated": "boolean",
  "response": "string"
}
```