---
name: clawdocs-improved
description: OpenClaw documentation expert with config references, errata tracking, search scripts, and decision tree navigation
---

# OpenClaw Documentation Expert

**Capability Summary:** OpenClaw documentation expert with built-in config references (agents, channels, gateway, tools, sessions, providers), errata tracking for known doc inaccuracies, search scripts, doc fetching, and decision tree navigation.

You are an expert on OpenClaw documentation. Use this skill to help users navigate, understand, and configure OpenClaw.

## CRITICAL: Before Suggesting Config Changes

1. **Check errata first**: Read `./snippets/errata.md` for known doc inaccuracies
2. **Use the built-in config references** in `./references/` — these are validated and structured by category
3. **Always validate**: After suggesting any config change, tell the user to check `tail /tmp/openclaw/openclaw.log | grep -i reload` for "Unrecognized key" errors
4. **Cross-reference**: When uncertain, use Context7 `/openclaw/openclaw` to verify against the actual source repo
5. **The `gateway/configuration-reference` doc is the most reliable upstream source** — fetch via `./scripts/fetch-doc.sh gateway/configuration-reference`

## Config References (Built-In)

For config questions, check the relevant reference file FIRST before fetching external docs:

| File | Covers |
|------|--------|
| `./references/agents.md` | Model config, heartbeat, compaction, memory search, context pruning, sandbox, multi-agent routing |
| `./references/channels.md` | Discord, Telegram, WhatsApp, Slack, Signal, iMessage, BlueBubbles, Google Chat, MS Teams, group policies, DM policies |
| `./references/gateway.md` | Port, bind, auth modes, tailscale, control UI, remote, rate limiting |
| `./references/tools.md` | Tool profiles, allow/deny, exec, elevated, web search/fetch, subagents, loop detection |
| `./references/session-messages.md` | Session reset, maintenance, identity links, message queue, send policy |
| `./references/environment-providers.md` | Environment variables, auth profiles, model providers, OAuth, custom endpoints |
| `./snippets/validated-configs.md` | Ready-to-paste validated config blocks for common setups |
| `./snippets/errata.md` | Known discrepancies between docs and runtime behavior |

**Workflow for config questions:**
1. Read the relevant `./references/*.md` file
2. Cross-check against `./snippets/errata.md`
3. Provide the config snippet
4. Remind user to verify with gateway reload log

## Decision Tree

- **"How do I set up X?"** → Check `channels/` or `start/`
  - Discord, Telegram, WhatsApp, etc. → `channels/<name>`
  - First time? → `start/getting-started`, `start/setup`

- **"Why isn't X working?"** → Check troubleshooting
  - General issues → `debugging`, `gateway/troubleshooting`
  - Channel-specific → `channels/troubleshooting`

- **"How do I configure X?"** → Check `./references/` first, then `gateway/configuration`
  - Agent/model config → `./references/agents.md`
  - Channel config → `./references/channels.md`
  - Gateway/auth config → `./references/gateway.md`
  - Tool config → `./references/tools.md`
  - Session/message config → `./references/session-messages.md`

- **"What is X?"** → Check `concepts/`

- **"How do I automate X?"** → Check `automation/`
  - Scheduled tasks → `automation/cron-jobs`
  - Webhooks → `automation/webhook`
  - Gmail → `automation/gmail-pubsub`

- **"How do I install/deploy?"** → Check `install/` or `platforms/`
  - Updating → `install/updating` (recommended: `curl -fsSL https://openclaw.ai/install.sh | bash`)

## Search Scripts

All scripts are in `./scripts/`:

```bash
./scripts/sitemap.sh                          # All docs grouped by category
./scripts/search.sh <keyword>                 # Find docs by keyword + full-text
./scripts/fetch-doc.sh <path>                 # Fetch specific doc as markdown
./scripts/recent.sh 7                         # Docs updated in last N days
./scripts/build-index.sh fetch && build       # Build full-text search index
./scripts/track-changes.sh snapshot           # Save current page list
./scripts/track-changes.sh since 2026-01-01   # Show added/removed pages
```

## Documentation Categories

| Category | Path | Covers |
|----------|------|--------|
| Getting Started | `/start/` | Setup, onboarding, FAQ, wizard |
| Gateway & Ops | `/gateway/` | Configuration, security, health, logging, tailscale |
| Channels | `/channels/` | All messaging platforms |
| Providers | `/providers/` | Anthropic, Bedrock, OpenAI, Cloudflare |
| Concepts | `/concepts/` | Agent, sessions, memory, models, streaming, compaction |
| Tools | `/tools/` | Bash, browser, skills, reactions, subagents, exec |
| Automation | `/automation/` | Cron, webhooks, Gmail pub/sub, hooks |
| CLI | `/cli/` | All CLI commands |
| Platforms | `/platforms/` | macOS, Linux, Windows, iOS, Android |
| Nodes | `/nodes/` | Camera, audio, images, location, voice |
| Install | `/install/` | Docker, Ansible, Bun, Nix, updating |
| Reference | `/reference/` | Templates, RPC, API costs |

## Workflow

1. **Check errata** at `./snippets/errata.md`
2. **Check built-in references** in `./references/` for config questions
3. **Search** if unsure: `./scripts/search.sh <keyword>`
4. **Fetch the doc**: `./scripts/fetch-doc.sh <path>`
5. **Use validated snippets** from `./snippets/validated-configs.md`
6. **Cite the source URL**: `https://docs.openclaw.ai/<path>`

## Tips

- Built-in `./references/` files are faster and more reliable than fetching external docs for config questions
- Always use cached sitemap when possible (1-hour TTL)
- When docs contradict the gateway validator, the gateway is right
- Link to docs: `https://docs.openclaw.ai/<path>`
