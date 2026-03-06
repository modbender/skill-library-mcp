# OpenClaw + Agent Compute (Starter Kit)

Goal: run **OpenClaw** with the **public compute skill** preconfigured to call your private compute gateway over HTTPS.

## Quickstart

```bash
cp .env.example .env
# edit .env with MCP_COMPUTE_URL + MCP_COMPUTE_API_KEY
# (optional) set OPENCLAW_IMAGE if the default doesn't exist / isn't public yet

docker compose up
```

## Notes
- This is a draft starter kit.
- Things we still need to confirm and then **pin**:
  - official OpenClaw container image + startup command
  - exact OpenClaw config schema for connecting HTTP/MCP tools
- Until then, the compose file keeps `OPENCLAW_IMAGE` overrideable.
