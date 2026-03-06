# newrelic-cli-skills

An [OpenClaw](https://openclaw.ai) agent skill for monitoring, querying, and managing New Relic observability data via the `newrelic` CLI.

## What It Does

- **Performance triage** — identify slow transactions, DB bottlenecks, and error spikes
- **NRQL queries** — run ad-hoc queries against your New Relic account from the terminal
- **Deployment markers** — record releases so you can correlate deploys with performance changes
- **Alert management** — create and manage alert policies, conditions, and channels
- **Infrastructure monitoring** — host CPU, memory, disk, and process metrics
- **Agent diagnostics** — validate agent config and connectivity

## Requirements

- [`newrelic` CLI](https://github.com/newrelic/newrelic-cli) installed
- `NEW_RELIC_API_KEY` — User key (starts with `NRAK-`)
- `NEW_RELIC_ACCOUNT_ID` — Numeric account ID

## Install CLI

```bash
curl -Ls https://download.newrelic.com/install/newrelic-cli/scripts/install.sh | bash
```

## Setup

```bash
newrelic profile add \
  --profile default \
  --apiKey $NEW_RELIC_API_KEY \
  --accountId $NEW_RELIC_ACCOUNT_ID \
  --region US

newrelic profile default --profile default
```

## Sub-skills

| Sub-skill | Purpose |
|---|---|
| `apm/` | Performance triage — slow transactions, DB analysis, error rates |
| `nrql/` | NRQL query patterns and ad-hoc data exploration |
| `deployments/` | Deployment markers and release tracking |
| `alerts/` | Alert policies, conditions, channels |
| `infrastructure/` | Host metrics — CPU, memory, disk, processes |
| `diagnostics/` | Agent health, config validation, connectivity |

## Scripts

| Script | Purpose |
|---|---|
| `check-performance.sh` | Health check across all apps |
| `deployment-marker.sh` | Record a deployment event |
| `top-slow-transactions.sh` | Find the 10 slowest transactions |
| `error-report.sh` | Recent errors with messages and counts |

## License

MIT
