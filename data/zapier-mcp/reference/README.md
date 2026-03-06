# Zapier MCP Reference Files

These files are the source implementations for the Zapier MCP integration in Clawdbot.

## Files

| File | Description |
|------|-------------|
| `zapier-backend.ts` | Gateway RPC handlers (`zapier.status`, `zapier.save`, etc.) |
| `zapier-controller.ts` | UI state management and API calls |
| `zapier-views.ts` | Lit templates for the dashboard UI |

## Installation

These files are included in Clawdbot v2026.1.0+. No manual installation required.

If you need to customize or debug:

1. Backend handlers are in `src/gateway/server-methods/zapier.ts`
2. UI controller is in `ui/src/ui/controllers/zapier.ts`
3. UI views are in `ui/src/ui/views/zapier.ts`

## API Reference

### Backend RPC Methods

```typescript
// Get connection status
zapier.status: {} → { configured, mcpUrl, toolCount, testError }

// Save MCP URL
zapier.save: { mcpUrl } → { success, toolCount, message, error }

// Test connection
zapier.test: { mcpUrl? } → { success, toolCount, error }

// Disconnect
zapier.disconnect: {} → { success, message, error }

// List tools
zapier.tools: {} → { success, tools[], error }
```

### SSE Response Parsing

Zapier returns Server-Sent Events format. The backend parses:

```
event: message
data: {"result":...,"jsonrpc":"2.0","id":1}
```

Extract JSON from the `data:` line.
