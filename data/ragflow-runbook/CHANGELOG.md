# Changelog

## 0.1.4

- Deploy safety: `deploy.sh` now requires explicit opt-in for runtime downloads and for starting containers.
- Deploy safety: fallback download path prints a review checklist before start.

## 0.1.3

- Metadata compatibility: duplicate required/optional env var declarations at top-level (`env`) and `metadata.env` to ensure registry/security scanners display them.

## 0.1.2

- Metadata: switch SKILL front matter metadata to pure YAML so registry can parse required env vars and optional bins.
- Alerting: declare `openclaw` as an optional required binary (only needed for sending alerts).

## 0.1.1

- Security: `ragflow_alert.py` no longer defaults to a hardcoded Telegram target and no longer includes base_url in the alert message.
- Metadata: declare required environment variables in skill front matter.

## 0.1.0

- Initial release.
- Runtime operations runbook for RAGFlow.
- Built-in scripts:
  - deploy, healthcheck
  - ping, smoke, status, alert
- Copy/paste scheduling examples for cron and launchd.
