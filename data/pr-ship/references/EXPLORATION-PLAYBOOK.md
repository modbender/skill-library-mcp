# Exploration Playbook

> Dynamic investigation procedures for PR review. These commands discover the current state
> of the codebase rather than relying on hardcoded file paths or static references.
> All discovery uses `grep`, `find`, `ls`, `wc`, and `git` -- never hardcoded file paths.

---

## 1. Module Identification

For each file in the diff, classify it by its `src/<module>/` path:

```bash
# List all changed files, grouped by module
git diff --name-only <base>...HEAD | grep '^src/' | sed 's|src/\([^/]*\)/.*|\1|' | sort -u
```

If a file is in a channel directory (e.g., `src/telegram/`, `src/discord/`), it's a **leaf module**.
If it's a top-level `src/*.ts` file (e.g., `runtime.ts`, `utils.ts`), treat it as **CRITICAL** -- these have 150-300+ consumers.

---

## 2. Dynamic Risk Classification

Don't rely on static risk tables. Count actual consumers to classify each changed module:

```bash
# Count production files outside <module> that import from it
grep -r "from ['\"].*/<module>/" src/ --include="*.ts" -l | grep -v "/<module>/" | grep -v "\.test\." | wc -l
```

### Risk Tier Thresholds

| Tier | Consumer Count | Action |
| --- | --- | --- |
| CRITICAL | 120+ | Full test suite required. Check all critical path flows. |
| HIGH | 40-119 | Targeted subsystem tests + pre-PR checklist. |
| MEDIUM | 10-39 | Module tests + verify direct callers. |
| LOW | <10 | Local tests + smoke check. |

### Quick Classification for Known Modules

Some modules are structurally stable in their tier. Use these as starting points, but verify with grep if the diff touches exports:

- **Always CRITICAL**: `config/`, `infra/`, `agents/`, `channels/`, `routing/`, `auto-reply/`
- **Always HIGH**: `cli/`, `logging/`, `gateway/`, `plugins/`, `process/`
- **Leaf/LOW to MEDIUM**: Individual channel implementations (`telegram/`, `discord/`, etc.). Most are MEDIUM by consumer count (10-39). Truly isolated ones (`whatsapp/`, `line/`) are LOW. Verify with grep if the diff touches shared types.

---

## 3. Blast Radius Discovery

For each changed file, determine what breaks if it changes:

### Step 1: Identify Exported Symbols

```bash
# Find all exports from the changed file
grep -n "^export " <changed-file>
```

### Step 2: Find Consumers

```bash
# Find all files that import from the changed file's module
grep -r "from ['\"].*/<module>/" src/ --include="*.ts" -l | grep -v "\.test\."
```

### Step 3: Check Barrel Exports

If the changed file's exports are re-exported through an `index.ts` barrel:

```bash
# Check if the module has a barrel
ls src/<module>/index.ts 2>/dev/null

# If yes, check what it re-exports from the changed file
grep "<changed-filename>" src/<module>/index.ts
```

**Barrel amplification**: If the changed export appears in the barrel, ALL consumers of that barrel are potentially affected, not just direct importers.

### Step 4: Cross-Module Dependencies

```bash
# Find which other modules import from this module
grep -r "from ['\"].*/<module>/" src/ --include="*.ts" -l | grep -v "/<module>/" | sed 's|src/\([^/]*\)/.*|\1|' | sort -u
```

---

## 4. Module-Specific Investigation Strategies

When a diff touches files in these modules, run the corresponding investigation:

### `config/`

```bash
# Find the Zod schema for a changed type
grep -r "Schema" src/config/zod-schema*.ts --include="*.ts" -l

# Check if a new config key has a matching Zod schema
# (type file and schema file must stay in sync)
grep -n "<key-name>" src/config/types.*.ts
grep -n "<key-name>" src/config/zod-schema.*.ts

# Check if defaults exist for the changed key
grep -n "<key-name>" src/config/defaults.ts

# Find all consumers of the changed config key
grep -r "<key-name>" src/ --include="*.ts" -l | grep -v "\.test\."
```

**Red flags**: Type without matching schema. Schema without matching type. Missing default. Changed key with no migration rule.

### `agents/`

```bash
# Check tool registration for changed tools
grep -n "registerTool\|defineTool\|openclaw-tools" src/agents/tools/*.ts

# Check tool policy for the changed tool
grep -rn "<tool-name>" src/agents/tool-policy*.ts

# Check system prompt impact
grep -rn "system-prompt\|systemPrompt" src/agents/ --include="*.ts" | head -20

# Check subagent depth/spawn constraints
grep -rn "maxSpawnDepth\|maxChildren\|subagent-depth" src/agents/ --include="*.ts"
```

