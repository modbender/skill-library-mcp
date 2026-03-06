---
name: MCP Engineering — Complete Model Context Protocol System
description: Build, integrate, secure, and scale MCP servers and clients. From
  first server to production multi-tool architecture.
---

# MCP Engineering — Complete Model Context Protocol System

Build, integrate, secure, and scale MCP servers and clients. From first server to production multi-tool architecture.

## When to Use

- Building an MCP server (any language)
- Integrating MCP tools into an AI agent
- Debugging MCP connection/auth issues
- Designing multi-server architectures
- Securing MCP endpoints for production
- Evaluating which MCP servers to use

---

## Phase 1: MCP Fundamentals

### What MCP Is
Model Context Protocol = standardized way for AI agents to call external tools. Think of it as "USB for AI" — one protocol, any tool.

### Architecture
```
Agent (Client) ←→ MCP Transport ←→ MCP Server ←→ External Service
                   (stdio/HTTP)      (your code)    (API, DB, file system)
```

### Core Concepts
| Concept | What It Does | Example |
|---------|-------------|---------|
| **Server** | Exposes tools, resources, prompts | A server wrapping the GitHub API |
| **Client** | Discovers and calls server capabilities | OpenClaw, Claude Desktop, Cursor |
| **Tool** | A callable function with typed params | `create_issue(title, body, labels)` |
| **Resource** | Read-only data the agent can access | `file://workspace/config.json` |
| **Prompt** | Reusable prompt templates | `summarize_pr(pr_url)` |
| **Transport** | How client↔server communicate | stdio (local) or HTTP+SSE (remote) |

### Transport Decision
| Factor | stdio | HTTP/SSE | Streamable HTTP |
|--------|-------|----------|-----------------|
| Setup complexity | Low | Medium | Medium |
| Multi-client | No | Yes | Yes |
| Remote access | No | Yes | Yes |
| Streaming | Via stdio | SSE | Native |
| Auth needed | No (local) | Yes | Yes |
| Best for | Local dev, single agent | Production, shared | Modern production |

**Rule:** Start with stdio for development. Move to HTTP for production or multi-agent.

---

## Phase 2: Building Your First MCP Server

### Server Brief YAML
```yaml
server_name: "[service]-mcp"
description: "[What this server does in one sentence]"
transport: stdio | http
tools:
  - name: "[verb_noun]"
    description: "[What it does — be specific for LLM tool selection]"
    params:
      - name: "[param]"
        type: "string | number | boolean | object | array"
        required: true | false
        description: "[What this param controls]"
    returns: "[What the tool returns]"
    error_cases:
      - "[When/how it fails]"
resources:
  - uri: "[protocol://path]"
    description: "[What data this exposes]"
external_dependencies:
  - "[API/service this wraps]"
auth_required: true | false
auth_method: "api_key | oauth2 | none"
```

### TypeScript Server Template (stdio)
```typescript
// server.ts — minimal MCP server
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const server = new McpServer({
  name: "my-service",
  version: "1.0.0",
});

// Define a tool
server.tool(
  "get_item",                          // tool name (verb_noun)
  "Fetch an item by ID",               // description (LLM reads this)
  { id: z.string().describe("Item ID") }, // params with descriptions
  async ({ id }) => {
    try {
      const result = await fetchItem(id);
      return {
        content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
      };
    } catch (error) {
      return {
        content: [{ type: "text", text: `Error: ${error.message}` }],
        isError: true,
      };
    }
  }
);

// Define a resource
server.resource(
  "config",
  "config://app",
  async (uri) => ({
    contents: [{ uri: uri.href, mimeType: "application/json", text: JSON.stringify(config) }],
  })
);

// Start
const transport = new StdioServerTransport();
await server.connect(transport);
```

