# INSTALL

## Purpose

Install the `websites-mcp` runtime for this skill. The runtime source is maintained in this repository and copied locally by script. `npm install --ignore-scripts` fetches npm dependencies at install time; Playwright downloads browser binaries on first use.

## Requirements

- `node` + `npm`
- OpenClaw installed

## Steps

1. Create a free Prospairrow account:

- Open `https://app.prospairrow.com`
- Use **Sign in with Google**
- Generate an API key from the dashboard

2. Run install script:

```bash
bash ./scripts/install-runtime.sh
```

This copies repository runtime source to `~/.openclaw/runtime/websites-mcp` and runs `npm install`.

3. Configure OpenClaw server mapping (see `CONFIGURATION.md`).

4. Start runtime:

```bash
cd "$HOME/.openclaw/runtime/websites-mcp"
PROSPAIRROW_API_KEY="..." npm run mcp:writes
```

5. Verify auth and MCP connectivity:

```bash
curl -sS http://127.0.0.1:8799 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $PROSPAIRROW_API_KEY" \
  -d '{"jsonrpc":"2.0","id":1,"method":"websites.list_sites","params":{}}'
```
