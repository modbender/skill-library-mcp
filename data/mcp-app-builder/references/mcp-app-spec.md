# MCP App Specification (Authoritative)

This reference defines the required dependencies, server/UI patterns, and build workflow for MCP Apps.

## Critical Dependencies (Exact Versions Required)

```json
{
  "dependencies": {
    "@modelcontextprotocol/ext-apps": "^1.0.0",
    "@modelcontextprotocol/sdk": "^1.24.0",
    "zod": "^4.1.13",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "cors": "^2.8.5",
    "express": "^5.1.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.3.4",
    "vite": "^6.0.0",
    "vite-plugin-singlefile": "^2.3.0",
    "tailwindcss": "^3.4.17",
    "autoprefixer": "^10.4.20",
    "postcss": "^8.4.49",
    "tsx": "^4.19.0",
    "typescript": "^5.9.3"
  }
}
```

## Key Differences from Standard MCP Servers

- UI Output: Text/JSON only -> Visual React components
- Package: `@modelcontextprotocol/sdk` only -> also `@modelcontextprotocol/ext-apps`
- Schema: JSON Schema objects -> Zod schemas directly
- Tool registration: `server.tool()` -> `registerAppTool()`
- Resource registration: `server.resource()` -> `registerAppResource()`
- Server pattern: single instance -> `createServer()` factory per request
- Express setup: manual -> `createMcpExpressApp()` helper
- HTTP handler: `app.post("/mcp", ...)` -> `app.all("/mcp", ...)`

## Workflow Summary

### Phase 1: Understand the App
Ask:
- What data will this visualize?
- What UI pattern (card, chart, table, dashboard, form)?
- What API/data source (REST API, database, generated data)?
- How many tools (start with 1-2)?

### Phase 2: Design Tools With UIs
Each tool needs:
- Tool definition with Zod input schema
- Visual React component for rendering results
- Resource URI linking tool to UI

Example mapping:
- Tool: `get-stock-detail`
- Input: `{ symbol: z.string() }`
- Resource URI: `ui://stock-detail/app.html`
- Component: `StockDetailCard.tsx`

### Phase 3: Project Structure

```
{app-name}/
├── server.ts
├── package.json
├── vite.config.ts
├── tsconfig.json
├── tailwind.config.js
├── postcss.config.js
├── .gitignore
├── src/
│   ├── index.css
│   ├── {tool-name}.tsx
│   └── components/
└── {tool-name}.html
```

### Phase 4: Server Implementation (Required Pattern)

```ts
import {
  registerAppTool,
  registerAppResource,
  RESOURCE_MIME_TYPE,
} from "@modelcontextprotocol/ext-apps/server";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { createMcpExpressApp } from "@modelcontextprotocol/sdk/server/express.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import type { CallToolResult, ReadResourceResult } from "@modelcontextprotocol/sdk/types.js";
import cors from "cors";
import fs from "node:fs/promises";
import path from "node:path";
import { z } from "zod";

// Works both from source (server.ts) and compiled (dist/server.js)
const DIST_DIR = import.meta.filename.endsWith(".ts")
  ? path.join(import.meta.dirname, "dist")
  : import.meta.dirname;

// Resource URIs
const toolUIResourceUri = "ui://tool-name/app.html";

// Server Factory - CRITICAL: New server per request
export function createServer(): McpServer {
  const server = new McpServer({
    name: "App Name",
    version: "1.0.0",
  });

  // Register tool with zod schema (NOT JSON Schema)
  registerAppTool(
    server,
    "tool-name",
    {
      title: "Tool Title",
      description: "When to use this tool...",
      inputSchema: {
        param: z.string().describe("Parameter description"),
      },
      _meta: { ui: { resourceUri: toolUIResourceUri } },
    },
    async ({ param }): Promise<CallToolResult> => {
      const result = await fetchData(param);
      return {
        content: [{ type: "text", text: JSON.stringify(result) }],
        structuredContent: result,
      };
    }
  );

  // Register UI resource
  registerAppResource(
    server,
    toolUIResourceUri,
    toolUIResourceUri,
    { mimeType: RESOURCE_MIME_TYPE },
    async (): Promise<ReadResourceResult> => {
      const html = await fs.readFile(
        path.join(DIST_DIR, "tool-name", "tool-name.html"),
        "utf-8"
      );
      return {
        contents: [
          {
            uri: toolUIResourceUri,
            mimeType: RESOURCE_MIME_TYPE,
            text: html,
          },
        ],
      };
    }
  );

  return server;
}

// HTTP Server - MUST use createMcpExpressApp and app.all
const port = parseInt(process.env.PORT ?? "3001", 10);
const app = createMcpExpressApp({ host: "0.0.0.0" });
app.use(cors());

app.all("/mcp", async (req, res) => {
  const server = createServer();
  const transport = new StreamableHTTPServerTransport({
    sessionIdGenerator: undefined,
  });

  res.on("close", () => {
    transport.close().catch(() => {});
    server.close().catch(() => {});
  });

  try {
    await server.connect(transport);
    await transport.handleRequest(req, res, req.body);
  } catch (error) {
    console.error("MCP error:", error);
    if (!res.headersSent) {
      res.status(500).json({
        jsonrpc: "2.0",
        error: { code: -32603, message: "Internal server error" },
        id: null,
      });
    }
  }
});

app.listen(port, () => {
  console.log(`Server listening on http://localhost:${port}/mcp`);
});
```

### Phase 5: React UI Implementation (Required Pattern)

```tsx
import { StrictMode, useState, useEffect } from "react";
import { createRoot } from "react-dom/client";
import { useApp, useHostStyles } from "@modelcontextprotocol/ext-apps/react";
import "./index.css";

