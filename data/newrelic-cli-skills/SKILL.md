---
name: newrelic-cli-skills
version: 1.0.1
description: >
  Monitor, query, and manage New Relic observability data via the newrelic CLI.
  Covers NRQL queries, APM performance triage, deployment markers, alert management,
  infrastructure monitoring, and agent diagnostics. Use when user asks about
  application performance, error rates, slow transactions, deployment tracking,
  or New Relic configuration.
metadata:
  openclaw:
    purpose: >
      Read-mostly observability skill. Reads APM metrics, NRQL query results, alert
      policies/conditions, and infrastructure host data from the New Relic API.
      Write operations are limited to: creating deployment markers (apm sub-skill)
      and muting/unmuting alert conditions (alerts sub-skill). No data is deleted.
      Scripts execute newrelic CLI commands only; no shell eval or dynamic execution.
    requires:
      env:
        - NEW_RELIC_API_KEY
        - NEW_RELIC_ACCOUNT_ID
      binaries:
        - newrelic
      notes: |
        NEW_RELIC_API_KEY must be a User Key (starts with NRAK-).
        NEW_RELIC_ACCOUNT_ID is the numeric account ID from the NR UI.
        See README.md for CLI installation instructions.
        Use an API key scoped to the minimum required accounts.
tags:
  - newrelic
  - observability
  - apm
  - monitoring
  - performance
  - nrql
---

# New Relic CLI Skills

## Quick Decision Tree

**Performance issue reported?** → [`apm/SKILL.md`](apm/SKILL.md)
**Need to query data with NRQL?** → [`nrql/SKILL.md`](nrql/SKILL.md)
**Recording a deployment?** → [`deployments/SKILL.md`](deployments/SKILL.md)
**Alert management?** → [`alerts/SKILL.md`](alerts/SKILL.md)
**Infrastructure/host issues?** → [`infrastructure/SKILL.md`](infrastructure/SKILL.md)
**Agent not reporting?** → [`diagnostics/SKILL.md`](diagnostics/SKILL.md)

---

## Setup & Auth

```bash
# Install
curl -Ls https://download.newrelic.com/install/newrelic-cli/scripts/install.sh | bash

# Configure profile
newrelic profile add \
  --profile default \
  --apiKey $NEW_RELIC_API_KEY \
  --accountId $NEW_RELIC_ACCOUNT_ID \
  --region US   # or EU

newrelic profile default --profile default

# Verify
newrelic profile list
```

---

## Common One-Liners

```bash
# Search for an entity by name
newrelic entity search --name "my-app"

# Run a NRQL query
newrelic nrql query --accountId $NEW_RELIC_ACCOUNT_ID \
  --query "SELECT average(duration) FROM Transaction WHERE appName='my-app' SINCE 1 hour ago"

# Record a deployment
newrelic apm deployment create \
  --applicationId <APP_ID> \
  --revision "v1.2.3" \
  --description "Feature: user auth"

# Run diagnostics
newrelic diagnose run
```

---

## Entity Reference

Find entity GUIDs (needed for API calls and deployment markers):

```bash
# List all APM apps
newrelic entity search --name "" --type APPLICATION --domain APM

# Get specific entity details
newrelic entity get --guid <GUID>

# List all hosts
newrelic entity search --name "" --type HOST
```

---

## Environment Variables

| Variable | Description |
|---|---|
| `NEW_RELIC_API_KEY` | User key (NRAK-...) |
| `NEW_RELIC_ACCOUNT_ID` | Numeric account ID |
| `NEW_RELIC_REGION` | `US` or `EU` |

---

## Sub-Skills

| Sub-skill | When to use |
|---|---|
| [`apm/`](apm/SKILL.md) | Performance triage, slow transactions, error analysis |
| [`nrql/`](nrql/SKILL.md) | Custom queries, dashboards, ad-hoc data exploration |
| [`deployments/`](deployments/SKILL.md) | Mark releases, correlate deploys with performance |
| [`alerts/`](alerts/SKILL.md) | Alert policies, conditions, notification channels |
| [`infrastructure/`](infrastructure/SKILL.md) | Host metrics, CPU/memory, process monitoring |
| [`diagnostics/`](diagnostics/SKILL.md) | Agent health, config validation, connectivity |

## Scripts

| Script | Purpose |
|---|---|
| [`scripts/check-performance.sh`](scripts/check-performance.sh) | Quick health check across all apps |
| [`scripts/deployment-marker.sh`](scripts/deployment-marker.sh) | Record a deployment event |
| [`scripts/top-slow-transactions.sh`](scripts/top-slow-transactions.sh) | Find the 10 slowest transactions |
| [`scripts/error-report.sh`](scripts/error-report.sh) | Recent errors with stack traces |

## References

- [`references/nrql-patterns.md`](references/nrql-patterns.md) — Common NRQL query patterns
- [`references/performance-triage.md`](references/performance-triage.md) — Step-by-step triage guide
