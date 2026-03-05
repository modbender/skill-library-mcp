---
name: flowise
description: Interact with Flowise AI workflows via REST API. Use when user mentions Flowise, chatflows, or wants to send messages to Flowise bots/agents. Supports listing flows, sending predictions, and managing conversations.
---

# Flowise Skill

Interact with Flowise AI platform via REST API.

## Configuration

Store Flowise settings in `TOOLS.md`:

```markdown
### Flowise
- Server: http://localhost:3000
- API Key: your-api-key-here
- Default Flow ID: your-default-flow-id (optional)
- Default Timeout: 300

#### Flows
| Flow ID | 名称 | 用途 | 参数 |
|---------|------|------|------|
| abc123 | 客服助手 | 处理客户咨询、售后问题 | - |
| def456 | 代码助手 | 代码生成、调试、技术问答 |  form格式: `script`=要执行的脚本, `device`=设备(可选) |
| ghi789 | 文档助手 | 文档总结、RAG知识库查询 | - |
```

## Flow Selection

When calling Flowise, match the user's request to the appropriate flow:
1. Check `TOOLS.md` for the Flows table
2. Select the flow whose "用途" best matches the task
3. If no specific match, use the Default Flow ID
4. If user explicitly names a flow, use that one

## Quick Reference

### Send a message (Prediction)

```bash
curl -X POST "${FLOWISE_URL}/api/v1/prediction/${FLOW_ID}" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello, how are you?"}'
```

### Send with streaming

```bash
curl -X POST "${FLOWISE_URL}/api/v1/prediction/${FLOW_ID}" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"question": "Tell me a story", "streaming": true}'
```

### Send with session/conversation memory

```bash
curl -X POST "${FLOWISE_URL}/api/v1/prediction/${FLOW_ID}" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"question": "What did I ask before?", "sessionId": "user-123"}'
```

### List all chatflows

```bash
curl -X GET "${FLOWISE_URL}/api/v1/chatflows" \
  -H "Authorization: Bearer ${API_KEY}"
```

### Get chatflow details

```bash
curl -X GET "${FLOWISE_URL}/api/v1/chatflows/${FLOW_ID}" \
  -H "Authorization: Bearer ${API_KEY}"
```

## Common Parameters for Prediction

| Parameter | Type | Description |
|-----------|------|-------------|
| `question` | string | The message to send |
| `streaming` | boolean | Enable streaming response (default: false) |
| `sessionId` | string | Session ID for conversation memory |
| `overrideConfig` | object | Override flow configuration (temperature, maxTokens, etc.) |
| `history` | array | Provide conversation history manually |
| `uploads` | array | File uploads (images, documents) |

### Flow-specific Variables

Some flows accept custom variables. Pass them in the request:

```json
{
  "question": "查询订单状态",
  "overrideConfig": {
    "vars": {
      "orderId": "12345",
      "userId": "user-abc"
    }
  }
}
```

### Using Parameters from TOOLS.md

Check `TOOLS.md` for flow-specific parameters. The "参数" column indicates:
- Required parameters (必填)
- Default values to use
- Custom variables needed for that flow

Example entry:
```
| abc123 | RAG知识库 | 文档查询 | sessionId=必填, variables={"namespace": "docs"} |
```

When calling this flow, include the specified parameters.

## Override Config Example

Override model settings or other flow parameters:

```json
{
  "question": "Explain quantum computing",
  "overrideConfig": {
    "temperature": 0.7,
    "maxTokens": 500
  }
}
```

## With File Upload

```bash
curl -X POST "${FLOWISE_URL}/api/v1/prediction/${FLOW_ID}" \
  -H "Authorization: Bearer ${API_KEY}" \
  -F "question=Analyze this document" \
  -F "files=@/path/to/document.pdf"
```

## Form Object Request

Some flows use a `form` object for structured input parameters:

```bash
curl -X POST "${FLOWISE_URL}/api/v1/prediction/${FLOW_ID}" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "form": {
      "script": "d.send_keys(\"小红书\")",
      "device": "192.168.1.100:5555"
    }
  }'
```

Check `TOOLS.md` "参数" column for `form格式` to identify these flows. Pass parameters inside the `form` object.

## Error Handling

| Status | Meaning |
|--------|---------|
| 200 | Success |
| 400 | Bad request - check input format |
| 401 | Unauthorized - check API key |
| 404 | Flow not found - verify flow ID |
| 500 | Server error - check Flowise logs |

## Workflow

1. Check `TOOLS.md` for Flowise server URL and API key
2. If not configured, ask user for:
   - Flowise server URL (e.g., `http://localhost:3000`)
   - API key (if authentication is enabled)
   - Flow ID to use
3. Use `exec` with `curl` to call the API
4. Parse JSON response and present results

## Tips

- Use `sessionId` consistently to maintain conversation context
- For long responses, enable `streaming: true`
- Test connectivity with `/api/v1/ping` endpoint first
- List available flows if user doesn't specify a flow ID