### Python Server Template (stdio)
```python
# server.py — minimal MCP server
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import json

server = Server("my-service")

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="get_item",
            description="Fetch an item by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {"type": "string", "description": "Item ID"}
                },
                "required": ["id"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "get_item":
        result = await fetch_item(arguments["id"])
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    raise ValueError(f"Unknown tool: {name}")

async def main():
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

### Tool Design Rules
1. **Verb-noun naming**: `create_issue`, `search_docs`, `update_config` — never `issue` or `doStuff`
2. **Descriptions are critical**: The LLM picks tools based on descriptions. Be specific. Include when NOT to use.
3. **Granular over god-tools**: `search_issues` + `get_issue` + `create_issue` beats `manage_issues`
4. **Return structured data**: JSON over prose. Let the LLM format for the user.
5. **Error messages for LLMs**: Include what went wrong AND what to try next
6. **Idempotent where possible**: `create_or_update` > `create` (prevents duplicates from retries)
7. **Limit output size**: Paginate or truncate. A 10MB response kills the context window.
8. **Include examples in descriptions**: "Search issues. Example: search_issues(query='bug label:critical')"

### Tool Description Quality Checklist
- [ ] Says what the tool DOES (not just the name restated)
- [ ] Mentions when to use vs. when NOT to use
- [ ] Each param has a description with format hints
- [ ] Return format is documented
- [ ] Edge cases mentioned (empty results, not found, etc.)

---

## Phase 3: HTTP Transport & Production Server

### HTTP Server Template (TypeScript)
```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import express from "express";

const app = express();
app.use(express.json());

const server = new McpServer({ name: "my-service", version: "1.0.0" });
// ... register tools ...

app.post("/mcp", async (req, res) => {
  const transport = new StreamableHTTPServerTransport("/mcp", res);
  await server.connect(transport);
  await transport.handleRequest(req, res);
});

app.listen(3001, () => console.log("MCP server on :3001"));
```

### Auth Patterns

#### API Key (simplest)
```typescript
// Middleware
function authMiddleware(req, res, next) {
  const key = req.headers["x-api-key"] || req.headers.authorization?.replace("Bearer ", "");
  if (!key || !validKeys.has(key)) {
    return res.status(401).json({ error: "Invalid API key" });
  }
  req.userId = keyToUser.get(key);
  next();
}
```

#### OAuth 2.0 (for user-scoped access)
```yaml
# MCP OAuth flow
1. Client requests tool → server returns 401 with auth URL
2. User completes OAuth in browser → gets access token
3. Client stores token, includes in subsequent requests
4. Server validates token, calls external API on user's behalf
```

### Production Checklist
- [ ] Rate limiting per client/key
- [ ] Request validation (schema check before execution)
- [ ] Structured logging (request ID, tool name, latency, status)
- [ ] Health check endpoint (`/health`)
- [ ] Graceful shutdown (finish in-flight requests)
- [ ] Timeout on external calls (don't let tools hang forever)
- [ ] Output size limits (truncate large responses)
- [ ] Error categorization (4xx client vs 5xx server)
- [ ] CORS if browser clients connect
- [ ] TLS in production (always HTTPS)

---

## Phase 4: Client Integration

### OpenClaw Configuration
```yaml
# In openclaw config — stdio server
mcpServers:
  my-service:
    command: "node"
    args: ["path/to/server.js"]
    env:
      API_KEY: "{{env.MY_SERVICE_API_KEY}}"
```

```yaml
# HTTP server
mcpServers:
  my-service:
    url: "https://mcp.myservice.com/mcp"
    headers:
      Authorization: "Bearer {{env.MY_SERVICE_TOKEN}}"
```

### Claude Desktop Configuration
```json
{
  "mcpServers": {
    "my-service": {
      "command": "node",
      "args": ["/path/to/server.js"],
      "env": { "API_KEY": "your-key" }
    }
  }
}
```

### Client-Side Tool Selection
When multiple MCP servers are connected, the agent sees ALL tools. Help the agent pick correctly:

1. **Unique tool names**: Prefix if needed (`github_search` vs `jira_search`)
2. **Clear descriptions**: Disambiguate similar tools across servers
3. **Don't overload**: 20-30 tools max across all servers. Beyond that, agents get confused.

### Multi-Server Architecture
```
Agent
├── github-mcp (code: create_pr, search_code, list_issues)
├── slack-mcp (comms: send_message, search_messages)
├── postgres-mcp (data: query, list_tables)
└── internal-mcp (business: get_customer, update_pipeline)
```

**Principle:** One server per domain. Don't build a mega-server.

---

## Phase 5: Testing MCP Servers

### Test Pyramid
```
        /  E2E  \        Agent actually uses the tool
       / Integration \    Tool calls real API (sandbox)
      /    Unit       \   Business logic without MCP layer
