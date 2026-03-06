# Architecture Map

> Structural context for understanding OpenClaw's module system, risk tiers, and critical paths.
> Describes concepts and patterns -- not specific file contents that drift with releases.

---

## 1. System Model: Hub-and-Spoke

OpenClaw follows a hub-and-spoke architecture:

- **Hub**: The gateway process orchestrates startup, configuration, routing, and agent execution
- **Spokes**: Channel implementations (Telegram, Discord, Slack, Signal, WhatsApp, iMessage, Line, Web) connect as leaf modules
- **Core**: Shared infrastructure (`config/`, `infra/`, `routing/`, `agents/`) is consumed by everything
- **Extensions**: Plugins, hooks, and skills extend behavior without modifying core

Messages flow inward from channel spokes through the routing hub to the agent runtime, then responses flow outward through the reply pipeline back to the originating channel.

---

## 2. Module Hierarchy

Modules are organized by dependency depth. Lower-level modules are more foundational and higher-risk.

| Level | Role | Modules |
| --- | --- | --- |
| 0 | **Foundation** -- pure types, config, utilities | `config/`, `shared/`, `utils/` |
| 1 | **Infrastructure** -- logging, process, errors | `infra/`, `logging/`, `process/` |
| 2 | **Routing layer** -- message routing, sessions, channels | `channels/`, `routing/`, `sessions/` |
| 3 | **Agent runtime** -- tool execution, model selection, streaming | `agents/` |
| 4 | **Reply pipeline** -- message orchestration, templating, thinking | `auto-reply/` |
| 5 | **Feature modules** -- memory, cron, hooks, plugins, security, browser, media, TTS | `memory/`, `cron/`, `hooks/`, `plugins/`, `security/`, `browser/`, `media/`, `tts/` |
| 6 | **Integration layer** -- gateway startup, protocol, server methods | `gateway/` |
| 7 | **Entry points** -- CLI, commands, TUI, daemon | `cli/`, `commands/`, `tui/`, `daemon/` |
| leaf | **Channel implementations** -- platform-specific SDK wrappers | `telegram/`, `discord/`, `slack/`, `signal/`, `whatsapp/`, `imessage/`, `line/`, `web/` |

---

## 3. Risk Tier Definitions

Risk tiers are determined by **production consumer count** -- how many files outside the module import from it.

| Tier | Threshold | Meaning | Required Validation |
| --- | --- | --- | --- |
| **CRITICAL** | 120+ prod consumers | Foundation modules. Breaking changes cascade to hundreds of files | Full test suite + all impacted subsystem tests |
| **HIGH** | 40-119 prod consumers | Heavily used infrastructure. Breaking changes affect dozens of files | Targeted subsystem tests + pre-PR checklist |
| **MEDIUM** | 10-39 prod consumers | Moderate reach. Changes affect specific subsystems | Module tests + caller verification |
| **LOW** | <10 prod consumers | Leaf/isolated modules. Changes are self-contained | Local tests + smoke checks |

### Dynamic Tier Discovery

To verify a module's current risk tier, count its external consumers:

```bash
# Count production files outside <module> that import from it
grep -r "from ['\"].*/<module>/" src/ --include="*.ts" -l | grep -v "/<module>/" | grep -v "\.test\." | wc -l
```

### Current Tier Assignments (calibrated Feb 2026)

| Tier | Modules |
| --- | --- |
| CRITICAL | `config` (666), `infra` (321), `agents` (247), `channels` (193), `routing` (149), `auto-reply` (132), top-level `runtime.ts` (309), `utils.ts` (205), `globals.ts` (160) |
| HIGH | `cli` (110), `logging` (93), `gateway` (79), `plugins` (59), `process` (55), `media` (48), `commands` (43), `shared` (40), `wizard` (40) |
| MEDIUM | `sessions` (30), `daemon` (29), `web` (25), `security` (24), `pairing` (23), `telegram` (23), `discord` (21), `markdown` (20), `slack` (18), `browser` (17), `hooks` (15), `signal` (12), `tts` (11), `imessage` (10) |
| LOW | `cron` (8), `plugin-sdk` (8), `compat` (7), `media-understanding` (7), `whatsapp` (7), `memory` (6), `canvas-host` (4), `line` (4), `providers` (4), all other leaf modules |

