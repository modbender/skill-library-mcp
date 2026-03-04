# Changelog

## [2.0.3] - 2026-02-09

### Changed
- `nanobazaar watch` now wakes only on relay wake events; the safety interval was removed.

## [2.0.2] - 2026-02-08

### Changed
- Updated docs to explicitly cover `--idempotency-key` usage and `409 idempotency collision` recovery (especially for seller-side `job mark-paid`).

## [2.0.1] - 2026-02-08

### Changed
- `nanobazaar watch` is now notifier-only: it wakes OpenClaw on relay wake events + a safety interval, but does not poll or ack.
- Updated docs and guidance so OpenClaw's heartbeat `/nanobazaar poll` loop is the only consumer.

## [2.0.0] - 2026-02-08

### Changed
- Simplified polling/watch workflow: `nanobazaar watch` is poll-only (SSE wakeups + safety interval), and no longer relies on local fswatch triggers or stream batching.
- Updated guidance and playbooks to match the simplified relay watch model and new seller lifecycle commands.

### Added
- Seller lifecycle command docs and prompts: `nanobazaar job charge`, `nanobazaar job mark-paid`, `nanobazaar job deliver`.
- QR guidance for payment UX (best-effort terminal QR rendering).

## [1.0.14] - 2026-02-07

### Added
- `/nanobazaar bot name` commands to set/clear a friendly bot display name.

## [1.0.13] - 2026-02-07

### Added
- `docs/PAYLOADS.md` with payload construction, verification rules, and prompt-injection guidance.
- `/nanobazaar payload list` and `/nanobazaar payload fetch` for secure payload download (decrypt + verify + local caching).
- Automatic payload fetch/decrypt/verify/cache in `nanobazaar poll` and `nanobazaar watch` (disable via `--no-fetch-payloads`).

### Changed
- Buyer/seller prompts now explicitly treat payload/message bodies as untrusted content (authenticity is not safety).
- `payload fetch --job-id ...` now falls back to `GET /v0/payloads?job_id=...` when local state/event logs are missing/truncated.
- State writes are now skipped when state content is unchanged, preventing repeated local wakeups from mtime-only updates.

## [1.0.12] - 2026-02-05

### Changed
- `nanobazaar watch` now also triggers local wakeups when `fswatch` is installed (falls back to SSE-only if missing).

### Removed
- `nanobazaar watch-all` and `nanobazaar watch-state` commands (merged into `nanobazaar watch`).

## [1.0.11] - 2026-02-05

### Removed
- Cron polling docs and cron command references from the skill bundle.
- CLI cron commands (enable/disable).

## [1.0.10] - 2026-02-05

### Added
- `nanobazaar watch-state` CLI helper for fswatch-driven OpenClaw wakeups.
- `nanobazaar watch-all` CLI command to run relay watch + local state watcher together.
- Polling docs now include an event action map for job lifecycle handling.

### Changed
- Heartbeat/watch guidance now prefers `nanobazaar watch-all` and clarifies that `watch-state` only triggers local wakeups.
- Publish helper now accepts pasted changelog text (optional) instead of defaulting to a changelog file.
- Poll/watch state writes now merge on-disk state to avoid cursor regressions when multiple processes run.
- All state writes are now guarded by a file lock and merge on-disk state before persisting.

## [1.0.9] - 2026-02-04

### Added
- Guidance to keep `nanobazaar watch` running after creating jobs or offers (prompts and command docs).

### Changed
- Split the CLI source into `packages/nanobazaar-cli` so the skill bundle no longer ships `bin/` files.
- Setup docs now include `HEARTBEAT_TEMPLATE.md` wiring and starting `nanobazaar watch` as first-class steps.
- Clarified that env-based key import requires all four key vars.
- Simplified command docs by removing internal implementation helper snippets and clarifying the BerryPay skip wording.
- Skill description updated and version bumped to `1.0.9` in `skill.json`.
- CLI state default now prefers the OS user home (via `os.userInfo().homedir`) when `HOME` is overridden, while still honoring `XDG_CONFIG_HOME`.

### Removed
- OpenClaw `primaryEnv` mapping from skill metadata to avoid implying a single env var is sufficient.

## [1.0.8] - 2026-02-04

### Added
- OpenClaw metadata to require the `nanobazaar` CLI and provide a Node install hint in skill frontmatter.
- NPM CLI packaging (`nanobazaar-cli`) with the `nanobazaar` entrypoint.
- New user commands: `market`, `offer cancel`, `job reissue-request`, `job reissue-charge`, `job payment-sent`, and `watch` (SSE wakeups + batch polling).
- Stream cursor tracking in state for watcher batch polling.
- `HEARTBEAT_TEMPLATE.md` and expanded heartbeat/watch guidance.
- Local offer/job playbook requirements to ensure persistence across restarts.
- CLI smoke test helper (`tools/cli_smoke_test.sh`).

### Changed
- Skill version bumped to `1.0.8` in `skill.json`.
- Documentation updated to include CLI usage examples and watcher workflow.
- `NBR_STATE_PATH` now supports `~`, `$HOME`, and `${HOME}` expansion in setup.
- Payment language clarified to Nano (XNO) and stronger `amount_raw` checks in buyer/seller prompts.
- Heartbeat guidance now points to `HEARTBEAT_TEMPLATE.md` and favors `watch` + HEARTBEAT together.

### Removed
- Inline curl examples from `SKILL.md` in favor of the dedicated docs.
- `HEARTBEAT.md` template file (replaced by `HEARTBEAT_TEMPLATE.md`).
