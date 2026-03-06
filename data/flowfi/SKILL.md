---
name: flowfi
description: REST API instructions for FlowFi—authorization, smart accounts, workflows (AI generate, edit, deploy, undeploy, delete, pause, resume, stop), execution (list, start, cancel, events), WebSocket (workflow-status namespace, subscribe execution/workflow/simulation), price (token/USD), templates (list, get, clone), DTO/request/response shapes (pagination, workflow, template, execution), and workflow knowledge base. Use when integrating with the backend API or when the user asks about workflow, execution, real-time, price, templates, DTOs, or auth endpoints.
---

# FlowFi OpenClaw skill

Instructions for the **FlowFi** backend API. Base URL is the backend API root (e.g. `https://api.seimoney.link`). Protected routes use **JWT** via `Authorization: Bearer <token>`.

**Grouped docs** (content split by topic):

| Topic | File |
|-------|------|
| Authorization | [docs/authorization.md](docs/authorization.md) |
| Smart accounts | [docs/smart-accounts.md](docs/smart-accounts.md) |
| AI workflows (generate, suggestions, edit by prompt) | [docs/ai-workflows.md](docs/ai-workflows.md) |
| Workflows (lifecycle, deploy/undeploy/pause/resume/stop/delete, list, draft) | [docs/workflows.md](docs/workflows.md) |
| DTOs & request/response shapes | [docs/dto.md](docs/dto.md) |
| Execution (REST) | [docs/execution.md](docs/execution.md) |
| WebSocket (real-time) | [docs/websocket.md](docs/websocket.md) |
| Price | [docs/price.md](docs/price.md) |
| Templates | [docs/templates.md](docs/templates.md) |
| Endpoint summary table | [docs/summary.md](docs/summary.md) |

See **[docs/README.md](docs/README.md)** for the full index.

**Quick entry points:** Generate workflow → `POST /ai/generate-workflow` (prompt + smartAccountId). Deploy → `POST /workflows/:id/deploy`. List workflows → `GET /workflows`. Real-time → WebSocket namespace `/workflow-status`; subscribe to execution/workflow/simulation.
