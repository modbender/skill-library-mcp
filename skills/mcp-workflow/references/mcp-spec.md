# MCP Specification Reference

## Overview

Model Context Protocol (MCP) is an open standard for connecting AI assistants to external data sources and tools.

## Core Concepts

### Resources

Resources are pieces of content identified by URIs:

```
file://path/to/file.md
git://repo/branch/path
https://api.example.com/data
```

### Resource Templates

Dynamic resources with parameters:

```javascript
{
  template: "file://recipes/{cuisine}.md",
  completions: {
    cuisine: ["italian", "mexican", "japanese"]
  }
}
```

### Prompts

Parameterized instructions:

```yaml
name: meal-planner
args:
  cuisine:
    type: string
    completions: [italian, mexican]
messages:
  - role: user
    content: "Plan meals for {cuisine}"
```

### Tools

Executable functions:

```javascript
{
  name: "execute_workflow",
  inputSchema: {
    type: "object",
    properties: {
      workflow: { type: "string" }
    }
  }
}
```

## Protocol Messages

### Initialize

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {
      "name": "client",
      "version": "1.0.0"
    }
  }
}
```

### Resource Request

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "resources/read",
  "params": {
    "uri": "file://recipes/italian.md"
  }
}
```

### Prompt Request

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "prompts/get",
  "params": {
    "name": "meal-planner",
    "arguments": {
      "cuisine": "italian"
    }
  }
}
```

## Data Types

### Text Content

```json
{
  "type": "text",
  "text": "Hello world"
}
```

### Resource Content

```json
{
  "type": "resource",
  "resource": {
    "uri": "file://data.json",
    "mimeType": "application/json",
    "text": "{\"key\": \"value\"}"
  }
}
```

### Image Content

```json
{
  "type": "image",
  "data": "base64encoded...",
  "mimeType": "image/png"
}
```

## Best Practices

1. **Single Responsibility**: Each server should have one clear purpose
2. **Resource Templates**: Use for scalable content serving
3. **Completions**: Provide helpful suggestions
4. **Error Handling**: Return structured errors
5. **Progressive Disclosure**: Start simple, add complexity as needed

## Implementation

### Server Setup

```javascript
const server = new McpServer({
  name: "my-server",
  version: "1.0.0"
});

server.registerResource(...);
server.registerPrompt(...);
server.registerTool(...);

const transport = new StdioServerTransport();
await server.connect(transport);
```

### Client Usage

```javascript
const client = new McpClient();
await client.connect(transport);

const resources = await client.listResources();
const prompts = await client.listPrompts();

const result = await client.callTool("tool-name", args);
```

## Resources

- [Official Spec](https://modelcontextprotocol.io/specification/2025-06-18)
- [Example Servers](https://github.com/modelcontextprotocol/servers)
- [SDK Documentation](https://github.com/modelcontextprotocol/sdk)
