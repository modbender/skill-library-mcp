---
name: vigil
description: AI agent safety guardrails for tool calls. Use when (1) you want to validate agent tool calls before execution, (2) building agents that run shell commands, file operations, or API calls, (3) adding a safety layer to any MCP server or agent framework, (4) auditing what your agents are doing. Catches destructive commands, SSRF, SQL injection, path traversal, data exfiltration, prompt injection, and credential leaks. Requires npm package vigil-agent-safety (12.3KB, under 2ms latency). Source: github.com/hexitlabs/vigil
---

# Vigil — Agent Safety Guardrails

Validates what AI agents DO, not what they SAY. Drop-in safety layer for any tool-calling agent.

## Prerequisites

This skill requires the `vigil-agent-safety` npm package (12.3KB, Apache 2.0 license):

```bash
npm install vigil-agent-safety
```

- **Source code:** https://github.com/hexitlabs/vigil
- **npm:** https://www.npmjs.com/package/vigil-agent-safety
- **The npm package has zero runtime dependencies.** This skill is a wrapper that calls that package.

## Quick Start

```typescript
import { checkAction } from 'vigil-agent-safety';

const result = checkAction({
  agent: 'my-agent',
  tool: 'exec',
  params: { command: 'rm -rf /' },
});

// result.decision === "BLOCK"
// result.reason === "Destructive command pattern"
// result.latencyMs === 0.3
```

## What It Catches

- Destructive commands (rm -rf, mkfs, reverse shells) → BLOCK
- SSRF (metadata endpoints, localhost, internal IPs) → BLOCK
- Data exfiltration (curl to external, .ssh/id_rsa access) → BLOCK
- SQL injection (DROP TABLE, UNION SELECT) → BLOCK
- Path traversal (../../../etc/shadow) → BLOCK
- Prompt injection (ignore instructions, [INST] tags) → BLOCK
- Encoding attacks (base64 decode, eval(atob())) → BLOCK
- Credential leaks (API keys, AWS keys, tokens) → ESCALATE

22 rules. Zero dependencies. Under 2ms per check.

## Modes

```typescript
import { configure } from 'vigil-agent-safety';

// warn = log violations but don't block (recommended to start)
configure({ mode: 'warn' });

// enforce = block dangerous calls
configure({ mode: 'enforce' });

// log = silent logging only
configure({ mode: 'log' });
```

## Use with Clawdbot

Add Vigil as a safety layer for your agent tool calls. The `scripts/vigil-check.js` wrapper lets you validate from the command line:

```bash
# Check a tool call
node scripts/vigil-check.js exec '{"command":"rm -rf /"}'
# → BLOCK: Destructive command pattern

# Check a safe call
node scripts/vigil-check.js read '{"path":"./README.md"}'
# → ALLOW
```

## Policies

Load built-in policy templates:

```typescript
import { loadPolicy } from 'vigil-agent-safety';

loadPolicy('restrictive');  // Tightest rules
loadPolicy('moderate');     // Balanced (default)
loadPolicy('permissive');   // Minimal blocking
```

## CLI

```bash
npx vigil-agent-safety check --tool exec --params '{"command":"ls -la"}'
npx vigil-agent-safety policies
```

## Links

- GitHub: https://github.com/hexitlabs/vigil
- npm: https://www.npmjs.com/package/vigil-agent-safety
- Docs: https://hexitlabs.com/vigil
