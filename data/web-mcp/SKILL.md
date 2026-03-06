---
name: web-mcp
description: WebMCP - Enable AI agents to interact with your web applications through structured tools. Implements the WebMCP standard for Next.js/React apps with tool registration, event bridge pattern, and contextual tool loading. Use when building AI-agent accessible web apps, adding MCP capabilities to existing projects, or creating tool-based interfaces for AI interactions.
version: "1.0.0"
user-invocable: true
triggers:
  - web mcp
  - webmcp
  - ai agent web
  - tool registration
  - navigator.modelContext
  - agent accessible
  - mcp website
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
metadata:
  clawdbot:
    emoji: "🌐"
    config:
      stateDirs: [".webmcp"]
---

# WebMCP

Enable AI agents to interact with your web applications through structured tools. WebMCP provides a clean, self-documenting interface between AI agents and your web app.

## What is WebMCP?

WebMCP is a web standard that gives AI agents an explicit, structured contract for interacting with websites. Instead of screen-scraping or brittle DOM selectors, a WebMCP-enabled page exposes **tools** — each with:
- A name
- A JSON Schema describing inputs and outputs
- An executable function
- Optional annotations (read-only hints, etc.)

## Quick Start

```bash
# Initialize WebMCP in your Next.js project
webmcp init

# Add a new tool
webmcp add-tool searchProducts

# Generate TypeScript types
webmcp generate-types
```

## Core Concepts

### 1. Tool Definition

```typescript
const searchTool = {
  name: "searchProducts",
  description: "Search for products by query",
  inputSchema: {
    type: "object",
    properties: {
      query: { type: "string", description: "Search query" }
    },
    required: ["query"]
  },
  outputSchema: { type: "string" },
  execute: async (params) => {
    // Implementation
  },
  annotations: {
    readOnlyHint: "true"
  }
};
```

### 2. Contextual Tool Loading

Tools are registered when components mount and unregistered when they unmount:

```tsx
useEffect(() => {
  registerSearchTools();  // Tools appear to agent
  return () => {
    unregisterSearchTools();  // Tools disappear
  };
}, []);
```

### 3. Event Bridge Pattern

Tools communicate with React through CustomEvents:

```
Agent → execute() → dispatch CustomEvent → React updates → signal completion → Agent receives result
```

## Architecture

```
┌─────────────────────────────────────────┐
│  Browser (navigator.modelContext)       │
│                                         │
│  ┌───────────┐    registers/     ┌────┐ │
│  │ AI Agent  │◄──unregisters────│web │ │
│  │ (Claude)  │    tools         │mcp│ │
│  │           │                  │.ts│ │
│  │ calls─────┼─────────────────►│    │ │
│  └───────────┘                  └──┬─┘ │
│                                    │    │
│                         CustomEvent│    │
│                         dispatch   │    │
│                                    ▼    │
│  ┌──────────────────────────────────┐   │
│  │ React Component Tree             │   │
│  │                                  │   │
│  │ ┌──────────┐   ┌──────────┐     │   │
│  │ │/products │   │  /cart   │     │   │
│  │ │useEffect:│   │useEffect:│     │   │
│  │ │ register │   │ register │     │   │
│  │ │ search   │   │  cart    │     │   │
│  │ │  tools   │   │  tools   │     │   │
│  │ └──────────┘   └──────────┘     │   │
│  └──────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

## Installation

```bash
# In your Next.js project
npx webmcp init

# Or install globally
npm install -g @webmcp/cli
webmcp init
```

## Usage

### 1. Initialize WebMCP

```bash
webmcp init
```

This creates:
- `lib/webmcp.ts` - Core implementation
- `hooks/useWebMCP.ts` - React hook
- `components/WebMCPProvider.tsx` - Provider component

### 2. Define Tools

```typescript
// lib/webmcp.ts
export const searchProductsTool = {
  name: "searchProducts",
  description: "Search for products",
  execute: async (params) => {
    return dispatchAndWait("searchProducts", params, "Search completed");
  },
  inputSchema: {
    type: "object",
    properties: {
      query: { type: "string" }
    },
    required: ["query"]
  },
  annotations: { readOnlyHint: "true" }
};
```

### 3. Register in Components

```tsx
// app/products/page.tsx
"use client";

