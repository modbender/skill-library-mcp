# S2G REST API Reference

**Base URL:** `https://s2g.run/api/v1` (public) or `http://YOUR_HOST:5184/api/v1` (self-hosted)
**Auth:** All endpoints require `X-API-Key` header.

```bash
KEY=$(python3 -c 'import json;print(json.load(open("'$HOME'/.config/s2g/credentials.json"))["apiKey"])')
BASE="https://s2g.run/api/v1"
```

---

## Workflows

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/workflows` | List all workflows |
| `GET` | `/workflows/{id}` | Get workflow with nodes and connections |
| `POST` | `/workflows` | Create new workflow |
| `PUT` | `/workflows/{id}` | Update workflow (**⚠️ regenerates node IDs**) |
| `DELETE` | `/workflows/{id}` | Delete workflow |
| `POST` | `/workflows/{id}/start` | Start workflow |
| `POST` | `/workflows/{id}/stop` | Stop workflow |
| `POST` | `/workflows/{id}/nodes` | Add a single node (safe — preserves IDs) |
| `DELETE` | `/workflows/{id}/nodes/{nodeId}` | Remove a node |
| `POST` | `/workflows/{id}/connections` | Add a connection |
| `DELETE` | `/workflows/{id}/connections/{connId}` | Remove a connection |

### Create a Workflow

```bash
curl -X POST "$BASE/workflows" \
  -H "X-API-Key: $KEY" -H "Content-Type: application/json" \
  -d '{
    "name": "Webhook Processor",
    "description": "Listens for webhooks and responds",
    "nodes": [
      {
        "nodeType": "HttpListener",
        "name": "Webhook",
        "isTrigger": true,
        "configuration": "{\"path\": \"/hook\", \"method\": \"POST\"}"
      },
      {
        "nodeType": "Custom_LoremIpsum",
        "name": "Generate",
        "configuration": "{\"count\": \"{{Webhook.body.count}}\", \"unit\": \"paragraphs\"}"
      },
      {
        "nodeType": "HttpResponse",
        "name": "Respond",
        "configuration": "{\"statusCode\": 200, \"body\": \"{{Generate.Text}}\"}"
      }
    ],
    "connections": [
      { "sourceName": "Webhook", "targetName": "Generate" },
      { "sourceName": "Generate", "targetName": "Respond" }
    ]
  }'
```

**Node fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `nodeType` | string | ✅ | Node type (e.g. `HttpListener`, `Custom_LoremIpsum`) |
| `name` | string | ✅ | Display name (used as key for connections) |
| `configuration` | string | — | JSON string of node-specific config |
| `isTrigger` | bool | — | Mark as active trigger (default: false) |
| `x`, `y` | number | — | Canvas position (auto-layout if omitted) |

**Connection fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `sourceName` | string | ✅ | Source node name (case-insensitive) |
| `targetName` | string | ✅ | Target node name (case-insensitive) |
| `label` | string | — | Connection label/tag |

> Custom node types use `Custom_` prefix. API is case-insensitive: `Custom_LoremIpsum`, `custom_loremipsum`, and bare `LoremIpsum` all resolve.

### Add a Node (preserves existing IDs)

```bash
curl -X POST "$BASE/workflows/$WF_ID/nodes" \
  -H "X-API-Key: $KEY" -H "Content-Type: application/json" \
  -d '{"nodeType":"Custom_HashGenerator","name":"HashGenerator","x":320,"y":600}'
# Returns: { "id": "new-uuid", "name": "HashGenerator", ... }
```

### Wire Nodes

```bash
curl -X POST "$BASE/workflows/$WF_ID/connections" \
  -H "X-API-Key: $KEY" -H "Content-Type: application/json" \
  -d '{"sourceNodeId":"trigger-uuid","targetNodeId":"tool-uuid","label":"tool:hashgenerator"}'
```

### Inspect a Workflow

```bash
curl -s -H "X-API-Key: $KEY" $BASE/workflows/{id} | python3 -c "
import json, sys
d = json.load(sys.stdin)
print(f'Workflow: {d[\"name\"]} (active: {d[\"isActive\"]})')
for n in d['nodes']:
    t = ' ⚡TRIGGER' if n.get('isTrigger') else ''
    print(f'  {n[\"name\"]} ({n[\"nodeType\"]}) id={n[\"id\"]}{t}')
