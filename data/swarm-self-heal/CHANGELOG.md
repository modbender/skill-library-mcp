# Changelog

## [0.1.0] - 2026-02-21

- Initial release.
- Added swarm-level self-heal watchdog (`swarm_self_heal.sh`).
- Added compatibility wrapper (`anvil_watchdog.sh`) for existing cron path.
- Added setup automation to deploy scripts and enforce watchdog cron lanes.
- Added one-shot canary checker (`check.sh`).
- Added passive-first lane health using `openclaw status --json` for lower noise and fewer unnecessary pings.
- Added infra vs soft-failure classification with bounded infra-only retry.
- Added lock protection to prevent overlapping watchdog runs.
- Added cron timeout hardening (`--timeout-seconds 900`) and concise healthy-run response guidance.
