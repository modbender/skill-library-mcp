# WebMCP Specification Reference

## Overview

WebMCP (Web Model Context Protocol) is a proposed web standard that enables AI agents to interact with web applications through structured tools.

## Core API

### navigator.modelContext

```typescript
interface Navigator {
  modelContext?: {
    registerTool(tool: WebMCPTool): void;
    unregisterTool(name: string): void;
  };
}
```

## Tool Structure

```typescript
interface WebMCPTool {
  name: string;
  description: string;
  execute: (params: Record<string, unknown>) => Promise<string | object>;
  inputSchema: JSONSchema;
  outputSchema?: JSONSchema;
  annotations?: {
    readOnlyHint?: string;
    title?: string;
    openWorldHint?: string;
  };
}
```

## JSON Schema

Tools use standard JSON Schema for input/output validation:

```typescript
{
  type: "object",
  properties: {
    query: {
      type: "string",
      description: "Search query"
    },
    maxResults: {
      type: "number",
      minimum: 1,
      maximum: 100
    }
  },
  required: ["query"]
}
```

## Annotations

### readOnlyHint

- `"true"` - Tool only reads data
- `"false"` - Tool modifies state

Used by agents to decide whether to ask for confirmation.

### title

Human-readable title for the tool.

### openWorldHint

Indicates the tool can handle open-ended inputs.

## Event Flow

```
1. Agent calls tool
2. Browser invokes execute()
3. execute() dispatches CustomEvent
4. React component receives event
5. Component updates state
6. Component signals completion
7. execute() resolves
8. Agent receives result
```

## Security Considerations

1. **Input Validation**: Always validate parameters using JSON Schema
2. **Timeout Handling**: Set reasonable timeouts for tool execution
3. **Error Handling**: Don't expose sensitive information in errors
4. **CSRF Protection**: Validate requests if modifying state
5. **Rate Limiting**: Prevent abuse of expensive operations

## Browser Support

WebMCP requires:
- CustomEvent API
- navigator.modelContext (proposed)

Polyfill available for unsupported browsers.

## Resources

- [WebMCP Proposal](https://github.com/webmcp/spec)
- [MCP Specification](https://modelcontextprotocol.io/)
