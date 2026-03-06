# Alerting Best Practices

## The Golden Rule

> **Every alert should require action.** If an alert fires and the response is "ignore it," delete the alert.

## Alert Types

| Type | Trigger | Best For |
|------|---------|----------|
| **Threshold** | Metric crosses static value | CPU > 90%, disk > 85% |
| **Anomaly** | Deviation from historical pattern | Traffic drops 50% vs last week |
| **Availability** | Endpoint unreachable | HTTP check fails 3 times |
| **SLO-based** | Error budget burning too fast | 99.9% SLO at risk |

## Severity Levels

| Severity | Response Time | Impact | Example |
|----------|---------------|--------|---------|
| **P1/Critical** | < 15 min | Revenue loss, total outage | Production down |
| **P2/High** | < 1 hour | Major feature broken | Payments failing |
| **P3/Medium** | < 4 hours | Minor feature affected | Notifications delayed |
| **P4/Low** | Next business day | No user impact yet | Disk at 70% |

## Notification Routing

```
P1 → PagerDuty → Phone call → SMS → Escalation
P2 → PagerDuty → Push notification → Slack
P3 → Slack channel only
P4 → Email digest (daily)
```

### Channel Selection

| Channel | Latency | Use For |
|---------|---------|---------|
| PagerDuty/Opsgenie | 30s | P1, P2 (on-call) |
| Phone call | 60s | P1 escalation |
| Slack/Discord | 1-5s | P2, P3 (team awareness) |
| Telegram | 1-3s | Personal alerts, small teams |
| Email | 1-5min | P4, summaries |

## Alert Fatigue

**Symptoms:**
- Alerts muted or ignored
- On-call dreads their shift
- Important alerts lost in noise

**Causes:**
- Too many alerts (>5/day per person)
- Flapping alerts (fires, resolves, fires)
- Non-actionable alerts ("CPU at 45%")
- Missing context (what to do?)

**Fixes:**

| Problem | Solution |
|---------|----------|
| Too many alerts | Delete alerts nobody acts on |
| Flapping | Add hysteresis (`for: 5m`) |
| Not actionable | Add runbook link |
| No context | Include key metrics in alert |

## Runbooks (Required for P1/P2)

Every critical alert needs a runbook:

```markdown
## Alert: payment_errors_high

### What does this mean?
Error rate in payment service > 5% for 5 minutes.

### Impact
Users cannot complete purchases.

### Quick diagnosis
1. Check Stripe status: status.stripe.com
2. Check recent deploys: kubectl rollout history
3. Check logs: kubectl logs -l app=payments --tail=100

### Actions
- If Stripe is down: Post status update, wait
- If our bug: Rollback with `kubectl rollout undo`
- If unclear: Page payments team lead

### Escalation
After 15 min without resolution → page engineering manager
```

## On-Call Setup

### Rotation Schedule
```
Week 1: Alice (primary), Bob (secondary)
Week 2: Bob (primary), Carol (secondary)
Week 3: Carol (primary), Alice (secondary)
```

### Escalation Policy
```
0-10 min:  Primary on-call
10-20 min: Secondary on-call
20-30 min: Team lead
30+ min:   Engineering manager
```

### Tools
| Tool | Pricing | Notes |
|------|---------|-------|
| **PagerDuty** | $21/user/mo | Industry standard |
| **Opsgenie** | $9/user/mo | Good value |
| **Grafana OnCall** | Free (OSS) | Self-hosted option |

## SLO-Based Alerting

Instead of "error rate > 1%", alert on "error budget burning too fast."

**Example:** 99.9% availability SLO = 43 min downtime/month budget

**Burn rate alerts:**
| Burn Rate | Alert After | Meaning |
|-----------|-------------|---------|
| 14.4x | 2 min | Budget gone in 2 hours |
| 6x | 15 min | Budget gone in 5 hours |
| 1x | 1 hour | Budget on track to exhaust |

```yaml
# Prometheus alert rule
- alert: ErrorBudgetBurn
  expr: |
    (
      sum(rate(http_requests_total{status=~"5.."}[1h]))
      / sum(rate(http_requests_total[1h]))
    ) > 14.4 * 0.001  # 14.4x burn rate for 99.9% SLO
  for: 2m
  labels:
    severity: critical
```

## Alertmanager Config Example

```yaml
# alertmanager.yml
global:
  resolve_timeout: 5m

route:
  receiver: 'default'
  group_by: ['alertname', 'severity']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  routes:
    - match:
        severity: critical
      receiver: 'pagerduty-critical'
    - match:
        severity: warning
      receiver: 'slack-warnings'

receivers:
  - name: 'default'
    slack_configs:
      - channel: '#alerts'
        
  - name: 'pagerduty-critical'
    pagerduty_configs:
      - service_key: 'xxx'
        
  - name: 'slack-warnings'
    slack_configs:
      - channel: '#alerts-low'
```
