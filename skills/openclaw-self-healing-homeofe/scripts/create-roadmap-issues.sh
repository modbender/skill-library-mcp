#!/usr/bin/env bash
# create-roadmap-issues.sh
#
# Creates v0.3 roadmap issues on GitHub.
# Requires: gh auth login (GitHub CLI authenticated)
#
# Usage: bash scripts/create-roadmap-issues.sh
#   --dry-run   Print commands without executing

set -euo pipefail

REPO="elvatis/openclaw-self-healing-elvatis"
DRY_RUN=false
if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=true
fi

run() {
  if $DRY_RUN; then
    echo "[dry-run] $*"
  else
    "$@"
  fi
}

echo "==> Ensuring labels exist..."
for label in "priority:high" "priority:medium" "priority:low" "type:testing" "type:infra" "type:feature" "type:observability" "type:dx"; do
  run gh label create "$label" -R "$REPO" --force --description "" 2>/dev/null || true
done

echo ""
echo "==> Creating v0.3 roadmap issues..."
echo ""

# --- Issue 1: Unit test suite (high) ---
run gh issue create -R "$REPO" \
  --title "Add unit test suite for core healing logic" \
  --label "priority:high,type:testing" \
  --body "$(cat <<'EOF'
## Summary

The plugin has zero tests. All core logic - failure detection, model fallback selection, session patching, state management - is untested. This is the highest-priority gap because every other change risks regressions without a safety net.

## Scope

- Set up a test runner (vitest or similar, matching openclaw ecosystem conventions)
- Add `tsconfig.json` for type-checking
- Unit tests for:
  - `isRateLimitLike()` - various error string patterns
  - `isAuthScopeLike()` - various auth error patterns
  - `pickFallback()` - model selection with cooldowns
  - `patchSessionModel()` - file I/O, edge cases (missing file, missing key)
  - `loadState()` / `saveState()` - round-trip, missing file, corrupt JSON
  - `isConfigValid()` - valid JSON, invalid JSON, missing file
  - `backupConfig()` / `cleanupPendingBackups()` - lifecycle
- Integration test for the `agent_end` and `message_sent` event handlers
- CI: add a `test` script to `package.json`

## Acceptance criteria

- `npm test` runs and passes
- Coverage for all exported/core functions
- TypeScript type-check passes (`tsc --noEmit`)
EOF
)"

# --- Issue 2: TypeScript build pipeline (high) ---
run gh issue create -R "$REPO" \
  --title "Add TypeScript build pipeline and type-checking" \
  --label "priority:high,type:infra" \
  --body "$(cat <<'EOF'
## Summary

No `tsconfig.json` exists. There is no build step or type-check step. TypeScript errors could ship undetected.

## Scope

- Add `tsconfig.json` with strict mode
- Add build script to `package.json` (compile or type-check only, depending on openclaw plugin loader)
- Ensure `tsc --noEmit` passes cleanly
- Add a `lint` script if not present (consider biome or eslint)
- Verify the plugin still loads correctly after adding the pipeline

## Acceptance criteria

- `npm run build` (or `npm run typecheck`) passes
- No type errors in `index.ts`
EOF
)"

# --- Issue 3: Structured plugin health monitoring (high) ---
run gh issue create -R "$REPO" \
  --title "Implement structured plugin health monitoring and auto-disable" \
  --label "priority:high,type:feature" \
  --body "$(cat <<'EOF'
## Summary

The `disableFailingPlugins` feature is a stub (index.ts lines 391-403). It parses plain-text output with a heuristic grep for "error". This needs a proper implementation once `openclaw plugins list --json` becomes available.

## Scope

- Watch for `openclaw plugins list --json` API availability
- When available: parse structured output, detect `status: "error"` or `status: "crash"`
- Auto-disable the failing plugin (with cooldown to prevent flapping)
- Create a GitHub issue (similar to cron failure healing)
- Add guardrail: never disable self (openclaw-self-healing)
- Respect `pluginDisableCooldownSec` config

## Blocked on

- `openclaw plugins list --json` or equivalent structured API

## Acceptance criteria

- Failing plugins are detected and disabled automatically
- The self-healing plugin never disables itself
- GitHub issue created with error context
- Cooldown prevents repeated disable/enable cycles
EOF
)"

# --- Issue 4: Health status endpoint (medium) ---
run gh issue create -R "$REPO" \
  --title "Expose self-heal status for external monitoring" \
  --label "priority:medium,type:feature" \
  --body "$(cat <<'EOF'
## Summary

