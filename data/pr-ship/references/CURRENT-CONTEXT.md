# CURRENT-CONTEXT.md — OpenClaw Version-Specific Gotchas

_Auto-updated by fork-manager sync. Last updated: 2026-03-03T23:21 UTC (upstream sync)_

---

## Active Version: 2026.3.3 (Released)

### Behavioral Changes (Breaking / Semantics)

- **BREAKING: Onboarding defaults `tools.profile` to `messaging`** for new local installs. New setups no longer start with broad coding/system tools unless explicitly configured.
- **BREAKING: ACP dispatch enabled by default** unless `acp.dispatch.enabled=false`. Pause routing explicitly if needed.
- **BREAKING: Plugin SDK removed `api.registerHttpHandler()`** — must use `api.registerHttpRoute({ path, auth, match, handler })`.
- **BREAKING: Zalouser no longer depends on external zca CLI binaries.** Use `openclaw channels login --channel zalouser` after upgrade.
- **BREAKING: Node exec approval payloads require `systemRunPlan`.** Rejection on missing plan.
- **BREAKING: Node `system.run` canonical path pinning.** Path-token commands resolve to `realpath`.
- **Secrets/SecretRef overhaul:** 64-target coverage, runtime collectors, fail-fast on active surfaces, non-blocking diagnostics on inactive.
- **Tools/PDF analysis:** First-class `pdf` tool with native Anthropic/Google PDF provider support.
- **Memory/Ollama embeddings:** `memorySearch.provider = "ollama"` support.
- **Telegram/Streaming defaults:** `channels.telegram.streaming` now defaults to `partial` (from `off`).
- **Sessions/Attachments:** Inline file attachment support for `sessions_spawn` with base64/utf8 encoding.
- **Plugin SDK/channel extensibility:** `channelRuntime` exposed on `ChannelGatewayContext`.
- **Plugin hooks/session lifecycle:** `sessionKey` in `session_start`/`session_end` hook events.
- **CLI/Banner taglines:** `cli.banner.taglineMode` (`random`|`default`|`off`) config.
- **Media understanding/audio echo:** `tools.media.audio.echoTranscript` + `echoFormat` config.

### New Gotchas (Things That Now Behave Differently)

- **Diffs guidance loading:** Moved from unconditional prompt-hook injection to plugin companion skill path.
- **Gateway/Plugin HTTP route precedence:** Plugin routes run before Control UI SPA catch-all.
- **Security/auth labels:** `/status` and `/models` no longer expose credential fragments — model-auth-label.ts updated.
- **Discord typing indicators:** Stopped after NO_REPLY/silent runs — affects PRs that check typing state post-reply.
- **Discord slash commands:** Intercepted and registered as native commands — text-based slash PRs must align.
- **Exec heartbeat routing:** Scoped wakes — PRs adding exec triggers must specify agent session keys to avoid cross-agent wakeup.
- **Agents/Compaction:** Staged-summary merge now preserves in-flight task context — compaction PRs must not strip active state.
- **Session startup date grounding:** YYYY-MM-DD placeholders auto-substituted — no need to inject dates manually in AGENTS context.
- **Gateway/Channel health monitor:** Startup-connect grace window prevents restart thrash for channels that just (re)started.
- **Slack/Bolt 4.6+:** Removed invalid `message.channels`/`message.groups` event registrations.
- **Slack/socket auth:** Fail fast on non-recoverable auth errors instead of retry-looping.
- **Feishu/group broadcast dispatch:** Multi-agent group broadcast with observer-session isolation.
- **Feishu/inbound debounce:** Same-chat sender bursts debounced into single dispatch.
- **Voice-call/runtime lifecycle:** `EADDRINUSE` loop prevention, idempotent webhook `start()`.
- **Exec approvals/allowlist:** Regex metacharacters escaped in path-pattern literals.
- **Browser profile defaults:** `openclaw` profile preferred over `chrome` in headless/no-sandbox.
- **Browser act request compatibility:** Legacy flattened `action="act"` params accepted.
- **Docker sandbox bootstrap hardening:** `OPENCLAW_SANDBOX` opt-in parsing, rollback on partial failures.
- **Gateway/WS security:** `ws://` loopback-only by default.
- **Security/Prompt spoofing hardening:** Runtime events use system-prompt context, spoof markers neutralized.
- **Tools/Diffs:** PDF file output support and quality customization.
- **CLI/Config:** `openclaw config validate` with `--json`.

### High-Risk Modules (Frequently Changed in 2026.3.x)

| Module Prefix | Reason |
|---|---|
| src/telegram/ | Streaming defaults, DM topics, multi-account routing, implicit mention forum handling |
| extensions/feishu/ | 20+ fixes: broadcast dispatch, debounce, topic routing, file uploads, typing, probes |
| src/security/ | SSRF guards, ACP sandbox inheritance, prompt spoofing, webhook hardening, fs-safe writes |
| src/browser/ | Extension relay reconnect, profile defaults, CDP startup, act compat, managed tab cap |
| extensions/slack/ | Bolt 4.6 compat, socket auth fail-fast, thread context, session routing, debounce |
| src/gateway/ | Plugin HTTP routes, Control UI basePath, WS security, channel health monitor |
| extensions/line/ | Auth boundary hardening synthesis, media download, context/routing, status/config |
| src/agents/ | Compaction continuity, skills runtime loading, subagent sessions |
| src/sandbox/ | Bootstrap boundary hardening, workspace mount perms, Docker setup commands |
| src/cli/ | Config validate, banner taglines, browser timeout |