```

### Unit Test Pattern
```typescript
// Test the tool handler directly, no MCP transport
describe("get_item", () => {
  it("returns item when found", async () => {
    mockDb.findById.mockResolvedValue({ id: "123", name: "Test" });
    const result = await getItemHandler({ id: "123" });
    expect(result.content[0].text).toContain("Test");
  });

  it("returns error for missing item", async () => {
    mockDb.findById.mockResolvedValue(null);
    const result = await getItemHandler({ id: "missing" });
    expect(result.isError).toBe(true);
  });

  it("handles API timeout gracefully", async () => {
    mockDb.findById.mockRejectedValue(new Error("timeout"));
    const result = await getItemHandler({ id: "123" });
    expect(result.isError).toBe(true);
    expect(result.content[0].text).toContain("try again");
  });
});
```

### Integration Test with MCP Inspector
```bash
# Use the MCP Inspector to manually test
npx @modelcontextprotocol/inspector node server.js

# Or use mcporter for CLI testing
mcporter call my-service.get_item id=123
mcporter list my-service --schema  # verify tool schemas
```

### Test Checklist Per Tool
- [ ] Happy path returns expected format
- [ ] Missing required params returns clear error
- [ ] Invalid param types return clear error
- [ ] Not-found cases handled (don't throw, return error content)
- [ ] Rate limit / quota exceeded handled
- [ ] Auth failure handled (expired token, invalid key)
- [ ] Large response truncated appropriately
- [ ] Timeout handled (external API slow)
- [ ] Concurrent calls don't interfere

---

## Phase 6: Common MCP Server Patterns

### 1. API Wrapper (most common)
Wrap an existing REST/GraphQL API as MCP tools.
```
External API → MCP Server → Agent
```
**Key decisions:**
- Map 1 API endpoint → 1 MCP tool (usually)
- Simplify params (agent doesn't need every API option)
- Aggregate related calls (e.g., get user + get user's repos = 1 tool)
- Cache where safe (reduce API calls)

### 2. Database Query
```
Database → MCP Server → Agent
```
**Safety rules:**
- Read-only by default. Write tools require explicit opt-in.
- Parameterized queries only. NEVER interpolate agent input into SQL.
- Row limit on all queries (agent can ask for more if needed).
- Schema as a resource (let agent discover tables/columns).

### 3. File System
```
File System → MCP Server → Agent
```
**Safety rules:**
- Sandbox to specific directories. Never allow `../` traversal.
- Read-only by default. Write requires allowlist.
- Size limits on reads. Don't send 1GB files through MCP.

### 4. Multi-Step Workflow
Some tools need to orchestrate multiple steps:
```typescript
server.tool("deploy_service", "Build, test, and deploy a service", {
  service: z.string(),
  environment: z.enum(["staging", "production"]),
}, async ({ service, environment }) => {
  // Step 1: Build
  const buildResult = await build(service);
  if (!buildResult.success) return error(`Build failed: ${buildResult.error}`);

  // Step 2: Test
  const testResult = await runTests(service);
  if (!testResult.success) return error(`Tests failed: ${testResult.summary}`);

  // Step 3: Deploy (only if build + tests pass)
  if (environment === "production") {
    // Extra safety: require confirmation resource
    return {
      content: [{
        type: "text",
        text: `Ready to deploy ${service} to production. Tests: ${testResult.passed}/${testResult.total} passed. Call confirm_deploy to proceed.`
      }]
    };
  }
  const deployResult = await deploy(service, environment);
  return success(`Deployed ${service} to ${environment}: ${deployResult.url}`);
});
```

### 5. Aggregator Server
Combine multiple data sources into unified tools:
```
GitHub + Jira + PagerDuty → DevOps MCP Server → Agent
```
One `get_service_status` tool that queries all three and returns a unified view.

---

## Phase 7: Security & Hardening

### Threat Model
| Threat | Risk | Mitigation |
|--------|------|------------|
| Prompt injection via tool output | Agent executes malicious instructions in API response | Sanitize output, strip HTML/scripts |
| Excessive permissions | Tool has write access it shouldn't | Principle of least privilege per tool |
| Data exfiltration | Agent sends sensitive data to wrong tool | Tool allowlists, audit logging |
| Denial of service | Agent calls tool in infinite loop | Rate limiting, circuit breakers |
| Credential leakage | API keys in tool responses | Strip sensitive fields from output |
| SSRF | Agent provides URL that hits internal network | URL allowlisting, no private IPs |

### Security Checklist
- [ ] Every tool has minimum required permissions
- [ ] Write operations require explicit confirmation or are behind feature flags
- [ ] API keys/secrets NEVER appear in tool responses
- [ ] Output sanitized (no HTML, no executable content)
- [ ] Rate limits per tool AND per client
- [ ] Audit log: who called what tool, when, with what params
- [ ] Input validation before any external call
- [ ] URL parameters validated against allowlist (prevent SSRF)
- [ ] Timeout on every external call (max 30s default)
- [ ] Circuit breaker: disable tool if error rate > 50% for 5 min

### Dangerous Tool Patterns (Avoid)
```
❌ server.tool("execute_sql", ..., async ({ query }) => db.raw(query))
❌ server.tool("run_command", ..., async ({ cmd }) => exec(cmd))
❌ server.tool("fetch_url", ..., async ({ url }) => fetch(url))  // SSRF
❌ server.tool("write_file", ..., async ({ path, content }) => fs.writeFile(path, content))
```

### Safe Alternatives
```
✅ Parameterized queries with allowlisted tables
✅ Predefined commands with argument validation
✅ URL allowlist + no private IP ranges
✅ Write to specific directory + filename validation
```

---

## Phase 8: Debugging & Troubleshooting

### Common Issues

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Tool not appearing in agent | Schema error / server not connected | Check `mcporter list` or client logs |
| "Connection refused" | Server not running or wrong port | Verify process, check port |
| Tool times out | External API slow or hanging | Add timeout, check API health |
| "Invalid params" | Schema mismatch between client/server | Verify schema with `--schema` flag |
| Agent picks wrong tool | Ambiguous descriptions | Rewrite descriptions, add "Use this when..." |
| Agent calls tool in loop | Tool returning confusing error | Return clearer error with "do NOT retry" |
| Large response crashes | No output truncation | Add pagination or character limit |
| Auth errors intermittent | Token expiry | Implement token refresh |

### Debug Workflow
1. **Verify server starts**: `node server.js` — does it start without errors?
2. **List tools**: `mcporter list my-server --schema` — are all tools registered?
3. **Call directly**: `mcporter call my-server.tool_name param=value` — does it return expected output?
4. **Check client config**: Is the server path/URL correct? Are env vars set?
5. **Read client logs**: Most clients log MCP connection errors
6. **Test with Inspector**: `npx @modelcontextprotocol/inspector` for interactive debugging

### Logging Template
```typescript
server.tool("my_tool", description, schema, async (params) => {
  const requestId = crypto.randomUUID().slice(0, 8);
  console.error(`[${requestId}] my_tool called:`, JSON.stringify(params));
  const start = Date.now();
  try {
    const result = await doWork(params);
    console.error(`[${requestId}] my_tool success: ${Date.now() - start}ms`);
    return success(result);
  } catch (error) {
    console.error(`[${requestId}] my_tool error: ${error.message} (${Date.now() - start}ms)`);
    return errorResponse(error.message);
  }
});
```

Note: Use `console.error` for logs in stdio transport (stdout is reserved for MCP protocol).

---

## Phase 9: MCP Server Selection Guide

### Evaluating Existing MCP Servers

Score 0-5 per dimension:

| Dimension | What to Check |
|-----------|--------------|
| **Maintained** | Last commit < 3 months? Issues addressed? Version > 1.0? |
| **Secure** | No raw SQL/exec? Auth implemented? Input validated? |
| **Well-typed** | Full JSON Schema for all tools? Descriptions useful? |
| **Tested** | Has tests? CI passing? |
| **Documented** | Setup instructions? Tool descriptions? Examples? |
| **Lightweight** | Minimal dependencies? Fast startup? |

**Score < 15/30**: Build your own. **Score 15-24**: Use with caution. **Score 25+**: Good to use.

### Popular MCP Server Categories
| Category | Use Case | Examples |
|----------|----------|---------|
| Code | GitHub, GitLab, code search | github-mcp, gitlab-mcp |
| Data | PostgreSQL, SQLite, Snowflake | postgres-mcp, sqlite-mcp |
| Comms | Slack, Discord, email | slack-mcp, gmail-mcp |
| Docs | Notion, Confluence, Google Docs | notion-mcp, gdocs-mcp |
| DevOps | AWS, GCP, Kubernetes, Terraform | aws-mcp, k8s-mcp |
| Search | Brave, Google, vector stores | brave-search, rag-mcp |
| Files | Local FS, S3, Google Drive | filesystem-mcp, s3-mcp |
| CRM | HubSpot, Salesforce | hubspot-mcp, sfdc-mcp |

---

## Phase 10: Architecture Patterns

### Single Agent + Multiple Servers
```
Agent ──┬── github-mcp
        ├── slack-mcp
        ├── postgres-mcp
        └── custom-mcp