for c in d['connections']:
    print(f'  {c[\"sourceNodeName\"]} --[{c[\"label\"]}]--> {c[\"targetNodeName\"]}')
"
```

---

## Catalog API

Discover available node types and their exact input/output schemas.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/catalog/categories` | List all node categories |
| `GET` | `/catalog/nodes` | List all available node types |
| `GET` | `/catalog/categories/{name}/nodes` | List nodes in a category |
| `GET` | `/catalog/nodes/{type}/schema` | Get full node schema |

### List Categories

```bash
curl -H "X-API-Key: $KEY" "$BASE/catalog/categories"
# [{"name":"HTTP","type":"builtin","nodeCount":3},
#  {"name":"AI","type":"builtin","nodeCount":13},
#  {"name":"Knowledge","type":"builtin","nodeCount":1}, ...]
```

Built-in categories: HTTP, AI, Database, Cloud, Processing, Storage, Triggers, Integrations, Scripting, Knowledge.

### Get Node Schema

```bash
curl -H "X-API-Key: $KEY" "$BASE/catalog/nodes/Custom_Base64/schema"
```

```json
{
  "nodeType": "Custom_Base64",
  "displayName": "Base64 Encode/Decode",
  "inputFields": [
    {
      "fieldName": "inputText",
      "displayLabel": "Input",
      "fieldType": "TextArea",
      "isRequired": true,
      "allowPlaceholders": true
    }
  ],
  "outputParameters": [
    { "parameterName": "Result", "dataType": "string" }
  ],
  "connectionTags": [
    { "tagName": "success", "color": "#22c55e" },
    { "tagName": "error", "color": "#ef4444" }
  ]
}
```

> **Always check the schema** before executing an unfamiliar node. The `fieldName` in `inputFields` is the exact key to use in params.

### Bulk Schema Discovery

```bash
curl -s -H "X-API-Key: $KEY" $BASE/workflows/{id} | python3 -c "
import json, sys
types = set(n['nodeType'] for n in json.load(sys.stdin)['nodes'])
for t in sorted(types): print(t)
" | while read ntype; do
  echo "=== $ntype ==="
  curl -s -H "X-API-Key: $KEY" "$BASE/catalog/nodes/$ntype/schema" | python3 -c "
import json, sys
d = json.load(sys.stdin)
print(', '.join(f['fieldName'] for f in d.get('inputFields',[])))
" 2>/dev/null
done
```

---

## Knowledge Base

The Knowledge Base is a built-in knowledge graph supporting entities, relations, and semantic search. Available as a workflow node (`Knowledge`) and via the node execution API.

**Node type:** `Knowledge`
**Operations:** Search, GetEntity, AddEntity, UpdateEntity, DeleteEntity, AddRelation, RemoveRelation, GetRelations, GetGraph, ListEntities, ListTypes

**Output parameters:** `Result`, `ResultJson`, `EntityId`, `RelationsJson`, `GraphJson`, `Success`

### Using via Bridge

Add a Knowledge node to your workflow, wire it to the OpenClaw trigger, then execute:

```bash
# Search the knowledge base
curl -X POST http://localhost:18792/execute/Knowledge \
  -H "Content-Type: application/json" \
  -d '{"params": {"operation": "Search", "query": "customer billing issues"}}'

# Add an entity
curl -X POST http://localhost:18792/execute/Knowledge \
  -H "Content-Type: application/json" \
  -d '{"params": {"operation": "AddEntity", "type": "Customer", "name": "Acme Corp", "content": "Enterprise customer since 2024"}}'

# Get relations
curl -X POST http://localhost:18792/execute/Knowledge \
  -H "Content-Type: application/json" \
  -d '{"params": {"operation": "GetRelations", "entityId": "entity-uuid"}}'
```

### Using via Workflow Configuration

Configure the Knowledge node in the S2G designer with operation-specific fields. The node supports personal and organization-scoped stores. Use `{{placeholder}}` syntax to wire upstream data into operations.

