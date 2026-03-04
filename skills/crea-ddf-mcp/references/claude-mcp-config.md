# Claude MCP Config

Use this server entry in Claude Desktop MCP config:

```json
{
  "mcpServers": {
    "crea-ddf": {
      "command": "node",
      "args": [
        "/ABSOLUTE/PATH/TO/packages/crea-ddf-mcp/dist/mcp-server.js"
      ],
      "env": {
        "DDF_BASE_URL": "https://your-ddf-api-base/",
        "DDF_AUTH_URL": "https://your-ddf-auth-url/",
        "DDF_TOKEN_GRANT": "client_credentials",
        "DDF_CLIENT_ID": "...",
        "DDF_CLIENT_SECRET": "..."
      }
    }
  }
}
```

If your DDF uses password grant, replace grant/env vars accordingly.
