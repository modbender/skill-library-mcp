# Ansible Coordination Mesh — Full Design Specification

**Status**: Active — Draft
**Author**: Architect (Aria) + Claude
**Date**: 2026-02-17
**Related**: [ansible-coding-skill-spec.md](./ansible-coding-skill-spec.md)

---

## Overview

The ansible coordination mesh is the inter-agent task delegation layer for OpenClaw. It enables agents to declare work requirements by capability, discover executors, delegate tasks, and receive structured replies — all through shared Yjs state synchronized across gateways.

The mental model is a **tool call analogy**: `requires` routing works like a tool call. The requester declares what it needs, the dispatcher resolves who can do it, and a result comes back. The requester never knows or cares which agent executed. Skills are tool definitions. Capability registration is tool registration. Stop-hook reply is the return value.

---

## Skill Naming and Structure

### Base Protocol Skill: `ansible-comms`

`ansible-comms` is the base protocol skill loaded on **all** agents. It teaches:

- The delegation pattern — when to delegate vs. do work inline
- How to format task proposals (schema, required fields)
- How to read and interpret replies
- How to claim and close tasks as an executor

**Decision rule injected by `ansible-comms`**:
> "If a registered capability covers the work you are about to do, delegate it — do not do it inline."

**Executor rule injected by `ansible-comms`**:
> "If you see an unclaimed task in your inbox matching your registered capability, claim it immediately."

### Task-Type Skills: Capability Contracts

Task-type skills (`ansible-coding`, `ansible-research`, `ansible-ops`) sit on top of `ansible-comms`. Each one is a **capability contract** that defines:

- Input schema (what the task must contain)
- Output schema (what the result must contain)
- Executor behavior (how the agent processes the task)

Any agent that loads a task-type skill automatically:
1. Calls `ansible_register_capability` to advertise the capability in the shared agents map
2. Becomes an eligible executor for tasks requiring that capability

Capability registration is a side effect of skill loading — no manual configuration required.

---

## Capability-Based Routing

Requesters declare `requires` instead of naming specific agents in `to_agents`:

```typescript
interface TaskProposal {
  id: string;                    // UUID, requester-generated
  from_agent: string;            // requester's agent ID
  requires: string;              // capability name, e.g. "ansible-coding"
  conversation_id: string;       // thread ID, propagated from parent or new
  corr: string;                  // correlation ID for this request/reply pair
  payload: Record<string, any>;  // capability-specific input (per task-type skill schema)
  status: "pending";
  to_agents?: string[];          // NOT set by requester — filled by dispatcher
  delivery?: DeliveryRecord;     // NOT set by requester — filled by dispatcher
}
```

The dispatcher resolves `requires` → `to_agents` by querying the live capability registry. The requester never addresses an agent directly.

---

## Dispatcher Write-Back

When the dispatcher routes a task by capability, it **writes `to_agents` and `delivery` back into the Yjs task record** before injecting the task into the executor's agent session.

```typescript
interface DeliveryRecord {
  dispatched_at: string;         // ISO timestamp
  dispatched_by: string;         // gateway ID that performed routing
  resolved_capability: string;   // capability name that matched
  resolved_agent: string;        // agent ID selected as executor
}
```

**Why write-back matters:**

1. **Visibility** — Routing decisions are stored in shared state. Any gateway or observer can see who was assigned what and why.
2. **Idempotent re-delivery** — If a gateway reconnects, it reads `to_agents` from Yjs and skips re-routing tasks that already have it set. No double-routing.
3. **Conflict prevention** — Only one gateway writes `to_agents` for a given task. Once written, other gateways treat the task as already dispatched.

Write-back uses a Yjs conditional transaction: set `to_agents` only if it is currently absent. This is the idempotency gate.

---

## Agent Inbox Model

An agent's inbox is all tasks matching:

```typescript
function isInInbox(task: Task, myId: string): boolean {
  return (
    (task.to_agents?.includes(myId) || task.claimedBy_agent === myId) &&
    task.status !== "completed"
  );
}
```

No capability matching at read time. The dispatcher already resolved routing. The agent just works its queue.

---

## Task Close-Out

Single tool call to complete a task:

```typescript
ansible_close_task({
  id: string;
  result: Record<string, any>;
})
```

The plugin handles everything else:
1. Marks `task.status = "completed"` in Yjs
2. Writes `task.result = result` in Yjs
3. Sends a reply message to `from_agent` using the same `corr` and `conversation_id` from the original task

The agent never handles addressing. Routing information is already in the task record.

---

## Threading Model

```typescript
interface ThreadIds {
  conversation_id: string;  // tracks the whole thread (request + all replies)
  corr: string;             // pairs a specific request/reply
}
```

- `conversation_id`: Assigned by the original requester at thread start. Propagated unchanged through all tasks and replies in that thread.
- `corr`: Unique per request/reply pair. The reply carries the same `corr` as the request. Allows the requester to match a reply to the specific task it sent.

Both values propagate automatically through `ansible_close_task`. The agent never sets them on replies.

