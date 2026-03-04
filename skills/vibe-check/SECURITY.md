# Security Policy — vibe-check

## Design Principles

1. **Read-only by default.** The skill reads source files and produces findings. It does not auto-edit project files.
2. **Human-in-the-loop fixes.** `--fix` only emits suggested unified diffs in the report.
3. **Explicit target scope.** The tool analyzes only files under the provided file/directory/diff target.
4. **Safe shell behavior.** Scripts use `set -euo pipefail`, quote file paths, and avoid `eval`.

## Data This Skill Touches

| Data | Access | Notes |
|------|--------|-------|
| Source files (`.py`, `.ts`, `.tsx`, `.js`, `.jsx`, `.mjs`, `.cjs`) | **Read-only** | Parsed for scoring and findings |
| Git metadata (`git diff`, staged files) | **Read-only** | Used only in `--diff` / `--staged` / `--branch` mode |
| LLM API keys (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`) | **Read-only** | Used only for outbound API auth; never printed intentionally |
| Report output file (`--output`) | **Write** (optional) | Written only when the user requests it |

## Network Behavior

- If `ANTHROPIC_API_KEY` is set, source content is sent to `https://api.anthropic.com` for analysis.
- If `OPENAI_API_KEY` is set, source content is sent to `https://api.openai.com` for analysis.
- If neither key is set and `openclaw` CLI is available, analysis can run through `openclaw llm`.
- If no LLM is available, the tool falls back to local heuristic analysis (no outbound API call).

## Abuse Cases & Mitigations

| Abuse Case | Risk | Mitigation |
|------------|------|------------|
| Scanning files that contain secrets and sending them to an LLM API | **Medium** | Run in heuristic mode (unset API keys) for sensitive repos, or scope analysis to safe paths |
| Applying generated patch suggestions without review | **Medium** | Fixes are emitted as text only; no automatic patch application |
| Command injection via path arguments | **Low** | Paths are quoted and not executed as shell code |
| Large-file denial of service | **Low** | Files above max size are skipped (`MAX_FILE_SIZE=50000`) |

## What This Skill Does Not Do

- Does not execute project code
- Does not auto-commit, push, or open pull requests
- Does not auto-apply suggested fixes
- Does not guarantee security/vulnerability completeness

