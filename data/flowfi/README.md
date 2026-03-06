# OpenClaw

OpenClaw provides skills and instructions for integrating with the **FlowFi** backend API. Use it when you need to call FlowFi workflows, smart accounts, or auth endpoints (e.g. from an agent or external client).

## How it works

- The **user** generates a JWT (e.g. via the FlowFi app or auth flow) and sends it to OpenClaw.
- OpenClaw uses that token in the `Authorization: Bearer <token>` header for all FlowFi API requests.

---

## How to generate a workflow with AI

1. **Get a smart account ID** — `GET /smart-accounts` (with JWT). Use one of the returned `id` values.
2. **Generate from a prompt** — `POST /ai/generate-workflow` with JSON body:
   - `prompt` (required): natural-language description, e.g. *"When ETH price goes above 3500, send me a Telegram message"*
   - `smartAccountId` (required): the smart account ID from step 1
3. The API returns the new workflow (`id`, `name`, `nodes`, `connections`) in **draft** status.

---

## What to do next

| Goal | What to do |
|------|------------|
| **Run the workflow** | **Deploy** — `POST /workflows/:id/deploy`. Status becomes **active**; it runs on its triggers/schedule. |
| **Change the workflow** | **Undeploy** first if it’s active or paused: `POST /workflows/:id/undeploy`. Then **edit by prompt**: `POST /ai/workflow/:id/prompt` or `PATCH /workflows/:id`. |
| **Get AI edit ideas** | `GET /ai/workflow/:id/suggestions` — returns short suggestions (e.g. "Add a delay", "Add a notification"). |
| **Pause running** | `POST /workflows/:id/pause`. Resume with `POST /workflows/:id/resume`. |
| **Stop and make editable** | `POST /workflows/:id/undeploy` — status goes back to **draft**. |
| **End the workflow** | `POST /workflows/:id/stop` — status **ended**; no more runs (you can deploy again later). |
| **Remove permanently** | **Delete** — `DELETE /workflows/:id`. Safe for any status; backend stops the scheduler if needed. |
| **List workflows** | `GET /workflows` with optional `?status=draft`, `?smartAccountId=...`, pagination. |
| **Run once / watch runs** | **Start run** — `POST /executions/workflows/:workflowId/start`. **List runs** — `GET /executions` or `GET /executions/workflows/:workflowId`. **Real-time** — WebSocket namespace `/workflow-status`; subscribe to `execution` or `workflow` for live status and history refresh. |
| **Start from a template** | **List** — `GET /templates` or `GET /templates/categories`. **Clone** — `POST /templates/:id/clone` with `smartAccountId` (and optional `name`, `network`) to create a **draft** workflow; then edit and deploy. |

---

## Capabilities summary

- **Smart accounts** — List and get smart accounts; use an account `id` as `smartAccountId` when creating workflows.
- **Workflows** — Generate with AI, get suggestions, edit by prompt, **deploy**, **undeploy**, **pause**, **resume**, **stop**, **delete**, list.
- **Execution** — List runs (all or by workflow), **start** a run, get one execution, **cancel**, get **events** (and per-node events).
- **WebSocket** — Real-time updates: connect to namespace `/workflow-status` with JWT; **subscribe** to execution, workflow, or simulation to receive status and node updates (and `workflow:update` / `workflow:history:refresh`).
- **Price** — **GET** `/price?symbol=BNB` (one token USD price); **GET** `/price/prices` (BNB + ETH). No auth.
- **Templates** — **GET** `/templates` (list with filters), `/templates/display`, `/templates/categories`, `/templates/:id` (full); **POST** `/templates/:id/clone` (JWT) creates a draft workflow from a template.
- **Knowledge** — The backend uses a workflow knowledge base (valid node types, structure) for AI generation; no API to fetch it; see [SKILL.md](SKILL.md#knowledge-workflow-generation) for prompt tips and node types. Templates follow the same structure; use templates for starting points.
- **Auth** — Long-lived bearer tokens and revoke (sign-in is done by the user outside OpenClaw).

---

## API reference

Full REST API details, **request/response DTOs** (pagination, auth, AI/workflows, templates, execution, price, error shape), and example prompts are in **[SKILL.md](SKILL.md)**. See the **DTO and request/response shapes** section for exact JSON request bodies and response types.

Quick reference:

| Action | Method | Endpoint |
|--------|--------|----------|
| List smart accounts | GET | `/smart-accounts` |
| Generate workflow (AI) | POST | `/ai/generate-workflow` |
| Get suggestions | GET | `/ai/workflow/:id/suggestions` |
| Edit by prompt | POST | `/ai/workflow/:id/prompt` |
| Deploy | POST | `/workflows/:id/deploy` |
| Undeploy | POST | `/workflows/:id/undeploy` |
| Delete | DELETE | `/workflows/:id` |
| Pause | POST | `/workflows/:id/pause` |
| Resume | POST | `/workflows/:id/resume` |
| Stop | POST | `/workflows/:id/stop` |
| List workflows | GET | `/workflows` |
| **Execution** | | |
| List executions | GET | `/executions` |
| Start execution | POST | `/executions/workflows/:workflowId/start` |
| List workflow runs | GET | `/executions/workflows/:workflowId` |
| Get execution | GET | `/executions/:id` |
| Cancel execution | DELETE | `/executions/:id/cancel` |
| Execution events | GET | `/executions/:id/events` |
| Node events | GET | `/executions/:id/events/node/:nodeId` |
| **Price** | | |
| Token price | GET | `/price?symbol=BNB` (no auth). Response: `{ symbol, priceUsd }`. |
| BNB/ETH prices | GET | `/price/prices` (no auth). Response: `{ BNB, ETH }` (strings). |
| **Templates** | | |
| List templates | GET | `/templates` (no auth) |
| Display info | GET | `/templates/display` (no auth) |
| By category | GET | `/templates/categories` (no auth) |
| Get template | GET | `/templates/:id` (no auth) |
| Clone template | POST | `/templates/:id/clone` |

**WebSocket:** Connect to `/workflow-status` with JWT in `auth.token` or query `token`. Subscribe with `subscribe:execution`, `subscribe:workflow`, or `subscribe:simulation` (body: `{ executionId }`, `{ workflowId }`, `{ simulationId }`). You receive `execution:status`, `execution:node-status`, `workflow:update`, `workflow:history:refresh`, and simulation events. See [SKILL.md](SKILL.md) for full event list and optional client `workflow:update` to push edits.

**Knowledge:** AI generation uses a server-side workflow knowledge base (valid node types and structure). See [SKILL.md – Knowledge](SKILL.md#knowledge-workflow-generation) for how to craft better prompts and which node types exist.

Base URL is your FlowFi backend (e.g. `https://api.flowfi.com`).
