# Event Watcher v0 Config Spec (Redis Streams + webhook JSONL)

## Goals
- No events → no agent wake → no token cost
- Events trigger agent via `sessions_send`
- Multiple watchers; each watcher can target a different session

---

## Environment Variables (Auth)
Use env vars for Redis auth (first version):

```
REDIS_URL=redis://:password@host:6379/0
# or
REDIS_HOST=...
REDIS_PORT=...
REDIS_PASSWORD=...
```

---

## Unified Event Schema
All sources normalized to:
```json
{
  "event_id": "...",
  "source": "redis_stream",
  "topic": "weather_events",
  "timestamp": "2026-02-03T12:00:00Z",
  "payload": {"weather": "rain"}
}
```

---

## YAML Config
```yaml
watchers:
  - name: weather_stream
    source: redis_stream
    stream: weather_events
    group: eventwatcher
    consumer: watcher-1
    batch_count: 10
    block_ms: 1000
    payloadField: payload
    payloadEncoding: json
    filter:
      field: "payload.weather"
      op: "!="
      value: "sunny"
    dedupe_ttl_seconds: 1800
    ack_timeout_seconds: 30
    retry:
      max: 3
      backoff_seconds: [60, 300, 900]
    wake:
      method: sessions_send
      reply_channel: slack
      reply_to: channel:YOUR_CHANNEL_ID
      # Option A: inline template
      message_template: |
        New event: {{event_id}}
      # Option B: prompt file reference (short message)
      # prompt_file: prompts/weather_guide.md
```

### Webhook Source (via OpenClaw hooks)
```yaml
watchers:
  - name: webhook_events
    source: webhook
    webhook_log_path: /root/.openclaw/workspace/webhook_events.jsonl
    batch_count: 50
    filter:
      field: "payload.type"
      op: "!="
      value: "sunny"
    wake:
      method: sessions_send
      reply_channel: slack
      reply_to: channel:YOUR_CHANNEL_ID
      message_template: "Webhook event {{event_id}}"
```

Use `scripts/webhook_bridge.py` as the hook target to append incoming payloads to the JSONL file.

### Fields
- `name`: unique watcher id
- `source`: `redis_stream | webhook | sqs | kafka`
- `stream`: Redis stream name (redis_stream)
- `group`, `consumer`: Redis consumer group settings (redis_stream)
- `batch_count`: number of events per read (default 10)
- `block_ms`: Redis block time (default 1000) (redis_stream)
- `payloadField`: field to parse as payload (redis_stream)
- `payloadEncoding`: `json|hash|string` (redis_stream)
- `webhook_log_path`: JSONL file path (webhook)
- `filter`: JSON rule (see below)
- `dedupe_ttl_seconds`: default 1800
- `ack_timeout_seconds`: default 30
- `retry`: max + backoff list
- `rate_limit.min_interval_seconds`: minimum seconds between deliveries
- `aggregate.window_seconds`: aggregate events for a window and send one message
- `aggregate.message_template`: template for aggregated message (supports `{{count}}`, `{{first_event_id}}`, `{{last_event_id}}`, `{{last_payload}}`)
- `wake.method`: `sessions_send | agent_gate`
- `wake.session_id`: optional explicit session id override
- `wake.session_key`: optional session key (resolved from session store)
- `wake.disable_session_store_lookup`: if true, skip reading local session store (privacy)
- `wake.add_source_preamble`: if true (default), prepend a safety header to the message
- `wake.message_template`: text for the agent
- `wake.reply_channel`: required for `sessions_send` and `agent_gate` (e.g., slack)
- `wake.reply_to`: required for `sessions_send` and `agent_gate` (channel/user target id)

---

## Filter Rules
Simple rule:
```json
{"field":"payload.weather","op":"!=","value":"sunny"}
```

Group rules:
```json
{"all":[
  {"field":"payload.type","op":"!=","value":"sunny"},
  {"any":[
    {"field":"payload.city","op":"==","value":"beijing"},
    {"field":"payload.city","op":"==","value":"shanghai"}
  ]}
]}
```

Supported `op`: `==`, `!=`, `>`, `<`, `>=`, `<=`, `in`, `contains`, `regex`

Natural language can be translated by the agent into JSON.

---

## Deduplication
- store `event_id` in Redis key
- default TTL: 1800s (configurable)

---

## Retry
- if delivery fails:
  - retry with backoff
  - after max attempts, append to dead_letter.jsonl

---

## Rate Limiting + Aggregation
```yaml
rate_limit:
  min_interval_seconds: 60
aggregate:
  window_seconds: 300
  message_template: "Burst: {{count}} events (last={{last_event_id}})"
```

---

## Session Routing
- Each watcher can target a session via `wake.session_id` or `wake.session_key`
- If neither is set, watcher resolves the **latest session** for `reply_channel` + `reply_to`
- Set `wake.disable_session_store_lookup: true` to skip local session file access
- `wake.method: sessions_send` runs agent and **delivers** to `reply_channel`/`reply_to`
- `wake.method: agent_gate` runs agent and only sends if reply != `NO_REPLY`

---

## Logging + Metrics
- Structured event logs: `EVENT_WATCHER_LOG` (default `event_watcher_events.jsonl`)
- State file includes counters per watcher: received/matched/delivered/failed/filtered/deduped/rate_limited

## Prompt Safety (recommended)
- By default, watcher prepends a safety header describing the event source and warning against prompt injection.
- Disable via `wake.add_source_preamble: false` if you have a controlled, trusted payload.

## Running in Background (recommended)
Use a lightweight background runner instead of system daemons:

**macOS / Linux**
```bash
nohup python3 {baseDir}/scripts/watcher.py --config {baseDir}/config/event_watcher.yaml \
  > {baseDir}/logs/watcher.log 2>&1 &
```

Or run inside `tmux`/`screen`.

---

## Future Extensions
- Add `source: sqs | kafka | webhook`
- Add per-watcher rate limits and quiet hours
