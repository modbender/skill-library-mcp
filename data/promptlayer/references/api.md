# PromptLayer API Reference

Base URL: `https://api.promptlayer.com`
Auth: `X-API-KEY: <PROMPTLAYER_API_KEY>` header on all requests

## Path Prefixes

PromptLayer uses three API path groups:
- `/prompt-templates` — template registry (list, get)
- `/rest/` — tracking, logging, publishing
- `/api/public/v2/` — datasets, evaluations

## Prompt Templates

### List Templates
`GET /prompt-templates`
Query params: `page`, `per_page`, `name` (partial match), `label`, `status` (active|deleted|all)

### Get Template
`POST /prompt-templates/{identifier}`
Identifier is prompt name (URL-encoded) or prompt ID.
```json
{"label": "prod", "version": 3, "provider": "openai", "input_variables": {"key": "val"}}
```
All body fields optional. Returns `prompt_name`, `version`, `prompt_template`, `metadata`, `llm_kwargs`.

### Publish Template
`POST /rest/prompt-templates`
```json
{"prompt_name": "my-prompt", "prompt_template": {"messages": [...]}, "commit_message": "update", "metadata": {"model": {"provider": "openai", "name": "gpt-4o"}}}
```

### List Labels
`GET /prompt-templates/labels`

## Logging

### Log Request
`POST /rest/log-request`
```json
{
  "provider": "openai",
  "model": "gpt-4o",
  "input": {"type": "chat", "messages": [{"role": "user", "content": [{"type": "text", "text": "Hello"}]}]},
  "output": {"type": "chat", "messages": [{"role": "assistant", "content": [{"type": "text", "text": "Hi!"}]}]},
  "request_start_time": "2026-01-01T00:00:00Z",
  "request_end_time": "2026-01-01T00:00:01Z"
}
```
Returns `{"success": true, "request_id": 123}`

## Tracking

### Track Prompt
`POST /rest/track-prompt`
```json
{"request_id": 123, "prompt_name": "my-prompt", "prompt_input_variables": {"key": "val"}, "version": 1}
```

### Track Score
`POST /rest/track-score`
```json
{"request_id": 123, "score": 95, "name": "accuracy"}
```
Score: 0-100. Name optional (defaults to "default").

### Track Metadata
`POST /rest/track-metadata`
```json
{"request_id": 123, "metadata": {"session_id": "abc", "user_id": "u1"}}
```

### Track Group
`POST /rest/track-group`
```json
{"request_id": 123, "group_id": 456}
```

## Datasets

### List Datasets
`GET /api/public/v2/datasets`
Query params: `page`, `per_page`, `name`, `status` (active|deleted|all)

## Evaluations

### List Evaluations
`GET /api/public/v2/evaluations`
Query params: `page`, `per_page`, `name`, `status`

### Run Evaluation
`POST /api/public/v2/evaluations/{eval_id}/run`

### Get Evaluation
`GET /api/public/v2/evaluations/{eval_id}`

## Agents (Workflows)

### List Agents
`GET /workflows`
Query params: `page`, `per_page`

### Run Agent
`POST /workflows/{agent_id}/run`
```json
{"input_variables": {"key": "value"}}
```

## Docs
- https://docs.promptlayer.com
- https://docs.promptlayer.com/reference/rest-api-reference
