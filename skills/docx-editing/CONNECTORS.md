# Safe-DOCX MCP Connectors

How to connect the Safe-DOCX MCP server to your AI editor or desktop client.

## Summary

| Property | Value |
|----------|-------|
| Transport | stdio |
| Command | `safe-docx` |
| Args | `[]` |
| API keys | None required |
| Path policy | `~/` and system temp dirs (default) |

## Prerequisite

Install a pinned Safe-DOCX CLI version before configuring the connector:

```bash
npm install -g @usejunior/safe-docx@0.1.2
```

## Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "safe-docx": {
      "command": "safe-docx",
      "args": []
    }
  }
}
```

## Cursor

Add to `.cursor/mcp.json` in your project root:

```json
{
  "mcpServers": {
    "safe-docx": {
      "command": "safe-docx",
      "args": []
    }
  }
}
```

## Notes

- **No API keys** — Safe-DOCX runs locally and does not call external services.
- **Path policy** — By default, only files under the home directory (`~/`) and system temp directories are accessible. Symlinks must resolve to allowed roots.
- **Node.js required** — `safe-docx` requires Node.js 18+ on the host machine.
