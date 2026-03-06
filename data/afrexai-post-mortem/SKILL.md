---
name: Post-Mortem & Incident Review Framework
description: Run structured post-mortems that actually prevent repeat failures.
  Blameless analysis, root cause identification, and action tracking.
---

# Post-Mortem & Incident Review Framework

Run structured post-mortems that actually prevent repeat failures. Blameless analysis, root cause identification, and action tracking.

## When to Use
- After any production incident, outage, or service degradation
- After a missed deadline, failed launch, or lost deal
- After any event costing >$5K or >4 hours of team time
- Quarterly review of recurring incident patterns

## Post-Mortem Template

### 1. Incident Summary (Complete Within 24 Hours)
```
Incident ID: [AUTO-GENERATED]
Date/Time: [Start] → [End] (Duration: X hours)
Severity: SEV-1 (revenue impact) | SEV-2 (customer impact) | SEV-3 (internal impact)
Impact: [Users affected] | [Revenue lost] | [SLA breached Y/N]
Detection: How was it found? (Monitoring / Customer report / Internal discovery)
Detection Delay: Time from incident start → first alert
```

### 2. Timeline (Minute-by-Minute for SEV-1, 15-min blocks for SEV-2/3)
```
HH:MM - Event description
HH:MM - First alert triggered
HH:MM - Team notified
HH:MM - Investigation started
HH:MM - Root cause identified
HH:MM - Fix deployed
HH:MM - Confirmed resolved
```

### 3. Root Cause Analysis — 5 Whys
```
Why 1: [Direct cause]
Why 2: [Why did that happen?]
Why 3: [Why did THAT happen?]
Why 4: [Systemic cause]
Why 5: [Organizational/cultural root]
```

### 4. Contributing Factors
Score each factor 0-3 (0=not a factor, 3=primary contributor):

| Factor | Score | Notes |
|---|---|---|
| Missing/inadequate monitoring | | |
| Insufficient testing | | |
| Documentation gaps | | |
| Process not followed | | |
| Knowledge concentration (bus factor) | | |
| Capacity/scaling limits | | |
| Third-party dependency | | |
| Communication breakdown | | |
| Change management failure | | |
| Technical debt | | |

### 5. What Went Well
List 3-5 things that worked during the response:
- Fast detection? Good runbooks? Strong communication? Quick escalation?

### 6. Action Items
Every action MUST have an owner and deadline:

| # | Action | Owner | Deadline | Priority | Status |
|---|---|---|---|---|---|
| 1 | | | | P0/P1/P2 | Open |

**Priority definitions:**
- P0: Must complete before next business day
- P1: Must complete within 1 week
- P2: Must complete within 1 sprint/month

### 7. Recurrence Prevention
- [ ] Monitoring added/improved for this failure mode
- [ ] Runbook created/updated
- [ ] Test coverage added
- [ ] Architecture change needed? (If yes, create RFC)
- [ ] Training needed for team?

## Blameless Post-Mortem Rules
1. Focus on systems, not individuals
2. "What happened" not "who did it"
3. Assume everyone acted with best intentions and available information
4. The goal is learning, not punishment
5. If you find yourself writing someone's name next to a mistake, rewrite it as a process gap

## Incident Cost Calculator
```
Direct costs:
  Revenue lost during downtime: $___
  SLA credits issued: $___
  Emergency vendor/contractor costs: $___

Indirect costs:
  Engineering hours × loaded rate: ___ hrs × $___/hr = $___
  Customer churn risk (affected users × churn probability × LTV): $___
  Brand/reputation (estimate): $___

Total incident cost: $___
Cost per minute of downtime: $___
```

## Quarterly Incident Review
Every quarter, analyze patterns across all post-mortems:

1. **Top 3 root cause categories** — Where should you invest in prevention?
2. **Mean time to detect (MTTD)** — Is monitoring improving?
3. **Mean time to resolve (MTTR)** — Is response getting faster?
4. **Action item completion rate** — Are you actually fixing things?
5. **Repeat incidents** — Same root cause twice = systemic failure
6. **Cost trend** — Total incident cost per quarter (should decrease)

## Industry-Specific Post-Mortem Considerations

| Industry | Key Focus | Regulatory Requirement |
|---|---|---|
| Fintech | Transaction integrity, audit trail | SOX, PCI-DSS incident reporting |
| Healthcare | PHI exposure, patient safety | HIPAA breach notification (60 days) |
| SaaS | SLA compliance, data integrity | SOC 2 incident management |
| E-commerce | Order integrity, payment processing | PCI-DSS, consumer protection |
| Manufacturing | Safety incidents, production loss | OSHA reporting requirements |

---

## Go Deeper

Your post-mortems reveal where AI agents should be deployed first — the repetitive failures, the manual monitoring gaps, the processes that break under load.

- **Find your highest-cost gaps:** [AI Revenue Leak Calculator](https://afrexai-cto.github.io/ai-revenue-calculator/)
- **Industry-specific deployment playbooks:** [AfrexAI Context Packs — $47](https://afrexai-cto.github.io/context-packs/)
  - Pick 3: $97 | All 10: $197 | Everything: $247
- **Deploy your first agent:** [Agent Setup Wizard](https://afrexai-cto.github.io/agent-setup/)

*Built by [AfrexAI](https://afrexai-cto.github.io/context-packs/) — turning incident patterns into automation opportunities.*