---

## AI Nodes & Providers

S2G has 13 built-in AI nodes: OpenAI, DeepSeek, DeepSeek Agent, Copilot Agent, OpenClaw Agent, Anthropic, Gemini, Mistral, Groq, Vector Store, Vector Client, PDF OCR (Mistral), and Orchestrator.

### List AI Providers

```bash
curl -H "X-API-Key: $KEY" "$BASE/ai/providers"
```

```json
[
  {
    "provider": "OpenAI",
    "models": ["gpt-4o", "gpt-4o-mini"],
    "defaultModel": "gpt-4o",
    "isConfigured": true,
    "authType": "api_key"
  }
]
```

### Generate Workflow with AI

```bash
curl -X POST "$BASE/ai/generate" \
  -H "X-API-Key: $KEY" -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a workflow that listens for webhooks and hashes the input",
    "provider": "OpenAI",
    "model": "gpt-4o",
    "temperature": "Focused"
  }'
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `prompt` | string | ✅ | Natural language workflow description |
| `provider` | string | — | `OpenAI`, `Anthropic`, `Gemini`, `Copilot` |
| `model` | string | — | Specific model |
| `temperature` | string | — | `Focused`, `Balanced`, `Creative` |

> Generated workflow is immediately persisted. Start with `POST /workflows/{id}/start`.

### Workflow Templates (Samples)

Pre-built workflow examples that can be imported directly. Use these as starting points or learning resources.

```bash
# List all available workflow templates
curl -H "X-API-Key: $KEY" "https://s2g.run/api/v1/ai/samples"
```

```json
[
  { "fileName": "simple-api-endpoint.json", "name": "Simple API Endpoint", "nodeCount": 2, "connectionCount": 1 },
  { "fileName": "ai-chat-endpoint.json", "name": "AI Chat Endpoint", "nodeCount": 3, "connectionCount": 2 },
  { "fileName": "database-query-api.json", "name": "Database Query API", "nodeCount": 3, "connectionCount": 2 },
  { "fileName": "conditional-processing.json", "name": "Conditional Processing", "nodeCount": 4, "connectionCount": 3 },
  { "fileName": "external-api-integration.json", "name": "External API Integration", "nodeCount": 3, "connectionCount": 2 },
  { "fileName": "onedrive-to-storage.json", "name": "OneDrive -> Storage", "nodeCount": 4, "connectionCount": 3 },
  { "fileName": "excel-to-json.json", "name": "Excel2JSON", "nodeCount": 9, "connectionCount": 8 },
  { "fileName": "vector-db-ingest-consume.json", "name": "Vector DB Ingest - Consume", "nodeCount": 14, "connectionCount": 12 },
  { "fileName": "scheduler-test.json", "name": "Scheduler Test", "nodeCount": 6, "connectionCount": 5 },
  { "fileName": "orchestrator-test.json", "name": "Orchestrator Test", "nodeCount": 7, "connectionCount": 7 },
  { "fileName": "aggregator-test.json", "name": "Aggregator Test", "nodeCount": 7, "connectionCount": 4 },
  { "fileName": "remote-client-test.json", "name": "Remote Client Tests", "nodeCount": 5, "connectionCount": 4 },
  { "fileName": "mspc-customer-sync.json", "name": "MSPC Customer/Sub Sync Events", "nodeCount": 3, "connectionCount": 2 }
]
```

```bash
# Get a specific template (returns full workflow JSON — can be used directly with POST /workflows)
curl -H "X-API-Key: $KEY" "https://s2g.run/api/v1/ai/samples/simple-api-endpoint"
```

> The returned JSON contains complete `nodes` and `connections` arrays. Use it as the body for `POST /api/v1/workflows` to create a new workflow from the template.

**Import a sample as a new workflow:**
```bash
# Fetch sample and create workflow in one step
SAMPLE=$(curl -s -H "X-API-Key: $KEY" "https://s2g.run/api/v1/ai/samples/ai-chat-endpoint")
curl -X POST "https://s2g.run/api/v1/workflows" \
  -H "X-API-Key: $KEY" -H "Content-Type: application/json" \
  -d "$SAMPLE"
