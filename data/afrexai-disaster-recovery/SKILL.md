---
name: IT Disaster Recovery Plan Generator
description: Build production-ready disaster recovery plans that actually get
  followed when things break.
---

# IT Disaster Recovery Plan Generator

Build production-ready disaster recovery plans that actually get followed when things break.

## What This Does

Generates a complete DR plan covering infrastructure, data, applications, and communications. Output includes RTO/RPO targets, failover procedures, testing schedules, and cost modeling.

## When to Use

- Building DR documentation for compliance (SOC 2, ISO 27001, HIPAA)
- After an outage exposed gaps in your recovery process
- Onboarding a new infrastructure team
- Annual DR plan review and update

## How to Use

Tell the agent what you need. Be specific about your stack and requirements.

### Quick Start
```
Generate a disaster recovery plan for our SaaS platform. Stack: AWS (us-east-1 primary, eu-west-1 secondary), PostgreSQL RDS, Redis, S3. RTO target: 4 hours. RPO target: 1 hour. Team size: 8 engineers.
```

### Inputs to Provide
- **Infrastructure**: Cloud provider, regions, key services
- **Data stores**: Databases, object storage, message queues
- **RTO target**: Maximum acceptable downtime
- **RPO target**: Maximum acceptable data loss
- **Team size**: Who's available during an incident
- **Compliance**: Which frameworks apply (SOC 2, ISO 27001, HIPAA, PCI DSS)
- **Budget tier**: Startup ($5K-$15K/yr) | Growth ($15K-$50K/yr) | Enterprise ($50K+/yr)

## Output Structure

### 1. Risk Assessment Matrix
| Threat | Likelihood (1-5) | Impact (1-5) | Risk Score | Mitigation |
|--------|------------------|--------------|------------|------------|
| Region outage | 2 | 5 | 10 | Multi-region active-active |
| Database corruption | 3 | 5 | 15 | Point-in-time recovery + cross-region replicas |
| Ransomware | 3 | 5 | 15 | Immutable backups + air-gapped copies |
| DNS failure | 2 | 4 | 8 | Multiple DNS providers |
| Key person unavailable | 4 | 3 | 12 | Runbook documentation + cross-training |

### 2. Recovery Tier Classification
**Tier 1 — Critical (RTO < 1hr)**
- Authentication service
- Payment processing
- Core API

**Tier 2 — Important (RTO < 4hr)**
- Admin dashboard
- Reporting
- Email delivery

**Tier 3 — Standard (RTO < 24hr)**
- Analytics
- Internal tools
- Dev/staging environments

### 3. Failover Procedures
For each Tier 1 service, generate step-by-step runbooks:
- Pre-failover health checks
- DNS/load balancer switchover steps
- Data consistency verification
- Post-failover smoke tests
- Rollback procedure if failover fails

### 4. Backup Strategy
| Data Store | Backup Frequency | Retention | Location | Recovery Test Frequency |
|-----------|-----------------|-----------|----------|----------------------|
| Primary DB | Continuous (WAL) | 30 days | Cross-region | Monthly |
| Object Storage | Cross-region replication | Indefinite | Secondary region | Quarterly |
| Config/Secrets | On change | 90 days | Encrypted S3 + local | Monthly |

### 5. Communication Plan
- **Internal escalation**: PagerDuty/Opsgenie chain with backup contacts
- **Status page**: Auto-update triggers at incident declaration
- **Customer notification**: Templates for P1-P4 severity levels
- **Executive briefing**: 15-min cadence during P1, hourly during P2

### 6. Testing Schedule
| Test Type | Frequency | Scope | Duration |
|-----------|-----------|-------|----------|
| Tabletop exercise | Quarterly | Full team walkthrough | 2 hours |
| Component failover | Monthly | Individual service | 1 hour |
| Full DR simulation | Annually | Complete failover | 4-8 hours |
| Backup restore | Monthly | Random data store | 1 hour |

### 7. Cost Model
Break down DR spending by category:
- Infrastructure (standby capacity, cross-region replication)
- Tooling (monitoring, alerting, backup software)
- Testing (engineer hours, cloud costs during drills)
- Training (onboarding, annual refreshers)

Benchmark: DR typically costs 15-25% of primary infrastructure spend. Companies without DR plans face average downtime costs of $5,600/minute.

## Compliance Mapping

Map each DR control to framework requirements:
- **SOC 2 CC7.4/CC7.5**: Incident response and recovery
- **ISO 27001 A.17**: Information security continuity
- **HIPAA §164.308(a)(7)**: Contingency plan
- **PCI DSS 12.10**: Incident response plan

## Rules
- Always include specific commands and CLI examples (not just "failover the database")
- Include estimated time for each step in runbooks
- Flag single points of failure explicitly
- Default to the 3-2-1 backup rule: 3 copies, 2 media types, 1 offsite
- Include cost estimates in USD for each recommendation
- Never assume unlimited budget — tier recommendations by cost

## Next Steps

Want to go deeper? Check out the full [AI Context Packs](https://afrexai-cto.github.io/context-packs/) — pre-built knowledge bases for SaaS, Healthcare, Legal, Manufacturing, and more. $47 per industry pack, or grab all 10 for $197.

Calculate what manual DR planning costs your team: [AI Revenue Calculator](https://afrexai-cto.github.io/ai-revenue-calculator/)

Set up your agent stack in 5 minutes: [Agent Setup Wizard](https://afrexai-cto.github.io/agent-setup/)
