# Inspected Upstream Skills

This meta-skill was authored against these ClawHub-inspected versions:

- `topic-monitor` latest `1.3.4`
- `polymarket-odds` latest `1.0.0`
- `simmer-weather` latest `1.7.1`

## Practical interpretation used in this meta-skill

- `topic-monitor`: signal discovery, confidence scoring, queued alerts.
- `polymarket-odds`: market lookup, implied probability extraction.
- `simmer-weather`: execution safety/runtime reference pattern (dry-run/live, API-key-gated operation).

## Scope boundary

This meta-skill intentionally provides orchestration instructions only.
It does not replace upstream skill logic and does not include custom execution scripts.
