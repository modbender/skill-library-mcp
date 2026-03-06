---
name: copilotkit-react-patterns
description: CopilotKit React best practices for agentic applications. Use when writing, reviewing, or refactoring React code that uses CopilotKit hooks (useAgent, useFrontendTool, useRenderTool, useCopilotAction, useCopilotReadable), providers (CopilotKit), or chat UI components (CopilotChat, CopilotSidebar, CopilotPopup). Triggers on tasks involving agent integration, tool rendering, shared state, or generative UI in React.
license: MIT
metadata:
  author: copilotkit
  version: "2.0.0"
---

# CopilotKit React Patterns

Best practices for building agentic React applications with CopilotKit. Contains 25 rules across 6 categories, prioritized by impact to guide code generation and refactoring. Covers both v1 (`@copilotkit/react-core`) and v2 (`@copilotkit/react-core/v2`) APIs.

## When to Apply

Reference these guidelines when:
- Setting up `CopilotKit` provider in a React application
- Using agent hooks (useAgent, useFrontendTool, useCopilotAction)
- Rendering tool calls or custom messages from agents
- Managing shared state between UI and agents via useCopilotReadable or useCoAgent
- Building chat interfaces with CopilotChat, CopilotSidebar, or CopilotPopup
- Configuring suggestions for proactive agent assistance

## Rule Categories by Priority

| Priority | Category | Impact | Prefix |
|----------|----------|--------|--------|
| 1 | Provider Setup | CRITICAL | `provider-` |
| 2 | Agent Hooks | HIGH | `agent-` |
| 3 | Tool Rendering | HIGH | `tool-` |
| 4 | Context & State | MEDIUM | `state-` |
| 5 | Chat UI | MEDIUM | `ui-` |
| 6 | Suggestions | LOW | `suggestions-` |

## Quick Reference

### 1. Provider Setup (CRITICAL)

- `provider-runtime-url` - Always configure runtimeUrl to connect to your agent backend
- `provider-single-endpoint` - Configure the agent prop for CoAgent routing
- `provider-nested-providers` - Scope agent configurations with nested CopilotKit providers
- `provider-tool-registration` - Register tools via hooks inside provider, not as props when possible

### 2. Agent Hooks (HIGH)

- `agent-use-agent-updates` - Specify update subscriptions to avoid unnecessary re-renders
- `agent-agent-id` - Always pass agentId when running multiple agents
- `agent-context-description` - Write descriptive context values for useCopilotReadable
- `agent-frontend-tool-deps` - Declare dependency arrays for useFrontendTool
- `agent-stable-tool-handlers` - Use useCallback for tool handler functions

### 3. Tool Rendering (HIGH)

- `tool-typed-args` - Define Zod schemas for useRenderTool parameters (v2)
- `tool-status-handling` - Handle all three tool call statuses (inProgress, executing, complete)
- `tool-wildcard-fallback` - Register a wildcard renderer as fallback for unknown tools
- `tool-render-vs-frontend` - Use useRenderTool for display-only, useFrontendTool for side effects
- `tool-component-hook` - Use useFrontendTool render prop for simple component rendering

### 4. Context & State (MEDIUM)

- `state-minimal-context` - Provide only relevant context to agents, not entire app state
- `state-structured-values` - Use structured objects in useCopilotReadable, not serialized strings
- `state-context-granularity` - Split context into multiple useCopilotReadable calls by domain
- `state-avoid-stale-closures` - Use functional state updates in tool handlers

### 5. Chat UI (MEDIUM)

- `ui-chat-layout` - Choose CopilotSidebar for persistent chat, CopilotPopup for on-demand
- `ui-custom-labels` - Always customize labels for your domain instead of defaults
- `ui-welcome-screen` - Provide a welcome screen with suggested prompts
- `ui-input-mode` - Use appropriate inputMode for your use case

### 6. Suggestions (LOW)

- `suggestions-configure` - Use useConfigureSuggestions (v2) or useCopilotChatSuggestions (v1)
- `suggestions-context-driven` - Provide rich context so suggestions are relevant
- `suggestions-loading-state` - Handle suggestion loading states via useSuggestions (v2)

## How to Use

Read individual rule files for detailed explanations and code examples:

```
rules/provider-runtime-url.md
rules/agent-use-agent-updates.md
rules/tool-typed-args.md
```

Each rule file contains:
- Brief explanation of why it matters
- Incorrect code example with explanation
- Correct code example with explanation
- Additional context and references

## Full Compiled Document

For the complete guide with all rules expanded: `AGENTS.md`
