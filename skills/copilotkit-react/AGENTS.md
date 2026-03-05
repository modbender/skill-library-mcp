# CopilotKit React Patterns

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

Best practices for building agentic React applications with CopilotKit. Contains 25 rules across 6 categories covering provider configuration, agent hooks, tool rendering, state management, chat UI, and suggestions. Each rule includes incorrect vs correct code examples for both v1 (@copilotkit/react-core) and v2 (@copilotkit/react-core/v2) APIs.

---

## Table of Contents

1. [Provider Setup](#1-provider-setup)
   1. [Always Configure runtimeUrl](#11-always-configure-runtimeurl)
   2. [Configure the agent Prop for Agent Routing](#12-configure-the-agent-prop-for-agent-routing)
   3. [Register Tools via Hooks Inside Provider](#13-register-tools-via-hooks-inside-provider)
   4. [Scope Agent Config with Nested Providers](#14-scope-agent-config-with-nested-providers)
2. [Agent Hooks](#2-agent-hooks)
   1. [Always Pass agentId for Multi-Agent](#21-always-pass-agentid-for-multi-agent)
   2. [Declare Dependency Arrays for useFrontendTool](#22-declare-dependency-arrays-for-usefrontendtool)
   3. [Specify useAgent Update Subscriptions](#23-specify-useagent-update-subscriptions)
   4. [Stabilize Tool Handler References](#24-stabilize-tool-handler-references)
   5. [Write Descriptive Context Values](#25-write-descriptive-context-values)
3. [Tool Rendering](#3-tool-rendering)
   1. [Define Zod Schemas for Tool Args](#31-define-zod-schemas-for-tool-args)
   2. [Handle All Tool Call Statuses](#32-handle-all-tool-call-statuses)
   3. [Register Wildcard Renderer as Fallback](#33-register-wildcard-renderer-as-fallback)
   4. [Use useFrontendTool render Prop for Simple UI](#34-use-usefrontendtool-render-prop-for-simple-ui)
   5. [useRenderTool for Display, useFrontendTool for Effects](#35-userendertool-for-display-usefrontendtool-for-effects)
4. [Context & State](#4-context--state)
   1. [Avoid Stale Closures in Tool Handlers](#41-avoid-stale-closures-in-tool-handlers)
   2. [Provide Only Relevant Context](#42-provide-only-relevant-context)
   3. [Split Context by Domain](#43-split-context-by-domain)
   4. [Use Structured Objects in Context](#44-use-structured-objects-in-context)
5. [Chat UI](#5-chat-ui)
   1. [Choose Appropriate Chat Layout](#51-choose-appropriate-chat-layout)
   2. [Customize Labels for Your Domain](#52-customize-labels-for-your-domain)
   3. [Provide Welcome Screen with Prompts](#53-provide-welcome-screen-with-prompts)
   4. [Use Appropriate Input Mode](#54-use-appropriate-input-mode)
6. [Suggestions](#6-suggestions)
   1. [Configure Suggestion Generation](#61-configure-suggestion-generation)
   2. [Handle Suggestion Loading States](#62-handle-suggestion-loading-states)
   3. [Provide Rich Context for Suggestions](#63-provide-rich-context-for-suggestions)

---

## 1. Provider Setup

**Impact:** CRITICAL  
Correct `CopilotKit` provider configuration is the foundation. Misconfiguration causes silent failures, broken agent connections, or degraded performance.

---

### 1.1 Always Configure runtimeUrl

**Impact: CRITICAL** — agents will not connect without a runtime URL

The `CopilotKit` provider requires a `runtimeUrl` to connect to your agent backend. Without it, all agent interactions silently fail. The runtime URL points to your CopilotKit runtime endpoint that bridges frontend and agent.

**Incorrect (no runtime URL, agents can't connect):**

```tsx
import { CopilotKit } from "@copilotkit/react-core";

function App() {
  return (
    <CopilotKit>
      <CopilotChat />
      <MyApp />
    </CopilotKit>
  )
}
```

**Correct (runtime URL configured):**

```tsx
import { CopilotKit } from "@copilotkit/react-core";

function App() {
  return (
    <CopilotKit runtimeUrl="/api/copilotkit">
      <CopilotChat />
      <MyApp />
    </CopilotKit>
  )
}
```

For Copilot Cloud, use `publicApiKey` instead of `runtimeUrl`:

```tsx
<CopilotKit publicApiKey="ck_pub_...">
  <CopilotChat />
  <MyApp />
</CopilotKit>
```

Reference: [CopilotKit Provider](https://docs.copilotkit.ai/reference/v1/components/CopilotKit)

---

### 1.2 Configure the agent Prop for Agent Routing

**Impact: CRITICAL** — without agent prop, requests may route to wrong agent or use default behavior

When using CoAgents (LangGraph, CrewAI), set the `agent` prop on `CopilotKit` to specify which agent handles requests. Without it, requests use default routing which may not match the agent you intend.

**Incorrect (no agent specified, ambiguous routing):**

```tsx
import { CopilotKit } from "@copilotkit/react-core";

function App() {
  return (
    <CopilotKit runtimeUrl="/api/copilotkit">
      <MyApp />
    </CopilotKit>
  )
}
```

**Correct (agent explicitly configured):**

```tsx
import { CopilotKit } from "@copilotkit/react-core";

function App() {
  return (
    <CopilotKit
      runtimeUrl="/api/copilotkit"
      agent="sample_agent"
    >
      <MyApp />
    </CopilotKit>
  )
}
```

When using Copilot Cloud with `publicApiKey`, the same `agent` prop applies:

```tsx
<CopilotKit publicApiKey="ck_pub_..." agent="sample_agent">
  <MyApp />
</CopilotKit>
```

Reference: [CopilotKit Provider](https://docs.copilotkit.ai/reference/v1/components/CopilotKit)

---

### 1.3 Register Tools via Hooks Inside Provider

**Impact: MEDIUM** — hooks provide dynamic registration and proper lifecycle management

Register tools using `useCopilotAction` (v1) or `useFrontendTool` (v2) hooks inside components that are children of `CopilotKit`, rather than passing tool definitions as props. Hook-based registration ties tool availability to component lifecycle and enables dynamic tool sets.

**Incorrect (static tool props on provider):**

```tsx
const tools = [
  { name: "search", handler: searchFn, description: "Search docs" }
]

function App() {
  return (
    <CopilotKit runtimeUrl="/api/copilotkit" tools={tools}>
      <MyApp />
    </CopilotKit>
  )
}
```

**Correct (hook-based registration inside provider, v1):**

```tsx
import { useCopilotAction } from "@copilotkit/react-core";

function MyApp() {
  useCopilotAction({
    name: "search",
    description: "Search the documentation",
    parameters: [{ name: "query", type: "string", description: "Search query" }],
    handler: async ({ query }) => {
      return await searchDocs(query)
    },
  })

  return <Dashboard />
}
```

**Correct (hook-based registration inside provider, v2 with Zod):**

```tsx
import { useFrontendTool } from "@copilotkit/react-core/v2";
import { z } from "zod";

function MyApp() {
  useFrontendTool({
    name: "search",
    description: "Search the documentation",
    parameters: z.object({ query: z.string().describe("Search query") }),
    handler: async ({ query }) => {
      return await searchDocs(query)
    },
  })

  return <Dashboard />
}
```

Reference: [useCopilotAction](https://docs.copilotkit.ai/reference/v1/hooks/useCopilotAction) | [useFrontendTool (v2)](https://docs.copilotkit.ai/reference/v2/hooks/useFrontendTool)

---

### 1.4 Scope Agent Config with Nested Providers

**Impact: HIGH** — prevents agent configuration conflicts in multi-agent apps

When different parts of your app need different agent configurations (different agents, tools, or context), nest `CopilotKit` providers to scope configuration. Inner providers inherit from outer ones but can override specific settings via the `agent` prop.

**Incorrect (single provider, all agents share config):**

```tsx
import { CopilotKit } from "@copilotkit/react-core";

function App() {
  return (
    <CopilotKit runtimeUrl="/api/copilotkit">
      <ResearchPanel />
      <WritingPanel />
    </CopilotKit>
  )
}
```

**Correct (nested providers scope agent config):**

```tsx
import { CopilotKit } from "@copilotkit/react-core";

function App() {
  return (
    <CopilotKit runtimeUrl="/api/copilotkit">
      <CopilotKit agent="researcher">
        <ResearchPanel />
      </CopilotKit>
      <CopilotKit agent="writer">
        <WritingPanel />
      </CopilotKit>
    </CopilotKit>
  )
}
```

Reference: [CopilotKit Provider](https://docs.copilotkit.ai/reference/v1/components/CopilotKit)

---

## 2. Agent Hooks

**Impact:** HIGH  
Patterns for useAgent (v2), useFrontendTool (v2), useCopilotReadable (v1), and useCopilotAction (v1). Incorrect usage causes re-render storms, stale state, or broken agent interactions.

---

### 2.1 Always Pass agentId for Multi-Agent

**Impact: HIGH** — without agentId, requests route to wrong agent or fail

When your application has multiple agents, always specify `agentId` in hooks like `useAgent` and `useFrontendTool`, or use the `agent` prop on the `CopilotKit` provider. Without it, CopilotKit cannot route requests to the correct agent, causing unexpected behavior or errors.

**Incorrect (no agentId, ambiguous routing):**

```tsx
import { useAgent, useFrontendTool } from "@copilotkit/react-core/v2";

function ResearchPanel() {
  const { agent } = useAgent({})

  useFrontendTool({
    name: "save_result",
    handler: async ({ result }) => saveToDb(result),
  })

  return <button onClick={() => agent.runAgent()}>Go</button>
}
```

**Correct (explicit agentId for routing):**

```tsx
import { useAgent, useFrontendTool } from "@copilotkit/react-core/v2";

function ResearchPanel() {
  const { agent } = useAgent({ agentId: "researcher" })

  useFrontendTool({
    name: "save_result",
    agentId: "researcher",
    handler: async ({ result }) => saveToDb(result),
  })

  return <button onClick={() => agent.runAgent()}>Go</button>
}
```

Reference: [useAgent Hook](https://docs.copilotkit.ai/reference/v2/hooks/useAgent)

---

### 2.2 Declare Dependency Arrays for useFrontendTool

**Impact: MEDIUM** — missing deps cause stale closures or infinite re-registrations

`useFrontendTool` (v2) and `useCopilotAction` (v1) accept a dependency array that controls when the tool re-registers. Without it, the tool re-registers on every render. Include all values from the component scope that the handler uses.

**Incorrect (no deps, re-registers every render):**

```tsx
import { useFrontendTool } from "@copilotkit/react-core/v2";

function TaskPanel({ projectId }: { projectId: string }) {
  useFrontendTool({
    name: "create_task",
    handler: async ({ title }) => {
      await createTask(projectId, title)
    },
  })

  return <TaskList projectId={projectId} />
}
```

**Correct (deps array controls re-registration):**

```tsx
import { useFrontendTool } from "@copilotkit/react-core/v2";

function TaskPanel({ projectId }: { projectId: string }) {
  useFrontendTool(
    {
      name: "create_task",
      handler: async ({ title }) => {
        await createTask(projectId, title)
      },
    },
    [projectId],
  )

  return <TaskList projectId={projectId} />
}
```

Reference: [useFrontendTool (v2)](https://docs.copilotkit.ai/reference/v2/hooks/useFrontendTool)

---

### 2.3 Specify useAgent Update Subscriptions

**Impact: HIGH** — prevents unnecessary re-renders from agent state changes

The `useAgent` hook (v2) accepts an `updates` array that controls which agent changes trigger a React re-render. By default it subscribes to all updates (`OnMessagesChanged`, `OnStateChanged`, `OnRunStatusChanged`). Only subscribe to the updates your component actually needs to avoid excessive re-renders.

**Incorrect (subscribes to all updates, causes re-render storms):**

```tsx
import { useAgent } from "@copilotkit/react-core/v2";

function AgentStatus() {
  const { agent } = useAgent({ agentId: "researcher" })

  return <div>Running: {agent.isRunning ? "yes" : "no"}</div>
}
```

**Correct (subscribes only to run status changes):**

```tsx
import { useAgent } from "@copilotkit/react-core/v2";

function AgentStatus() {
  const { agent } = useAgent({
    agentId: "researcher",
    updates: ["OnRunStatusChanged"],
  })

  return <div>Running: {agent.isRunning ? "yes" : "no"}</div>
}
```

Available update types:
- `"OnMessagesChanged"` - re-render when messages update
- `"OnStateChanged"` - re-render when agent state changes
- `"OnRunStatusChanged"` - re-render when run status changes

Reference: [useAgent Hook (v2)](https://docs.copilotkit.ai/reference/v2/hooks/useAgent)

---

### 2.4 Stabilize Tool Handler References

**Impact: MEDIUM** — unstable handler references cause tool re-registration churn

When passing handler functions to `useFrontendTool` (v2) or `useCopilotAction` (v1), wrap them with `useCallback` to maintain stable references. Unstable function references trigger unnecessary tool re-registrations, which can interrupt in-flight agent tool calls.

**Incorrect (new handler created every render):**

```tsx
import { useFrontendTool } from "@copilotkit/react-core/v2";

function DocumentEditor({ docId }: { docId: string }) {
  useFrontendTool(
    {
      name: "update_document",
      handler: async ({ content }) => {
        await updateDoc(docId, content)
      },
    },
    [docId],
  )

  return <Editor docId={docId} />
}
```

**Correct (stable handler via useCallback):**

```tsx
import { useCallback } from "react";
import { useFrontendTool } from "@copilotkit/react-core/v2";

function DocumentEditor({ docId }: { docId: string }) {
  const handler = useCallback(
    async ({ content }: { content: string }) => {
      await updateDoc(docId, content)
    },
    [docId]
  )

  useFrontendTool(
    {
      name: "update_document",
      handler,
    },
    [docId],
  )

  return <Editor docId={docId} />
}
```

Reference: [useFrontendTool (v2)](https://docs.copilotkit.ai/reference/v2/hooks/useFrontendTool)

---

### 2.5 Write Descriptive Context Values

**Impact: HIGH** — vague context produces vague agent responses

When using `useCopilotReadable` to provide context to your agent, supply specific, descriptive values that help the agent understand the current application state. Vague or minimal context leads to generic agent responses that don't match the user's situation.

**Incorrect (vague context, agent lacks understanding):**

```tsx
import { useCopilotReadable } from "@copilotkit/react-core";

useCopilotReadable({
  description: "Current page",
  value: "dashboard",
})
```

**Correct (specific context with relevant details):**

```tsx
import { useCopilotReadable } from "@copilotkit/react-core";

useCopilotReadable({
  description: "Current project dashboard state",
  value: {
    projectName: project.name,
    totalTasks: tasks.length,
    overdueTasks: tasks.filter(t => t.status === "overdue").length,
    userRole: "admin",
  },
})
```

In v2, you can also provide context via `useAgent` shared state:

```tsx
import { useAgent } from "@copilotkit/react-core/v2";

const { agent } = useAgent({ agentId: "researcher" });
agent.setState({ projectName: project.name, taskCount: tasks.length });
```

Reference: [useCopilotReadable](https://docs.copilotkit.ai/reference/v1/hooks/useCopilotReadable)

---

## 3. Tool Rendering

**Impact:** HIGH  
Rules for rendering agent tool calls in the UI. Proper tool rendering is what makes CopilotKit's generative UI possible.

---

### 3.1 Define Zod Schemas for Tool Args

**Impact: HIGH** — enables type-safe rendering and partial arg streaming

When using `useRenderTool` (v2), always define a Zod schema for the `parameters` field. This enables type-safe access to tool arguments and allows CopilotKit to stream partial arguments while the tool call is in progress, giving users real-time feedback.

**Incorrect (no schema, parameters are untyped):**

```tsx
import { useRenderTool } from "@copilotkit/react-core/v2";

useRenderTool({
  name: "show_weather",
  render: ({ parameters, status }) => {
    return (
      <WeatherCard
        city={parameters.city}
        temp={parameters.temperature}
      />
    )
  },
})
```

**Correct (Zod schema provides type safety and streaming):**

```tsx
import { useRenderTool } from "@copilotkit/react-core/v2";
import { z } from "zod";

useRenderTool({
  name: "show_weather",
  parameters: z.object({
    city: z.string(),
    temperature: z.number(),
    condition: z.enum(["sunny", "cloudy", "rainy"]),
  }),
  render: ({ parameters, status }) => {
    if (status === "inProgress") {
      return <WeatherCardSkeleton city={parameters.city} />
    }
    return (
      <WeatherCard
        city={parameters.city}
        temp={parameters.temperature}
        condition={parameters.condition}
      />
    )
  },
})
```

The Zod schema enables:
- TypeScript inference for `parameters` in the render function
- Partial parameters during `inProgress` status (for streaming UI)
- Validation before `executing` and `complete` statuses

In v1, use `useCopilotAction` with `render` and plain parameter arrays instead.

Reference: [useRenderTool (v2)](https://docs.copilotkit.ai/reference/v2/hooks/useRenderTool)

---

### 3.2 Handle All Tool Call Statuses

**Impact: HIGH** — unhandled statuses cause blank UI or missing loading states

Tool renders receive a `status` field with three possible values: `inProgress`, `executing`, and `complete`. Handle all three to provide proper loading states, execution feedback, and final results. Ignoring statuses causes jarring UI transitions.

**Incorrect (only handles complete, no loading state):**

```tsx
import { useRenderTool } from "@copilotkit/react-core/v2";
import { z } from "zod";

useRenderTool({
  name: "search_results",
  parameters: z.object({ query: z.string(), results: z.array(z.string()) }),
  render: ({ parameters }) => {
    return <ResultsList results={parameters.results} />
  },
})
```

**Correct (handles all three statuses):**

```tsx
import { useRenderTool } from "@copilotkit/react-core/v2";
import { z } from "zod";

useRenderTool({
  name: "search_results",
  parameters: z.object({ query: z.string(), results: z.array(z.string()) }),
  render: ({ parameters, status }) => {
    if (status === "inProgress") {
      return <SearchSkeleton query={parameters.query} />
    }
    if (status === "executing") {
      return <SearchProgress query={parameters.query} />
    }
    return <ResultsList results={parameters.results} />
  },
})
```

The same status values apply to v1's `useCopilotAction` render prop.

Reference: [useRenderTool (v2)](https://docs.copilotkit.ai/reference/v2/hooks/useRenderTool)

---

### 3.3 Register Wildcard Renderer as Fallback

**Impact: MEDIUM** — prevents missing UI when agent calls unregistered tools

Register a wildcard `"*"` renderer with `useRenderTool` to catch tool calls that don't have a dedicated renderer. Without a fallback, unregistered tool calls render nothing in the chat, confusing users.

**Incorrect (no fallback, unknown tools render blank):**

```tsx
import { useRenderTool } from "@copilotkit/react-core/v2";
import { z } from "zod";

useRenderTool({
  name: "show_chart",
  parameters: z.object({ data: z.array(z.number()) }),
  render: ({ parameters }) => <Chart data={parameters.data} />,
})
```

**Correct (wildcard fallback for unknown tools):**

```tsx
import { useRenderTool } from "@copilotkit/react-core/v2";
import { z } from "zod";

useRenderTool({
  name: "show_chart",
  parameters: z.object({ data: z.array(z.number()) }),
  render: ({ parameters }) => <Chart data={parameters.data} />,
})

useRenderTool({
  name: "*",
  render: ({ name, parameters, status }) => (
    <GenericToolCard
      toolName={name}
      args={parameters}
      isLoading={status === "inProgress"}
    />
  ),
})
```

Reference: [useRenderTool (v2)](https://docs.copilotkit.ai/reference/v2/hooks/useRenderTool)

---

### 3.4 Use useFrontendTool render Prop for Simple UI

**Impact: MEDIUM** — reduces boilerplate for common component-rendering patterns

When a tool call needs both side effects and UI rendering, use `useFrontendTool` with its optional `render` prop instead of registering separate `useFrontendTool` and `useRenderTool` hooks. This keeps the tool definition in one place.

**Incorrect (separate hooks for a simple tool):**

```tsx
import { useFrontendTool, useRenderTool } from "@copilotkit/react-core/v2";
import { z } from "zod";

const schema = z.object({ name: z.string(), email: z.string() });

useFrontendTool({
  name: "show_user_card",
  parameters: schema,
  handler: async ({ name, email }) => {
    return `Showing card for ${name}`
  },
})

useRenderTool({
  name: "show_user_card",
  parameters: schema,
  render: ({ parameters, status }) => {
    if (status !== "complete") return <UserCardSkeleton />
    return <UserCard name={parameters.name} email={parameters.email} />
  },
})
```

**Correct (single useFrontendTool with render prop):**

```tsx
import { useFrontendTool } from "@copilotkit/react-core/v2";
import { z } from "zod";

useFrontendTool({
  name: "show_user_card",
  parameters: z.object({ name: z.string(), email: z.string() }),
  handler: async ({ name, email }) => {
    return `Showing card for ${name}`
  },
  render: ({ name, args, status, result }) => {
    if (status !== "complete") return <UserCardSkeleton />
    return <UserCard name={args.name} email={args.email} />
  },
})
```

In v1, `useCopilotAction` similarly combines `handler` and `render` in one definition.

Reference: [useFrontendTool (v2)](https://docs.copilotkit.ai/reference/v2/hooks/useFrontendTool)

---

### 3.5 useRenderTool for Display, useFrontendTool for Effects

**Impact: HIGH** — mixing concerns causes side effects during streaming or double execution

Use `useRenderTool` when you only need to display UI in response to a tool call. Use `useFrontendTool` when the tool call should trigger side effects (API calls, state mutations, navigation). Mixing them causes side effects to fire during streaming or display-only tools to swallow return values.

**Incorrect (side effects in a render tool):**

```tsx
import { useRenderTool } from "@copilotkit/react-core/v2";

useRenderTool({
  name: "create_ticket",
  render: ({ parameters, status }) => {
    if (status === "complete") {
      createTicketInDb(parameters)
    }
    return <TicketCard {...parameters} />
  },
})
```

**Correct (separate render from effects):**

```tsx
import { useFrontendTool, useRenderTool } from "@copilotkit/react-core/v2";
import { z } from "zod";

const ticketSchema = z.object({
  title: z.string(),
  priority: z.enum(["low", "medium", "high"]),
});

useFrontendTool({
  name: "create_ticket",
  parameters: ticketSchema,
  handler: async ({ title, priority }) => {
    const ticket = await createTicketInDb({ title, priority })
    return `Created ticket ${ticket.id}`
  },
})

useRenderTool({
  name: "create_ticket",
  parameters: ticketSchema,
  render: ({ parameters, status }) => {
    if (status === "inProgress") return <TicketSkeleton />
    return <TicketCard title={parameters.title} priority={parameters.priority} />
  },
})
```

In v1, use `useCopilotAction` with both `handler` and `render` props on the same action.

Reference: [useFrontendTool (v2)](https://docs.copilotkit.ai/reference/v2/hooks/useFrontendTool) | [useRenderTool (v2)](https://docs.copilotkit.ai/reference/v2/hooks/useRenderTool)

---

## 4. Context & State

**Impact:** MEDIUM  
Patterns for providing context to agents and managing shared state. Good context = good agent responses.

---

### 4.1 Avoid Stale Closures in Tool Handlers

**Impact: HIGH** — stale closures cause tools to operate on outdated state

Tool handlers registered with `useFrontendTool` (v2) or `useCopilotAction` (v1) capture variables from their closure. If state changes between registration and invocation, the handler sees stale values. Use functional state updates or refs to always access current state.

**Incorrect (stale closure captures initial items):**

```tsx
import { useCopilotAction } from "@copilotkit/react-core";

function TodoPanel() {
  const [items, setItems] = useState<string[]>([])

  useCopilotAction({
    name: "add_todo",
    parameters: [{ name: "title", type: "string", description: "Todo title" }],
    handler: async ({ title }) => {
      setItems([...items, title])
    },
  })

  return <TodoList items={items} />
}
```

**Correct (functional update always uses current state):**

```tsx
import { useCopilotAction } from "@copilotkit/react-core";

function TodoPanel() {
  const [items, setItems] = useState<string[]>([])

  useCopilotAction({
    name: "add_todo",
    parameters: [{ name: "title", type: "string", description: "Todo title" }],
    handler: async ({ title }) => {
      setItems(prev => [...prev, title])
    },
  })

  return <TodoList items={items} />
}
```

Reference: [useCopilotAction](https://docs.copilotkit.ai/reference/v1/hooks/useCopilotAction) | [useFrontendTool (v2)](https://docs.copilotkit.ai/reference/v2/hooks/useFrontendTool)

---

### 4.2 Provide Only Relevant Context

**Impact: MEDIUM** — excessive context wastes tokens and confuses agents

Only provide context that the agent needs for its current task. Dumping entire app state into context wastes LLM tokens, increases latency, and can confuse the agent with irrelevant information.

**Incorrect (entire app state as context):**

```tsx
import { useCopilotReadable } from "@copilotkit/react-core";

function App() {
  const appState = useAppStore()

  useCopilotReadable({
    description: "Application state",
    value: JSON.stringify(appState),
  })

  return <Dashboard />
}
```

**Correct (only relevant context for the current view):**

```tsx
import { useCopilotReadable } from "@copilotkit/react-core";

function ProjectView({ projectId }: { projectId: string }) {
  const project = useProject(projectId)
  const tasks = useTasks(projectId)

  useCopilotReadable({
    description: "Current project details",
    value: {
      name: project.name,
      status: project.status,
      activeTasks: tasks.filter(t => t.status === "active").length,
      userRole: project.currentUserRole,
    },
  })

  return <ProjectDashboard project={project} tasks={tasks} />
}
```

Reference: [useCopilotReadable](https://docs.copilotkit.ai/reference/v1/hooks/useCopilotReadable)

---

### 4.3 Split Context by Domain

**Impact: MEDIUM** — granular context updates avoid re-sending unchanged data

Instead of one large `useCopilotReadable` call, split context into multiple calls by domain. This way, only the changed domain's context gets re-sent to the agent, reducing token usage and improving response quality.

**Incorrect (single monolithic context):**

```tsx
import { useCopilotReadable } from "@copilotkit/react-core";

function Dashboard() {
  const user = useUser()
  const projects = useProjects()
  const notifications = useNotifications()

  useCopilotReadable({
    description: "Everything",
    value: `User: ${user.name}, Role: ${user.role}. 
Projects: ${JSON.stringify(projects)}. 
Notifications: ${notifications.length} unread.`,
  })

  return <DashboardView />
}
```

**Correct (split context by domain):**

```tsx
import { useCopilotReadable } from "@copilotkit/react-core";

function Dashboard() {
  const user = useUser()
  const projects = useProjects()
  const notifications = useNotifications()

  useCopilotReadable({
    description: "Current user information",
    value: { userName: user.name, role: user.role },
  })

  useCopilotReadable({
    description: "User's projects",
    value: { projects: projects.map(p => ({ id: p.id, name: p.name, status: p.status })) },
  })

  useCopilotReadable({
    description: "Notification status",
    value: { unreadCount: notifications.length },
  })

  return <DashboardView />
}
```

Reference: [useCopilotReadable](https://docs.copilotkit.ai/reference/v1/hooks/useCopilotReadable)

---

### 4.4 Use Structured Objects in Context

**Impact: MEDIUM** — structured data enables better agent reasoning than flat strings

When providing context via `useCopilotReadable`, use structured objects for the `value` rather than serialized strings. Structured data helps agents parse and reason about context more reliably than free-form text.

**Incorrect (serialized string, hard for agent to parse):**

```tsx
import { useCopilotReadable } from "@copilotkit/react-core";

useCopilotReadable({
  description: "Cart items",
  value: `items: ${items.map(i => `${i.name}(${i.price})`).join(", ")}`,
})
```

**Correct (structured object for reliable parsing):**

```tsx
import { useCopilotReadable } from "@copilotkit/react-core";

useCopilotReadable({
  description: "Shopping cart contents",
  value: {
    cartItems: items.map(item => ({
      name: item.name,
      price: item.price,
      quantity: item.quantity,
    })),
    total: items.reduce((sum, i) => sum + i.price * i.quantity, 0),
    itemCount: items.length,
  },
})
```

Reference: [useCopilotReadable](https://docs.copilotkit.ai/reference/v1/hooks/useCopilotReadable)

---

## 5. Chat UI

**Impact:** MEDIUM  
Rules for configuring and customizing CopilotChat, CopilotSidebar, and CopilotPopup components.

---

### 5.1 Choose Appropriate Chat Layout

**Impact: MEDIUM** — wrong layout choice degrades UX for the use case

Choose `CopilotSidebar` for persistent, always-visible agent interaction (e.g., copilot-assisted workflows). Choose `CopilotPopup` for on-demand, quick interactions. Choose `CopilotChat` for inline, embedded chat in a specific page section.

**Incorrect (popup for a workflow that needs persistent chat):**

```tsx
function ProjectWorkspace() {
  return (
    <div>
      <ProjectBoard />
      <CopilotPopup />
    </div>
  )
}
```

**Correct (sidebar for persistent workflow assistance):**

```tsx
function ProjectWorkspace() {
  return (
    <CopilotSidebar
      defaultOpen={true}
      labels={{ title: "Project Assistant" }}
    >
      <ProjectBoard />
    </CopilotSidebar>
  )
}
```

Reference: [Chat Components](https://docs.copilotkit.ai/reference/components/chat)

---

### 5.2 Customize Labels for Your Domain

**Impact: LOW** — default labels feel generic and reduce user trust

Always customize the `labels` prop on chat components to match your application's domain. Default labels like "How can I help?" feel generic and don't build user confidence in the agent's capabilities.

**Incorrect (default labels, generic feel):**

```tsx
<CopilotSidebar>
  <MyApp />
</CopilotSidebar>
```

**Correct (domain-specific labels):**

```tsx
<CopilotSidebar
  labels={{
    title: "Sales Assistant",
    placeholder: "Ask about leads, deals, or forecasts...",
    initial: "I can help you analyze your pipeline, draft outreach, or update deal stages.",
  }}
>
  <MyApp />
</CopilotSidebar>
```

Reference: [Chat Components](https://docs.copilotkit.ai/reference/components/chat)

---

### 5.3 Provide Welcome Screen with Prompts

**Impact: LOW** — users don't know what to ask without guidance

Configure a welcome screen with suggested prompts to guide users on what the agent can do. An empty chat box with no guidance leads to low engagement because users don't know what to ask.

**Incorrect (no welcome screen, empty chat):**

```tsx
<CopilotChat />
```

**Correct (welcome screen with actionable prompts):**

```tsx
<CopilotChat
  welcomeScreen={{
    title: "Welcome to your AI Assistant",
    description: "I can help you with your projects and tasks.",
    suggestedPrompts: [
      "Summarize my overdue tasks",
      "Draft a status update for the team",
      "Create a new task for the landing page redesign",
    ],
  }}
/>
```

Reference: [Chat Components](https://docs.copilotkit.ai/reference/components/chat)

---

### 5.4 Use Appropriate Input Mode

**Impact: LOW** — wrong input mode creates friction for the interaction type

Set the `inputMode` prop to match your use case. Use `"text"` for general chat, `"voice"` for hands-free workflows, and `"multi"` to let users switch between text and voice.

**Incorrect (default text mode for a driving assistant):**

```tsx
function DrivingAssistant() {
  return (
    <CopilotChat
      labels={{ title: "Navigation Assistant" }}
    />
  )
}
```

**Correct (voice mode for hands-free interaction):**

```tsx
function DrivingAssistant() {
  return (
    <CopilotChat
      inputMode="voice"
      labels={{ title: "Navigation Assistant" }}
    />
  )
}
```

Reference: [Chat Components](https://docs.copilotkit.ai/reference/components/chat)

---

## 6. Suggestions

**Impact:** LOW  
Patterns for configuring proactive suggestions that help users discover agent capabilities.

---

### 6.1 Configure Suggestion Generation

**Impact: LOW** — unconfigured suggestions are generic and unhelpful

Use `useConfigureSuggestions` (v2) or `useCopilotChatSuggestions` (v1) to control how and when suggestions are generated. Without configuration, suggestions may be too generic or generated at inappropriate times, wasting LLM calls.

**Incorrect (no suggestion configuration):**

```tsx
import { CopilotKit } from "@copilotkit/react-core";

function App() {
  return (
    <CopilotKit runtimeUrl="/api/copilotkit">
      <CopilotSidebar>
        <Dashboard />
      </CopilotSidebar>
    </CopilotKit>
  )
}
```

**Correct (v2 configured suggestion generation):**

```tsx
import { useConfigureSuggestions } from "@copilotkit/react-core/v2";

function Dashboard() {
  useConfigureSuggestions({
    instructions: "Suggest actions relevant to the user's current project and recent activity.",
    maxSuggestions: 3,
    available: "after-first-message",
  })

  return <DashboardView />
}
```

**Correct (v1 alternative):**

```tsx
import { useCopilotChatSuggestions } from "@copilotkit/react-ui";

function Dashboard() {
  useCopilotChatSuggestions({
    instructions: "Suggest actions relevant to the user's current project.",
    maxSuggestions: 3,
  })

  return <DashboardView />
}
```

Reference: [useConfigureSuggestions (v2)](https://docs.copilotkit.ai/reference/v2/hooks/useConfigureSuggestions) | [useCopilotChatSuggestions (v1)](https://docs.copilotkit.ai/reference/v1/hooks/useCopilotChatSuggestions)

---

### 6.2 Handle Suggestion Loading States

**Impact: LOW** — unhandled loading causes layout shift when suggestions appear

When rendering suggestions in the UI, use the `useSuggestions` hook (v2) to access loading state and prevent layout shifts. Suggestions are generated asynchronously and may take a moment to appear.

**Incorrect (no loading state, content jumps when suggestions load):**

```tsx
function SuggestionBar({ suggestions }: { suggestions: string[] }) {
  return (
    <div className="suggestions">
      {suggestions.map(s => (
        <button key={s}>{s}</button>
      ))}
    </div>
  )
}
```

**Correct (useSuggestions hook with loading state):**

```tsx
import { useSuggestions } from "@copilotkit/react-core/v2";

function SuggestionBar() {
  const { suggestions, isLoading } = useSuggestions()

  return (
    <div className="suggestions" style={{ minHeight: 48 }}>
      {isLoading ? (
        <SuggestionSkeleton count={3} />
      ) : (
        suggestions.map(s => (
          <button key={s.title} onClick={() => /* send s.message */}>
            {s.title}
          </button>
        ))
      )}
    </div>
  )
}
```

Reference: [useSuggestions (v2)](https://docs.copilotkit.ai/reference/v2/hooks/useSuggestions)

---

### 6.3 Provide Rich Context for Suggestions

**Impact: LOW** — suggestions without context are generic and irrelevant

Suggestions are only as good as the context available. Combine `useConfigureSuggestions` (v2) with `useCopilotReadable` to give the suggestion engine enough information to produce relevant, actionable suggestions.

**Incorrect (suggestions without context):**

```tsx
import { useConfigureSuggestions } from "@copilotkit/react-core/v2";

function TaskBoard() {
  useConfigureSuggestions({
    instructions: "Suggest helpful actions",
    maxSuggestions: 3,
  })

  return <Board />
}
```

**Correct (suggestions enriched with context):**

```tsx
import { useCopilotReadable } from "@copilotkit/react-core";
import { useConfigureSuggestions } from "@copilotkit/react-core/v2";

function TaskBoard() {
  const tasks = useTasks()
  const overdue = tasks.filter(t => t.isOverdue)

  useCopilotReadable({
    description: "Task board state",
    value: {
      totalTasks: tasks.length,
      overdueTasks: overdue.map(t => ({ id: t.id, title: t.title, dueDate: t.dueDate })),
      currentSprint: "Sprint 14",
    },
  })

  useConfigureSuggestions({
    instructions: "Suggest actions based on overdue tasks and sprint progress. Prioritize urgent items.",
    maxSuggestions: 3,
    available: "after-first-message",
  })

  return <Board tasks={tasks} />
}
```

Reference: [useConfigureSuggestions (v2)](https://docs.copilotkit.ai/reference/v2/hooks/useConfigureSuggestions)

---

## References

- https://docs.copilotkit.ai
- https://github.com/CopilotKit/CopilotKit
- https://docs.copilotkit.ai/reference/v1/hooks
- https://docs.copilotkit.ai/reference/v2/hooks
- https://docs.copilotkit.ai/reference/v1/components