### High-Blast-Radius Files

These individual files have outsized impact. Changes to them affect many consumers.

| File | What It Exports |
| --- | --- |
| `config/config.ts` | `loadConfig()`, `OpenClawConfig`, `clearConfigCache()` |
| `config/types.ts` | All config type re-exports |
| `config/paths.ts` | `resolveStateDir()`, `resolveConfigPath()`, `resolveGatewayPort()` |
| `config/sessions.ts` | Session store CRUD |
| `infra/errors.ts` | Error utilities |
| `infra/json-file.ts` | `loadJsonFile()`, `saveJsonFile()` |
| `agents/agent-scope.ts` | `resolveDefaultAgentId()`, `resolveAgentWorkspaceDir()` |
| `channels/registry.ts` | `CHAT_CHANNEL_ORDER`, `normalizeChatChannelId()` |
| `routing/session-key.ts` | `buildAgentPeerSessionKey()`, `normalizeAgentId()` |
| `auto-reply/templating.ts` | `MsgContext`, `TemplateContext` types |
| `auto-reply/thinking.ts` | `ThinkLevel`, `VerboseLevel`, `normalizeVerboseLevel()` |
| `logging/subsystem.ts` | `createSubsystemLogger()` |

---

## 4. Critical Path Patterns

These are the core execution flows. Changes to files in these paths have amplified impact.

### Message Lifecycle: Inbound -> Response

```
Channel SDK event
-> channel bot-handlers / monitor
-> channel bot-message-context (normalize to MsgContext)
-> auto-reply/dispatch (dispatchInboundMessage)
-> routing/resolve-route (resolveAgentRoute)
-> auto-reply/reply pipeline (get-reply orchestrator)
   |- media understanding
   |- command auth
   |- session init
   |- directive parsing
   |- inline actions
   `- agent runner execution
