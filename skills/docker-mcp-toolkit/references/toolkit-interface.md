# Docker MCP Toolkit interface (notes)

Docker MCP Toolkit is integrated into **Docker Desktop**.

## Primary integration surface: `docker mcp` CLI

Key commands discovered locally:

- `docker mcp server ls|enable|disable|inspect|reset`
- `docker mcp tools ls|inspect|call|enable|disable`
- `docker mcp gateway run` (stdio by default; can listen on TCP with flags)

The skill’s default approach is to invoke tools via **`docker mcp tools call`** so OpenClaw workflows can use MCP tools without a separate MCP client integration.

## Dynamic MCP (gateway-provided tools)

Docker’s gateway can expose management tools like:
- `mcp-find`, `mcp-add`, `mcp-config-set`, `mcp-remove`, `mcp-exec`, `code-mode`

If we want OpenClaw to use those, we either:
- call them via `docker mcp tools call <tool>` (if they appear in the tool list), or
- run the gateway in TCP mode and use a real MCP client (pair with `mcporter`).

## TODO

Once Docker Desktop is running on the target host, validate:
- `docker mcp tools --format json ls` output shape
- exact `docker mcp tools call` payload mechanics per tool schema
- whether `docker mcp tools call` reads JSON from stdin (current script assumes yes)
