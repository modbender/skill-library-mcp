# Security

## How the skill invokes CLI agents

The skill runs CLI agents via Node.js `child_process.spawn()`, **not** a shell, for all supported providers (Kimi, Claude Code, OpenCode):

- **No shell:** The prompt is passed as a single element in the `args` array to `spawn(cmd, args, options)`. The operating system passes it as one argument to the CLI process. There is no `execSync('cli -p "' + prompt + '"')` or similar; therefore there is no shell command injection at this layer.
- **Input sanitization:** Before calling any CLI, the prompt is sanitized by a shared `sanitizePrompt()` function:
  - Null bytes (`\0`) are removed (they could truncate arguments in C-style parsers).
  - Other C0 control characters (except tab, newline, carriage return) are replaced with spaces to avoid control sequences that could confuse downstream parsers.
- **Trust boundary:** The skill does not store or log credentials. It only verifies that the user has already authenticated the CLI; the CLI runs with the user's privileges in the configured worktree.

### Provider-specific security notes

All providers follow the same security model:

| Provider | CLI Path Validation | Auth Method | No-shell Execution |
|----------|-------------------|-------------|-------------------|
| **Kimi** | `KIMI_CLI_PATH` validated | `~/.kimi/` credentials | ✓ |
| **Claude** | `CLAUDE_CLI_PATH` validated | `ANTHROPIC_API_KEY` env | ✓ |
| **OpenCode** | `OPENCODE_CLI_PATH` validated | `~/.local/share/opencode/` | ✓ |

CLI paths are validated (no spaces, no shell metacharacters, length limit). Verify and spawn use `spawnSync` / `spawn` with an argument array and `shell: false`, so the path is never passed to a shell. Invalid values fall back to the default command name.

## Git worktree commands

- **`git worktree add`** (in `createWorktree`): Uses `spawnSync("git", ["worktree", "add", "-b", branchName, worktreeBase, baseBranch], { cwd: repoPath })` with an **argument array** (no shell). This prevents command injection if `worktree.basePath` in config or a future caller passed untrusted values. `taskId` is validated with `isSafeTaskId()` before use.
- **`git worktree list`** / **`git worktree remove --force .`**: Fixed command strings with `cwd` only; no user input in the command.

## Path traversal (taskId)

The `taskId` argument for `cli-worker status <taskId>` and `cli-worker worktree remove <taskId>` is validated before use:

- **Allowed:** Single segment only: alphanumeric and hyphens (e.g. UUIDs like `550e8400-e29b-41d4-a716-446655440000`). No path separators (`/`, `\`), no `..`, no leading hyphen.
- **Resolution:** Paths are resolved with `path.resolve(basePath, taskId)` and checked to remain under `basePath` before reading files or running `git worktree remove`. Invalid `taskId` is rejected with an error.

This prevents arbitrary file read (e.g. `status ../../../../etc/passwd`) and destructive worktree remove in arbitrary directories.

## Credentials and environment variables

- **No required env vars.** The skill works with defaults (CLI on PATH, config in standard locations, `~/.openclaw` for config/logs/worktrees). All env vars are optional overrides.
- **Optional env vars:**
  - `OPENCLAW_CLI_PROVIDER` - Default provider selection
  - `KIMI_CLI_PATH`, `CLAUDE_CLI_PATH`, `OPENCODE_CLI_PATH` - CLI executable paths
  - `ANTHROPIC_API_KEY` - Claude Code authentication
  - `KIMI_HOME`, `OPENCODE_CONFIG` - Config directories
  - `OPENCLAW_CONFIG`, `OPENCLAW_LOG_DIR`, `KIMI_NO_BROWSER`
- **CLI paths:** Validated (no spaces, no shell metacharacters, length limit). Verify and spawn use `spawnSync` / `spawn` with an argument array and `shell: false`, so values are never passed to a shell. Invalid values fall back to defaults.
- **Paths:** The skill reads config/credentials under `~/.kimi`, `~/.local/share/opencode` (for verification) and writes logs and task manifests under `~/.openclaw`. No credentials are stored by the skill.

## RCE / argument injection

The ClawHub finding concerns possible RCE if a CLI were susceptible to argument or command injection. On the skill side:

1. We never invoke a shell; we use `spawn` with an argument array for all providers.
2. We sanitize the prompt (null bytes and control characters) via the shared `sanitizePrompt()` before passing it as an argument.
3. CLI paths are validated before use.
4. The CLIs are dependencies run by the user; we recommend keeping them updated. Any vulnerability inside the CLIs themselves would need to be addressed by their maintainers.

## Dependencies and npm audit

- **Runtime:** The published package (`npm pack` / `files: ["bin", "skills", "scripts", "SECURITY.md"]`) has **no runtime npm dependencies**. Only devDependencies (eslint, typescript, etc.) are used for build and lint.
- **npm audit:** Reported vulnerabilities are in **devDependencies only** (e.g. eslint’s transitive minimatch/ajv). They do not affect production installs or the CLI at runtime. Upgrading to eslint@10 to fix them would be a breaking change; we monitor and will upgrade when practical.

## Reporting a vulnerability

If you believe you've found a security issue, please open an issue on the [repository](https://github.com/quratus/openclaw_cli_agent_skill) or contact the maintainers privately.
