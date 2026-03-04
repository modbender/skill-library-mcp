# WebSocket (real-time)

**Namespace:** `/workflow-status` (e.g. `wss://api.example.com/workflow-status`).

**Authentication:** Connect with JWT in handshake:
- `auth.token` or query `token`. Invalid/missing token disconnects.

**Subscribe (client → server):**

| Message (event) | Body | Effect |
|-----------------|------|--------|
| `subscribe:execution` | `{ executionId: string }` | Join room for this execution; receive `execution:status`, `execution:node-status`. |
| `unsubscribe:execution` | `{ executionId?: string }` | Leave room. |
| `subscribe:workflow` | `{ workflowId: string }` | Join room for workflow; receive `workflow:update`, `workflow:history:refresh`. |
| `unsubscribe:workflow` | `{ workflowId?: string }` | Leave room. |
| `subscribe:simulation` | `{ simulationId: string }` | Join room for simulation; receive `simulation:status`, `simulation:node-status`. |
| `unsubscribe:simulation` | `{ simulationId?: string }` | Leave room. |

**Server → client events:**

| Event | When | Payload |
|-------|------|---------|
| `execution:status` | Execution state changes | `{ executionId, status, progress?, timestamp?, ... }` |
| `execution:node-status` | Node starts/completes in a run | `{ executionId, nodeId, ... }` |
| `workflow:update` | Workflow nodes/connections/name/variables updated (e.g. after edit) | `{ type: 'updated', workflow, changes, timestamp }` |
| `workflow:history:refresh` | Execution list for workflow changed (e.g. new run started/finished) | `{ executionId?, reason? }` |
| `simulation:status` | Simulation state | `{ simulationId, ... }` |
| `simulation:node-status` | Simulation node step | `{ simulationId, nodeId, ... }` |

**Client can push workflow edits over WebSocket:**  
Send `workflow:update` with body `{ workflowId, update: { nodes?, connections?, name?, variables? } }`. Server persists and broadcasts to other subscribers; response `{ success, message? }` or `{ success: false, error }`.
