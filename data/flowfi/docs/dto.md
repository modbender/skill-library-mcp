# DTO and request/response shapes

Use these shapes when building requests or parsing responses. All request bodies are JSON; responses are JSON unless noted.

## Pagination (query + list responses)

**Query params** (where supported: workflows, smart-accounts, executions, templates, comments, execution events):

| Param     | Type   | Default | Description                          |
|----------|--------|--------|--------------------------------------|
| `page`   | number | 1      | Page index (min 1)                   |
| `limit`  | number | 10     | Items per page (1–100)               |
| `sortBy` | string | —      | Field to sort by                     |
| `sortOrder` | string | DESC | `ASC` or `DESC`                     |
| `search` | string | —      | Search term (where supported)        |

**Paginated response:** `{ data: T[], meta: { page, limit, total, totalPages, hasNext, hasPrev } }`.

## Auth

**POST /auth/bearer-token**  
Request: `{ expiresInSeconds: number }` (60–31536000).  
Response: `{ token: string, expiresAt?: number }` — use `token` as `Authorization: Bearer <token>`.

## AI / workflows

**POST /ai/generate-workflow**  
Request: `{ prompt: string, smartAccountId: string }`.  
Response: workflow object (see Workflow below).

**POST /ai/workflow/:id/prompt**  
Request: `{ prompt: string }`.  
Response: `{ message: string, workflow: Workflow }`.

**GET /ai/workflow/:id/suggestions**  
Response: `{ suggestions: string[] }`.

**POST /workflows** (create workflow manually)  
Request: `{ name: string, nodes: WorkflowNode[], connections: Connection[], variables?: WorkflowVariable[], smartAccountId: string, config?: WorkflowConfig }`.  
- **WorkflowNode:** `{ id, definitionId, type: "settings"|"node", title, x, y, config?: Record<string, string> }`.  
- **Connection:** `{ id, fromNode, fromPort, toNode, toPort }`.  
- **WorkflowVariable:** `{ key, value, defaultValue?, description? }`.  
Response: workflow object.

**PATCH /workflows/:id**  
Request: partial `{ name?, nodes?, connections?, variables? }`. Do not send `status`; use deploy/undeploy/pause/resume.  
Response: workflow object.

**POST /workflows/:id/variables**  
Request: `{ key: string, value?: string, defaultValue?: string, description?: string }`. **Important:** `key` must start with `"user."` (e.g. `user.threshold`).  
Response: updated variables or success.

## Workflow (response shape)

Workflow object: `{ id, name, status, nodes, connections, variables?, config?, smartAccountId, commentCount?, executionCount?, createdAt, updatedAt }`.  
- **status:** `"draft" | "active" | "paused" | "archived" | "ended"`.  
- **nodes:** array of WorkflowNode.  
- **connections:** array of Connection.

## Templates

**GET /templates** (and **GET /templates/display**)  
Response: `{ data: TemplateDisplayInfo[], meta }` (list) or `TemplateDisplayInfo[]` (display).  
**TemplateDisplayInfo:** `{ id, name, description, category, uses, steps, setupTime, price, nodeCount, connectionCount, featured? }`.

**GET /templates/:id**  
Response: full template `{ id, name, description, category, nodes, connections, variables?, uses, steps, setupTime, price, featured? }`.

**POST /templates/:id/clone**  
Request: `{ smartAccountId: string, name?: string, network?: string }`.  
Response: created workflow (draft).

## Execution

**POST /executions/workflows/:workflowId/start**  
Response: execution object `{ id, workflowId, status, startedAt, completedAt?, error?, result? }`. **status:** `"pending" | "running" | "completed" | "failed" | "cancelled"`.

**GET /executions**, **GET /executions/workflows/:workflowId**  
Response: `{ data: Execution[], meta }`.

**GET /executions/:id/events**  
Response: `{ data: ExecutionEvent[], meta }`. Event: `{ id, executionId, eventType, level, message, nodeId?, nodeDefinitionId?, metadata?, createdAt }`.

## Price (no auth)

**GET /price**  
Query: `symbol?: string` (e.g. `BNB`, `ETH`, `BTC`; default `BNB`).  
Response: **TokenPriceResponse** — `{ symbol: string, priceUsd: string }`. `priceUsd` is `"0"` on failure.

**GET /price/prices**  
No request body or query.  
Response: **TokenPricesResponse** — `{ BNB: string, ETH: string }`. USD prices as strings.

## Errors

API errors: `{ statusCode: number, message: string, error?: string }`. Use `statusCode` for HTTP status; `message` for user-facing text.
