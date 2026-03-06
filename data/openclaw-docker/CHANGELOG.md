# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `docker_compose_ps` tool - inspect running services in a Compose project via `docker compose ps --format json`, with optional service name filter
- `compose_ps` is allowed in `readOnly` mode since it is a read-only operation

## [0.2.0] - 2026-02-27

### Added

- Optional follow mode for `docker_logs` tool - stream container logs in real-time with bounded duration (`follow: true`, `followDurationMs`)
- `openclaw.extensions` field in package.json for plugin auto-discovery

### Changed

- Replaced em dashes with hyphens across docs and package metadata for consistency

## [0.1.2] - 2026-02-23

### Added

- Docker daemon connection via unix socket or TCP with optional TLS
- Container tools: `docker_ps`, `docker_logs`, `docker_inspect`, `docker_start`, `docker_stop`, `docker_restart`
- Docker Compose tools: `docker_compose_up`, `docker_compose_down`
- Safety controls with `readOnly` mode and `allowedOperations` guard
- Configurable command timeout via `timeoutMs`
- Plugin manifest with full `configSchema` for OpenClaw integration
- MIT license

[0.2.0]: https://github.com/elvatis/openclaw-docker/compare/v0.1.2...v0.2.0
[0.1.2]: https://github.com/elvatis/openclaw-docker/releases/tag/v0.1.2
