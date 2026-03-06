# Changelog

## v3.0 — 2026-02-25

Full security audit by Claude Opus with all findings fixed.

### Security Fixes (HIGH)

- **H-1: XSS in UI fixed** — Replaced broken `esc()` function with proper HTML encoding via `textContent`/`createElement`. All `innerHTML` usages with user/model data converted to safe DOM APIs. Inline `onclick` handlers with string interpolation replaced with `data-*` attributes and `addEventListener`.
- **H-2: Shell injection in import_config fixed** — Removed all `$input` shell variable interpolation inside inline Python strings. All file paths now passed exclusively via environment variables (`SWITCHBOARD_IMPORT_FILE`).

### New Features (MEDIUM)

- **M-1: Cron model validation** — New `validate-cron-models` command validates all model references in cron jobs against the registry and allowlist. Added `validate_cron_models()` to validate.py.
- **M-2: Updated task-routing.json** — Changed `google/gemini-2.5-flash` to `google/gemini-3-flash-preview` for cron and heartbeat routing.

### Bug Fixes (MEDIUM)

- **M-3: Backup pruning race condition** — Added `flock`-based locking to prevent concurrent backup pruning operations.
- **M-4: Redundancy engine fail-open** — Added registry validation at top of `generate_redundant_config()`. Returns error if registry is empty or corrupt instead of generating empty config.
- **M-5: Schema validation on import** — Import atomic write now validates merged config schema before committing (rename). Invalid schemas cause the import to abort.

### Improvements (LOW)

- **L-1: Version updated to v3.0** across all files (SKILL.md, README.md, UI title, switchboard.sh header).
- **L-2: Setup script guard** — `setup`/`init` command now checks `setup.sh` exists before executing.
- **L-3: Python stderr logging** — Validation engine stderr redirected to `$BACKUP_DIR/switchboard-stderr.log` instead of `/dev/null` for debugging.
- **L-4: Backup directory permissions** — `chmod 700` applied to backup directory after creation.
- **L-6: innerHTML elimination** — All remaining `innerHTML` + `esc()` patterns in the UI converted to `textContent`/`createElement` (renderRoles, renderPipeline, renderProviders, renderChannels, renderIssues, drawPickerList, renderStatus).

## v2.0 — 2026-02-24

Initial release with full model orchestration, validation engine, redundancy engine, backup/restore, and Canvas UI.
