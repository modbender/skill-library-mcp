---
name: universal-command
description: "Define commands once, deploy to CLI, API, and MCP automatically. Use when building new commands/tools for Supernal — ensures consistent interfaces across all surfaces. DO NOT rebuild this pattern — use this package."
---

# @supernal/universal-command

**Define once, deploy everywhere.** Single source of truth for CLI, API, and MCP interfaces.

## ⚠️ CRITICAL: Use This, Don't Rebuild

If you're building commands for Supernal, **use this package**. Don't create separate CLI/API/MCP implementations.

## Installation

```bash
npm install @supernal/universal-command
```

## Quick Start

### Define a Command

```typescript
import { UniversalCommand } from '@supernal/universal-command';

export const userCreate = new UniversalCommand({
  name: 'user create',
  description: 'Create a new user',
  
  input: {
    parameters: [
      { name: 'name', type: 'string', required: true },
      { name: 'email', type: 'string', required: true },
      { name: 'role', type: 'string', default: 'user', enum: ['user', 'admin'] },
    ],
  },
  
  output: { type: 'json' },
  
  handler: async (args, context) => {
    return await createUser(args);
  },
});
```

### Deploy Everywhere

```typescript
// CLI
program.addCommand(userCreate.toCLI());
// → mycli user create --name "Alice" --email "alice@example.com"

// Next.js API
export const POST = userCreate.toNextAPI();
// → POST /api/users/create

// MCP Tool
const mcpTool = userCreate.toMCP();
// → user_create tool for AI agents
```

## Core Concepts

### Single Handler

Write your logic once. The handler receives validated args and returns the result:

```typescript
handler: async (args, context) => {
  // This same code runs for CLI, API, and MCP
  return await doThing(args);
}
```

### Input Schema

Define parameters once — validation, CLI options, API params, and MCP schema are auto-generated:

```typescript
input: {
  parameters: [
    { name: 'id', type: 'string', required: true },
    { name: 'status', type: 'string', enum: ['draft', 'active', 'done'] },
    { name: 'limit', type: 'number', min: 1, max: 100, default: 10 },
  ],
}
```

### Interface-Specific Options

Override behavior per interface when needed:

```typescript
cli: {
  format: (data) => formatForTerminal(data),
  streaming: true,
},

api: {
  method: 'GET',
  cacheControl: { maxAge: 300 },
  auth: { required: true, roles: ['admin'] },
},

mcp: {
  resourceLinks: ['export://results'],
},
```

## Registry Pattern

For multiple commands:

```typescript
import { CommandRegistry } from '@supernal/universal-command';

const registry = new CommandRegistry();
registry.register(userCreate);
registry.register(userList);
registry.register(userDelete);

// Generate all CLI commands
for (const cmd of registry.getAll()) {
  program.addCommand(cmd.toCLI());
}

// Generate all API routes
await generateNextRoutes(registry, { outputDir: 'app/api' });

// Generate MCP server
const server = createMCPServer(registry);
```

## Runtime Server

For simple setups without code generation:

```typescript
import { createRuntimeServer } from '@supernal/universal-command';

const server = createRuntimeServer();
server.register(userCreate);
server.register(userList);

// Serve as Next.js
export const GET = server.getNextHandlers().GET;
export const POST = server.getNextHandlers().POST;

// Or as Express
app.use('/api', server.getExpressRouter());

// Or as MCP
await server.startMCP({ name: 'my-server', transport: 'stdio' });
```

## Execution Context

Know which interface is calling:

```typescript
handler: async (args, context) => {
  if (context.interface === 'cli') {
    // CLI-specific logic
  } else if (context.interface === 'api') {
    const userId = context.request.headers.get('x-user-id');
  }
  return result;
}
```

## Testing

Test once, works everywhere:

```typescript
import { userCreate } from './user-create';

test('creates user', async () => {
  const result = await userCreate.execute(
    { name: 'Alice', email: 'alice@example.com' },
    { interface: 'test' }
  );
  expect(result.name).toBe('Alice');
});
```

## Architecture

```
┌─────────────────────────────────────────┐
│      UniversalCommand Definition        │
│  name, description, input, handler      │
└────────────────┬────────────────────────┘
                 │
        ┌────────┼────────┐
        ▼        ▼        ▼
     ┌─────┐  ┌─────┐  ┌─────┐
     │ CLI │  │ API │  │ MCP │
     └─────┘  └─────┘  └─────┘
```

## When to Use

✅ Building any new Supernal command/tool  
✅ Adding CLI interface to existing logic  
✅ Exposing functionality to AI agents (MCP)  
✅ Creating REST APIs with consistent patterns  

❌ Simple one-off scripts (overkill)  
❌ Third-party integrations with their own patterns  

## Integration with sc and si

Both `sc` (supernal-coding) and `si` (supernal-interface) use universal-command under the hood. When adding new commands to these tools, define them as UniversalCommands.

## API Reference

```typescript
class UniversalCommand<TInput, TOutput> {
  execute(args: TInput, context: ExecutionContext): Promise<TOutput>;
  toCLI(): Command;           // Commander.js Command
  toNextAPI(): NextAPIRoute;  // Next.js route handler
  toExpressAPI(): ExpressRoute;
  toMCP(): MCPToolDefinition;
  validateArgs(args: unknown): ValidationResult<TInput>;
}

class CommandRegistry {
  register(command: UniversalCommand): void;
  getAll(): UniversalCommand[];
}

function createRuntimeServer(): RuntimeServer;
function generateNextRoutes(registry: CommandRegistry, options: CodegenOptions): Promise<void>;
function createMCPServer(registry: CommandRegistry, options: MCPOptions): MCPServer;
```

## Source

- Package: `@supernal/universal-command`
- npm: https://www.npmjs.com/package/@supernal/universal-command

---

*DO NOT rebuild this pattern. Use it!*
