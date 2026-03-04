---
name: mcp-app-builder
description: Build new MCP Apps (MCP servers with React UI output) using @modelcontextprotocol/ext-apps and the MCP SDK. Use when asked to scaffold or implement MCP App servers, add UI-rendering tools/resources, or migrate a standard MCP server to an MCP App with Vite single-file UI bundles.
---

# MCP App Builder

## Overview
Create MCP Apps that expose tools with visual React UIs for ChatGPT or Claude. Follow the exact dependency versions and server/UI patterns in `references/mcp-app-spec.md`.

## Workflow
1. Clarify requirements: what data to visualize, UI pattern (card, table, chart, dashboard, form), data source, and how many tools (start with 1-2).
2. Design tools and UI mapping: define tool names, zod input schemas, output shape, and UI resource URIs (`ui://.../app.html`). Map each tool to one React entrypoint and one HTML file.
3. Scaffold the project: start from `assets/mcp-app-template/` when possible, then customize tool names, schemas, and UI. Ensure `package.json` uses the exact versions, plus `tsconfig.json`, `vite.config.ts`, Tailwind + PostCSS, and per-tool build scripts.
4. Implement the server: use `registerAppTool`/`registerAppResource`, zod schemas directly, `createServer()` factory per request, and `createMcpExpressApp` with `app.all("/mcp", ...)`.
5. Implement the UI: use `useApp` + `useHostStyles`, parse tool results, handle loading/error/empty states, and apply safe-area insets.
6. Build and test: run `npm run build`, then `npm run serve`, then verify via a tunnel if needed.

## Hard Requirements
- Use the exact dependency versions listed in `references/mcp-app-spec.md`.
- Use `registerAppTool`/`registerAppResource` and zod schemas directly (not JSON Schema objects).
- Create a new `McpServer` instance per request via `createServer()`.
- Use `createMcpExpressApp` and `app.all("/mcp", ...)`.
- Bundle UI into single-file HTML via `vite-plugin-singlefile`.
- Use host CSS variables for theme compatibility.

## References
- `references/mcp-app-spec.md` (authoritative spec, patterns, code templates, gotchas)
## Assets
- `assets/mcp-app-template/` (ready-to-copy MCP App skeleton with one tool + UI)