---

## Tool Inventory

### New Tools Required

#### `ansible_my_tasks`
Returns the agent's current inbox.

```typescript
// Input: { status_filter?: "pending" | "claimed" | "in_progress" | "all" }
// Output:
interface MyTasksResult {
  tasks: Task[];   // tasks where to_agents.includes(myId) or claimedBy_agent === myId, status != completed
}
```

#### `ansible_close_task`
Marks a task complete, writes result, sends reply.

```typescript
interface CloseTaskInput {
  id: string;
  status: "completed" | "failed";
  result?: Record<string, any>;
  error?: string;
}
// Output: { ok: boolean, reply_message_id: string }
```

#### `ansible_list_capabilities`
Returns currently registered capabilities from the agents map.

```typescript
// Output:
interface CapabilitiesResult {
  capabilities: {
    capability: string;
    agent_id: string;
    agent_name: string;
    gateway_id: string;
  }[];
}
```

#### `ansible_register_capability`
Called when a task-type skill loads. Writes to `AgentRecord.capabilities[]` in the Yjs agents map. Idempotent.

```typescript
interface RegisterCapabilityInput {
  capabilities: string[];
}
// Output: { ok: boolean, agent_id: string, capabilities: string[] }
```

#### `ansible_delegate_task` (update to existing)
Add `requires` field. When set and `to_agents` is empty, dispatcher resolves routing. When `to_agents` is explicit, direct addressing is used as before.

---

## Capability Registry

Capabilities are stored in the Yjs agents map on each `AgentRecord`:

```typescript
interface AgentRecord {
  id: string;
  name: string;
  gateway_id: string;
  status: "online" | "offline";
  capabilities: string[];      // e.g. ["ansible-coding", "ansible-comms"]
  last_seen: string;
}
```

All nodes replicate the agents map via Yjs CRDT sync. There is no central registry server — it is emergent from CRDT replication.

When a skill is unloaded or an agent goes offline, its capabilities must be cleared from the registry. Stale capabilities cause dispatch failures.

---

## Context Injection at Agent Start

When an agent session starts, the gateway injects a context block containing:

- The agent's own ID and name
- Available capabilities (from the live agents map at connection time)
- Loaded skills

This ensures the agent knows what capabilities are available without a tool call at startup. The agent can call `ansible_list_capabilities` at any time for a fresh read.

---

## Automatic Invocation

### Requester Side

`ansible-comms` SKILL.md contains:
> Before beginning work that falls under a registered capability, call `ansible_list_capabilities`. If a capability matches, create a task proposal using the matching task-type skill's input schema and submit it. Do not perform the work inline.

### Executor Side

`ansible-comms` SKILL.md contains:
> At the start of each reasoning step, call `ansible_my_tasks`. If unclaimed tasks are present matching your registered capability, claim the first one and process it before doing any other work. Use `ansible_close_task` to complete and reply.

---

## Agent Topology

```
mac-jane gateway
├── architect (Aria)         — loads: ansible-comms
├── mac-jane (Jane)          — loads: ansible-comms, ansible-coding, ansible-ops
└── librarian (Astrid)       — loads: ansible-comms, ansible-research

vps-jane gateway
├── vps-jane (Jane)          — loads: ansible-comms, ansible-coding, ansible-ops
└── chief-of-staff (Beacon)  — loads: ansible-comms

External (CLI poll only)
├── claude
└── codex
```

External agents participate via CLI polling. The dispatcher handles external agents by writing the task to Yjs and allowing the CLI poller to pick it up — they are never session-injected.

---

## Dispatcher Algorithm

```
On new task in Yjs tasks map with status = "pending" and no to_agents:

1. Read task.requires
2. Read agents map — find online agents where capabilities includes task.requires
3. Select executor (round-robin or load-based — TBD)
4. Conditional Yjs transaction:
   IF task.to_agents is still absent:
     SET task.to_agents = [selected_agent_id]
     SET task.delivery = { dispatched_at, dispatched_by, resolved_capability, resolved_agent }
     SET task.status = "claimed"
     SET task.claimedBy_agent = selected_agent_id
5. Inject task into executor's agent session

If no capable agent is online: task remains pending.
When a capable agent comes online and registers, dispatcher re-evaluates pending tasks.
```

---

## Implementation Notes for Aria

1. **Start with tools**: Implement `ansible_my_tasks`, `ansible_close_task`, `ansible_list_capabilities`, `ansible_register_capability` before writing any SKILL.md content.
2. **Write-back transaction**: The idempotency gate (conditional set on `to_agents`) is critical. Implement before multi-gateway testing.
3. **SKILL.md content**: `ansible-comms` is the most important document — it drives automatic invocation on both sides. Draft after tools are working.
4. **Task-type skills**: Each SKILL.md should contain only the capability contract. Protocol mechanics live in `ansible-comms`.
5. **Capability cleanup**: Define the offline/unload cleanup path before shipping — stale capabilities cause dispatch failures.

---

*End of specification.*
