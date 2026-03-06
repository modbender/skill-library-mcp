# Claude Batch API Reference

Complete API documentation for the Message Batches API.

## Batch Request Structure

Each request in a batch follows this structure:

```json
{
  "custom_id": "unique-identifier-string",
  "params": {
    "model": "claude-opus-4-6",
    "max_tokens": 1024,
    "system": "You are...",
    "messages": [
      {"role": "user", "content": "..."}
    ]
  }
}
```

### Required Fields

- **custom_id** (string): Unique identifier for this request within the batch. Used to match results.
- **params** (object): Standard Messages API parameters
  - **model** (string): Model to use
  - **max_tokens** (integer): Max output tokens
  - **messages** (array): Message history

### Optional Fields in params

- **system** (string/array): System prompt(s)
- **temperature** (float): 0.0 to 1.0, defaults to 1.0
- **top_p** (float): 0.0 to 1.0
- **top_k** (integer): Top-k sampling
- **stop_sequences** (array): Stop generation at these sequences
- **tools** (array): Tool definitions for tool use
- **tool_choice** (object): Force tool use with {"type": "tool", "name": "..."}
- **betas** (array): Beta features

## API Endpoints

### Create Batch

**POST** `/messages/batches`

```bash
curl https://api.anthropic.com/v1/messages/batches \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{
    "requests": [...]
  }'
```

**Response:**

```json
{
  "id": "msgbatch_01HkcTjaV5uDC8jWR4ZsDV8d",
  "type": "message_batch",
  "processing_status": "in_progress",
  "request_counts": {
    "processing": 2,
    "succeeded": 0,
    "errored": 0,
    "canceled": 0,
    "expired": 0
  },
  "ended_at": null,
  "created_at": "2024-09-24T18:37:24.100435Z",
  "expires_at": "2024-09-25T18:37:24.100435Z",
  "cancel_initiated_at": null,
  "results_url": null
}
```

### Retrieve Batch Status

**GET** `/messages/batches/{batch_id}`

Returns current batch status and request counts. Use this to poll for completion.

```bash
curl https://api.anthropic.com/v1/messages/batches/msgbatch_01HkcTjaV5uDC8jWR4ZsDV8d \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01"
```

### List Batches

**GET** `/messages/batches?limit=20`

Lists all batches in the workspace with pagination support.

### Get Results

**GET** `/messages/batches/{batch_id}/results`

Returns JSONL stream of results. Each line is a result object.

```bash
curl https://api.anthropic.com/v1/messages/batches/msgbatch_01HkcTjaV5uDC8jWR4ZsDV8d/results \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01"
```

### Cancel Batch

**POST** `/messages/batches/{batch_id}/cancel`

Cancels a batch. Requests already processing may still complete.

## Result Types

Each result in the JSONL stream contains:

```json
{
  "custom_id": "task-1",
  "result": {
    "type": "succeeded|errored|expired|canceled",
    "message": {...},
    "error": {...}
  }
}
```

### Succeeded Result

```json
{
  "custom_id": "task-1",
  "result": {
    "type": "succeeded",
    "message": {
      "id": "msg_...",
      "type": "message",
      "role": "assistant",
      "model": "claude-opus-4-6",
      "content": [
        {"type": "text", "text": "..."}
      ],
      "stop_reason": "end_turn",
      "stop_sequence": null,
      "usage": {
        "input_tokens": 10,
        "output_tokens": 34
      }
    }
  }
}
```

### Errored Result

```json
{
  "custom_id": "task-2",
  "result": {
    "type": "errored",
    "error": {
      "type": "invalid_request_error",
      "message": "..."
    }
  }
}
```

**Error types:**
- `invalid_request_error` - Request format is invalid (fix before retry)
- `authentication_error` - API key issue (fix auth before retry)
- `rate_limit_error` - Rate limit exceeded (can retry later)
- `api_error` - Server error (safe to retry)

### Expired Result

Request didn't process within 24 hours. No charge for expired requests.

### Canceled Result

Request was canceled. No charge for canceled requests.

## Request Counts

The batch object includes `request_counts`:

```json
{
  "request_counts": {
    "processing": 50,
    "succeeded": 100,
    "errored": 5,
    "canceled": 0,
    "expired": 0
  }
}
```

These add up to total requests submitted.

## Batch Status Lifecycle

```
created → in_progress → canceling → ended
             ↓
          ended (when all requests complete)
```

## Prompt Caching in Batches

Add `cache_control` to system or message content:

```json
{
  "custom_id": "task-1",
  "params": {
    "model": "claude-opus-4-6",
    "max_tokens": 1024,
    "system": [
      {
        "type": "text",
        "text": "You are analyzing documents..."
      },
      {
        "type": "text",
        "text": "<entire document content here>",
        "cache_control": {"type": "ephemeral"}
      }
    ],
    "messages": [...]
  }
}
```

**Cache hit rates:** 30-98% typical (best-effort basis in batches)

## Rate Limits

The Batch API has separate rate limits from the Messages API:

- HTTP requests to batch endpoints: Standard account limits apply
- Requests within batches: Per-account processing queue limits
- Processing may slow based on demand and your volume

## Pricing

| Model | Batch Input | Batch Output |
|-------|------------|----------|
| Claude Opus 4.6 | $2.50 / MTok | $12.50 / MTok |
| Claude Sonnet 4.6 | $1.50 / MTok | $7.50 / MTok |
| Claude Haiku 4.5 | $0.50 / MTok | $2.50 / MTok |

**50% discount vs. standard prices**

Prompt caching discount stacks with batch discount:
- With 1-hour cache: Additional 25% off cached tokens

## Limits & Constraints

- **Max batch size:** 100,000 requests OR 256 MB
- **Processing time:** Typically < 1 hour, max 24 hours
- **Result availability:** 29 days after creation
- **Concurrent processing:** Requests may be processed in any order
- **Result order:** Not guaranteed to match input order

## Unique custom_id Requirement

Each request must have a unique `custom_id` within the batch. Duplicates will cause validation errors.

## Data Retention

- Batches isolated per workspace
- Results available for 29 days after creation
- Standard retention policy applies to data

## Special Considerations

### Vision Support

Include images in messages:

```json
{
  "role": "user",
  "content": [
    {"type": "text", "text": "Analyze this:"},
    {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": "..."}}
  ]
}
```

### Tool Use Support

Define tools in params:

```json
{
  "tools": [
    {
      "name": "calculator",
      "description": "...",
      "input_schema": {...}
    }
  ]
}
```

### Multi-turn Conversations

Include full message history:

```json
{
  "messages": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."},
    {"role": "user", "content": "..."}
  ]
}
```