```

---

## Connections (OAuth/Auth)

Manage external service connections (OAuth tokens, API keys).

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/connections` | List all connections |
| `GET` | `/connections/{id}` | Get connection details |
| `POST` | `/connections` | Create connection |
| `PUT` | `/connections/{id}` | Update connection |
| `DELETE` | `/connections/{id}` | Delete connection |

---

## Usage & Quotas

```bash
curl -H "X-API-Key: $KEY" "$BASE/usage"
```

```json
{
  "executions": { "used": 1250, "limit": 5000, "percent": 25.0 },
  "storage": { "usedBytes": 52428800, "limitBytes": 1073741824, "percent": 4.9 },
  "vectorDocs": { "used": 150, "limit": 1000, "percent": 15.0 },
  "workflows": { "used": 8, "limit": 25, "percent": 32.0 }
}
```

---

## Node Logs

```bash
# Get execution logs (with filters)
curl "$BASE/workflows/$WF/nodes/$NODE/logs?level=Error&pageSize=10" \
  -H "X-API-Key: $KEY"

# Query params: level (Info/Warning/Error/Debug), dateFrom, dateTo, search, page, pageSize
```

```json
{
  "totalCount": 42,
  "logs": [
    {
      "nodeName": "HTTP Listener",
      "timestamp": "2026-02-14T18:30:00Z",
      "level": "Error",
      "message": "Request timed out after 300s"
    }
  ]
}
```

---

---

## HTTP Listener (Webhook API)

Trigger workflows from external services via public HTTP endpoints. The HTTP Listener node acts as a webhook receiver — any external system can call it to start a workflow execution.

**Public endpoint:**
```
https://listener.s2g.run/api/trigger?nodeId=<NODE_ID>
```

**Self-hosted:**
```
http://YOUR_HOST:5184/api/trigger?nodeId=<NODE_ID>
```

### Node ID Resolution (priority order)

1. **Query parameter** (recommended): `?nodeId=<UUID>`
2. **Custom header**: `X-S2G-Node-Id: <UUID>`
3. **Subdomain** (requires wildcard DNS): `<nodeId>.listener.s2g.run`

### Supported Methods

GET, POST, PUT, DELETE, PATCH — all forwarded to the workflow with full request context.

### Request Examples

```bash
# POST with JSON body
curl -X POST "https://listener.s2g.run/api/trigger?nodeId=YOUR_NODE_ID" \
  -H "Content-Type: application/json" \
  -d '{"message": "hello", "user": "john"}'

# GET with query parameters
curl "https://listener.s2g.run/api/trigger?nodeId=YOUR_NODE_ID&param1=value1&param2=value2"

# POST with custom path (accessible via {{NodeName.Path}})
curl -X POST "https://listener.s2g.run/api/trigger/my/custom/path?nodeId=YOUR_NODE_ID" \
  -H "Content-Type: application/json" \
  -d '{"data": "test"}'

# Empty body trigger (health check / cron ping)
curl -X POST "https://listener.s2g.run/api/trigger?nodeId=YOUR_NODE_ID"
```

### Response Behavior

- If the workflow contains an **HttpResponse node**: the response body, status code, and headers are controlled by that node
- If **no HttpResponse node**: S2G returns a default `200 OK` with `"OK"` body after the workflow completes
- If the workflow **times out**: returns the configured default response (or 200 OK)

### Output Placeholders

Access request data in downstream nodes using placeholders:

| Placeholder | Description |
|-------------|-------------|
| `{{NodeName.Body}}` | Raw request body (JSON auto-parsed) |
| `{{NodeName.body.fieldName}}` | Specific field from JSON body |
| `{{NodeName.Method}}` | HTTP method (GET, POST, etc.) |
| `{{NodeName.Path}}` | Request path after `/api/trigger` |
| `{{NodeName.Headers}}` | All request headers as JSON |
| `{{NodeName.QueryString}}` | Query string parameters |

### HttpResponse Node

To send custom responses back to the caller, add an HttpResponse node to the workflow:

