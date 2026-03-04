# WebSocket Protocol Reference

## Connection

```
# Public S2G
wss://s2g.run/api/openclaw/ws/{nodeId}

# Self-hosted
ws://YOUR_HOST:PORT/api/openclaw/ws/{nodeId}
```

The `nodeId` is the UUID of the OpenClaw node in the S2G workflow. Find it in the S2G designer node properties.

## Authentication

If an auth secret is set on the S2G OpenClaw node (node properties → Auth Secret), the bridge **must** send the auth message as its **very first message** after WebSocket open — before any execute or ping:

```json
→ {"type": "auth", "secret": "your-secret"}
```

- ✅ Auth succeeds → S2G sends `connected` with available nodes
- ❌ Wrong secret → S2G sends `auth_failed` and closes the connection
- ❌ No auth sent when required → S2G sends `auth_required`

If no secret is set on the node (Auth Secret field left blank), authentication is skipped and the connection is open/unauthenticated.

```bash
# Start bridge with auth
node s2g-bridge.js --s2g wss://s2g.run --node-id UUID --secret YOUR_SECRET

# Or via environment variable
S2G_SECRET=YOUR_SECRET node s2g-bridge.js --s2g wss://s2g.run --node-id UUID
```

## Per-Request Timeout

Each node execution request has a configurable timeout (default: 60 seconds). If S2G doesn't respond within the timeout, the bridge returns an error:

```json
{"success": false, "output": {}, "error": "Timeout after 60000ms"}
```

Override per request:
```bash
curl -X POST http://localhost:18792/execute/SqlServer \
  -H "Content-Type: application/json" \
  -d '{"params": {"Query": "SELECT * FROM large_table"}, "timeout": 120000}'
```

The S2G OpenClaw node also has a **Per-Request Timeout** setting in its properties — this is the server-side maximum time S2G will wait for a node to execute before returning an error to the bridge.

## Messages

### Connected (auto-sent by S2G on connect)
```json
← {
    "type": "connected",
    "nodeId": "...",
    "availableNodes": [
      {"NodeId": "uuid", "Name": "PasswordGenerator", "NodeType": "Custom_PasswordGenerator", "OutputParams": []}
    ]
  }
```

> **Note:** Property names in `availableNodes` are **PascalCase** (`NodeId`, `Name`, `NodeType`).

### Execute a node
```json
→ {"type": "execute", "requestId": "r1", "nodeId": "target-uuid", "params": {"key": "value"}}
← {"type": "result", "requestId": "r1", "success": true, "output": {...}}
```

### Error response
```json
← {"type": "error", "requestId": "r1", "message": "Node not found"}
```

### Refresh node list
```json
→ {"type": "list_nodes"}
← {"type": "node_list", "nodes": [...]}
```

### Keepalive (send every ~30s)
```json
→ {"type": "ping"}
← {"type": "pong"}
```

### Data push (S2G → OpenClaw)
When S2G Input Forwarding is enabled on the OpenClaw node, upstream data arrives as:
```json
← {"type": "data", "data": {"field1": "value1", "field2": "value2"}}
```

## Error Scenarios

| Scenario | Response | Action |
|----------|----------|--------|
| Workflow not started | HTTP 409 on WS connect | Start workflow via API or designer, retry |
| Wrong secret | `auth_failed` + WS close | Fix secret |
| Node not found | `error` frame | Check node list |
| Execution timeout | `error` frame | Retry or reduce scope |
| WS disconnected | WS close event | Bridge auto-reconnects in 5s |