```
Best for: Most use cases. Simple, effective.

### Gateway Pattern
```
Agent ── MCP Gateway ──┬── server-1
                       ├── server-2
                       └── server-3
```
Gateway handles: auth, rate limiting, logging, routing.
Best for: Enterprise, multi-tenant, compliance requirements.

### Agent-per-Domain
```
Orchestrator Agent
├── Code Agent (github-mcp, gitlab-mcp)
├── Data Agent (postgres-mcp, analytics-mcp)
└── Comms Agent (slack-mcp, email-mcp)
```
Best for: Complex workflows, specialized agents.

### Tool Count Guidelines
| Total Tools | Recommendation |
|-------------|---------------|
| 1-10 | Great. Agent handles well. |
| 10-20 | Good. Ensure distinct descriptions. |
| 20-30 | Caution. Group by server, review descriptions. |
| 30-50 | Risk. Consider agent-per-domain pattern. |
| 50+ | Dangerous. Agent WILL pick wrong tools. Split or use gateway. |

---

## Phase 11: Publishing MCP Servers

### Package Structure
```
my-mcp-server/
├── src/
│   ├── server.ts        # MCP server entry
│   ├── tools/           # Tool handlers
│   │   ├── search.ts
│   │   └── create.ts
│   ├── auth.ts          # Auth middleware
│   └── config.ts        # Configuration
├── tests/
│   ├── tools.test.ts
│   └── integration.test.ts
├── package.json
├── tsconfig.json
├── README.md            # Setup + tool docs
└── LICENSE
```

### README Template for MCP Servers
```markdown
# [Service] MCP Server

