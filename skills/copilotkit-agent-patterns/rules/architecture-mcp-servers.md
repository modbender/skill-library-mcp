---
title: Configure MCP Servers for External Tools
impact: MEDIUM
impactDescription: MCP extends agent capabilities without custom tool implementation
tags: architecture, MCP, servers, external-tools
---

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