```json
{
  "nodeType": "HttpResponse",
  "name": "Respond",
  "configuration": "{\"statusCode\": 200, \"body\": \"{{Generate.Result}}\", \"contentType\": \"application/json\"}"
}
```

The HttpResponse node correlates with the original request using an internal `RequestId` — no manual wiring needed.

---

## Placeholder Syntax

S2G uses `{{NodeName.OutputParam}}` placeholders to pass data between nodes. This is the core data wiring mechanism.

### Basic Syntax

```
{{NodeName.OutputParam}}
```

- `NodeName` — The display name of the source node (case-sensitive)
- `OutputParam` — The output parameter name from the node schema

### Examples

```
{{Webhook.Body}}                    — Raw body from HTTP Listener
{{Webhook.body.email}}              — Nested field from JSON body
{{PasswordGenerator.Password}}      — Generated password
{{HashGenerator.Hash}}              — Hash output
{{DateMath.Result}}                 — Date calculation result
{{Knowledge.ResultJson}}            — Knowledge Base query result
{{OpenAI.Response}}                 — AI model response
```

### Usage in Node Configuration

Placeholders are used in the `configuration` JSON string when creating/updating nodes:

```json
{
  "nodeType": "Custom_HashGenerator",
  "name": "HashInput",
  "configuration": "{\"text\": \"{{Webhook.body.password}}\", \"algorithm\": \"SHA256\"}"
}
```

### Nested Access

For JSON body fields, use dot notation:
```
{{Webhook.body.user.name}}          — Deep nested field
{{Webhook.body.items[0].id}}        — Array access
```

---

## Active Triggers & Auto-Start

### Active Triggers

A workflow must have at least one node marked as an **active trigger** to start. Trigger nodes are entry points that listen for external events (HTTP requests, schedules, WebSocket connections).

**Which nodes should be triggers:**
- **HttpListener** — Listens for incoming HTTP/webhook requests
- **Scheduler** — Fires on cron schedule
- **OpenClaw** — Listens for WebSocket connections from OpenClaw agents

Mark a node as trigger by setting `"isTrigger": true` when creating via API, or toggling the trigger icon in the S2G designer.

### Auto-Start (🚀)

The **Auto-Start** flag (🚀 rocket icon in the S2G toolbar) ensures a workflow automatically restarts after:
- Service restarts or deployments
- Server reboots
- Crash recovery

**Strongly recommended** for workflows with OpenClaw nodes — ensures the bridge can always reconnect without manual intervention.

Enable via the designer toolbar or check `isActive: true` in the workflow API response.

---

## Connection Tags & Routing

### How Routing Works

