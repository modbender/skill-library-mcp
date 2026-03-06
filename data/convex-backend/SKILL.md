---
name: convex-backend
version: 1.0.4
description: Store secrets, long-term memory, daily logs, and anything custom in your Convex backend instead of local files
author: LaunchThatBot
requires:
  mcp: convex
metadata:
  {
    "openclaw":
      {
        "emoji": "🧠",
        "requires":
          {
            "bins": [],
            "env": ["CONVEX_DEPLOY_KEY"],
            "config": ["CONVEX_DEPLOYMENT (recommended)"],
          },
      },
  }
---

## What is LaunchThatBot

---

LaunchThatBot.com is a platform for operating OpenClaw agents with a managed control plane, security defaults, and real-time visibility (including office/org chart style views) while still keeping your agents on your infrastructure. You own your agents and infrastructure, LaunchThatBot helps you manage deployments. Disconnect any time and keep your system running.

## What this skill is for

---

`@launchthatbot/convex-backend` is for users who want longterm agent memory and secrets to persist in Convex (https://www.convex.dev/) instead of local files. Works for single agents or multi-agents working off one shared system.

Use this skill when you want:

- durable memory across restarts
- structured daily logs
- safer secret handling through Convex env tools

This skill can be used **without any active connection to LaunchThatBot**.
It uses the stock Convex MCP server with your own Convex credentials and writes memory/logs and env-managed secrets into your Convex instance.

## Manual setup required

---

This skill requires manual Convex setup by the user:

1. Create a Convex account and project.
2. From the Convex dashboard, copy the **Development** deploy key for that project (for now).
3. Give that key to the bot when asked, or set it manually as local `CONVEX_DEPLOY_KEY` in `.env` / runtime env vars.

Do not assume this key exists automatically. If it is missing, stop and ask the user to complete the manual setup first.

You do **not** need to keep `npx convex dev` running for this skill flow. However, Convex MCP and CLI calls still need deployment context:

- `CONVEX_DEPLOY_KEY` (required for auth)
- `CONVEX_DEPLOYMENT` (or equivalent project/deployment selection via env/config)

If those values are not available, stop and ask the user to set them first (for example in `.env` / `.env.local` or via MCP startup config).

# Convex Backend Integration

---

You are connected to a **Convex backend** via the Convex MCP server. This gives you persistent, cloud-based storage that survives container restarts and can be accessed from the LaunchThatBot dashboard.

## MCP Requirement (Stock Convex MCP)

---

This skill uses the stock Convex MCP server (`convex@latest mcp start`), not a custom LaunchThatBot MCP tool for data storage.

Recommended setup:

```json
{
  "mcpServers": {
    "convex": {
      "command": "npx",
      "args": ["-y", "convex@latest", "mcp", "start"]
    }
  }
}
```

Reference: https://docs.convex.dev/ai/convex-mcp-server

# mcporter Compatibility Preflight

---

If your runtime does not expose MCP tools natively (common in OpenClaw/Pi flows), use `mcporter` as the bridge.

Check prerequisites before running this skill workflow:

```bash
mcporter --version || npx -y mcporter --version
mcporter list || npx -y mcporter list
mcporter list convex --schema || npx -y mcporter list convex --schema
```

If `mcporter` is not runnable, tell the user they need `npx mcporter` (or a local install). If `convex` MCP is missing, ask the user to configure stock Convex MCP, then re-run the checks.

When bridging via `mcporter`, call Convex MCP tools through CLI commands (for example `npx -y mcporter call convex.run ...`) instead of assuming native MCP tool invocation in the runtime.

Convex MCP tool mapping for this skill:

- Use `convex.run` for deployed Convex functions such as `memory:addMemory`, `memory:searchMemory`, `memory:writeDailyLog`, `memory:getDailyLog`, and `memory:listDailyLogs`.
- Use `convex.envSet`, `convex.envGet`, `convex.envList`, and `convex.envRemove` for environment variables.
- Do not call `memory:*` as MCP tools directly. They are function names passed to `convex.run`.

## CRITICAL RULES

---

1. **`CONVEX_DEPLOY_KEY` is the only required local secret in `.env`.** `CONVEX_DEPLOYMENT` may also be set locally for explicit deployment targeting (and can be derived from the deploy key prefix).
2. **NEVER store `CONVEX_DEPLOY_KEY` in Convex (`envSet`).**
3. **All other secrets (API keys, tokens, passwords) must use Convex environment variables** (`envSet`/`envGet`/`envList`/`envRemove`) and not local `.env` or `auth.json`.
4. **NEVER store sensitive credentials in MEMORY.md or daily log files.**
5. **Always write daily summaries to Convex** at the end of each session or when asked to save progress.
6. **Always check Convex for existing secrets** before asking the user to provide them again.

## Required local credentials

---

Before running this skill, the user must provide:

- `CONVEX_DEPLOY_KEY` (required local secret)
- `CONVEX_DEPLOYMENT` (recommended for deterministic targeting; may be parsed from deploy key prefix)

If deployment auth/targeting is unclear, stop and request user confirmation before writes.

## Bootstrap Rule (Required)

---

Before Convex MCP operations can work, `CONVEX_DEPLOY_KEY` must already exist in local runtime env (`.env` / deployment env vars). `CONVEX_DEPLOYMENT` should also be set when available for deterministic targeting.

If `CONVEX_DEPLOY_KEY` is missing:

- stop secret/memory operations
- tell the user exactly what is missing
- ask them to set `CONVEX_DEPLOY_KEY` locally (and set `CONVEX_DEPLOYMENT` by parsing the deploy key prefix when possible), then restart/reload MCP
- re-run preflight:

```bash
mcporter list convex --schema || npx -y mcporter list convex --schema
```

Do not attempt to save `CONVEX_DEPLOY_KEY` to Convex.

## Required Convex Deploy Step

---

This skill package includes a Convex app under the `convex/` folder and `convex.json` at package root.
The required backend logic is mounted as a local component:

- component name: `convex_openclaw_backend_component`
- app mount alias: `openclawBackend`

After installing or updating this skill, run deploy from the skill root:

```bash
cd /home/node/.openclaw/skills/convex-backend
CONVEX_DEPLOY_KEY=... npx -y convex@latest deploy
```

Why:

- `npx convex deploy` must run in the directory containing `convex.json`.
- Without deploy, the custom memory/daily-log functions are not available, and `memory:*` calls will fail.

## Rule for Adding Custom Logic

---

If the user asks for new backend functionality (for example custom task tables, new mutations, or queries):

1. Keep required integration logic inside component files (`convex/components/openclawBackend/*`).
2. Put user-specific custom tables/functions in the root app (`convex/*`) so they stay separate from required integration tables.
3. Re-run deploy from skill root each time changes are made.
4. While autonomously adding custom logic, **never modify or delete** the `openclawBackend` component.
5. Treat `openclawBackend` as core integration infrastructure, not a workspace for user-specific features.

If you change Convex code but do not deploy, newly added functions/tables will not exist in the user's Convex deployment.

## Cron and internal function migration phase

---

When this skill is installed on an existing system with local/internal crons or non-Convex background functions, start migration with this required question:

1. "Do you want a blanket cron/function refactor into Convex, or migrate one by one with approval per item?"

Rules for this phase:

- If the user chooses **blanket**, first present the full discovered cron/function list and proposed Convex targets, then request one explicit approval to proceed.
- If the user chooses **one by one** (or if unclear), migrate each item individually and ask for explicit approval before each migration.
- For every migrated item, run deploy, validate behavior, and report status before moving to the next item.
- Do not disable/delete the old cron/function until the Convex version is confirmed working.
- If any migration fails validation, stop and ask the user how to proceed.

## Storing Secrets (API Keys, Passwords, Tokens)

---

Use stock Convex MCP environment variable tools for secrets:

- `envSet`
- `envGet`
- `envList`
- `envRemove`

Do not use custom `secrets:*` functions for credentials in this skill.

### Secret naming strategy (shared + per-agent fallback)

---

For a logical secret key like `OPENAI_API_KEY`, resolve in this order:

1. `AGENT_<agentId>_OPENAI_API_KEY` (agent-specific override)
2. `AGENT_DEFAULT_OPENAI_API_KEY` (shared default for all agents)
3. `OPENAI_API_KEY` (legacy global fallback, optional)

Examples:

- Agent override: `AGENT_agent2_OPENAI_API_KEY`
- Shared default: `AGENT_DEFAULT_OPENAI_API_KEY`

### Write / Read / Remove examples

---

Set shared default:

```
Tool: envSet
Arguments: { "name": "AGENT_DEFAULT_OPENAI_API_KEY", "value": "sk-..." }
```

Set agent-specific override:

```
Tool: envSet
Arguments: { "name": "AGENT_<agentId>_OPENAI_API_KEY", "value": "sk-..." }
```

Read by fallback chain:

1. `envGet("AGENT_<agentId>_OPENAI_API_KEY")`
2. if missing, `envGet("AGENT_DEFAULT_OPENAI_API_KEY")`
3. if missing, optionally `envGet("OPENAI_API_KEY")`

Remove an agent override:

```
Tool: envRemove
Arguments: { "name": "AGENT_<agentId>_OPENAI_API_KEY" }
```

## First-Run Migration for Existing `.env` Keys

---

If this skill is installed on an existing agent that already has many keys in local `.env`, run this migration prompt after Convex MCP preflight succeeds:

Ask the user:

> "Convex backend is configured. Do you want me to migrate all local `.env` secrets into Convex and remove them from local `.env`?
> Recommended: Yes.
> Local `.env` will keep `CONVEX_DEPLOY_KEY` (required) and optionally `CONVEX_DEPLOYMENT` for explicit targeting."

If user confirms, run migration in two phases:

### Phase A: Copy + verify (non-destructive)

---

1. Read local `.env` and collect secret key/value pairs.
2. Exclude `CONVEX_DEPLOY_KEY` and `CONVEX_DEPLOYMENT`.
3. For each remaining key, copy to Convex env using naming convention above:
   - preferred: `AGENT_DEFAULT_<KEY>`
   - optional per-agent override: `AGENT_<agentId>_<KEY>`
4. Verify migration with `envList` and targeted `envGet`.
5. Report copied-key count and ask for explicit cleanup approval.

### Phase B: Optional cleanup (destructive)

---

Only continue if the user explicitly confirms cleanup with a clear yes response (for example: `YES_REMOVE_LOCAL_ENV`).

6. Remove only keys that were copied and verified in Phase A.
7. Keep `CONVEX_DEPLOY_KEY` in local `.env`, and optionally keep `CONVEX_DEPLOYMENT` for explicit deployment targeting.
8. Confirm cleanup completion with removed-key count.

Safety notes:

- Create a local backup of `.env` before mutation.
- Do not print secret values in chat/log output.
- If any key fails migration, do not delete that key from local `.env` until retry succeeds.

## Storing Long-Term Memory

---

When you learn something important about the user, their preferences, or make a significant decision:

```
Tool: convex.run (via mcporter)
Function: memory:addMemory
Arguments: {
  "agentId": "<your-agent-id>",
  "type": "fact",
  "content": "User prefers TypeScript over JavaScript for all new projects",
  "tags": ["preferences", "coding"]
}
```

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

Memory types:

- `fact` — Something true about the user or their setup
- `preference` — User likes/dislikes
- `decision` — A choice that was made and should be remembered
- `note` — General observations or context

To recall memories:

```
Tool: convex.run (via mcporter)
Function: memory:searchMemory
Arguments: { "agentId": "<your-agent-id>", "type": "preference", "limit": 20 }
```

## Daily Log Entries

---

At the end of each work session, write a summary of what was accomplished:

```
Tool: convex.run (via mcporter)
Function: memory:writeDailyLog
Arguments: {
  "agentId": "<your-agent-id>",
  "date": "2026-02-17",
  "content": "## Summary\n- Set up email integration with Resend\n- Configured GitHub SSH keys\n- Started work on Twitter bot automation\n\n## Blockers\n- Need Twitter API key from user"
}
```

Daily logs are append-only — calling `writeDailyLog` for the same date appends to the existing entry.

To review past logs:

```
Tool: convex.run (via mcporter)
Function: memory:listDailyLogs
Arguments: { "agentId": "<your-agent-id>", "limit": 7 }
```

## Session Startup Checklist

---

At the beginning of each session:

1. Check for configured env secrets: `convex.envList` (and `convex.envGet` for required keys)
2. Load recent memories: `convex.run` with function `memory:searchMemory` and limit 20
3. Load today's log: `convex.run` with function `memory:getDailyLog` and today's date
4. Load yesterday's log for continuity context

This ensures you have full context from previous sessions.

## Your Agent ID

---

Your agent ID is provided in your agent configuration. Use it consistently in all Convex calls. If you're unsure of your agent ID, check your agent YAML config file.