[One sentence: what this enables]

## Quick Start
[3 steps max to get running]

## Tools
| Tool | Description | Params |
|------|-------------|--------|
[Table of all tools]

## Configuration
[Env vars, auth setup]

## Examples
[2-3 real usage examples with agent conversation]
```

### npm Publishing
```bash
# package.json
{
  "name": "@myorg/service-mcp",
  "version": "1.0.0",
  "bin": { "service-mcp": "./dist/server.js" },
  "files": ["dist"],
  "keywords": ["mcp", "model-context-protocol", "ai-tools"]
}

npm publish
```

---

## Quality Rubric (0-100)

| Dimension | Weight | What to Score |
|-----------|--------|--------------|
| Tool design | 20% | Names, descriptions, granularity, params |
| Security | 20% | Auth, input validation, output sanitization, least privilege |
| Reliability | 15% | Error handling, timeouts, circuit breakers |
| Testing | 15% | Unit + integration coverage, edge cases |
| Documentation | 10% | Setup, tool docs, examples |
| Performance | 10% | Response time, output size, caching |
| Maintainability | 10% | Code structure, types, logging |

**Score 0-40**: Not production ready. **40-70**: Usable with caveats. **70-90**: Solid. **90+**: Excellent.

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| God-tool that does everything | Split into focused tools |
| Vague tool descriptions | Write descriptions as if explaining to a new hire |
| No error handling | Every external call wrapped in try/catch |
| Returning raw API responses | Shape output for agent consumption |
| No rate limiting | Add per-tool and per-client limits |
| Ignoring output size | Paginate or truncate responses |
| Hardcoded credentials | Use env vars or secret manager |
| No logging | Can't debug what you can't see |
| Testing only happy path | Test errors, timeouts, edge cases |
| Building before checking | Search for existing MCP server first |

---

## Natural Language Commands

- "Build an MCP server for [service]" → Use Phase 2 templates
- "Add a tool to my MCP server" → Follow tool design rules
- "Secure my MCP server" → Phase 7 checklist
- "Debug MCP connection issue" → Phase 8 workflow
- "Evaluate this MCP server" → Phase 9 scoring
- "Design multi-server architecture" → Phase 10 patterns
- "Publish my MCP server" → Phase 11 structure
- "Convert REST API to MCP" → Phase 6 Pattern 1
- "Add auth to my MCP server" → Phase 3 auth patterns
- "Test my MCP server" → Phase 5 checklist
- "How many tools is too many?" → Phase 10 tool count table
- "Review my tool descriptions" → Phase 2 quality checklist
