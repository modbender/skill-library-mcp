# Changelog — pager-triage

All notable changes to this skill are documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/).

---

## [0.1.1] — 2026-02-16

### Added

- Discord v2 delivery guidance in `SKILL.md` for OpenClaw v2026.2.14+:
  - Compact first response for incident triage
  - Component-style quick actions
  - Numbered fallback when components are unavailable
- `discord` and `discord-v2` tags in skill metadata

### Changed

- Metadata normalization: `author` set to `CacheForge`.
- README: version badge bumped to `0.1.1`.
- README install command normalized to `pager-triage`.
- README: added "OpenClaw Discord v2 Ready" compatibility section.

## [0.1.0] — 2026-02-15

### Added

- **`incidents`** — List active PagerDuty incidents (triggered + acknowledged), sorted by urgency
- **`detail <id>`** — Incident deep-dive with timeline (log entries), alerts, notes, and automated analysis
- **`oncall`** — Show current on-call schedules and escalation policies
- **`services`** — List PagerDuty services with operational status (active/warning/critical/disabled)
- **`recent`** — Recent incident history with MTTR statistics (`--since 24h|7d|30d`, `--service <id>`)
- **`ack <id> --confirm`** — Acknowledge incident (stops escalation). Requires `--confirm` flag.
- **`resolve <id> --confirm`** — Resolve incident (marks as fixed). Requires `--confirm` flag.
- **`note <id> --content "..." --confirm`** — Add note to incident. Requires `--confirm` flag.
- Confirmation gates for all write operations — shows incident context and refuses without `--confirm`
- API key masking in all error messages (`****<last 4>`)
- Input sanitization — incident and service IDs validated as alphanumeric
- HTTPS-only enforcement — refuses non-HTTPS URLs
- Retry logic — 5xx and network errors get 1 retry with 2-second backoff
- 10-second curl timeout per API call
- Structured JSON output for all subcommands (machine-parseable)
- Structured JSON errors on stderr with non-zero exit codes
- Dependency checking for `curl` and `jq` at startup
- Comprehensive documentation: SKILL.md, README.md, SECURITY.md, TESTING.md, OPERABILITY.md
- Smoke test script (`scripts/smoke.sh`)

### Not Yet Implemented

- OpsGenie provider support (planned for v0.2.0)
- Fallback to `pd` CLI when API is unreachable
- Pagination beyond first page (25 incidents / 100 services)
- Parallel API calls in `detail` subcommand