### Pre-PR Checklist Additions (Version-Specific)

- **Node exec PRs:** Must include `systemRunPlan` in approval payloads and accept canonical paths.
- **Browser PRs:** Check profile defaults (openclaw vs chrome), act request format compatibility, CDP startup diagnostics.
- **Feishu PRs:** Multi-account routing, rich-text post parsing, docx API changes, media type classification.
- **Telegram PRs:** DM topic routing, reply media context, outbound chunk splitting.
- **Docker PRs:** Sandbox opt-in parsing, socket paths, health check probes, systemd container detection.
- **Cron PRs:** Light bootstrap mode, announce delivery status, session routing for reminders.
- **Security PRs:** Prompt spoofing neutralization, WS loopback enforcement, webhook path validation.

---

## Recent Behavioral Changes (Rolling Window: Last 4 Versions)

### 2026.3.3

- **4 BREAKING changes:** Onboarding tools.profile=messaging default, ACP dispatch enabled by default, plugin SDK registerHttpHandler removed, Zalouser native zca-js.
- **Secrets/SecretRef overhaul** with 64-target coverage and fail-fast semantics.
- **LINE synthesis mega-fixes:** Auth boundary, media download, context/routing, status/config (9 merged synthesis PRs).
- **Feishu 20+ fixes:** Broadcast dispatch, debounce, topic routing, file uploads, typing, probes.
- **Security hardening wave:** ACP sandbox inheritance, SSRF guards, prompt spoofing, fs-safe writes, webhook req hardening, skills archive extraction.
- **Telegram streaming defaults** to `partial`, implicit mention forum handling.
- **Slack/Bolt 4.6+** message event compat, socket auth fail-fast, debounce routing.
- **Security/auth labels (#33262):** Token/API-key snippets removed from `/status` and `/models` — PRs touching model-auth-label.ts must not re-expose credential fragments.
- **Gateway/session agent discovery (#32831):** Disk-scanned agent IDs included in `listConfiguredAgentIds` even when `agents.list` is configured.
- **Discord mega-wave:** Presence defaults (online on ready), typing cleanup after NO_REPLY, mention formatting+rewrites, media SSRF CDN allowlist, chunk ordering/retry, voice messages JSON upload, Opus→opusscript fallback, slash command native registration, thread session lifecycle reset on archive, audit wildcard fix, inbound debouncer bot-own skip.
- **Telegram/DM draft finalization (#32118):** Requires verified final-text emission before marking delivered; falls back to normal send.
- **Telegram/draft preview boundary (#33169):** Answer-lane boundary stabilization; NO_REPLY lead-fragment suppression.
- **Telegram/device pairing notifications (#33299):** Auto-arm on `/pair qr`, auto-ping on new requests.
- **Exec heartbeat routing (#32724):** Heartbeat wakes scoped to agent session keys — unrelated agents no longer woken.
- **Agents/Compaction continuity (#8903):** Staged-summary merge preserves active task status, batch progress, latest user request.
- **Agents/Session startup date grounding (#32381):** `YYYY-MM-DD` placeholders in AGENTS context substituted at startup and post-compaction.
- **Discord/allowBots mention gating:** `allowBots: "mentions"` only accepts bot messages that mention the bot.
- **Tools/Diffs guidance loading (#32630):** Moved from unconditional prompt-hook to plugin companion skill path.

### 2026.3.2

- **OpenAI Responses WS-first default** with SSE fallback and warm-up option.
- **Telegram DM topics** with per-DM config and topic-aware routing.
- **Subagent typed completion events** (`task_completion`) replacing system-message handoff.
- **Node exec canonical path pinning** and `systemRunPlan` requirement.
- **Browser profile defaults** prefer `openclaw` in headless environments.
- **Docker/Container probes** (`/healthz`, `/readyz`) and sandbox bootstrap hardening.

### 2026.2.27

- **German locale** support in Web UI.
- **Discord thread lifecycle** inactivity-based controls.
- **Android nodes** camera, device, notifications actions.
- **Security** webhook rate-limit state bounding.

### 2026.2.26

- **Heartbeat `directPolicy` reverted** back to `allow` (was `block` in 2026.2.24-25).
- **Secrets management** workflow (`audit`, `configure`, `apply`, `reload`).
- **OpenAI Codex** WebSocket-first transport.
- **Agent binding CLI** (`openclaw agents bindings/bind/unbind`).

---

## Foundational Gotchas (Always Apply)

- **Package manager:** Always use `pnpm` — not `npm`, not `bun`. Build: `pnpm build`. Install: `pnpm install`.
- **Branch force push:** Use `--force-with-lease`, never `--force`.
- **PM2 for gateway:** `pm2 restart openclaw` — never `kill <pid>` or `systemctl restart`.
- **Test files:** Must be co-located with source as `<module>.test.ts` — not in a `__tests__/` dir.
- **No `any` types** in production code paths. TypeScript strictness applies.
- **Channel plugins must remain stateless across reconnects** — no persistent mutable module-level state.