**Red flags**: Tool registered but no policy. Changed tool not in policy pipeline. System prompt changes without LLM testing.

### `auto-reply/`

```bash
# Check bidirectional deps with agents/
grep -r "from ['\"].*agents/" src/auto-reply/ --include="*.ts" -l
grep -r "from ['\"].*auto-reply/" src/agents/ --include="*.ts" -l

# Check template context consumers
grep -r "MsgContext\|TemplateContext" src/ --include="*.ts" -l | grep -v "\.test\."

# Check thinking/verbose level consumers
grep -r "ThinkLevel\|VerboseLevel" src/ --include="*.ts" -l | grep -v "\.test\."
```

**Red flags**: Changed `MsgContext` type (15+ consumers). Changed `VerboseLevel` enum (breaks session persistence). Reply pipeline changes without fallback path testing.

### `channels/` (any channel module)

```bash
# Verify ChannelPlugin compliance
grep -n "ChannelPlugin\|implements.*Channel" src/<channel>/ --include="*.ts" -r

# Check outbound adapter
ls src/channels/plugins/outbound/<channel>*.ts 2>/dev/null

# Check channel registry
grep -n "<channel>" src/channels/registry.ts

# Check dock metadata
grep -n "<channel>" src/channels/dock.ts 2>/dev/null
```

**Red flags**: Channel capability change without dock update. Missing outbound adapter. Broken ChannelPlugin contract.

### `routing/`

```bash
# Check session key format consumers
grep -r "sessionKey\|session-key\|buildAgentPeerSessionKey\|normalizeAgentId" src/ --include="*.ts" -l | grep -v "\.test\."

# Check route resolution consumers
grep -r "resolveAgentRoute\|resolveRoute\|resolve-route" src/ --include="*.ts" -l | grep -v "\.test\."
```

**Red flags**: Session key format changes ripple to cron, subagents, and all route resolution.

### `gateway/`

```bash
# Check protocol schema for breaking changes
ls src/gateway/protocol/schema/*.ts

# Check startup sequence dependencies
grep -rn "server-startup\|serverStartup\|startGateway" src/gateway/ --include="*.ts" | head -10

# Check auth changes
grep -rn "gateway.auth\|auth.mode\|auth.token" src/ --include="*.ts" -l | head -20
```

**Red flags**: Protocol schema changes break CLI/TUI clients. Startup order changes can break subsystem initialization. Auth changes need `openclaw security audit`.

### `hooks/`

```bash
# Check hook loading pipeline
grep -rn "loadInternalHooks\|loadWorkspaceHookEntries\|registerInternalHook" src/ --include="*.ts" -l

# Check bundled hooks
ls src/hooks/bundled/*/handler.ts 2>/dev/null

# Check hook frontmatter parsing
grep -rn "frontmatter\|HOOK.md" src/hooks/ --include="*.ts"
```

**Red flags**: Hook loading order changes. Missing `HOOK.md` frontmatter. Changed hook registration interface.

### `plugins/`

```bash
# Check plugin discovery
grep -rn "discoverOpenClawPlugins\|openclaw.plugin.json" src/plugins/ --include="*.ts"

# Check plugin SDK contract
grep -rn "definePlugin\|PluginRegistry" src/plugins/ --include="*.ts"

# Check plugin loader
grep -rn "loadOpenClawPlugins\|jiti" src/plugins/ --include="*.ts"
```

**Red flags**: Changed plugin manifest format. Broken `definePlugin()` contract. Discovery path changes.

### `security/`

```bash
# Check SSRF guard patterns
grep -rn "ssrf\|SsrfGuard\|fetchWithSsrf" src/ --include="*.ts" -l

# Check audit patterns
grep -rn "security.*audit\|securityAudit" src/ --include="*.ts" -l

# Check sandbox patterns
grep -rn "sandbox\|safeBins\|trustedBin" src/ --include="*.ts" -l
```

**Red flags**: Any security change requires `openclaw security audit` before PR. SSRF guard bypass. Sandbox escape.

---

## 5. Test Discovery

Tests are co-located with source files. Use algorithmic discovery:

