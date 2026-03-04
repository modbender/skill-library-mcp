# @launchthatbot/convex-backend

## What is LaunchThatBot

LaunchThatBot is a platform for operating OpenClaw agents with a managed control plane, security defaults, and real-time visibility (including office/org chart style views) while still keeping your agents on your infrastructure.

## What this skill is for

`@launchthatbot/convex-backend` is for users who want longterm agent memory and secrets to persist in Convex (https://www.convex.dev/) instead of local files. Works for single agents or multi-agents working off one shared system.

Use this skill when you want:

- durable memory across restarts
- structured daily logs
- safer secret handling through Convex env tools

This skill can be used **without any active connection to LaunchThatBot.com**.
It uses the stock Convex MCP server (https://docs.convex.dev/ai/convex-mcp-server) with your own Convex credentials and writes memory/logs and env-managed secrets into your Convex instance.

## Manual setup required

This integration is intentionally a manual setup flow. Before the bot can use this skill, the user must:

1. Create their own Convex account and project.
2. Open that project and copy the **Development** deploy key (for now).
3. Provide that key to the bot during setup, or set it manually as `CONVEX_DEPLOY_KEY` in local `.env` / runtime env vars.

Without a valid Development deploy key, Convex MCP bootstrap and deploy commands will fail.

You do **not** need to keep `npx convex dev` running for this workflow. But Convex MCP and CLI still need deployment context (`CONVEX_DEPLOY_KEY` plus `CONVEX_DEPLOYMENT` or equivalent env/config selection).

## Base component (core integration)

The required integration backend is mounted as a local Convex component:

- component id: `convex_openclaw_backend_component`
- app alias: `openclawBackend`
- Convex local component docs: https://docs.convex.dev/components/authoring#local-components

This core component holds the minimum required schema + logic for replacing stock OpenClaw memory and daily-log behavior.

Do not modify or delete this base component when adding user-specific logic.

## Custom tables and bespoke logic

Users can still add custom domain logic freely:

- tasks table
- projects table
- automation tables and workflows

Those additions should be created in root `convex/*` (or additional custom components if needed), not by editing the base `openclawBackend` component.

## Before vs After

### Before this skill

- OpenClaw commonly writes secrets to local `.env` or similar local files.
- Memory/history is primarily kept in local filesystem artifacts.
- Context and credentials are tied to one machine/container unless you manually sync state.

### After this skill

- `CONVEX_DEPLOY_KEY` remains local in `.env` for MCP bootstrap (`CONVEX_DEPLOYMENT` may also be set locally for explicit targeting).
- All other secrets are read/written through stock Convex env tools (`envSet`, `envGet`, `envList`, `envRemove`), not local plaintext files.
- Memory and daily logs are read/written through Convex (`memory:*`, `writeDailyLog`).
- Agent context persists in your Convex instance and can survive local restarts/redeploys.

## How this skill changes behavior

The skill works by changing the bot's operational instructions:

- It explicitly tells the bot to stop using default local file patterns for secrets/memory.
- It instructs the bot to call stock Convex MCP tools for those operations instead.
- It reinforces this rule every session (check existing backend state first, then write updates to Convex).

So the key mechanism is not a custom LaunchThatBot runtime hook -- it is instruction-level behavior override + MCP tool usage with your own Convex credentials.

## Instructions

1. Run stock Convex MCP server:

```bash
npx -y convex@latest mcp start
```

2. For OpenClaw/Pi-style runtimes, confirm bridge availability:

```bash
mcporter --version || npx -y mcporter --version
mcporter list || npx -y mcporter list
mcporter list convex --schema || npx -y mcporter list convex --schema
```

3. Use Convex operations for persistence (exact MCP tool mapping):
   - store/retrieve secrets via `convex.envSet` / `convex.envGet` / `convex.envList` / `convex.envRemove`
   - call Convex functions via `convex.run` (for example `memory:addMemory`, `memory:searchMemory`, `memory:writeDailyLog`)
   - do not treat `memory:*` as MCP tool names; they are function names passed to `convex.run`

Example (`mcporter` + Convex MCP `run`):

```bash
npx -y mcporter call convex.run --args '{
  "functionName": "memory:addMemory",
  "args": {
    "agentId": "<your-agent-id>",
    "type": "fact",
    "content": "User prefers TypeScript over JavaScript for all new projects",
    "tags": ["preferences", "coding"]
  }
}'
```

4. Deploy the skill's Convex app from the skill root:

```bash
cd /home/node/.openclaw/skills/convex-backend
CONVEX_DEPLOY_KEY=... npx -y convex@latest deploy
```

This package includes `convex.json` + `convex/` functions. Deploy must run from that directory so Convex picks up the app correctly.
Required integration tables/functions are isolated in a mounted local component (`convex_openclaw_backend_component` mounted as `openclawBackend`).

5. Bootstrap rule:
   - `CONVEX_DEPLOY_KEY` must exist locally (`.env` / runtime env vars)
   - set `CONVEX_DEPLOYMENT` locally when available (for example parsed from deploy key prefix) for deterministic targeting
   - never store `CONVEX_DEPLOY_KEY` in Convex
   - if missing, set it locally first, restart MCP/runtime, then continue

6. First-run migration for existing local `.env`:
   - Phase A (non-destructive): copy keys to Convex with `envSet` and verify with `envList` / `envGet`
   - exclude `CONVEX_DEPLOY_KEY` and `CONVEX_DEPLOYMENT` from migration
   - Phase B (destructive): remove local keys only after explicit user approval (for example `YES_REMOVE_LOCAL_ENV`)
   - keep `CONVEX_DEPLOY_KEY` in local `.env` and optionally `CONVEX_DEPLOYMENT`

7. Secret naming fallback:
   - first check `AGENT_<agentId>_<KEY>`
   - then `AGENT_DEFAULT_<KEY>`
   - then optional legacy `<KEY>`

8. When adding custom backend logic (tables/functions):
   - keep required integration logic in `convex/components/openclawBackend/*`
   - add user-specific custom tables/functions in root `convex/*`
   - never modify/delete `openclawBackend` while autonomously building user custom logic
   - re-run `npx -y convex@latest deploy` from the same skill root every time
   - without redeploy, new functions/tables will not exist in deployment

## Security

- Keep `CONVEX_DEPLOY_KEY` in local `.env` for MCP bootstrap; `CONVEX_DEPLOYMENT` may also be stored locally for explicit deployment targeting.
- Never store `CONVEX_DEPLOY_KEY` in Convex.
- Store all other credentials in Convex env vars, not local plaintext files.
- Do not put raw keys/tokens in memory markdown or chat logs.
- Keep secret operations least-privilege and scoped to correct agent.
- Validate MCP runtime/auth context before reading or writing secrets.
- Prefer backend persistence over local ephemeral storage for sensitive state.
- Your data remains in your Convex instance under your credentials and access controls. **LaunchThatBot never sees or touches your secrets.**

## Support

- Website: https://launchthatbot.com
- Discord: https://discord.gg/launchthatbot
