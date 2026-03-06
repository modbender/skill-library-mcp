# Stable Principles

> Timeless coding standards for OpenClaw contributions. These principles rarely change.
> Extracted from project conventions and contributor experience.

---

## 1. Testing Guide

### Running Tests

```bash
# Full suite (parallel runner, matches CI)
pnpm test

# Single module (direct vitest for targeted runs)
pnpm vitest run src/config/

# Single file
pnpm vitest run src/config/io.test.ts

# Watch mode
pnpm vitest src/config/io.test.ts

# With coverage
pnpm vitest run --coverage
```

### Test Framework: Vitest

- Config: `vitest.config.ts` at project root
- Mocking: `vi.mock()`, `vi.fn()`, `vi.spyOn()`
- Assertions: `expect()` with Vitest matchers

### Test Patterns

| Pattern      | Example                                |
| ------------ | -------------------------------------- |
| Unit test    | `src/config/io.test.ts`                |
| E2E test     | `src/cli/program.smoke.e2e.test.ts`    |
| Test harness | `src/cron/service.test-harness.ts`     |
| Test helpers | `src/test-helpers/`, `src/test-utils/` |
| Mock file    | `src/cron/isolated-agent.mocks.ts`     |

### CI Pipeline

- **Fail-fast scoping gates run first**: `docs-scope` and `changed-scope` determine whether heavy Node/macOS/Android jobs run.
- **Docs-only PRs skip heavy lanes** and run `check-docs` instead.
- **Node quality gate**: `pnpm check` remains the required type+lint+format gate.
- **Build artifact reuse**: `build-artifacts` builds `dist/` once and downstream jobs consume it.

---

## 2. File Naming Conventions

### Within Modules

```
src/<module>/
├── index.ts                    # Barrel re-exports (public API)
├── types.ts                    # Type definitions
├── *.ts                        # Implementation files
├── *.test.ts                   # Co-located unit tests
├── *.e2e.test.ts               # End-to-end tests
├── *.test-harness.ts           # Reusable test fixtures
├── *.mocks.ts                  # Test mocks
```

### Naming Patterns

| Pattern             | Meaning                             | Example                     |
| ------------------- | ----------------------------------- | --------------------------- |
| `*.test.ts`         | Unit test                           | `io.test.ts`                |
| `*.e2e.test.ts`     | End-to-end test                     | `program.smoke.e2e.test.ts` |
| `*.test-harness.ts` | Reusable test fixture               | `service.test-harness.ts`   |
| `*.mocks.ts`        | Test mock definitions               | `isolated-agent.mocks.ts`   |
| `*.impl.ts`         | Implementation (when barrel exists) | `auto-reply.impl.ts`        |
| `zod-schema.*.ts`   | Zod validation schema               | `zod-schema.agents.ts`      |
| `types.*.ts`        | Domain-specific types               | `types.telegram.ts`         |

### Where to Put New Files

| Adding a...            | Put it in...                                                           |
| ---------------------- | ---------------------------------------------------------------------- |
| New tool               | `src/agents/tools/<tool-name>.ts` + register in `openclaw-tools.ts`    |
| New channel            | `src/<channel>/` + `extensions/<channel>/` for plugin                  |
| New CLI command        | `src/cli/<command>-cli.ts` + `src/commands/<command>.ts`               |
| New config type        | `src/config/types.<section>.ts` + `src/config/zod-schema.<section>.ts` |
| New hook               | `src/hooks/bundled/<hook-name>/handler.ts` + `HOOK.md`                 |
| New gateway RPC method | `src/gateway/server-methods/<method>.ts`                               |
| New test               | Co-locate with source: `src/<module>/<file>.test.ts`                   |

---

## 3. Safety Invariants (Never Violate)

1. Never call `loadConfig()` in hot paths (`auto-reply/*`, channel send paths, streaming handlers).
2. Use subsystem logger instead of `console.*` in runtime paths.
3. Do exact identity checks (`a === b`), not truthy co-existence checks.
4. Treat primary operations as fail-fast (throw); only convenience wrappers should catch.
5. Keep file locking for sessions/cron stores; do not remove lock wrappers.
6. For security-sensitive changes (auth, SSRF, exec), run `openclaw security audit` before PR.
7. For config mutations, patch full nested path and verify by immediate read-back.

---

## 4. Common Pitfalls

