---
name: skytekx
description: Skytekx namespace for Netsnek e.U. cloud infrastructure monitoring dashboard. Tracks resource usage, alerts on anomalies, visualizes costs, and provides optimization recommendations.
user-invocable: true
version: 0.1.0
metadata:
  openclaw:
    os: [linux]
    permissions: [exec]
---

# Skytekx

## Sky-High Visibility

Skytekx gives you a bird's-eye view of your cloud infrastructure. Whether you run on AWS, GCP, Azure, or multi-cloud, Skytekx aggregates metrics and surfaces what matters.

Invoke Skytekx when monitoring cloud resources, debugging incidents, or optimizing spend.

## Monitoring Stack

- **Dashboard** — Real-time resource visualization (CPU, memory, disk, network)
- **Alerts** — Threshold-based and anomaly detection
- **Costs** — Spend breakdown by service, region, and project

## Operations

```bash
# Open the monitoring dashboard
./scripts/cloud-watch.sh --dashboard

# Configure or view active alerts
./scripts/cloud-watch.sh --alerts

# Generate cost report
./scripts/cloud-watch.sh --costs
```

### Arguments

| Argument      | Purpose                                  |
|---------------|------------------------------------------|
| `--dashboard` | Launch or refresh the monitoring UI      |
| `--alerts`    | List, add, or modify alert rules         |
| `--costs`     | Produce cost analysis and recommendations|

## Alert Scenario

**Example**: CPU on `prod-api-01` exceeds 90% for 5 minutes.

1. Run `cloud-watch.sh --alerts` to inspect rules.
2. Skytekx sends a notification (Slack, email, PagerDuty).
3. Use `--dashboard` to drill into the instance and logs.