```bash
# Find unit tests for changed files
for f in $(git diff --name-only <base>...HEAD | grep '\.ts$' | grep -v '\.test\.'); do
  test_file="${f%.ts}.test.ts"
  [ -f "$test_file" ] && echo "$test_file"
done

# Find E2E tests for changed modules
for module in $(git diff --name-only <base>...HEAD | grep '^src/' | sed 's|src/\([^/]*\)/.*|\1|' | sort -u); do
  find "src/$module" -name "*.e2e.test.ts" 2>/dev/null
done

# Find test harnesses for the changed module
for module in $(git diff --name-only <base>...HEAD | grep '^src/' | sed 's|src/\([^/]*\)/.*|\1|' | sort -u); do
  find "src/$module" -name "*.test-harness.ts" 2>/dev/null
done

# Discover test helpers
ls src/test-helpers/ src/test-utils/ 2>/dev/null
```

### Test Execution Priority

1. Run co-located unit tests for changed files first
2. Run module-level tests for changed modules
3. For CRITICAL/HIGH modules: run full suite (`pnpm test`)
4. For config changes: run config-specific tests + read-back validation

---

## 6. Red Flags Table

Pattern-based signals that indicate elevated risk, regardless of module:

| Signal | Detection | Why It's Risky |
| --- | --- | --- |
| `async` keyword removed from exported function | `git diff` shows `-async` on export line | Changes return type from `Promise<T>` to `T`. All `await` callers break silently. |
| Barrel `index.ts` modified | `git diff --name-only` includes `index.ts` | All consumers of that module's exports are affected. |
| Cache/memoization pattern changed | Diff contains `WeakMap`, `cache`, `memoize`, `clearCache` | Cache invalidation bugs are subtle and hard to test. |
| Session key format touched | Diff contains `sessionKey`, `buildAgentPeer`, `normalizeAgentId` | Format changes ripple to cron, subagents, route resolution. |
| Enum value changed | Diff modifies `enum` or union literal type | Persisted enum values in sessions/config break on change. |
| `loadConfig()` added in hot path | Diff adds `loadConfig()` in `auto-reply/`, channel send, streaming | Sync disk I/O in hot path. Performance regression. |
| `console.log/warn/error` in runtime code | Diff adds `console.*` outside tests | Must use subsystem logger for runtime paths. |
| Try/catch on primary operation | Diff adds try/catch around core logic (not convenience wrapper) | Swallowing errors on critical paths hides bugs. |
| File locking removed | Diff removes `locked()`, `withLock`, lock wrappers | Race conditions in concurrent session/cron access. |
| `--force` in git operation | Diff or command uses `git push --force` | Data loss risk. Must use `--force-with-lease`. |
| New tool without policy entry | New tool file without matching policy configuration | Tool runs without access controls. |
| Protocol schema changed | Diff touches `gateway/protocol/schema/*.ts` | CLI/TUI client compatibility. Recommend running `pnpm protocol:gen:swift` + `pnpm protocol:check` before PR. |

---

## 7. Pre-PR Command Verification

**Never hardcode build/test commands.** Always source them from the project:

```bash
# Discover available commands from package.json
grep -A1 '"scripts"' package.json | head -30
# Or more specifically:
node -e "const p=require('./package.json'); Object.keys(p.scripts).forEach(k=>console.log(k+': '+p.scripts[k]))"

# Discover CI commands from workflow
grep -n "run:" .github/workflows/ci.yml | head -30
```

### Standard Commands (recommend to the user, do NOT execute)

These are commands the **user** should run before submitting a PR. List them in findings as suggested actions, but do not execute them -- they modify files or run long processes.

- `pnpm build` -- TypeScript compilation
- `pnpm check` -- Format + type check + lint
- `pnpm test` -- Full test suite
- `pnpm check:docs` -- Documentation validation
- `pnpm protocol:check` -- Protocol compatibility
- `pnpm protocol:gen:swift` -- Regenerate Swift protocol (after schema changes, generates files)

### Conditional Recommendations

Recommend these in findings when the corresponding files are in the diff:

- Protocol schema changes: recommend `pnpm protocol:gen:swift && pnpm protocol:check`
- Docs changes: recommend `pnpm check:docs && pnpm format:check -- <changed-doc>`
- Config changes: recommend `pnpm vitest run src/config/`

---

## 8. Cross-Reference Workflow

When investigation reveals a concerning pattern, cross-reference with:

1. **CURRENT-CONTEXT.md** -- Check if a recent release introduced new constraints or gotchas relevant to the changed module
2. **STABLE-PRINCIPLES.md** -- Verify the change doesn't violate safety invariants or common pitfall patterns
3. **ARCHITECTURE-MAP.md** -- Understand the module's position in the hierarchy and its coupling patterns

The exploration playbook produces **evidence**. The reference documents provide **judgment criteria**. The report combines both.