-> agent runtime (system prompt, model selection, tools, streaming)
-> reply block pipeline (coalesce)
-> reply dispatcher (buffer + human delay)
-> channel outbound plugin (format + chunk)
-> channel send (API call)
```

### Tool Execution: Tool Call -> Result

```
LLM stream -> tool call extraction
-> tool registry lookup
-> pre-call hooks
-> tool policy pipeline (allow/deny/ask)
-> tool implementation
-> result truncation
-> result returned to LLM stream
```

### Config Loading: JSON -> Validated Object

```
Path resolution -> file read (JSON5, sync)
-> $include resolution -> env substitution
-> Zod validation -> legacy migration
-> defaults application -> runtime overrides
-> path normalization -> memory cache
```

---

## 5. Cross-Module Coupling Patterns

These coupling patterns are architectural -- they're not bugs but require awareness.

### Bidirectional Dependencies

- **`agents/` <-> `auto-reply/`**: By design. `agents/` provides runtime, `auto-reply/` orchestrates it. Changes to agent run result types affect reply delivery.
- **`config/` -> everything**: Config is imported by virtually every module. Config type changes have maximal blast radius.

### Hidden Coupling

- **`auto-reply/thinking.ts` -> `sessions/`**: `VerboseLevel` enum values are persisted in sessions. Changing enum values breaks session persistence.
- **`channels/dock.ts`**: Returns lightweight channel metadata without importing heavy channel code. Must stay in sync with channel capabilities.
- **`infra/outbound/deliver.ts`**: Used by both cron delivery AND message tool sends. Test both paths.
- **`routing/session-key.ts`**: Session key format is consumed by cron sessions, subagent sessions, and all route resolution. Format changes ripple everywhere.

### Barrel Export Amplification

Changes to `index.ts` barrel files amplify blast radius. A renamed or removed export from a barrel affects every consumer of that module, even if only one internal file changed.

### Change Impact Quick Reference

The highest-impact "if you change X, you MUST also check Y" mappings:

| If You Change... | You MUST Also Check... |
| --- | --- |
| `config/zod-schema*.ts` | ALL config validation tests, `config/defaults.ts`, JSON schema generation, every module reading the changed key |
| `config/types*.ts` | Every file importing the changed type (grep!), Zod schema must match |
| `routing/session-key.ts` | Session key parsing everywhere, cron sessions, subagent sessions |
| `agents/pi-tools.ts` | ALL tool tests, tool policy, tool display, sandbox tool policy |
| `agents/pi-embedded-runner/run/` | Entire agent execution path, fallback, compaction, streaming |
| `auto-reply/dispatch.ts` | All channel inbound paths |
| `auto-reply/reply/get-reply.ts` | The entire reply pipeline -- most impactful single file |
| `auto-reply/templating.ts` | `MsgContext` type used by 15+ files |
| `channels/registry.ts` | Channel normalization, routing, dock, all channel references |
| `gateway/protocol/schema/*.ts` | WS protocol compat, CLI client, TUI. User should run `pnpm protocol:gen:swift` before PR |
| Any `index.ts` barrel | All consumers of that module's exports |

For the full list, use EXPLORATION-PLAYBOOK.md's dynamic investigation commands.

---

## 6. Key Design Patterns

| Pattern | Where Used | Implication |
| --- | --- | --- |
| Zod schema + type file pairs | `config/` | Schema and types must stay in sync |
| Channel plugin contract | `channels/plugins/` | All channels implement `ChannelPlugin` interface |
| Hook frontmatter metadata | `hooks/bundled/` | `HOOK.md` frontmatter controls hook loading |
| Plugin discovery + manifest | `plugins/` | `openclaw.plugin.json` manifest drives discovery |
| Session key hierarchy | `routing/` | Hierarchical key format encodes agent/channel/peer |
| Tool policy pipeline | `agents/` | allow/deny/ask flow before tool execution |
| Config caching with `WeakMap` | `routing/` | Cache keyed on config object identity |
| Subsystem logger factory | `logging/` | All runtime logging through `createSubsystemLogger()` |
| File locking for stores | `sessions/`, `cron/` | Concurrent access serialized via lock wrappers |
| `locked()` serialization | `cron/service/` | Cron operations serialized to prevent races |
| Streaming state machine | `agents/pi-embedded-subscribe` | SSE chunk processing with stateful parsing |
| Extension factory pattern | `agents/pi-embedded-runner/` | Extensions loaded as factory functions, not file paths |
| Reply block coalescing | `auto-reply/reply/` | Multiple LLM outputs merged into delivery blocks |
| Outbound adapter pattern | `channels/plugins/outbound/` | Per-channel formatting + chunking |
| Gateway startup sequence | `gateway/` | Ordered subsystem initialization |

---

## 7. Config Architecture

Configuration uses a layered system:

1. **File**: `openclaw.json` (JSON5 format, supports comments and trailing commas)
2. **Includes**: `$include` directives (confined to config directory)
3. **Environment**: `${ENV_VAR}` substitution
4. **Validation**: Zod schemas enforce types
5. **Migration**: Legacy format auto-migration
6. **Defaults**: Module-specific defaults applied
7. **Runtime overrides**: Environment variable overrides
8. **Cache**: In-memory with `clearConfigCache()` invalidation

### Adding a Config Key

1. Add type to `config/types.*.ts`
2. Add Zod schema to `config/zod-schema.*.ts` (must match type)
3. Add default in `config/defaults.ts` if applicable
4. Update `config/schema.hints.ts` for UI labels
5. Add test in `config/config.*.test.ts`
6. If migrating: add rule in `config/legacy.migrations.part-*.ts`
