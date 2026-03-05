# Release Guide

## 1.1.1

### Summary

This release aligns `persistent-code-terminal` with recommended Codex CLI non-interactive usage and improves documentation consistency.

### Highlights

- `persistent-code-terminal-codex-exec.sh` now defaults to:
  - `codex exec --full-auto --sandbox workspace-write --cd <current-dir> "<instruction>"`
- Supports passing extra `codex exec` flags before the instruction
  - Example: `--json -o /tmp/codex-run.json`
- Added opt-out env var:
  - `PCT_CODEX_NO_DEFAULT_FLAGS=1`
- Updated docs to reflect default behavior and approval/sandbox expectations

### User-visible behavior changes

- Running:
  - `./bin/persistent-code-terminal-codex-exec.sh "Do X"`
- Now executes Codex with default automation-oriented flags unless opted out.

### Compatibility notes

- No breaking changes to existing script entrypoints.
- Existing calls with only an instruction continue to work.
- Calls that already pass explicit flags are now supported directly.

### Validation checklist

Run locally (if tools are installed):

```bash
bash -n bin/*.sh
shfmt -d bin test
shellcheck bin/*.sh
bats test
```

Or rely on CI (`.github/workflows/ci.yml`) for `shfmt`, `shellcheck`, and `bats`.

### Suggested tag message

`v1.1.1: codex-exec defaults to full-auto/workspace-write, plus docs alignment`

---

## 1.2.0 Release Checklist

### Pre-flight

1. Ensure toolchain is available:
   - `tmux`, `bash`, `shellcheck`, `shfmt`, `bats`
2. Run quality checks:
   - `bash -n bin/*.sh`
   - `shfmt -d bin test`
   - `shellcheck bin/*.sh`
   - `bats test`
3. Smoke test key workflows:
   - `start/send/read/summary/status/doctor`
   - `read --json` and `summary --json`
   - `auto --instruction "..."`
   - `list/switch` with at least two sessions
   - `route` single-project and multi-project message

### Versioning

1. Confirm `CHANGELOG.md` includes `1.2.0` entry.
2. Confirm docs updated (`README.md`, `SKILL.md`).

### Publish

1. Commit release changes.
2. Create annotated tag:
   - `git tag -a v1.2.0 -m "v1.2.0: routing, multi-project, json, auto-loop"`
3. Push branch and tag:
   - `git push`
   - `git push origin v1.2.0`
4. Create GitHub release notes from `CHANGELOG.md`.
