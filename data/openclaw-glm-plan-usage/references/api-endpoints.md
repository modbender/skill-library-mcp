# GLM Coding Plan API Endpoints Reference

This document provides detailed information about the GLM Coding Plan monitoring endpoints used by the glm-plan-usage skill.

## Base URL

```
https://open.bigmodel.cn/api/coding/paas/v4
```

**Important**: This skill only works with providers configured to use the GLM Coding Plan dedicated endpoint. The `baseUrl` in your OpenClaw configuration must contain `api/coding/paas/v4` or `open.bigmodel.cn`.

## Authentication

All endpoints require authentication using a direct API token (no "Bearer" prefix).

### Headers

```http
Authorization: {your-api-key}
Accept-Language: en-US,en;q=0.9
Content-Type: application/json
```

### Example using curl

```bash
curl -sS \
  -H "Authorization: your-api-key-here" \
  -H "Accept-Language: en-US,en" \
  -H "Content-Type: application/json" \
  "https://open.bigmodel.cn/api/coding/paas/v4/api/monitor/usage/quota/limit"
```

## Endpoints

### 1. Quota Limits

Get current quota usage percentages for token and MCP usage.

**Endpoint**: `GET /api/monitor/usage/quota/limit`

**Full URL**: `https://open.bigmodel.cn/api/coding/paas/v4/api/monitor/usage/quota/limit`

**Response**:
```json
{
  "success": true,
  "data": {
    "tokenUsage5Hour": 45.2,
    "mcpUsage1Month": 12.3
  }
}
```

**Fields**:
- `tokenUsage5Hour` (number): Token usage percentage over 5-hour window (0-100)
- `mcpUsage1Month` (number): MCP usage percentage over 1-month window (0-100)

### 2. Model Usage

Get 24-hour model usage statistics including total tokens and call counts.

**Endpoint**: `GET /api/monitor/usage/model-usage`

**Full URL**: `https://open.bigmodel.cn/api/coding/paas/v4/api/monitor/usage/model-usage`

**Response**:
```json
{
  "success": true,
  "data": {
    "totalTokens": 12500000,
    "totalCalls": 1234,
    "models": [
      {
        "modelName": "glm-4-flash",
        "tokens": 8000000,
        "calls": 800
      },
      {
        "modelName": "glm-4-plus",
        "tokens": 4500000,
        "calls": 434
      }
    ]
  }
}
```

**Fields**:
- `totalTokens` (number): Total tokens used in 24-hour period
- `totalCalls` (number): Total API calls in 24-hour period
- `models` (array): Breakdown by model (optional)
  - `modelName` (string): Model identifier
  - `tokens` (number): Tokens used by this model
  - `calls` (number): Calls made to this model

### 3. Tool Usage

Get 24-hour MCP (Model Context Protocol) tool usage statistics.

**Endpoint**: `GET /api/monitor/usage/tool-usage`

**Full URL**: `https://open.bigmodel.cn/api/coding/paas/v4/api/monitor/usage/tool-usage`

**Response**:
```json
{
  "success": true,
  "data": {
    "tools": [
      {
        "toolName": "bash",
        "usageCount": 156
      },
      {
        "toolName": "file-read",
        "usageCount": 89
      },
      {
        "toolName": "web-search",
        "usageCount": 34
      }
    ],
    "totalToolCalls": 279
  }
}
```

**Fields**:
- `tools` (array): MCP tool usage breakdown
  - `toolName` (string): Name of the MCP tool
  - `usageCount` (number): Number of times this tool was called
- `totalToolCalls` (number): Total tool calls in 24-hour period

## Error Responses

### 401 Unauthorized

Invalid or missing API key.

```json
{
  "code": 401,
  "message": "Unauthorized"
}
```

### 403 Forbidden

API key does not have access to GLM Coding Plan features.

```json
{
  "code": 403,
  "message": "Forbidden"
}
```

### Rate Limiting

Too many requests.

```json
{
  "code": 429,
  "message": "Too many requests"
}
```

## Request Examples

### Using bash and curl

```bash
#!/bin/bash

API_KEY="your-api-key-here"
API_BASE="https://open.bigmodel.cn/api/coding/paas/v4"

# Query quota limits
curl -sS \
  -H "Authorization: $API_KEY" \
  -H "Accept-Language: en-US,en" \
  -H "Content-Type: application/json" \
  "$API_BASE/api/monitor/usage/quota/limit" | jq '.'

# Query model usage
curl -sS \
  -H "Authorization: $API_KEY" \
  -H "Accept-Language: en-US,en" \
  -H "Content-Type: application/json" \
  "$API_BASE/api/monitor/usage/model-usage" | jq '.'

# Query tool usage
curl -sS \
  -H "Authorization: $API_KEY" \
  -H "Accept-Language: en-US,en" \
  -H "Content-Type: application/json" \
  "$API_BASE/api/monitor/usage/tool-usage" | jq '.'
```

### Using Python

```python
import requests

API_KEY = "your-api-key-here"
API_BASE = "https://open.bigmodel.cn/api/coding/paas/v4"

headers = {
    "Authorization": API_KEY,
    "Accept-Language": "en-US,en",
    "Content-Type": "application/json"
}

# Query quota limits
response = requests.get(
    f"{API_BASE}/api/monitor/usage/quota/limit",
    headers=headers
)
print(response.json())

# Query model usage
response = requests.get(
    f"{API_BASE}/api/monitor/usage/model-usage",
    headers=headers
)
print(response.json())

# Query tool usage
response = requests.get(
    f"{API_BASE}/api/monitor/usage/tool-usage",
    headers=headers
)
print(response.json())
```

### Using Node.js

```javascript
const API_KEY = 'your-api-key-here';
const API_BASE = 'https://open.bigmodel.cn/api/coding/paas/v4';

const headers = {
  'Authorization': API_KEY,
  'Accept-Language': 'en-US,en',
  'Content-Type': 'application/json'
};

async function queryUsage() {
  const response = await fetch(`${API_BASE}/api/monitor/usage/quota/limit`, {
    method: 'GET',
    headers
  });
  const data = await response.json();
  console.log(data);
}

queryUsage();
```

## Rate Limits

The monitoring endpoints have the following rate limits:

- **Quota Limits**: 60 requests per minute
- **Model Usage**: 60 requests per minute
- **Tool Usage**: 60 requests per minute

Exceeding rate limits will result in HTTP 429 responses.

## Data Retention

Usage data is retained for:

- **Token usage**: 5-hour rolling window
- **MCP usage**: 1-month rolling window
- **Model usage**: 24-hour rolling window
- **Tool usage**: 24-hour rolling window

## Platform Detection

The skill determines the output language based on the detected platform:

| Platform | baseUrl Pattern | Output Language |
|----------|-----------------|-----------------|
| ZAI | Contains `api.z.ai` | English |
| ZHIPU/GLM | Contains `open.bigmodel.cn` or `api/coding/paas/v4` | Chinese |

## Related Resources

- [OpenClaw Documentation](https://openclaw.dev)
- [GLM Coding Plan](https://open.bigmodel.cn)
- [zai-coding-plugins](https://github.com/zai-org/zai-coding-plugins)
- [opencode-glm-quota](https://github.com/guyinwonder168/opencode-glm-quota)
