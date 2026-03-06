---
name: justinx
description: Connect live streaming data (MQTT, Kafka, Webhook) to your AI agent via MCP with automated alerts and anomaly detection.
metadata: {"openclaw":{"primaryEnv":"JUSTINX_API_KEY","requires":{"env":["JUSTINX_API_KEY"]},"homepage":"https://justinx.ai","emoji":"📡"}}
---

# justinx

Use `justinx` for real-time streaming data -- MQTT brokers, Kafka topics, webhooks -- piped directly into your AI agent via MCP. Connect a data source, read live messages, set up automated alerts and anomaly detection, and get WebSocket URLs to embed in generated apps.

## When to use this skill

- You need to connect to an MQTT broker (IoT sensors, industrial telemetry, smart devices)
- You need to consume from Kafka topics
- You need a webhook endpoint to receive pushed data
- You want to build a live dashboard on streaming data
- You need automated alerting or anomaly detection on a data stream
- You want a WebSocket URL that any frontend can subscribe to for real-time updates

## Setup

### 1. Get an API key

Sign up at https://justinx.ai and copy your API key from Dashboard > Settings.

### 2. Configure the MCP server

Add JustinX as an MCP server. Choose one of the following methods depending on your environment.

**Direct MCP config** (Claude Code, Cursor, or any MCP client):

Add to your MCP settings (e.g. `.claude/settings.json`, `~/.openclaw/openclaw.json`, or your tool's MCP config):

```json
{
  "mcpServers": {
    "justinx": {
      "url": "https://api.justinx.ai/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY"
      }
    }
  }
}
```

**Via mcporter** (if you have the mcporter skill installed):

```
mcporter add justinx --url https://api.justinx.ai/mcp --header "Authorization: Bearer YOUR_API_KEY"
```

Then call tools with:

```
mcporter call justinx.list_connections
mcporter call justinx.create_connection type=mqtt broker=broker.emqx.io topics='["sensors/#"]'
```

## Tools reference

| Tool | Purpose |
|------|---------|
| `create_connection` | Connect to MQTT broker, Kafka cluster, or create a webhook endpoint |
| `list_connections` | List all active connections with status and WebSocket URLs |
| `get_connection` | Get a specific connection's status, message count, and WebSocket URL |
| `destroy_connection` | Tear down a connection and clean up its stream |
| `read_stream` | Sample live entries from a connection (backfill + live window) |
| `create_watcher` | Create a managed automation on a connection (alerting, aggregation) |
| `list_watchers` | List watchers with status, PID, and restart count |
| `get_watcher` | Get watcher details and configuration |
| `get_watcher_logs` | Read stdout/stderr from a running or crashed watcher |
| `update_watcher_config` | Update a watcher's JSON config (restarts automatically) |
| `restart_watcher` | Restart a stopped or crashed watcher |
| `delete_watcher` | Stop and remove a watcher |

## Common workflows

### Connect to an MQTT broker and read data

```
# Connect to a public IoT demo broker
create_connection type=mqtt broker=broker.emqx.io port=8883 tls=true topics=["justinx/demo/#"]

# Read the last 5 minutes of data + 3 seconds of live entries
read_stream connectionId=<id> backfillSeconds=300 liveSeconds=3 maxEntries=50
```

For a private broker with credentials:

```
create_connection type=mqtt broker=my-broker.example.com port=8883 tls=true username=myuser password=mypass topics=["sensors/#","alerts/#"]
```

### Create a webhook endpoint

```
# Creates an HTTP ingest URL -- POST JSON to it and messages appear in the stream
create_connection type=webhook

# The response includes an ingestUrl. Send data to it:
# POST https://api.justinx.ai/connections/<id>/ingest
```

### Connect to Kafka

```
create_connection type=kafka brokers=["kafka1.example.com:9092"] kafkaTopics=["events","logs"]

# With SASL auth:
create_connection type=kafka brokers=["kafka.example.com:9092"] kafkaTopics=["events"] saslUsername=user saslPassword=pass ssl=true
```

### Create a watcher for alerts

Watchers are managed automations that continuously monitor a connection for conditions you define — threshold alerts, metric aggregation, or notifications. Each watcher is scoped to a single connection.

```
# Create a watcher that alerts when temperature exceeds a threshold
create_watcher connectionId=<id> config='{"threshold": 45}'

# The platform provides a script template. See https://justinx.ai/docs for
# watcher script examples and the full scripting reference.
```

### Manage watchers

```
# List all watchers on a connection
list_watchers connectionId=<id>

# Check logs for debugging
get_watcher_logs connectionId=<id> watcherId=<wid>

# Update threshold without redeploying
update_watcher_config connectionId=<id> watcherId=<wid> config='{"threshold": 50}'

# Restart a crashed watcher
restart_watcher connectionId=<id> watcherId=<wid>

# Remove a watcher
delete_watcher connectionId=<id> watcherId=<wid>
```

### Build a live dashboard

After creating a connection, use the WebSocket URL from the response to build a frontend:

1. Call `create_connection` or `list_connections` to get the WebSocket URL
2. The WebSocket sends a `backfill` message on connect (recent history), then individual `entry` messages in real time
3. Each entry has `{ id, fields: { topic, payload }, ts }` format
4. Pass the WebSocket URL to any generated React/Next.js/HTML app

WebSocket message format:

```json
// Backfill (sent once on connect)
{ "type": "backfill", "entries": [{ "id": "...", "fields": { "topic": "...", "payload": "..." }, "ts": 1234567890 }] }

// Live entry (streamed continuously)
{ "type": "entry", "id": "...", "fields": { "topic": "...", "payload": "..." }, "ts": 1234567890 }
```

Topic filtering: append `?topics=sensor/temp,sensor/humidity` to the WebSocket URL.

## Tips

- Every new account gets a demo connection to `broker.emqx.io` with live IoT data -- call `list_connections` to find it
- Use `read_stream` with `backfillSeconds=0 liveSeconds=5` to see only fresh data
- Watcher config is passed as a JSON string and can be updated without redeploying
- Watcher alerts appear on the connection's WebSocket stream automatically
- The WebSocket URL works from any client (browser, Node.js, Python, mobile) -- no SDK needed
- Full tool reference and parameter schemas: https://justinx.ai/llms-full.txt
