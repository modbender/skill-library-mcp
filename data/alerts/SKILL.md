---
name: Alerts
description: Smart alerting patterns for AI agents - deduplication, routing, escalation, and fatigue prevention
---

## Alert Fatigue Prevention

**Group alerts by root cause, never by individual symptoms.**
Use labels: `alertname`, `service`, `cluster` - not instance IDs.
```bash
# Good: One alert for database down affecting 50 pods
group_by: ['alertname', 'service']
# Bad: 50 individual alerts for each failed pod
```

**Implement severity hierarchy: P0 (pages immediately) > P1 (within 15min) > P2 (business hours) > P3 (weekly review).**
P0: Service completely down, data loss, security breach.
P1: Degraded performance, partial outage, high error rates.

**Set cooldown periods to prevent alert spam.**
Minimum 5 minutes between identical alerts, 30 minutes for cost alerts.
```bash
repeat_interval: 5m  # For critical alerts
repeat_interval: 30m # For cost/performance alerts
```

**Use inhibition rules to suppress symptoms when root cause fires.**
If "Database Unreachable" fires, silence all "API High Latency" alerts from same cluster.

## AI Agent Monitoring Patterns

**Monitor token/API usage with exponential alerting thresholds.**
Alert at 2x, 5x, 10x normal usage - costs can spiral quickly.
Track: tokens per minute, cost per request, API rate limits approached.

**Set behavioral drift alerts on response quality degradation.**
Compare current outputs to baseline with sample prompts every hour.
Alert when success rate drops below 85% or response time exceeds 2x baseline.

**Monitor for infinite loops in multi-agent workflows.**
Alert if same prompt sent >3 times in 5 minutes or agent hasn't responded in 10 minutes.
Include correlation IDs to trace conversation chains.

**Track silent failures through downstream metrics.**
Monitor: tasks completed vs started, user satisfaction scores, retry attempts.
These catch errors that don't throw exceptions.

## Routing and Escalation Rules

**Route by expertise domain, not arbitrary on-call schedules.**
Database alerts → DB team, API alerts → backend team, cost alerts → platform team.
Only escalate to managers for P0 incidents lasting >30 minutes.

**Use progressive escalation with increasing urgency.**
P1 alerts: Slack notification → 5min wait → SMS → 10min wait → phone call.
Include runbook links in every alert for faster resolution.

**Set context-aware routing based on time and impact.**
Business hours: Route to primary team. Off-hours: Route to on-call only for P0/P1.
If >100 users affected: Immediately escalate regardless of severity.

## Webhook Reliability Patterns

**Always include correlation IDs for alert lifecycle management.**
Generate UUID for each incident, use it to create/update/resolve alerts.
Essential for bi-directional integrations with PagerDuty/Slack.

**Implement exponential backoff for webhook failures.**
Retry after 1s, 2s, 4s, 8s, 16s, then mark failed and escalate.
Log webhook response codes/times for debugging delivery issues.

**Use webhook verification to prevent spoofing.**
Validate signatures using HMAC-SHA256 with shared secret.
Always check timestamp to prevent replay attacks (max 5 min old).

**Implement circuit breaker pattern for unreliable endpoints.**
After 5 consecutive failures, mark endpoint down and use backup channel.
Re-test every 30 seconds until recovery confirmed.

## Status Page Integration

**Update status page automatically when P0/P1 alerts fire.**
Create incident, post initial assessment within 5 minutes.
Include ETA and workaround if available.

**Use component-based status updates matching your alert groups.**
Map alert labels to status page components (API, Database, Auth, etc.).
Partial outages should show "Degraded Performance", not "Operational".

## Runbook Automation

**Embed runbook links directly in alert messages.**
Format: "Alert: High CPU on web-01. Runbook: https://wiki/runbooks/high-cpu-web"
Links must be accessible from mobile devices for on-call engineers.

**Trigger automated remediation for known issues.**
Auto-restart stuck services, clear full disks, reset rate limits.
Always require human approval for destructive actions (scaling down, deleting data).

**Log all automated actions taken in response to alerts.**
Include: timestamp, action, result, approval chain.
Essential for post-incident reviews and compliance audits.
