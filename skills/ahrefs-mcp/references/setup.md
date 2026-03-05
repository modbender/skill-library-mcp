# Ahrefs MCP Setup Guide

Complete instructions for connecting Ahrefs to AI tools via Model Context Protocol.

## Prerequisites

- Ahrefs account with **Lite plan or higher** (required for remote MCP)
- OR Enterprise account with APIv3 access (for local MCP server)

## Connection URL

Use the **Streamable HTTP** endpoint (recommended):
```
https://api.ahrefs.com/mcp/mcp
```

Legacy SSE endpoint (deprecated in many tools):
```
https://api.ahrefs.com/mcp/mcpSse
```

## Platform-Specific Setup

### Claude Desktop / Web

1. Open Claude settings
2. Navigate to MCP integrations
3. Add new MCP server
4. Enter connection URL: `https://api.ahrefs.com/mcp/mcp`
5. Authorize when prompted
6. Grant permissions to your Ahrefs account

**Detailed guide:** https://docs.ahrefs.com/docs/mcp/reference/claude-desktop-web

### Claude Mobile

1. Open Claude mobile app
2. Go to Settings → Integrations
3. Add MCP server
4. Enter URL: `https://api.ahrefs.com/mcp/mcp`
5. Complete authorization flow

**Detailed guide:** https://docs.ahrefs.com/docs/mcp/reference/claude-mobile

### ChatGPT Web

1. Open ChatGPT settings
2. Navigate to Integrations or Plugins
3. Add custom MCP connection
4. Enter URL: `https://api.ahrefs.com/mcp/mcp`
5. Authenticate with Ahrefs

**Detailed guide:** https://docs.ahrefs.com/docs/mcp/reference/chatgpt-web

### Other MCP-Compatible Tools

Most MCP-compatible AI clients support the remote server connection. Steps typically:
1. Find MCP/integrations settings
2. Add remote server
3. Use URL: `https://api.ahrefs.com/mcp/mcp`
4. Complete OAuth authorization

## Authorization Process

When connecting, you'll see an authorization consent screen:
1. Review requested permissions
2. Approve the connection
3. An API key will be generated automatically (tagged with `MCP` scope)
4. Connection syncs across all your devices

## Verifying Connection

After setup:
1. Check Account settings → API keys in Ahrefs
2. Verify the MCP connection appears with active status
3. Test with a simple query: "Get domain rating for ahrefs.com"

## Managing Connections

### View Active Connections

Go to: https://app.ahrefs.com/account/api-keys

All MCP connections appear with `MCP` scope tag.

### Set Usage Limits

Workspace admins can set monthly API unit limits per key to prevent over-usage:
1. Navigate to API keys report
2. Select MCP connection
3. Set unit limit

### Revoke Connection

To disconnect:
1. Go to API keys report
2. Find the MCP connection
3. Revoke or delete the key

## API Limits and Usage

### Plan Limits

Each plan includes:
- Maximum rows per request
- Monthly API unit allowance

Higher tiers = more units and higher row limits.

### Tracking Usage

Monitor consumption at:
**Account settings → Limits and usage**
https://app.ahrefs.com/account/limits-and-usage/web

### Unit Consumption

API calls consume units from your monthly allowance based on:
- Request type
- Data volume
- Endpoint used

See full pricing guide: https://docs.ahrefs.com/docs/api/reference/limits-consumption

### Enterprise Add-ons

Enterprise customers can purchase additional API unit packages if needed.

## Local MCP Server (Enterprise Only)

If you have Enterprise account with APIv3 access:

1. Clone the repository:
   ```bash
   git clone https://github.com/ahrefs/ahrefs-mcp-server
   ```

2. Follow installation instructions in the repo

3. Configure with your APIv3 credentials

4. Run locally instead of using remote server

**GitHub repository:** https://github.com/ahrefs/ahrefs-mcp-server

## Troubleshooting

### Connection Fails

- Verify you have Lite plan or higher
- Check the URL is exactly: `https://api.ahrefs.com/mcp/mcp`
- Try the legacy SSE endpoint if Streamable HTTP fails
- Ensure your AI tool supports MCP protocol

### Authorization Issues

- Confirm you're logged into Ahrefs
- Check API keys report for active connection
- Revoke and reconnect if needed
- Verify workspace permissions (if using team account)

### API Limit Errors

- Check current usage in Limits and usage
- Wait for monthly reset
- Optimize queries to use fewer units
- Consider upgrading plan or purchasing add-ons (Enterprise)

### Can't Find MCP Settings

Not all AI tools support MCP yet. Verify your tool's documentation for MCP support.

## Terms of Use

- The external MCP server is for **AI client use only** (ChatGPT, Claude, etc.)
- Do NOT use via custom scripts, bridges, or standalone HTTP clients
- For programmatic API access, use the official Ahrefs API: https://docs.ahrefs.com/docs/api/reference/introduction

## Additional Resources

- Full MCP documentation: https://docs.ahrefs.com/docs/mcp/reference/introduction
- Use cases and prompts: https://ahrefs.com/blog/mcp-use-cases/
- API documentation: https://docs.ahrefs.com/docs/api/reference/introduction
- Ahrefs pricing: https://ahrefs.com/pricing
