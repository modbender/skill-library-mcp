# CopilotKit Agent Patterns

**Version 2.0.0**  
CopilotKit  
February 2026

> **Note:**  
> This document is mainly for agents and LLMs to follow when maintaining,  
> generating, or refactoring CopilotKit codebases. Humans  
> may also find it useful, but guidance here is optimized for automation  
> and consistency by AI-assisted workflows.

---

## Abstract

Architecture and implementation patterns for building AI agents that integrate with CopilotKit via the AG-UI protocol. Contains 20 rules covering agent design with BuiltInAgent (@copilotkit/runtime/v2), event streaming, state synchronization, human-in-the-loop checkpoints, and generative UI emission. Applies to both BuiltInAgent and custom agent implementations.

---

## Table of Contents

1. [Agent Architecture](#1-agent-architecture) — **CRITICAL**
   - 1.1 [Configure MCP Servers for External Tools](#11-configure-mcp-servers-for-external-tools)
   - 1.2 [Set maxSteps to Prevent Infinite Loops](#12-set-maxsteps-to-prevent-infinite-loops)
   - 1.3 [Use BuiltInAgent for Direct-to-LLM Agents](#13-use-builtinagent-for-direct-to-llm-agents)
   - 1.4 [Use Provider/Model String Format for Model Selection](#14-use-providermodel-string-format-for-model-selection)
2. [AG-UI Protocol](#2-ag-ui-protocol) — **HIGH**
   - 2.1 [Always Emit Error Events on Failure](#21-always-emit-error-events-on-failure)
   - 2.2 [Emit AG-UI Events in Correct Order](#22-emit-ag-ui-events-in-correct-order)
   - 2.3 [Emit STATE_SNAPSHOT for Frontend Sync](#23-emit-state_snapshot-for-frontend-sync)
   - 2.4 [Follow Tool Call Event Lifecycle](#24-follow-tool-call-event-lifecycle)
   - 2.5 [Stream Text Incrementally](#25-stream-text-incrementally)
3. [State Management](#3-state-management) — **HIGH**
   - 3.1 [Emit State Snapshots at Meaningful Checkpoints](#31-emit-state-snapshots-at-meaningful-checkpoints)
   - 3.2 [Handle Bidirectional State Conflicts](#32-handle-bidirectional-state-conflicts)
   - 3.3 [Isolate State Per Thread](#33-isolate-state-per-thread)
   - 3.4 [Keep State Snapshots Minimal and Serializable](#34-keep-state-snapshots-minimal-and-serializable)
4. [Human-in-the-Loop](#4-human-in-the-loop) — **MEDIUM**
   - 4.1 [Include Context for User Decisions](#41-include-context-for-user-decisions)
   - 4.2 [Preserve State When Resuming After Approval](#42-preserve-state-when-resuming-after-approval)
   - 4.3 [Set Timeouts with Fallback Behavior](#43-set-timeouts-with-fallback-behavior)
   - 4.4 [Use Tool Calls for Approval Gates](#44-use-tool-calls-for-approval-gates)
5. [Generative UI Emission](#5-generative-ui-emission) — **MEDIUM**
   - 5.1 [Emit Tool Calls That Map to useRenderTool](#51-emit-tool-calls-that-map-to-userendertool)
   - 5.2 [Stream Tool Args for Real-Time UI](#52-stream-tool-args-for-real-time-ui)
   - 5.3 [Use Text Messages for Status Updates](#53-use-text-messages-for-status-updates)

---

## 1. Agent Architecture

**Impact: CRITICAL**

Fundamental patterns for structuring agents that integrate with CopilotKit. Correct architecture prevents infinite loops, model misconfiguration, and tool registration failures.

### 1.1 Configure MCP Servers for External Tools

**Impact: MEDIUM (MCP extends agent capabilities without custom tool implementation)**

## Configure MCP Servers for External Tools

Use MCP (Model Context Protocol) server configuration to give agents access to external tools and data sources. CopilotKit supports MCP endpoints on the runtime, avoiding the need to reimplement tool integrations that already exist as MCP servers.

**Incorrect (reimplementing existing tool integrations):**

```typescript
import { CopilotRuntime } from "@copilotkit/runtime"

const runtime = new CopilotRuntime()
// Manually reimplementing file read, search, etc. as custom tools
```

**Correct (MCP endpoints on the runtime):**

```typescript
import { CopilotRuntime } from "@copilotkit/runtime"

const runtime = new CopilotRuntime({
  mcpEndpoints: [
    {
      endpoint: "https://mcp-server.example.com/sse",
      apiKey: process.env.MCP_API_KEY,
    },
  ],
})
```

On the frontend, MCP endpoints can also be configured via the `CopilotKit` provider:

```tsx
<CopilotKit
  runtimeUrl="/api/copilotkit"
  mcpEndpoints={[
    { endpoint: "https://mcp-server.example.com/sse" },
  ]}
>
  <MyApp />
</CopilotKit>
```

Reference: [CopilotRuntime](https://docs.copilotkit.ai/reference/v1/classes/CopilotRuntime)

### 1.2 Set maxSteps to Prevent Infinite Loops

**Impact: CRITICAL (unbounded agents can loop indefinitely, consuming tokens and time)**

## Set maxSteps to Prevent Infinite Loops

Always set `maxSteps` on agents to limit the number of tool-call cycles. Without a limit, an agent that repeatedly calls tools without converging on an answer will loop indefinitely, consuming tokens and blocking the user.

**Incorrect (no step limit, potential infinite loop):**

```typescript
const agent = new BuiltInAgent({
  name: "data_processor",
  tools: [queryTool, transformTool, validateTool],
})
```

**Correct (step limit prevents runaway execution):**

```typescript
const agent = new BuiltInAgent({
  name: "data_processor",
  tools: [queryTool, transformTool, validateTool],
  maxSteps: 10,
})
```

Choose a `maxSteps` value based on the expected complexity of your agent's workflow. Simple Q&A agents may need 3-5 steps; complex multi-tool workflows may need 10-20.

Reference: [BuiltInAgent](https://docs.copilotkit.ai/reference/runtime/built-in-agent)

### 1.3 Use BuiltInAgent for Direct-to-LLM Agents

**Impact: CRITICAL (BuiltInAgent handles AG-UI protocol automatically)**

## Use BuiltInAgent for Direct-to-LLM Agents

For agents that primarily need tool-calling capabilities without complex state graphs, use `BuiltInAgent` from `@copilotkit/runtime/v2`. It handles AG-UI protocol event emission, message management, and streaming automatically. Only reach for custom agents or LangGraph when you need multi-step workflows or complex state.

**Incorrect (manual AG-UI event handling for a simple agent):**

```typescript
import { Agent } from "@ag-ui/core"

class MyAgent extends Agent {
  async run(input: RunInput) {
    const stream = new EventStream()
    stream.emit({ type: "RUN_STARTED" })
    stream.emit({ type: "TEXT_MESSAGE_START", messageId: "1" })
    // ... 50+ lines of manual event handling
    return stream
  }
}
```

**Correct (BuiltInAgent from v2):**

```typescript
import { BuiltInAgent } from "@copilotkit/runtime/v2"
import { z } from "zod"

const agent = new BuiltInAgent({
  name: "researcher",
  description: "Researches topics and provides summaries",
  model: "openai/gpt-4o",
  tools: [
    {
      name: "search",
      description: "Search for information on a topic",
      parameters: z.object({ query: z.string() }),
      handler: async ({ query }) => {
        return await searchApi(query)
      },
    },
  ],
})
```

`BuiltInAgent` replaces the older adapter pattern (`OpenAIAdapter`, `AnthropicAdapter`) with a unified interface that uses the `"provider/model"` string format.

Reference: [BuiltInAgent](https://docs.copilotkit.ai/guides/self-hosting)

### 1.4 Use Provider/Model String Format for Model Selection

**Impact: HIGH (hardcoded model names break when switching providers)**

## Use Provider/Model String Format for Model Selection

Use the `"provider/model"` string format when specifying models for `BuiltInAgent`. This allows swapping between OpenAI, Anthropic, or other providers without changing the underlying agent architecture. Use environment variables for flexibility across environments.

**Incorrect (ambiguous model name without provider):**

```typescript
import { BuiltInAgent } from "@copilotkit/runtime/v2"

const agent = new BuiltInAgent({
  name: "writer",
  model: "gpt-4o",
})
```

**Correct (explicit provider/model format):**

```typescript
import { BuiltInAgent } from "@copilotkit/runtime/v2"

const agent = new BuiltInAgent({
  name: "writer",
  model: process.env.LLM_MODEL || "openai/gpt-4o",
})
```

**Correct (environment-based model selection):**

```typescript
import { BuiltInAgent } from "@copilotkit/runtime/v2"

const MODEL_MAP: Record<string, string> = {
  fast: "openai/gpt-4o-mini",
  powerful: "openai/gpt-4o",
  anthropic: "anthropic/claude-sonnet-4-20250514",
}

const modelKey = process.env.MODEL_TIER || "powerful"

const agent = new BuiltInAgent({
  name: "writer",
  model: MODEL_MAP[modelKey],
})
```

Reference: [Self Hosting](https://docs.copilotkit.ai/guides/self-hosting)

## 2. AG-UI Protocol

**Impact: HIGH**

Rules for correctly implementing the AG-UI event protocol. Incorrect event ordering or missing events causes broken streaming, lost messages, or UI desync.

### 2.1 Always Emit Error Events on Failure

**Impact: HIGH (silent failures leave the frontend hanging with no feedback)**

## Always Emit Error Events on Failure

When an agent encounters an error, always emit a `RUN_ERROR` event before stopping. Without it, the frontend hangs indefinitely waiting for `RUN_FINISHED`, and the user sees no feedback about what went wrong.

**Incorrect (error swallowed, frontend hangs):**

```typescript
async function* handleRun(input: RunInput) {
  yield { type: "RUN_STARTED" }
  try {
    const result = await riskyOperation()
    yield { type: "TEXT_MESSAGE_START", messageId: "1", role: "assistant" }
    yield { type: "TEXT_MESSAGE_CONTENT", messageId: "1", delta: result }
    yield { type: "TEXT_MESSAGE_END", messageId: "1" }
  } catch (error) {
    console.error(error)
    // Frontend never knows the run failed
  }
}
```

**Correct (error event notifies frontend):**

```typescript
async function* handleRun(input: RunInput) {
  yield { type: "RUN_STARTED" }
  try {
    const result = await riskyOperation()
    yield { type: "TEXT_MESSAGE_START", messageId: "1", role: "assistant" }
    yield { type: "TEXT_MESSAGE_CONTENT", messageId: "1", delta: result }
    yield { type: "TEXT_MESSAGE_END", messageId: "1" }
    yield { type: "RUN_FINISHED" }
  } catch (error) {
    yield { type: "RUN_ERROR", message: error.message, code: "OPERATION_FAILED" }
  }
}
```

Reference: [AG-UI Protocol](https://docs.ag-ui.com/concepts/events)

### 2.2 Emit AG-UI Events in Correct Order

**Impact: CRITICAL (wrong event order causes broken streaming and lost messages)**

## Emit AG-UI Events in Correct Order

AG-UI events must follow a strict ordering: `RUN_STARTED` -> content events -> `RUN_FINISHED`. Text messages require `TEXT_MESSAGE_START` -> `TEXT_MESSAGE_CONTENT` (one or more) -> `TEXT_MESSAGE_END`. Out-of-order events cause the frontend to drop messages or display corrupted content.

**Incorrect (missing start event, content before start):**

```typescript
async function* handleRun(input: RunInput) {
  yield { type: "TEXT_MESSAGE_CONTENT", delta: "Hello" }
  yield { type: "TEXT_MESSAGE_END", messageId: "1" }
  yield { type: "RUN_FINISHED" }
}
```

**Correct (proper event ordering):**

```typescript
async function* handleRun(input: RunInput) {
  yield { type: "RUN_STARTED" }
  yield { type: "TEXT_MESSAGE_START", messageId: "1", role: "assistant" }
  yield { type: "TEXT_MESSAGE_CONTENT", messageId: "1", delta: "Hello" }
  yield { type: "TEXT_MESSAGE_CONTENT", messageId: "1", delta: " world" }
  yield { type: "TEXT_MESSAGE_END", messageId: "1" }
  yield { type: "RUN_FINISHED" }
}
```

Reference: [AG-UI Protocol](https://docs.ag-ui.com/concepts/events)

### 2.3 Emit STATE_SNAPSHOT for Frontend Sync

**Impact: HIGH (without snapshots, frontend state drifts from agent state)**

## Emit STATE_SNAPSHOT for Frontend Sync

Emit `STATE_SNAPSHOT` events to synchronize agent state with the frontend. The frontend uses these snapshots to update shared state via `useAgent`. Without them, the UI shows stale data that doesn't reflect agent progress.

**Incorrect (no state snapshots, frontend shows stale data):**

```typescript
async function* handleRun(input: RunInput) {
  yield { type: "RUN_STARTED" }
  const results = await performResearch(input.query)
  // Frontend never sees the results until run finishes
  yield { type: "TEXT_MESSAGE_START", messageId: "1", role: "assistant" }
  yield { type: "TEXT_MESSAGE_CONTENT", messageId: "1", delta: "Done researching." }
  yield { type: "TEXT_MESSAGE_END", messageId: "1" }
  yield { type: "RUN_FINISHED" }
}
```

**Correct (state snapshot keeps frontend in sync):**

```typescript
async function* handleRun(input: RunInput) {
  yield { type: "RUN_STARTED" }
  yield { type: "STATE_SNAPSHOT", snapshot: { status: "researching", results: [] } }

  const results = await performResearch(input.query)
  yield { type: "STATE_SNAPSHOT", snapshot: { status: "complete", results } }

  yield { type: "TEXT_MESSAGE_START", messageId: "1", role: "assistant" }
  yield { type: "TEXT_MESSAGE_CONTENT", messageId: "1", delta: `Found ${results.length} results.` }
  yield { type: "TEXT_MESSAGE_END", messageId: "1" }
  yield { type: "RUN_FINISHED" }
}
```

Reference: [AG-UI Protocol](https://docs.ag-ui.com/concepts/events)

### 2.4 Follow Tool Call Event Lifecycle

**Impact: HIGH (incomplete lifecycle causes frontend to hang or miss results)**

## Follow Tool Call Event Lifecycle

Tool calls require a complete event lifecycle: `TOOL_CALL_START` -> `TOOL_CALL_ARGS` (streamed) -> `TOOL_CALL_END`. Missing any step causes the frontend's `useRenderTool` to hang in an incorrect status or miss the tool call entirely.

**Incorrect (missing TOOL_CALL_END, frontend stays in "executing"):**

```typescript
async function* handleToolCall(tool: string, args: object) {
  yield { type: "TOOL_CALL_START", toolCallId: "tc_1", toolName: tool }
  yield { type: "TOOL_CALL_ARGS", toolCallId: "tc_1", delta: JSON.stringify(args) }
  // Missing TOOL_CALL_END
}
```

**Correct (complete tool call lifecycle):**

```typescript
async function* handleToolCall(tool: string, args: object) {
  yield { type: "TOOL_CALL_START", toolCallId: "tc_1", toolName: tool }
  yield { type: "TOOL_CALL_ARGS", toolCallId: "tc_1", delta: JSON.stringify(args) }
  yield { type: "TOOL_CALL_END", toolCallId: "tc_1" }
}
```

Reference: [AG-UI Protocol](https://docs.ag-ui.com/concepts/events)

### 2.5 Stream Text Incrementally

**Impact: HIGH (sending entire response at once defeats streaming UX)**

## Stream Text Incrementally

Emit `TEXT_MESSAGE_CONTENT` events with small deltas as they become available, rather than buffering the entire response and sending it at once. Incremental streaming gives users real-time feedback and perceived performance.

**Incorrect (buffer entire response, send at once):**

```typescript
async function* handleRun(input: RunInput) {
  yield { type: "RUN_STARTED" }
  yield { type: "TEXT_MESSAGE_START", messageId: "1", role: "assistant" }

  const fullResponse = await generateFullResponse(input)
  yield { type: "TEXT_MESSAGE_CONTENT", messageId: "1", delta: fullResponse }

  yield { type: "TEXT_MESSAGE_END", messageId: "1" }
  yield { type: "RUN_FINISHED" }
}
```

**Correct (stream incrementally as tokens arrive):**

```typescript
async function* handleRun(input: RunInput) {
  yield { type: "RUN_STARTED" }
  yield { type: "TEXT_MESSAGE_START", messageId: "1", role: "assistant" }

  for await (const chunk of streamResponse(input)) {
    yield { type: "TEXT_MESSAGE_CONTENT", messageId: "1", delta: chunk }
  }

  yield { type: "TEXT_MESSAGE_END", messageId: "1" }
  yield { type: "RUN_FINISHED" }
}
```

Reference: [AG-UI Protocol](https://docs.ag-ui.com/concepts/events)

## 3. State Management

**Impact: HIGH**

Patterns for synchronizing state between agent and frontend. Bidirectional state sync is CopilotKit's core differentiator.

### 3.1 Emit State Snapshots at Meaningful Checkpoints

**Impact: HIGH (too frequent snapshots waste bandwidth; too rare loses real-time feel)**

## Emit State Snapshots at Meaningful Checkpoints

Emit `STATE_SNAPSHOT` events at meaningful points in the agent workflow — after completing a step, receiving results, or changing status. Avoid emitting on every token or loop iteration, which wastes bandwidth and causes excessive re-renders.

**Incorrect (snapshot on every iteration, causes re-render storms):**

```typescript
async function* processItems(items: string[]) {
  for (let i = 0; i < items.length; i++) {
    const result = await processItem(items[i])
    yield { type: "STATE_SNAPSHOT", snapshot: { processed: i + 1, total: items.length, results: [result] } }
  }
}
```

**Correct (snapshots at meaningful checkpoints):**

```typescript
async function* processItems(items: string[]) {
  yield { type: "STATE_SNAPSHOT", snapshot: { phase: "processing", total: items.length, processed: 0 } }

  const results = []
  for (const item of items) {
    results.push(await processItem(item))
  }

  yield { type: "STATE_SNAPSHOT", snapshot: { phase: "complete", total: items.length, processed: items.length, results } }
}
```

Reference: [AG-UI Protocol](https://docs.ag-ui.com/concepts/events)

### 3.2 Handle Bidirectional State Conflicts

**Impact: MEDIUM (unhandled conflicts cause data loss or UI flicker)**

## Handle Bidirectional State Conflicts

CopilotKit supports bidirectional state sync — both the frontend and agent can modify shared state. When both sides update simultaneously, implement conflict resolution logic to prevent data loss.

**Incorrect (agent blindly overwrites frontend state):**

```typescript
async function* updateTasks(agentTasks: Task[]) {
  yield {
    type: "STATE_SNAPSHOT",
    snapshot: { tasks: agentTasks },
  }
}
```

**Correct (merge strategy preserves both-side changes):**

```typescript
async function* updateTasks(agentTasks: Task[], frontendState: AppState) {
  const mergedTasks = agentTasks.map(agentTask => {
    const frontendTask = frontendState.tasks.find(t => t.id === agentTask.id)
    if (frontendTask && frontendTask.updatedAt > agentTask.updatedAt) {
      return frontendTask
    }
    return agentTask
  })

  yield {
    type: "STATE_SNAPSHOT",
    snapshot: { tasks: mergedTasks },
  }
}
```

Reference: [State Management](https://docs.copilotkit.ai/guides/state-management)

### 3.3 Isolate State Per Thread

**Impact: HIGH (shared state across threads causes cross-user data leaks)**

## Isolate State Per Thread

Each conversation thread must have its own isolated state. Sharing state across threads causes one user's data to leak into another user's conversation, especially in multi-tenant environments.

**Incorrect (global state shared across all threads):**

```typescript
const globalState = { results: [], status: "idle" }

class ResearchAgent {
  async run(input: RunInput) {
    globalState.status = "running"
    globalState.results = await search(input.query)
  }
}
```

**Correct (state isolated per thread):**

```typescript
class ResearchAgent {
  async run(input: RunInput) {
    const threadState = {
      results: [] as SearchResult[],
      status: "running" as const,
    }

    threadState.results = await search(input.query)
    threadState.status = "complete"

    yield { type: "STATE_SNAPSHOT", snapshot: threadState }
  }
}
```

Reference: [Thread Management](https://docs.copilotkit.ai/guides/threads)

### 3.4 Keep State Snapshots Minimal and Serializable

**Impact: MEDIUM (large or non-serializable state causes transmission failures)**

## Keep State Snapshots Minimal and Serializable

State snapshots are serialized as JSON and sent over the wire. Keep them minimal — include only the state the frontend needs to render UI. Avoid including non-serializable values (functions, class instances) or large datasets.

**Incorrect (non-serializable and bloated state):**

```typescript
yield {
  type: "STATE_SNAPSHOT",
  snapshot: {
    dbConnection: pool,
    fullDataset: await fetchAllRecords(),
    processFn: (x: any) => x.toString(),
    internalBuffer: Buffer.alloc(1024),
  },
}
```

**Correct (minimal, serializable state):**

```typescript
yield {
  type: "STATE_SNAPSHOT",
  snapshot: {
    recordCount: 1500,
    processedCount: 750,
    status: "processing",
    lastProcessedId: "rec_abc123",
  },
}
```

Reference: [AG-UI Protocol](https://docs.ag-ui.com/concepts/events)

## 4. Human-in-the-Loop

**Impact: MEDIUM**

Patterns for pausing agent execution to request user input, approval, or corrections before continuing.

### 4.1 Include Context for User Decisions

**Impact: LOW (users can't make informed decisions without sufficient context)**

## Include Context for User Decisions

When requesting human approval or input, include enough context in the tool call args for the user to make an informed decision. Don't ask "Proceed?" — tell them exactly what will happen.

**Incorrect (vague approval request):**

```typescript
yield {
  type: "TOOL_CALL_ARGS",
  toolCallId: "tc_1",
  delta: JSON.stringify({ message: "Proceed with the operation?" }),
}
```

**Correct (detailed context for informed decision):**

```typescript
yield {
  type: "TOOL_CALL_ARGS",
  toolCallId: "tc_1",
  delta: JSON.stringify({
    action: "send_emails",
    recipientCount: 150,
    subject: "Q1 Report Update",
    estimatedCost: "$0.45",
    message: "Send 150 emails with subject 'Q1 Report Update'? Estimated cost: $0.45.",
  }),
}
```

Reference: [Human-in-the-Loop](https://docs.copilotkit.ai/guides/human-in-the-loop)

### 4.2 Preserve State When Resuming After Approval

**Impact: MEDIUM (lost state after resume forces the agent to redo work)**

## Preserve State When Resuming After Approval

When an agent pauses for human input and then resumes, ensure all intermediate state is preserved. Losing state forces the agent to redo expensive computations, wasting time and tokens.

**Incorrect (state lost after human approval pause):**

```typescript
async function* handleRun(input: RunInput) {
  const analysis = await performExpensiveAnalysis(input.data)
  yield { type: "TOOL_CALL_START", toolCallId: "tc_1", toolName: "confirm_action" }
  // ... wait for approval
  // After resume: analysis variable is gone, must recompute
}
```

**Correct (state persisted across pause/resume):**

```typescript
async function* handleRun(input: RunInput) {
  const analysis = await performExpensiveAnalysis(input.data)

  yield {
    type: "STATE_SNAPSHOT",
    snapshot: { analysis, phase: "awaiting_approval" },
  }

  yield { type: "TOOL_CALL_START", toolCallId: "tc_1", toolName: "confirm_action" }
  yield { type: "TOOL_CALL_ARGS", toolCallId: "tc_1", delta: JSON.stringify({ summary: analysis.summary }) }
  yield { type: "TOOL_CALL_END", toolCallId: "tc_1" }
}
```

Reference: [Human-in-the-Loop](https://docs.copilotkit.ai/guides/human-in-the-loop)

### 4.3 Set Timeouts with Fallback Behavior

**Impact: MEDIUM (agents waiting forever for human input block resources indefinitely)**

## Set Timeouts with Fallback Behavior

When waiting for human input, always set a timeout with fallback behavior. Without it, an unresponsive user causes the agent to hang indefinitely, consuming server resources and blocking the thread.

**Incorrect (wait forever for human response):**

```typescript
const approval = await waitForHumanApproval(toolCallId)
if (approval.approved) {
  await deleteRecords()
}
```

**Correct (timeout with safe fallback):**

```typescript
const approval = await Promise.race([
  waitForHumanApproval(toolCallId),
  timeout(60_000).then(() => ({ approved: false, reason: "timeout" })),
])

if (approval.approved) {
  await deleteRecords()
} else {
  yield { type: "TEXT_MESSAGE_START", messageId: "m1", role: "assistant" }
  yield { type: "TEXT_MESSAGE_CONTENT", messageId: "m1", delta: "Action timed out. No changes were made." }
  yield { type: "TEXT_MESSAGE_END", messageId: "m1" }
}
```

Reference: [Human-in-the-Loop](https://docs.copilotkit.ai/guides/human-in-the-loop)

### 4.4 Use Tool Calls for Approval Gates

**Impact: MEDIUM (custom events for approvals break the standard AG-UI flow)**

## Use Tool Calls for Approval Gates

Implement human-in-the-loop approval gates as tool calls that the frontend renders with `useRenderTool`, rather than custom event types. This keeps the approval flow within the standard AG-UI protocol and lets you use CopilotKit's built-in HITL handling.

**Incorrect (custom event type for approval):**

```typescript
yield { type: "CUSTOM_EVENT", eventType: "APPROVAL_NEEDED", data: { action: "delete_records", count: 50 } }
// Frontend has no standard way to handle this
```

**Correct (tool call triggers frontend approval UI):**

```typescript
yield { type: "TOOL_CALL_START", toolCallId: "tc_1", toolName: "confirm_deletion" }
yield {
  type: "TOOL_CALL_ARGS",
  toolCallId: "tc_1",
  delta: JSON.stringify({ action: "delete_records", count: 50, message: "Delete 50 records?" }),
}
yield { type: "TOOL_CALL_END", toolCallId: "tc_1" }
```

Reference: [Human-in-the-Loop](https://docs.copilotkit.ai/guides/human-in-the-loop)

## 5. Generative UI Emission

**Impact: MEDIUM**

Rules for emitting tool calls and events that render dynamic UI components in the frontend.

### 5.1 Emit Tool Calls That Map to useRenderTool

**Impact: MEDIUM (mismatched tool names cause blank renders in the frontend)**

## Emit Tool Calls That Map to useRenderTool

When emitting tool calls that should render UI in the frontend, ensure the `toolName` matches exactly what the frontend has registered with `useRenderTool`. Mismatched names cause the tool call to render nothing.

**Incorrect (tool name mismatch between agent and frontend):**

```typescript
// Agent emits:
yield { type: "TOOL_CALL_START", toolCallId: "tc_1", toolName: "showWeather" }

// Frontend registers:
useRenderTool({ name: "show_weather", render: ({ args }) => <WeatherCard {...args} /> })
// Names don't match — nothing renders
```

**Correct (matching tool names):**

```typescript
// Agent emits:
yield { type: "TOOL_CALL_START", toolCallId: "tc_1", toolName: "show_weather" }

// Frontend registers:
useRenderTool({ name: "show_weather", render: ({ args }) => <WeatherCard {...args} /> })
```

Establish a naming convention (e.g., `snake_case`) and share tool name constants between agent and frontend.

Reference: [Generative UI](https://docs.copilotkit.ai/guides/generative-ui)

### 5.2 Stream Tool Args for Real-Time UI

**Impact: MEDIUM (streaming args enables progressive UI rendering during tool calls)**

## Stream Tool Args for Real-Time UI

Stream tool call arguments incrementally via multiple `TOOL_CALL_ARGS` events rather than sending the complete JSON at once. This enables the frontend to render partial UI (skeletons, progressive content) while the agent is still generating arguments.

**Incorrect (all args sent at once, no streaming UI):**

```typescript
const args = { city: "San Francisco", temperature: 68, forecast: ["sunny", "partly cloudy", "sunny"] }
yield { type: "TOOL_CALL_START", toolCallId: "tc_1", toolName: "show_weather" }
yield { type: "TOOL_CALL_ARGS", toolCallId: "tc_1", delta: JSON.stringify(args) }
yield { type: "TOOL_CALL_END", toolCallId: "tc_1" }
```

**Correct (args streamed incrementally for progressive UI):**

```typescript
yield { type: "TOOL_CALL_START", toolCallId: "tc_1", toolName: "show_weather" }
yield { type: "TOOL_CALL_ARGS", toolCallId: "tc_1", delta: '{"city":"San' }
yield { type: "TOOL_CALL_ARGS", toolCallId: "tc_1", delta: ' Francisco","temperature":' }
yield { type: "TOOL_CALL_ARGS", toolCallId: "tc_1", delta: '68,"forecast":["sunny",' }
yield { type: "TOOL_CALL_ARGS", toolCallId: "tc_1", delta: '"partly cloudy","sunny"]}' }
yield { type: "TOOL_CALL_END", toolCallId: "tc_1" }
```

Reference: [Generative UI](https://docs.copilotkit.ai/guides/generative-ui)

### 5.3 Use Text Messages for Status Updates

**Impact: LOW (status updates that aren't tool calls should use text messages, not fake tool calls)**

## Use Text Messages for Status Updates

Use lightweight text messages for status updates that don't correspond to tool calls (e.g., "Searching...", "Analyzing results..."). Don't create fake tool calls just to show status — this causes unnecessary rendering and confusing UI in the chat.

**Incorrect (fake tool call for a status message):**

```typescript
yield { type: "TOOL_CALL_START", toolCallId: "tc_status", toolName: "show_status" }
yield { type: "TOOL_CALL_ARGS", toolCallId: "tc_status", delta: '{"message":"Searching..."}' }
yield { type: "TOOL_CALL_END", toolCallId: "tc_status" }
```

**Correct (text message for status updates):**

```typescript
yield { type: "TEXT_MESSAGE_START", messageId: "status_1", role: "assistant" }
yield { type: "TEXT_MESSAGE_CONTENT", messageId: "status_1", delta: "Searching databases..." }
yield { type: "TEXT_MESSAGE_END", messageId: "status_1" }

// For CoAgents using LangGraph, emit state updates instead:
// await copilotkit_emit_state(config, { status: "searching" })
```

For CoAgents, the recommended approach is to emit agent state via `copilotkit_emit_state` and render the status in the frontend using `useCoAgentStateRender`.

Reference: [Generative UI](https://docs.copilotkit.ai/coagents/generative-ui/agentic)

---

## References

- https://docs.copilotkit.ai
- https://docs.copilotkit.ai/guides/self-hosting
- https://docs.copilotkit.ai/guides/state-management
- https://docs.copilotkit.ai/guides/human-in-the-loop
- https://docs.copilotkit.ai/guides/generative-ui
- https://docs.copilotkit.ai/guides/threads
- https://docs.copilotkit.ai/coagents/generative-ui/agentic
- https://docs.copilotkit.ai/reference/runtime/built-in-agent
- https://docs.copilotkit.ai/reference/v1/classes/CopilotRuntime
- https://docs.ag-ui.com/concepts/events
- https://github.com/CopilotKit/CopilotKit
- https://github.com/ag-ui-protocol/ag-ui
