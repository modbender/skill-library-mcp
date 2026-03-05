# Roadmap - v0.3

Prioritized list of work items for the next release cycle. Each item maps to a GitHub issue (create with `bash scripts/create-roadmap-issues.sh` once `gh` is authenticated).

## High priority

### 1. Add unit test suite for core healing logic
**Labels:** `priority:high`, `type:testing`

The plugin has zero tests. All core logic - failure detection, model fallback selection, session patching, state management - is untested. This is the single highest-priority gap because every other change risks regressions without a safety net.

Scope:
- Set up a test runner (vitest or similar)
- Add `tsconfig.json` for type-checking
- Unit tests for `isRateLimitLike`, `isAuthScopeLike`, `pickFallback`, `patchSessionModel`, `loadState`/`saveState`, `isConfigValid`, backup lifecycle
- Integration test for `agent_end` and `message_sent` event handlers
- CI: add `test` script to `package.json`

### 2. Add TypeScript build pipeline and type-checking
**Labels:** `priority:high`, `type:infra`

No `tsconfig.json` exists. No build step or type-check. TypeScript errors could ship undetected.

Scope:
- Add `tsconfig.json` with strict mode
- Add build/typecheck script to `package.json`
- Ensure `tsc --noEmit` passes
- Verify the plugin still loads correctly

### 3. Implement structured plugin health monitoring and auto-disable
**Labels:** `priority:high`, `type:feature`

The `disableFailingPlugins` feature is a stub (`index.ts` lines 391-403). Needs proper implementation when `openclaw plugins list --json` becomes available.

Scope:
- Parse structured output from `openclaw plugins list --json`
- Auto-disable failing plugins (with cooldown)
- Create GitHub issue with error context
- Guardrail: never disable self
- Blocked on: `openclaw plugins list --json` API

## Medium priority

### 4. Expose self-heal status for external monitoring
**Labels:** `priority:medium`, `type:feature`

External tools cannot query self-heal state. No way to check which models are in cooldown, heal history, or WhatsApp status without reading the raw state file.

Scope:
- Register a plugin command or API endpoint returning JSON status
- Include: active cooldowns, WhatsApp status, recent heal actions

### 5. Emit structured observability events for heal actions
**Labels:** `priority:medium`, `type:observability`

No structured events emitted. Monitoring systems cannot track heal actions or failure rates.

Scope:
- Emit events via `api.emit()` for: model cooldown, session patching, WhatsApp restart, cron disable, plugin disable
- Include timestamp, action type, and context in each event

### 6. Add dry-run mode for safe validation
**Labels:** `priority:medium`, `type:dx`

No way to test healing logic without executing real side-effects.

Scope:
- `dryRun: boolean` config option
- Log all actions without executing them
- State tracking still updates for validation

## Low priority

### 7. Active model recovery probing
**Labels:** `priority:low`, `type:feature`

Models in cooldown are recovered passively only. If a model recovers early, the plugin still uses the fallback until the full cooldown expires.

Scope:
- Periodic probe (e.g., every 5 minutes) testing cooldown models
- Early recovery detection and cooldown clearing
- Configurable and respects rate limits

### 8. Config hot-reload without gateway restart
**Labels:** `priority:low`, `type:dx`

Plugin config is read once at startup. Changes require a full gateway restart.

Scope:
- Watch for config changes or support reload command
- Re-read and update internal variables
- Reject invalid config gracefully