import { useEffect, useState } from "react";
import { registerProductTools, unregisterProductTools } from "@/lib/webmcp";

export default function ProductsPage() {
  const [results, setResults] = useState([]);
  const [completedRequestId, setCompletedRequestId] = useState(null);

  // Signal completion after render
  useEffect(() => {
    if (completedRequestId) {
      window.dispatchEvent(
        new CustomEvent(`tool-completion-${completedRequestId}`)
      );
      setCompletedRequestId(null);
    }
  }, [completedRequestId]);

  // Register tools + listen for events
  useEffect(() => {
    const handleSearch = (event: CustomEvent) => {
      const { requestId, query } = event.detail;
      // Perform search
      setResults(searchProducts(query));
      if (requestId) setCompletedRequestId(requestId);
    };

    window.addEventListener("searchProducts", handleSearch);
    registerProductTools();

    return () => {
      window.removeEventListener("searchProducts", handleSearch);
      unregisterProductTools();
    };
  }, []);

  return <div>{/* Product UI */}</div>;
}
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `webmcp init` | Initialize WebMCP in project |
| `webmcp add-tool <name>` | Add new tool definition |
| `webmcp generate-types` | Generate TypeScript types |
| `webmcp example <type>` | Create example project |

## Tool Types

### Read-Only Tools

```typescript
{
  name: "viewCart",
  description: "View cart contents",
  annotations: { readOnlyHint: "true" }
}
```

### Mutating Tools

```typescript
{
  name: "addToCart",
  description: "Add item to cart",
  annotations: { readOnlyHint: "false" }
}
```

### Tools with Parameters

```typescript
{
  name: "setFilters",
  inputSchema: {
    type: "object",
    properties: {
      category: { type: "string", enum: ["electronics", "clothing"] },
      maxPrice: { type: "number" }
    }
  }
}
```

## Examples

### E-Commerce

```bash
webmcp example e-commerce
```

Features:
- Product search
- Cart management
- Checkout flow
- Order tracking

### Dashboard

```bash
webmcp example dashboard
```

Features:
- Widget interactions
- Data filtering
- Export functionality
- Real-time updates

### Blog

```bash
webmcp example blog
```

Features:
- Article search
- Comment posting
- Category filtering
- Related articles

## Best Practices

### 1. Tool Naming

Use camelCase verbs that describe the action:
- ✅ `searchProducts`
- ✅ `addToCart`
- ✅ `updateProfile`
- ❌ `product_search`
- ❌ `handleCart`

### 2. Descriptions

Write clear, specific descriptions:
- ✅ "Search for products by name or category"
- ❌ "Search stuff"

### 3. Schema Completeness

Always include descriptions for parameters:

```typescript
properties: {
  query: {
    type: "string",
    description: "The search query to find products by name or category"
  }
}
```

### 4. Contextual Loading

Register tools only when relevant:

```tsx
// Product page
useEffect(() => {
  registerProductTools();
  return () => unregisterProductTools();
}, []);

// Cart page  
useEffect(() => {
  registerCartTools();
  return () => unregisterCartTools();
}, []);
```

### 5. Error Handling

Always handle timeouts and errors:

```typescript
async function execute(params) {
  try {
    return await dispatchAndWait("action", params, "Success", 5000);
  } catch (error) {
    return `Error: ${error.message}`;
  }
}
```

## Browser Support

WebMCP requires browsers that support:
- CustomEvent API
- navigator.modelContext (proposed standard)

For development, use the WebMCP polyfill:

```typescript
import "@webmcp/polyfill";
```

## Resources

- [WebMCP Specification](https://github.com/webmcp/spec)
- [Example Projects](https://github.com/webmcp/examples)
- [React Integration Guide](https://webmcp.dev/react)

## Integration with Other Skills

- **ai-labs-builder**: Use WebMCP to make AI apps agent-accessible
- **mcp-workflow**: Combine with workflow automation
- **gcc-context**: Version control your tool definitions
