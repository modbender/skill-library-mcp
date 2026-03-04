---
title: Use BuiltInAgent for Direct-to-LLM Agents
impact: CRITICAL
impactDescription: BuiltInAgent handles AG-UI protocol automatically
tags: architecture, BuiltInAgent, setup
---

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