Each node defines **connection tags** (visible in the schema's `connectionTags` array). When a node finishes execution, it fires one of its tags (e.g., `success` or `error`). Connections between nodes are labeled with these tags to control flow.

### The `_TriggeredTags` Output

Every node execution result includes `_TriggeredTags` — a JSON array of which tags fired:

```json
{
  "output": {
    "Result": "...",
    "_TriggeredTags": "[\"success\"]"
  }
}
```

Use this to detect success/failure programmatically when calling nodes via the bridge.

### Common Tag Patterns

| Tag | Meaning |
|-----|---------|
| `success` | Node executed successfully |
| `error` | Node encountered an error |
| `tool:nodename` | OpenClaw bridge routing — connects trigger to specific tool nodes |
| `complete` | Reserved for HttpResponse node — signals response completion |

### Wiring Convention for OpenClaw Bridge

When connecting the OpenClaw trigger node to tool nodes, use the `tool:` prefix:

```bash
# Connect OpenClaw trigger → PasswordGenerator
curl -X POST "$BASE/workflows/$WF/connections" \
  -H "X-API-Key: $KEY" -H "Content-Type: application/json" \
  -d '{"sourceNodeId":"openclaw-node-id","targetNodeId":"password-node-id","label":"tool:passwordgenerator"}'
```

---

## Custom Node Designer

S2G includes a **Custom Node Designer** for creating your own node types with JavaScript logic. Custom nodes run in a sandboxed Jint (JavaScript) runtime.

### Creating Custom Nodes

Custom nodes are created in the S2G designer under the node catalog. Each custom node defines:

- **Input fields** — Parameters the node accepts (Text, TextArea, Boolean, Number, Dropdown)
- **Output parameters** — Values the node produces
- **JavaScript logic** — Sandboxed code that processes inputs and sets outputs
- **Connection tags** — Routing tags (typically `success` and `error`)
- **Category** — Where the node appears in the catalog

### Custom Node Type Naming

- Custom nodes get a `Custom_` prefix: `Custom_PasswordGenerator`, `Custom_HashGenerator`
- The catalog API is case-insensitive: `Custom_LoremIpsum`, `custom_loremipsum`, and bare `LoremIpsum` all resolve
- When adding via API, use the single `Custom_` prefix — S2G normalizes automatically

### Using Custom Nodes via Bridge

Custom nodes work identically to built-in nodes via the bridge. The bridge auto-discovers them on connect:

```bash
# Execute a custom node by name
curl -X POST http://localhost:18792/execute/MyCustomNode \
  -H "Content-Type: application/json" \
  -d '{"params": {"inputField": "value"}}'
```

---

## Error Catalog

All S2G API errors use consistent JSON format:

```json
{"error": "Human-readable error message", "statusCode": 400}
```

| HTTP Status | Error | Cause | Fix |
|-------------|-------|-------|-----|
| `400` | `Invalid Node ID format` | Not a valid GUID | Check nodeId is UUID format |
| `400` | `Could not extract Node ID` | No Node ID in request | Use `?nodeId=`, `X-S2G-Node-Id` header, or subdomain |
| `400` | `Listener node is not running` | Workflow not started | Start via designer or `POST .../start` |
| `404` | `Listener node not found` | No matching node | Verify node ID and type |
| `409` | `OpenClaw node is not running` | Workflow not active | Start the workflow first |
| `500` | `Error processing request` | Internal workflow error | Check workflow logs via API |
| `502` | `Could not reach S2G Web` | App unreachable | Retry after a few seconds |

---

## ⚠️ Warnings

1. **`PUT /workflows/{id}` regenerates ALL node IDs.** Never use PUT to update node configs.
2. **When PUT includes `nodes`, you MUST also include `connections`** (and vice versa). Both replaced atomically.
3. **Workflow must be running** for WebSocket/trigger connections. 409 = not started.
4. **Use `POST /workflows/{id}/nodes`** to add nodes — preserves existing IDs.

---

## Quick Reference — All 28 Endpoints

| # | Method | Endpoint |
|---|--------|----------|
| 1 | GET | `/workflows` |
| 2 | GET | `/workflows/{id}` |
| 3 | POST | `/workflows` |
| 4 | PUT | `/workflows/{id}` |
| 5 | DELETE | `/workflows/{id}` |
| 6 | POST | `/workflows/{id}/start` |
| 7 | POST | `/workflows/{id}/stop` |
| 8 | POST | `/workflows/{id}/nodes` |
| 9 | DELETE | `/workflows/{id}/nodes/{nodeId}` |
| 10 | POST | `/workflows/{id}/connections` |
| 11 | DELETE | `/workflows/{id}/connections/{connId}` |
| 12 | GET | `/catalog/categories` |
| 13 | GET | `/catalog/nodes` |
| 14 | GET | `/catalog/categories/{name}/nodes` |
| 15 | GET | `/catalog/nodes/{type}/schema` |
| 16 | GET | `/connections` |
| 17 | GET | `/connections/{id}` |
| 18 | POST | `/connections` |
| 19 | PUT | `/connections/{id}` |
| 20 | DELETE | `/connections/{id}` |
| 21 | GET | `/usage` |
| 22 | GET | `.../nodes/{nodeId}/logs` |
| 23 | GET | `.../nodes/{nodeId}/logging-settings` |
| 24 | PUT | `.../nodes/{nodeId}/logging-settings` |
| 25 | GET | `/ai/providers` |
| 26 | POST | `/ai/generate` |
| 27 | GET | `/ai/samples` |
| 28 | GET | `/ai/samples/{name}` |
