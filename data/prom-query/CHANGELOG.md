# Changelog

All notable changes to the `prom-query` skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] — 2026-02-16

### Added
- Discord v2 delivery guidance in `SKILL.md` for OpenClaw v2026.2.14+:
  - Compact first response for incident triage in Discord channels
  - Component-style quick actions for common follow-up queries
  - Fallback numbered actions when components are unavailable

### Changed
- README: added "OpenClaw Discord v2 Ready" compatibility section.
- `SKILL.md` metadata tags now include `discord` and `discord-v2`.
- README version badge updated to `1.0.1`.

## [1.0.0] — 2026-02-15

### Added
- Initial release of prom-query skill
- **query** command — instant PromQL queries against Prometheus HTTP API
- **range** command — range queries with automatic downsampling for large result sets
- **alerts** command — fetch and format active alerts, grouped by severity and state
- **targets** command — scrape target health overview with up/down summary
- **explore** command — search available metrics by pattern with type and help metadata
- **rules** command — alerting and recording rules with health status
- SKILL.md with comprehensive PromQL examples for common scenarios (error rate, latency p99, CPU, memory, disk, Kubernetes)
- Automatic step adjustment for range queries exceeding 500 data points
- Per-series statistical summaries (min, max, avg, first, last) for range results
- Support for Prometheus, Thanos, Mimir, and VictoriaMetrics backends
- Bearer token authentication via PROMETHEUS_TOKEN
- URL scheme validation (http/https only)
- Comprehensive error messages with troubleshooting hints

Powered by Anvil AI 📊