External tools (dashboards, other plugins, CLI) cannot query the self-heal plugin state. There is no way to know which models are in cooldown, how many heals have occurred, or the current WhatsApp connection status without reading the raw state file.

## Scope

- Register a plugin command or API endpoint (depends on openclaw plugin API):
  - `openclaw self-heal status` or similar
  - Returns JSON with: cooldown models, WhatsApp status, cron heal history, last heal actions
- Alternatively, write a summary to a well-known status file on each tick

## Acceptance criteria

- Self-heal state is queryable externally
- Output is structured JSON
- Includes: active cooldowns, WhatsApp connection status, recent heal actions
EOF
)"

# --- Issue 5: Observability events (medium) ---
run gh issue create -R "$REPO" \
  --title "Emit structured observability events for heal actions" \
  --label "priority:medium,type:observability" \
  --body "$(cat <<'EOF'
## Summary

The plugin uses `api.logger` for logging but emits no structured events. Monitoring and alerting systems cannot track heal actions, cooldown entries, or failure rates.

## Scope

- Emit structured events via `api.emit()` or equivalent for:
  - `self-heal:model-cooldown` - model put into cooldown (with model ID, reason, duration)
  - `self-heal:session-patched` - session model pin overridden (with session key, old/new model)
  - `self-heal:whatsapp-restart` - WhatsApp gateway restarted (with streak count)
  - `self-heal:cron-disabled` - cron job disabled (with job ID, failure count)
  - `self-heal:plugin-disabled` - plugin disabled (with plugin ID)
- Include timestamp, action type, and context in each event

## Acceptance criteria

- Each heal action emits a structured event
- Events are consumable by other plugins or monitoring tools
- No performance impact on the monitor tick loop
EOF
)"

# --- Issue 6: Dry-run mode (medium) ---
run gh issue create -R "$REPO" \
  --title "Add dry-run mode for safe validation of healing logic" \
  --label "priority:medium,type:dx" \
  --body "$(cat <<'EOF'
## Summary

There is no way to test what the plugin would do without it actually taking healing actions (restarting gateways, disabling crons, patching sessions). A dry-run mode is needed for validation and debugging.

## Scope

- Add a `dryRun: boolean` config option (default: false)
- When enabled: log all actions that _would_ be taken, but do not execute them
- State tracking still updates (to test state transitions) but side-effects are skipped
- Useful for: initial setup validation, debugging, testing new config values

## Acceptance criteria

- `dryRun: true` logs all heal actions without executing them
- Gateway restarts, session patches, cron disables are all skipped in dry-run
- State file still updates to validate state machine logic
EOF
)"

# --- Issue 7: Active model recovery probing (low) ---
run gh issue create -R "$REPO" \
  --title "Add active model recovery probing to shorten cooldown periods" \
  --label "priority:low,type:feature" \
  --body "$(cat <<'EOF'
## Summary

Models in cooldown are currently recovered passively: `pickFallback()` checks `nextAvailableAt` only when a new failure occurs. If a model recovers early, the plugin still uses the fallback until the full cooldown expires.

## Scope

- Add a periodic probe (e.g., every 5 minutes) that tests cooldown models
- Use a lightweight API call (e.g., model info endpoint or small completion)
- If the model responds successfully, remove it from cooldown early
- Configurable probe interval and enable/disable flag
- Respect rate limits during probing (do not cause the very problem we are healing)

## Acceptance criteria

- Cooldown models are probed periodically
- Early recovery is detected and cooldown is cleared
- Probing does not trigger rate limits
- Feature can be disabled via config
EOF
)"

# --- Issue 8: Config hot-reload (low) ---
run gh issue create -R "$REPO" \
  --title "Support configuration hot-reload without gateway restart" \
  --label "priority:low,type:dx" \
  --body "$(cat <<'EOF'
## Summary

Plugin config (`modelOrder`, `cooldownMinutes`, `autoFix.*`) is read once at startup via `api.pluginConfig`. Changing any config value requires a full gateway restart.

## Scope

- Watch for config changes (file watch or periodic re-read)
- Re-read plugin config on change and update internal variables
- Handle edge cases: invalid new config (keep old), partial updates
- Alternatively, support a reload command: `openclaw self-heal reload`

## Acceptance criteria

- Config changes take effect without gateway restart
- Invalid config changes are rejected gracefully (old config preserved)
- Log message confirms reload
EOF
)"

echo ""
echo "==> Done. Created 8 roadmap issues."
echo "    Run 'gh issue list -R $REPO' to verify."
