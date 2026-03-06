---
name: sla-monitor
description: Set up SLA monitoring and uptime tracking for AI agents and services. Generates monitoring configs, alert rules, and incident response playbooks. Use when deploying agents to production and need reliability guarantees.
---

# SLA Monitor Skill

## Purpose
Help teams set up production-grade monitoring for AI agents and automated services. Covers uptime tracking, response time SLAs, error budgets, and incident escalation.

## When to Use
- Deploying AI agents to production
- Setting up monitoring for client-facing automation
- Creating SLA documentation for service agreements
- Building incident response procedures

## Monitoring Stack Options

### Option 1: UptimeRobot (Free tier available)
- 50 monitors free, 5-minute intervals
- HTTP, keyword, ping, port monitors
- Email + Slack + webhook alerts

### Option 2: Better Stack (Formerly Uptime.com)
- Status pages included
- Incident management built-in
- Free tier: 10 monitors

### Option 3: Self-Hosted (Uptime Kuma)
```bash
docker run -d --restart=always -p 3001:3001 -v uptime-kuma:/app/data --name uptime-kuma louislam/uptime-kuma:1
```

## SLA Tiers

### Tier 1: Standard ($1,500/mo)
- 99.5% uptime guarantee (43.8h downtime/year)
- Response within 4 hours (business hours)
- Monthly performance report

### Tier 2: Professional ($3,000/mo)
- 99.9% uptime guarantee (8.76h downtime/year)
- Response within 1 hour (business hours)
- Weekly performance reports
- Quarterly optimization reviews

### Tier 3: Enterprise ($5,000+/mo)
- 99.95% uptime (4.38h downtime/year)
- Response within 15 minutes (24/7)
- Real-time dashboard access
- Dedicated support channel

## Alert Configuration Template

```yaml
monitors:
  - name: "Agent Health Check"
    type: http
    url: "https://your-agent-endpoint/health"
    interval: 300  # 5 minutes
    alerts:
      - type: email
        threshold: 1  # alert after 1 failure
      - type: slack
        webhook: "${SLACK_WEBHOOK}"
        threshold: 2  # alert after 2 consecutive failures
      - type: sms
        threshold: 3  # escalate after 3 failures

  - name: "API Response Time"
    type: http
    url: "https://your-agent-endpoint/api"
    interval: 60
    expected_response_time: 2000  # ms
    alerts:
      - type: slack
        condition: "response_time > 5000"

error_budget:
  monthly_target: 99.9
  burn_rate_alert: 2.0  # Alert if burning 2x normal rate
```

## Incident Response Playbook

### Severity 1 — Total Outage
1. Acknowledge within 5 minutes
2. Status page update within 10 minutes
3. Root cause identification within 30 minutes
4. Resolution or workaround within 2 hours
5. Post-mortem within 24 hours

### Severity 2 — Degraded Performance
1. Acknowledge within 15 minutes
2. Investigation within 30 minutes
3. Resolution within 4 hours
4. Summary report within 48 hours

### Severity 3 — Minor Issue
1. Acknowledge within 1 hour
2. Resolution within 24 hours
3. Logged for next review cycle

## Error Budget Calculator

```
Monthly minutes: 43,200 (30 days)
99.9% SLA = 43.2 minutes downtime allowed
99.5% SLA = 216 minutes downtime allowed
99.0% SLA = 432 minutes downtime allowed

Burn rate = (actual downtime / budget) × 100
If burn rate > 50% with 2+ weeks remaining → review needed
If burn rate > 80% → freeze deployments
```

## Status Page Template

Provide clients with a public status page showing:
- Current system status (operational / degraded / outage)
- Component-level status (Agent A, Agent B, API, Dashboard)
- Uptime percentage (30-day rolling)
- Incident history with resolution notes
- Scheduled maintenance windows

## Next Steps

Need managed AI agents with built-in SLA monitoring?
→ AfrexAI handles deployment, monitoring, and maintenance for $1,500/mo
→ Book a call: https://calendly.com/cbeckford-afrexai/30min
→ Learn more: https://afrexai-cto.github.io/aaas/landing.html
