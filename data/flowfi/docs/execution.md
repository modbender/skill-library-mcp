# Execution (REST)

Workflow runs (executions) and their events. All require JWT.

**List all executions for the user:** **GET** `/executions`  
Query: `page`, `limit`, `sortBy`, `sortOrder`, `status`.

**Start a run:** **POST** `/executions/workflows/:workflowId/start`  
Starts one execution of an **active** workflow. Returns the created execution.

**List executions for a workflow:** **GET** `/executions/workflows/:workflowId`  
Query: `page`, `limit`, `sortBy`, `sortOrder`, `search`, `status`.

**Get one execution:** **GET** `/executions/:id`

**Cancel a running execution:** **DELETE** `/executions/:id/cancel`

**Get events for an execution:** **GET** `/executions/:id/events`  
Query: `page`, `limit`, `sortBy`, `sortOrder`, `search`, `eventType`, `level`. Returns execution events (e.g. node start/complete, errors).

**Get events for a specific node in an execution:** **GET** `/executions/:id/events/node/:nodeId`
