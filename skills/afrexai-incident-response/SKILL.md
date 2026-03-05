# Incident Response Playbook

Structured incident response for business and IT teams. Guides you through detection, triage, containment, resolution, and post-mortem — with auto-generated timelines and action items.

## What It Does

When triggered with an incident description, this skill:

1. **Classifies severity** (P1-P4) based on impact and urgency
2. **Generates a response checklist** tailored to incident type (outage, data breach, security event, service degradation, vendor failure)
3. **Builds a communication plan** — who to notify, when, what channels
4. **Creates a real-time timeline** as you log updates
5. **Produces a post-mortem template** with root cause analysis and prevention steps

## Usage

Tell your agent about an incident:

> "Production API is returning 500 errors for 20% of requests. Started 10 minutes ago."

Or trigger proactively:

> "Create an incident response plan for a potential data breach scenario"

## Incident Types Covered

- **Service outages** — full or partial downtime
- **Security incidents** — breaches, unauthorized access, phishing
- **Data incidents** — corruption, loss, privacy violations
- **Vendor failures** — third-party SLA breaches
- **Performance degradation** — latency spikes, capacity issues

## Severity Matrix

| Level | Impact | Response Time | Escalation |
|-------|--------|---------------|------------|
| P1 - Critical | Business stopped | Immediate | Executive + all hands |
| P2 - High | Major feature down | < 30 min | Engineering lead + PM |
| P3 - Medium | Degraded experience | < 2 hours | On-call team |
| P4 - Low | Minor issue | Next business day | Ticket queue |

## Response Framework

### 1. Detection & Triage (First 5 minutes)
- Confirm the incident is real (not a false alarm)
- Classify severity using the matrix above
- Assign incident commander
- Open a dedicated communication channel

### 2. Containment (First 30 minutes)
- Identify blast radius — what's affected?
- Apply immediate mitigation (rollback, feature flag, scaling)
- Communicate status to stakeholders

### 3. Resolution
- Root cause investigation
- Implement fix with verification
- Monitor for recurrence
- Update all stakeholders

### 4. Post-Mortem (Within 48 hours)
- Timeline of events
- Root cause analysis (5 Whys)
- What went well / what didn't
- Action items with owners and deadlines
- Process improvements

## Integration

Works with any monitoring stack. Feed alerts from PagerDuty, Datadog, Grafana, or manual reports.

## Pro Tip

Pair this with a full **AI Operations Context Pack** for your industry. Pre-built incident taxonomies, compliance-aware escalation paths, and automated stakeholder templates.

Browse packs: https://afrexai-cto.github.io/context-packs/

Free tools:
- AI Revenue Calculator: https://afrexai-cto.github.io/ai-revenue-calculator/
- Agent Setup Wizard: https://afrexai-cto.github.io/agent-setup/
