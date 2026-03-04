# Changelog

## 1.2.0
- Added structured JSON mode:
  - `persistent-code-terminal-read.sh --json`
  - `persistent-code-terminal-summary.sh --json`
- Added auto closed-loop runner:
  - `persistent-code-terminal-auto.sh`
- Added multi-project session tools:
  - `persistent-code-terminal-list.sh`
  - `persistent-code-terminal-switch.sh`
  - `persistent-code-terminal-start.sh --project <custom-name>`
- Added intelligent auto-routing entrypoint:
  - `persistent-code-terminal-route.sh`
  - config toggle: `openclaw.config.dev.autoCodeRouting` (default false)
- Added multi-project natural-language routing:
  - parse `给/为/<project> 项目 ...` patterns
  - serial per-project execution with consolidated report
  - invalid project isolation (does not block other tasks)
- Added routing decision logging fields:
  - `detectedMultiProject`, `tasksCount`, `parsedProjects`
- Added route parsing and routing safety tests in Bats

## 1.1.1
- Updated `persistent-code-terminal-codex-exec.sh` to use safer defaults:
  - `--full-auto --sandbox workspace-write --cd <current-dir>`
- Added support for passing custom `codex exec` flags before the instruction
- Added opt-out env var: `PCT_CODEX_NO_DEFAULT_FLAGS=1`
- Updated README to document codex-exec defaults and approval expectations

## 1.1.0
- Added shared shell helpers in `bin/persistent-code-terminal-lib.sh`
- `send/read/attach` now auto-create the tmux session if missing
- Improved `tmux` availability checks and error messaging consistency
- Added Bats tests under `test/`
- Added GitHub Actions CI for `shfmt`, `shellcheck`, and `bats`

## 1.0.0
- Initial release
- Per-project tmux session: <project>-code-session
- start/send/read/attach/kill scripts
- Codex one-shot helper: persistent-code-terminal-codex-exec.sh
- Examples and publishing-ready README
