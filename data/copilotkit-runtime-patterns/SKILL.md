---
name: copilotkit-runtime-patterns
description: Server-side runtime patterns for CopilotKit. Use when setting up CopilotKit runtime endpoints (Express, Hono, Next.js), configuring remote agent endpoints, adding middleware, or securing the runtime. Triggers on backend tasks involving @copilotkit/runtime, CopilotRuntime, agent registration, or API endpoint configuration.
license: MIT
metadata:
  author: copilotkit
  version: "2.0.0"
---

# CopilotKit Runtime Patterns

Server-side runtime configuration patterns. Contains 15 rules across 5 categories.

## When to Apply

Reference these guidelines when:
- Setting up CopilotKit runtime endpoints (Express, Hono, Next.js API routes)
- Configuring CopilotRuntime with service adapters (OpenAIAdapter, etc.)
- Registering agents via remote endpoints (LangGraph, CrewAI)
- Adding middleware for logging, auth, or request modification
- Securing the runtime (CORS, auth, rate limiting)
- Optimizing runtime performance

## Rule Categories by Priority

| Priority | Category | Impact | Prefix |
|----------|----------|--------|--------|
| 1 | Endpoint Setup | CRITICAL | `endpoint-` |
| 2 | Agent Configuration | HIGH | `runner-` |
| 3 | Middleware | MEDIUM | `middleware-` |
| 4 | Security | HIGH | `security-` |
| 5 | Performance | MEDIUM | `perf-` |

## Quick Reference

### 1. Endpoint Setup (CRITICAL)

- `endpoint-express-setup` - Configure Express endpoint with CopilotRuntime and CORS
- `endpoint-hono-setup` - Configure Hono endpoint for edge runtimes
- `endpoint-nextjs-route` - Set up Next.js API route with copilotRuntimeNextJSAppRouterEndpoint

### 2. Agent Configuration (HIGH)

- `runner-inmemory-vs-sqlite` - Use persistent storage for production thread management
- `runner-agent-registration` - Register agents via remoteEndpoints
- `runner-multiple-agents` - Configure routing for multi-agent setups

### 3. Middleware (MEDIUM)

- `middleware-before-request` - Use onBeforeRequest for auth, logging, context injection
- `middleware-after-request` - Use onAfterRequest for response logging and cleanup
- `middleware-error-handling` - Handle errors in middleware without crashing the runtime

### 4. Security (HIGH)

- `security-cors-config` - Configure CORS for your specific frontend origin
- `security-auth-middleware` - Authenticate requests before agent execution
- `security-rate-limiting` - Rate limit by user or API key

### 5. Performance (MEDIUM)

- `perf-streaming-response` - Ensure streaming is not buffered by proxies

## Full Compiled Document

For the complete guide with all rules expanded: `AGENTS.md`
