# Changelog

All notable changes to this project will be documented in this file.

## [0.2.3] - 2026-02-19

### Security

- **Credentials / KIMI_CLI_PATH:** Verify no longer uses `execSync` with a string command. It uses `spawnSync` with an argument array and `shell: false`, so `KIMI_CLI_PATH` cannot be abused for shell injection. `KIMI_CLI_PATH` is validated (no spaces, no shell metacharacters); invalid values fall back to `kimi`. Same helper used in spawn/run.
- **Env vars documented:** No required env vars; optional vars (`KIMI_CLI_PATH`, `KIMI_HOME`, `OPENCLAW_CONFIG`, `OPENCLAW_LOG_DIR`, `KIMI_NO_BROWSER`) listed in README and SECURITY.md.

### Added

- `src/safe-cli-path.ts`: `getSafeKimiCliPath()` for validated CLI path.
- Unit tests in `tests/unit/safe-cli-path.test.js`.

## [0.2.2] - 2026-02-19

### Security

- **Path traversal:** `taskId` for `cli-worker status` and `cli-worker worktree remove` is validated: only alphanumeric and hyphens allowed; resolved path must stay under worktree base. Prevents arbitrary file read and worktree remove in arbitrary directories (ClawHub path traversal finding).
- **SECURITY.md** updated with path traversal section.

### Added

- `src/safe-task-id.ts`: `isSafeTaskId()`, `resolveTaskIdPath()` for safe taskId handling.
- Unit tests in `tests/unit/safe-task-id.test.js`.

## [0.2.1] - 2026-02-19

### Security

- **Prompt sanitization:** User prompt is sanitized before being passed to the Kimi CLI: null bytes are stripped and C0 control characters (except tab, newline, CR) are replaced with spaces. This is defense-in-depth; the skill already uses `child_process.spawn()` with an argument array (no shell), so the prompt is a single argv.
- **SECURITY.md** added: documents no-shell invocation and sanitization for ClawHub/audit.

### Added

- Unit tests for `sanitizePrompt` in `tests/unit/spawn-run.test.js`.

## [0.1.0] - 2026-02-16

### Added

- Initial release: Kimi CLI Worker Skill for OpenClaw
- `cli-worker verify` – check Kimi CLI install and auth
- `cli-worker execute "<prompt>"` – run task in worktree (or cwd), with `--constraint`, `--success`, `--files`, `--timeout`, `--output-format text|json`
- `cli-worker status <taskId>` – show parsed report status
- `cli-worker worktree list | remove <taskId>`
- `cli-worker cleanup [--older-than N]` – remove stale worktrees
- AGENTS.md template and task manifest (`.openclaw/task.manifest.json`)
- Report parser for `.openclaw/kimi-reports/{taskId}.json`
- Config: `~/.openclaw/openclaw.json` with `worktree.basePath`
- Logging to `~/.openclaw/logs/cli-worker.log` with 10MB rotation
- `skills/cli-worker/SKILL.md` for OpenClaw agent discovery