interface ToolData {
  // Define based on tool output
}

function ToolUI() {
  const [data, setData] = useState<ToolData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const { app } = useApp({
    appInfo: { name: "Tool Name", version: "1.0.0" },
    onAppCreated: (app) => {
      app.ontoolresult = (result) => {
        setLoading(false);
        const text = result.content?.find((c) => c.type === "text")?.text;
        if (text) {
          try {
            const parsed = JSON.parse(text);
            if (parsed.error) {
              setError(parsed.message);
            } else {
              setData(parsed);
            }
          } catch {
            setError("Failed to parse data");
          }
        }
      };
    },
  });

  // Apply host CSS variables for theme integration
  useHostStyles(app);

  // Handle safe area insets for mobile
  useEffect(() => {
    if (!app) return;
    app.onhostcontextchanged = (ctx) => {
      if (ctx.safeAreaInsets) {
        const { top, right, bottom, left } = ctx.safeAreaInsets;
        document.body.style.padding = `${top}px ${right}px ${bottom}px ${left}px`;
      }
    };
  }, [app]);

  if (loading) return <LoadingSkeleton />;
  if (error) return <ErrorDisplay message={error} />;
  if (!data) return <EmptyState />;

  return <DataVisualization data={data} />;
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ToolUI />
  </StrictMode>
);
```

### Phase 6: Host CSS Variable Integration

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  margin: 0;
  padding: 0;
  font-family: var(--font-sans, system-ui, -apple-system, sans-serif);
  background: var(--color-background-primary, #ffffff);
  color: var(--color-text-primary, #1a1a1a);
}

.card {
  background: var(--color-background-primary, #ffffff);
  border: 1px solid var(--color-border-primary, #e5e5e5);
  border-radius: var(--border-radius-lg, 12px);
  padding: 1.5rem;
}

.card-inner {
  background: var(--color-background-secondary, #f5f5f5);
  border-radius: var(--border-radius-md, 8px);
  padding: 1rem;
}

.text-secondary {
  color: var(--color-text-secondary, #525252);
}

.text-tertiary {
  color: var(--color-text-tertiary, #737373);
}
```

### Phase 7: Vite Single-File Bundling

```ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { viteSingleFile } from "vite-plugin-singlefile";

export default defineConfig({
  plugins: [react(), viteSingleFile()],
  build: {
    outDir: "dist",
    rollupOptions: {
      input: process.env.INPUT,
    },
  },
});
```

Build scripts (one entry point per tool):

```json
{
  "scripts": {
    "build": "npm run build:tool1 && npm run build:tool2",
    "build:tool1": "INPUT=tool1.html vite build --outDir dist/tool1",
    "build:tool2": "INPUT=tool2.html vite build --outDir dist/tool2",
    "serve": "tsx server.ts",
    "dev": "npm run build && npm run serve"
  }
}
```

## Common Gotchas

- `zod@^4.1.13` is required. Older versions cause `v3Schema.safeParseAsync is not a function` errors.
- `inputSchema` uses Zod directly, not JSON Schema objects.
- Handler args are destructured: `async ({ symbol })` not `async (args)`.
- Use `app.all` (not `app.post`).
- `createServer()` factory is required per request.
- Use `createMcpExpressApp`, not manual Express setup.
- UI must be bundled into a single HTML file with `viteSingleFile`.
- Import `RESOURCE_MIME_TYPE` from `@modelcontextprotocol/ext-apps/server`.
- Call `useHostStyles(app)` in the React UI.

## Testing

1. Build the UI: `npm run build`
2. Start the server: `npm run serve`
3. Expose locally: `npx cloudflared tunnel --url http://127.0.0.1:3001`
4. Connect to Claude/ChatGPT via the tunnel URL
5. Invoke the tool and verify UI renders