1. **Never call `loadConfig()` in render/hot paths** - it does sync `fs.readFileSync`. Thread config through params.
2. **Verify function is actually `async` before adding `await`** - causes `await-thenable` lint errors.
3. **Removing `async` from exported functions is BREAKING** - changes return type from `Promise<T>` to `T`. All `await` callers break.
4. **Primary operations must throw; only convenience ops get try/catch** - don't swallow errors on critical paths.
5. **Guard numeric comparisons against NaN** - use `Number.isFinite()` before `>` / `<`.
6. **Normalize paths before string comparison** - `path.resolve()` before `===`.
7. **Derive context from parameters, not global state** - use explicit paths, not env var fallbacks.
8. **Run FULL `pnpm lint` before every push** - not just changed files. Type-aware linting catches cross-file issues.

---

## 5. Commit Message Conventions

- `feat:` - New feature
- `fix:` - Bug fix
- `perf:` - Performance improvement
- `refactor:` - Code restructuring
- `test:` - Test additions/changes
- `docs:` - Documentation

---

## 6. PR & Bug Filing Best Practices

### Multi-Model Review

- Use multiple models for PR review when complexity warrants it. Different models catch different classes of bugs.

### Test Matrices

- **Test across ALL config permutations.** A fix for one mode can break another. Build a test matrix covering every mode x every failure scenario.
- File bugs with full test matrices: reproduction steps, all root causes, gap matrix showing which PRs fix which scenarios.

### Issue & PR Workflow

- **Search existing issues before filing.** `gh issue list --search "<keywords>"` surfaces prior analysis.
- **Scope PRs to one logical change when possible.** Separate PRs are easier to review, revert, and bisect.
- **Call out behavior-default shifts explicitly in PR descriptions.** Include "old assumption vs new behavior" notes.

### Documentation Guardrails

- **Run doc checks before push, not after CI fails.** `pnpm check:docs`, `pnpm format:check`, `npx markdownlint-cli2`.
- **Verify command names against source, never memory.** Confirm in `package.json`, `CONTRIBUTING.md`, and `.github/workflows/ci.yml`.
- **Keep comments shell-safe when posting with `gh pr comment`.** Prefer single-quoted heredoc or escaped backticks.
- **After conflict resolution, run type checks.** Merge conflict fixes can drop `import type` lines.
- **Apply style rules to ALL locale variants.** Rules apply to `docs/zh-CN`, `docs/ja-JP`, etc.
- **Edit i18n docs via pipeline, not directly.** `docs/zh-CN/**` is generated by `scripts/docs-i18n`.

---

## 7. Debugging & Triage Workflow

1. Reproduce once with minimal scope.
2. Map symptom to module using the architecture map.
3. Check relevant gotchas in the current context document.
4. Run targeted tests first, then full suite if touching CRITICAL/HIGH-blast modules.
5. Confirm fix did not regress fallback paths (cron, channel send, subagent completion).

For ambiguous runtime failures: capture exact error string, check common errors table, then inspect nearest owning module.

### Common Errors -> First Fix

| Error / Symptom | First Check | First Fix |
| --- | --- | --- |
| `SQLITE_CANTOPEN` in daemon mode | LaunchAgent env (`TMPDIR`) | Reinstall/restart gateway service |
| `config.patch` "ok" but behavior unchanged | Wrong nesting path | Patch full nested key + read-back verify |
| Startup fails with token conflict | `hooks.token` equals `gateway.auth.token` | Set different values; restart gateway |
| SSRF block on webhook/browser URL | Target is private/metadata | Use public HTTPS endpoint |
| `await-thenable` lint error | Function is not async | Fix signature or remove incorrect `await` |

---

## 8. Pre-PR Checklist (Static Items)

> For the canonical command source, always check `CONTRIBUTING.md` + `.github/workflows/ci.yml`.

```
[] pnpm build                        # TypeScript compilation (always)
[] pnpm check                        # Format + type check + lint (always)
[] pnpm test                         # Full suite for high/blast changes
[] pnpm check:docs                   # Required when docs files changed
[] git diff --stat                   # Review staged scope
[] grep all callers                  # If changing exported signatures
[] Squash fix-on-fix commits         # Keep logical commits only

Conditional checks:
[] If `config/*` changed: run config-focused tests + read-back validation
[] If `routing/*` changed: verify session key parsing + cron + subagent routing
[] If `agents/pi-tools*` changed: run tool policy + tool execution paths
[] If `auto-reply/reply/get-reply.ts` changed: run reply pipeline checks across fallback paths
```
