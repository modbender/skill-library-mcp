# Summary

| Action                | Method | Endpoint                              |
|-----------------------|--------|----------------------------------------|
| Bearer token          | POST   | `/auth/bearer-token`                   |
| List smart accounts   | GET    | `/smart-accounts`                      |
| Get smart account     | GET    | `/smart-accounts/:id`                  |
| Workflow count        | GET    | `/smart-accounts/:id/workflows/count`  |
| Generate workflow     | POST   | `/ai/generate-workflow`                |
| Get suggestions       | GET    | `/ai/workflow/:id/suggestions`         |
| Edit by prompt        | POST   | `/ai/workflow/:id/prompt`              |
| Deploy                | POST   | `/workflows/:id/deploy`                |
| Undeploy              | POST   | `/workflows/:id/undeploy`              |
| Delete                | DELETE | `/workflows/:id`                      |
| Pause                 | POST   | `/workflows/:id/pause`                |
| Resume                | POST   | `/workflows/:id/resume`                |
| Stop                  | POST   | `/workflows/:id/stop`                 |
| List workflows        | GET    | `/workflows`                          |
| List executions       | GET    | `/executions`                         |
| Start execution       | POST   | `/executions/workflows/:workflowId/start` |
| List workflow runs    | GET    | `/executions/workflows/:workflowId`   |
| Get execution        | GET    | `/executions/:id`                    |
| Cancel execution      | DELETE | `/executions/:id/cancel`              |
| Execution events     | GET    | `/executions/:id/events`             |
| Node events          | GET    | `/executions/:id/events/node/:nodeId` |
| Token price          | GET    | `/price?symbol=BNB` (no auth)         |
| BNB/ETH prices       | GET    | `/price/prices` (no auth)             |
| List templates       | GET    | `/templates` (no auth)                |
| Display info         | GET    | `/templates/display` (no auth)        |
| By category          | GET    | `/templates/categories` (no auth)     |
| Get template         | GET    | `/templates/:id` (no auth)            |
| Clone template       | POST   | `/templates/:id/clone`                 |

**WebSocket:** Connect to namespace `/workflow-status` with JWT; use `subscribe:execution`, `subscribe:workflow`, `subscribe:simulation` (and unsubscribe) for real-time execution/workflow/simulation updates.

**Knowledge:** Workflow AI uses a server-side knowledge base (valid node types and structure); see [Knowledge](knowledge.md). No API to fetch it. **Templates** are pre-built workflows (same structure); list via `GET /templates` or `GET /templates/categories`; clone via `POST /templates/:id/clone` to create a draft.

Protected REST routes require `Authorization: Bearer <jwt>`. User is inferred from JWT; workflow and smart-account ownership is enforced by `smartAccountAddress` / `userId`.
