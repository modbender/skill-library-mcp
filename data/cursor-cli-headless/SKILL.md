---
name: cursor-cli-headless
description: Execute coding tasks using the Cursor CLI in headless print mode. Use when delegating code writing, refactoring, analysis, or review tasks to a headless Cursor agent process, running automated code changes, or batch-processing files with the agent CLI.
---

# Cursor CLI Headless

Execute coding tasks using the Cursor CLI in non-interactive (print) mode via the wrapper script for scripts, automation, and batch processing.

## Prerequisites

- **Cursor CLI installed**: Run `agent --version`. If missing, install: `curl https://cursor.com/install -fsS | bash` (macOS/Linux/WSL) or see [Installation](https://cursor.com/docs/cli/installation).
- **Authenticated**: Set `CURSOR_API_KEY` in the environment for scripts, or run `agent login` interactively once. Check if already logged in with `agent status` or `agent whoami`.

## Quick start

Use `scripts/run-task.sh` with either an inline prompt or a prompt file:

```bash
# Prompt from file (stream progress by default)
./scripts/run-task.sh -f prompt.txt

# Inline prompt, run in a specific project directory
./scripts/run-task.sh -p "Add tests for auth module" -d /path/to/project
```

## Wrapper script: run-task.sh

`scripts/run-task.sh` runs the Cursor agent in headless mode. **Recommended:** keep file modifications and stream progress **on** (default). Use `--no-force` only with tmux for interactive mode (agent proposes changes for review). Use `--no-stream` for plain output.

**Arguments:**

- `-p "prompt"` — inline prompt (mutually exclusive with `-f`)
- `-f prompt-file.txt` — read prompt from file (for long prompts)
- `-d dir` — working directory (default: current directory)
- `-o format` — `text`, `json`, or `stream-json` (with default streaming, format is stream-json)
- `-m model` — model name
- `--mode mode` — `agent`, `plan`, or `ask`
- `--force` — allow file modifications (default)
- `--no-force` — do not modify files; agent only proposes changes
- `--stream` — stream-json with progress display (default; requires `jq` for progress)
- `--no-stream` — plain output only; use with `-o text` or `-o json`

**Output formats:**

| Format | Use when |
|--------|----------|
| (default stream) | Live progress (model, tool calls, chars); NDJSON on stdout, progress on stderr |
| `-o text --no-stream` | Only the final assistant message |
| `-o json --no-stream` | Single JSON object with `result`, `duration_ms`, etc.; parse with `jq -r '.result'` |

**Examples:**

```bash
# Task from file, apply changes, stream progress (default)
./scripts/run-task.sh -f tasks/refactor-auth.txt

# Inline prompt, specific project, JSON result only
./scripts/run-task.sh -p "Summarize README.md" -d /path/to/repo --no-stream -o json

# Plain text output, no progress
./scripts/run-task.sh -f tasks/review.txt --no-stream -o text
```

## Working directory

The agent runs in the script’s working directory. Use `-d /path/to/project` so the agent sees that project as the root.

## Error handling

- **Exit code**: Non-zero means the run failed; check stderr for the error message.
- With `-o json`, on failure no JSON is emitted; only stderr.
- In scripts, check `$?` after the wrapper and exit accordingly.

## Additional resources

- For detailed output schemas and event types: [reference.md](reference.md)
- Official docs: [Using Headless CLI](https://cursor.com/docs/cli/headless), [Output format](https://cursor.com/docs/cli/reference/output-format)
