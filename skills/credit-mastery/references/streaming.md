# Streaming Responses

Enable real-time SSE (Server-Sent Events) streaming from Swarms agents.

## Enable
Set `streaming_on: true` in agent config.

## SSE Event Types

| Event | Data | Description |
|-------|------|-------------|
| `metadata` | `{job_id, name}` | Job info at start |
| `chunk` | `{content}` | Incremental text |
| `usage` | `{tokens_used, cost}` | Token/cost summary |
| `done` | `{status}` | Completion signal |
| `error` | `{error}` | Error details |

## Python Example

```python
headers = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no"
}

payload = {
    "agent_config": {
        "agent_name": "StreamAgent",
        "model_name": "claude-sonnet-4-20250514",
        "max_tokens": 8192,
        "streaming_on": True
    },
    "task": "Your task"
}

response = requests.post(
    f"{BASE_URL}/v1/agent/completions",
    headers=headers, json=payload, stream=True
)

for line in response.iter_lines():
    line = line.decode("utf-8")
    if line.startswith("event: "):
        current_event = line[7:].strip()
    elif line.startswith("data: "):
        data = json.loads(line[6:])
        if current_event == "chunk":
            print(data.get("content", ""), end="", flush=True)
```

## Multi-Agent Streaming
Set `"stream": true` in SwarmSpec (top-level, not per-agent).
