---
name: SRE & Incident Management Platform
description: Complete Site Reliability Engineering system — from SLO definition
  through incident response, chaos engineering, and operational excellence. Zero
  dependencies.
---

# SRE & Incident Management Platform

Complete Site Reliability Engineering system — from SLO definition through incident response, chaos engineering, and operational excellence. Zero dependencies.

---

## Phase 1: Reliability Assessment

Before building anything, assess where you are.

### Service Catalog Entry

```yaml
service:
  name: ""
  tier: ""  # critical | important | standard | experimental
  owner_team: ""
  oncall_rotation: ""
  dependencies:
    upstream: []    # services we call
    downstream: []  # services that call us
  data_classification: ""  # public | internal | confidential | restricted
  deployment_frequency: ""  # daily | weekly | biweekly | monthly
  architecture: ""  # monolith | microservice | serverless | hybrid
  language: ""
  infra: ""  # k8s | ECS | Lambda | VM | bare-metal
  traffic_pattern: ""  # steady | diurnal | spiky | seasonal
  peak_rps: 0
  storage_gb: 0
  monthly_cost_usd: 0
```

### Maturity Assessment (Score 1-5 per dimension)

| Dimension | 1 (Ad-hoc) | 3 (Defined) | 5 (Optimized) | Score |
|-----------|-----------|-------------|---------------|-------|
| SLOs | No SLOs defined | SLOs exist, reviewed quarterly | Data-driven SLOs, auto error budgets | |
| Monitoring | Basic health checks | Golden signals + dashboards | Full observability, anomaly detection | |
| Incident Response | No runbooks, hero culture | Documented process, postmortems | Automated detection, structured ICS | |
| Automation | Manual deployments | CI/CD pipeline, some automation | Self-healing, auto-scaling, GitOps | |
| Chaos Engineering | No testing | Basic failure injection | Continuous chaos in production | |
| Capacity Planning | Reactive scaling | Quarterly forecasting | Predictive auto-scaling | |
| Toil Management | >50% toil | Toil tracked, reduction plans | <25% toil, systematic elimination | |
| On-Call Health | Burnout, 24/7 individuals | Rotation exists, escalation paths | Balanced load, <2 pages/shift | |

**Score interpretation:**
- 8-16: Firefighting mode — start with SLOs + incident process
- 17-24: Foundation built — add chaos engineering + toil reduction
- 25-32: Maturing — optimize error budgets + capacity planning
- 33-40: Advanced — focus on predictive reliability + culture

---

## Phase 2: SLI/SLO Framework

### SLI Selection by Service Type

| Service Type | Primary SLI | Secondary SLIs |
|-------------|-------------|----------------|
| API/Backend | Request success rate | Latency p50/p95/p99, throughput |
| Frontend/Web | Page load (LCP) | FID/INP, CLS, error rate |
| Data Pipeline | Freshness | Correctness, completeness, throughput |
| Storage | Durability | Availability, latency |
| Streaming | Processing latency | Throughput, ordering, data loss rate |
| Batch Job | Success rate | Duration, SLA compliance |
| ML Model | Prediction latency | Accuracy drift, feature freshness |

### SLI Specification Template

```yaml
sli:
  name: "request_success_rate"
  description: "Proportion of valid requests served successfully"
  type: "availability"  # availability | latency | quality | freshness
  measurement:
    good_events: "HTTP responses with status < 500"
    total_events: "All HTTP requests excluding health checks"
    source: "load balancer access logs"
    aggregation: "sum(good) / sum(total) over rolling 28-day window"
  exclusions:
    - "Health check endpoints (/healthz, /readyz)"
    - "Synthetic monitoring traffic"
    - "Requests from blocked IPs"
    - "4xx responses (client errors)"
```

### SLO Target Selection Guide

| Nines | Uptime % | Downtime/month | Appropriate for |
|-------|----------|----------------|-----------------|
| 2 nines | 99% | 7h 18m | Internal tools, dev environments |
| 2.5 | 99.5% | 3h 39m | Non-critical services, backoffice |
| 3 nines | 99.9% | 43m 50s | Standard production services |
| 3.5 | 99.95% | 21m 55s | Important customer-facing services |
| 4 nines | 99.99% | 4m 23s | Critical services, payments, auth |
| 5 nines | 99.999% | 26s | Life-safety, financial clearing |

**Rules for setting targets:**
1. Start lower than you think — you can always tighten
2. SLO < SLA (always have buffer — typically 0.1-0.5% margin)
3. Internal SLO < External SLO (catch problems before customers do)
4. Each nine costs ~10x more to achieve
5. If you can't measure it, you can't SLO it

### SLO Document Template

```yaml
slo:
  service: ""
  sli: ""
  target: 99.9  # percentage
  window: "28d"  # rolling window
  error_budget: 0.1  # 100% - target
  error_budget_minutes: 40  # per 28-day window
  
  burn_rate_alerts:
    - name: "fast_burn"
      burn_rate: 14.4  # exhausts budget in 2 hours
      short_window: "5m"
      long_window: "1h"
      severity: "page"
    - name: "medium_burn"
      burn_rate: 6.0   # exhausts budget in ~5 hours
      short_window: "30m"
      long_window: "6h"
      severity: "page"
    - name: "slow_burn"
      burn_rate: 1.0   # exhausts budget in 28 days
      short_window: "6h"
      long_window: "3d"
      severity: "ticket"
  
  review_cadence: "monthly"
  owner: ""
  stakeholders: []
  
  escalation_when_budget_exhausted:
    - "Halt non-critical deployments"
    - "Redirect engineering to reliability work"
    - "Escalate to VP Engineering if no improvement in 48h"
```

---

## Phase 3: Error Budget Management

### Error Budget Policy

```yaml
error_budget_policy:
  service: ""
  
  budget_states:
    healthy:
      condition: "remaining_budget > 50%"
      actions:
        - "Normal development velocity"
        - "Feature work prioritized"
        - "Chaos experiments allowed"
    
    warning:
      condition: "remaining_budget 25-50%"
      actions:
        - "Increase monitoring scrutiny"
        - "Review recent changes for risk"
        - "Limit risky deployments to business hours"
        - "No chaos experiments"
    
    critical:
      condition: "remaining_budget 0-25%"
      actions:
        - "Feature freeze — reliability work only"
        - "All deployments require SRE approval"
        - "Mandatory rollback plan for every change"
        - "Daily error budget review"
    
    exhausted:
      condition: "remaining_budget <= 0"
      actions:
        - "Complete deployment freeze"
        - "All engineering redirected to reliability"
        - "VP Engineering notified"
        - "Postmortem required for budget exhaustion"
        - "Freeze maintained until budget recovers to 10%"
  
  exceptions:
    - "Security patches always allowed"
    - "Regulatory compliance changes always allowed"
    - "Data loss prevention always allowed"
  
  reset: "Rolling 28-day window (no manual resets)"
```

### Burn Rate Calculation

```
Burn rate = (error rate observed) / (error rate allowed by SLO)

Example:
- SLO: 99.9% (error budget = 0.1%)
- Current error rate: 0.5%
- Burn rate = 0.5% / 0.1% = 5x

At 5x burn rate → budget exhausted in 28d / 5 = 5.6 days
```

### Error Budget Dashboard

Track weekly:

| Metric | Current | Trend | Status |
|--------|---------|-------|--------|
| Budget remaining (%) | | ↑↓→ | 🟢🟡🔴 |
| Budget consumed this week | | | |
| Burn rate (1h / 6h / 24h) | | | |
| Incidents consuming budget | | | |
| Top error contributor | | | |
| Projected exhaustion date | | | |

---

## Phase 4: Monitoring & Alerting Architecture

### Four Golden Signals

| Signal | What to Measure | Alert When |
|--------|----------------|------------|
| **Latency** | p50, p95, p99 response time | p99 > 2x baseline for 5 min |
| **Traffic** | Requests/sec, concurrent users | >30% drop (indicates upstream issue) OR >50% spike |
| **Errors** | 5xx rate, timeout rate, exception rate | Error rate > SLO burn rate threshold |
| **Saturation** | CPU, memory, disk, connections, queue depth | >80% sustained for 10 min |

### USE Method (Infrastructure)

For every resource, track:
- **Utilization**: % of capacity used (0-100%)
- **Saturation**: queue depth / wait time (0 = no waiting)
- **Errors**: error count / error rate

### RED Method (Services)

For every service, track:
- **Rate**: requests per second
- **Errors**: failed requests per second
- **Duration**: latency distribution

### Alert Design Rules

1. **Every alert must have a runbook link** — no exceptions
2. **Every alert must be actionable** — if you can't act on it, delete it
3. **Symptoms over causes** — alert on "users can't check out" not "database CPU high"
4. **Multi-window, multi-burn-rate** — avoid single-threshold alerts
5. **Page only for customer impact** — everything else is a ticket
6. **Alert fatigue = death** — review alert volume monthly; target <5 pages/week per service

### Alert Severity Guide

| Severity | Response Time | Notification | Examples |
|----------|--------------|-------------|----------|
| P0/Page | <5 min | PagerDuty + phone | SLO burn rate critical, data loss, security breach |
| P1/Urgent | <30 min | Slack + PagerDuty | Degraded service, elevated errors, capacity warning |
| P2/Ticket | Next business day | Ticket auto-created | Slow burn, non-critical component down |
| P3/Log | Weekly review | Dashboard only | Informational, trend detection |

### Structured Log Standard

```json
{
  "timestamp": "2026-02-17T11:24:00.000Z",
  "level": "error",
  "service": "payment-api",
  "trace_id": "abc123",
  "span_id": "def456",
  "message": "Payment processing failed",
  "error_type": "TimeoutException",
  "error_message": "Gateway timeout after 30s",
  "http_method": "POST",
  "http_path": "/api/v1/payments",
  "http_status": 504,
  "duration_ms": 30012,
  "customer_id": "cust_xxx",
  "payment_id": "pay_yyy",
  "amount_cents": 4999,
  "retry_count": 2,
  "environment": "production",
  "host": "payment-api-7b4d9-xk2p1",
  "region": "us-east-1"
}
```

---

## Phase 5: Incident Response Framework

### Severity Classification Matrix

| | Impact: 1 User | Impact: <25% Users | Impact: >25% Users | Impact: All Users |
|-|----------------|--------------------|--------------------|-------------------|
| **Core function down** | SEV3 | SEV2 | SEV1 | SEV1 |
| **Degraded performance** | SEV4 | SEV3 | SEV2 | SEV1 |
| **Non-core feature down** | SEV4 | SEV3 | SEV3 | SEV2 |
| **Cosmetic/minor** | SEV4 | SEV4 | SEV3 | SEV3 |

**Auto-escalation triggers:**
- Any data loss → SEV1 minimum
- Security breach with PII → SEV1
- Revenue-impacting → SEV1 or SEV2
- SLA breach imminent → auto-escalate one level

### Incident Command System (ICS)

| Role | Responsibility | Assigned |
|------|---------------|----------|
| **Incident Commander (IC)** | Owns resolution, makes decisions, manages timeline | |
| **Communications Lead** | Status updates, stakeholder comms, customer-facing | |
| **Operations Lead** | Hands-on-keyboard, executing fixes | |
| **Subject Matter Expert** | Deep knowledge of affected system | |
| **Scribe** | Documenting timeline, actions, decisions | |

**IC Rules:**
1. IC does NOT debug — IC coordinates
2. IC makes final decisions when team disagrees
3. IC can escalate severity at any time
4. IC owns handoff if rotation changes
5. IC calls end-of-incident

### Incident Response Workflow

```
DETECT → TRIAGE → RESPOND → MITIGATE → RESOLVE → REVIEW

Step 1: DETECT (0-5 min)
├── Alert fires OR user report received
├── On-call acknowledges within SLA
└── Quick assessment: is this real? What severity?

Step 2: TRIAGE (5-15 min)
├── Classify severity using matrix above
├── Assign IC and roles
├── Open incident channel (#inc-YYYY-MM-DD-title)
├── Post initial status update
└── Start timeline document

Step 3: RESPOND (15 min - ongoing)
├── IC briefs team: "Here's what we know, here's what we don't"
├── Operations Lead begins investigation
├── Check: recent deployments? Config changes? Dependency issues?
├── Parallel investigation tracks if needed
└── 15-minute check-ins for SEV1, 30-min for SEV2

Step 4: MITIGATE (ASAP)
├── Priority: STOP THE BLEEDING
├── Options (fastest first):
│   ├── Rollback last deployment
│   ├── Feature flag disable
│   ├── Traffic shift / failover
│   ├── Scale up / circuit breaker
│   └── Manual data fix
├── Mitigated ≠ Resolved — temporary fix is OK
└── Update status: "Impact mitigated, root cause investigation ongoing"

Step 5: RESOLVE
├── Root cause identified and fixed
├── Verification: SLIs back to normal for 30+ minutes
├── All-clear communicated
└── IC declares incident resolved

Step 6: REVIEW (within 5 business days)
├── Blameless postmortem written
├── Action items assigned with owners and deadlines
├── Postmortem review meeting
└── Action items tracked to completion
```

### Communication Templates

**Initial notification (internal):**
```
🔴 INCIDENT: [Title]
Severity: SEV[X]
Impact: [Who/what is affected]
Status: Investigating
IC: [Name]
Channel: #inc-[date]-[slug]
Next update: [time]
```

**Customer-facing status:**
```
[Service] - Investigating increased error rates

We are currently investigating reports of [symptom]. 
Some users may experience [user-visible impact].
Our team is actively working on a resolution.
We will provide an update within [time].
```

**Resolution notification:**
```
✅ RESOLVED: [Title]
Duration: [X hours Y minutes]
Impact: [Summary]
Root cause: [One sentence]
Postmortem: [Link] (within 5 business days)
```

---

## Phase 6: Postmortem Framework

### Blameless Postmortem Template

```yaml
postmortem:
  title: ""
  date: ""
  severity: ""  # SEV1-4
  duration: ""  # total incident duration
  authors: []
  reviewers: []
  status: "draft"  # draft | in-review | final
  
  summary: |
    One paragraph: what happened, what was the impact, how was it resolved.
  
  impact:
    users_affected: 0
    duration_minutes: 0
    revenue_impact_usd: 0
    slo_budget_consumed_pct: 0
    data_loss: false
    customer_tickets: 0
  
  timeline:
    - time: ""
      event: ""
      # Chronological, every significant event
      # Include detection time, escalation, mitigation attempts
  
  root_cause: |
    Technical explanation of WHY it happened.
    Go deep — surface causes are not root causes.
  
  contributing_factors:
    - ""  # What made it worse or delayed resolution?
  
  detection:
    how_detected: ""  # alert | user report | manual check
    time_to_detect_minutes: 0
    could_have_detected_sooner: ""
  
  resolution:
    how_resolved: ""
    time_to_mitigate_minutes: 0
    time_to_resolve_minutes: 0
  
  what_went_well:
    - ""  # Explicitly call out what worked
  
  what_went_wrong:
    - ""
  
  where_we_got_lucky:
    - ""  # Things that could have made it worse
  
  action_items:
    - id: "AI-001"
      type: ""  # prevent | detect | mitigate | process
      description: ""
      owner: ""
      priority: ""  # P0 | P1 | P2
      deadline: ""
      status: "open"  # open | in-progress | done
      ticket: ""
```

### Root Cause Analysis Methods

**Five Whys (simple incidents):**
1. Why did users see errors? → API returned 500s
2. Why did API return 500s? → Database connection pool exhausted
3. Why was pool exhausted? → Long-running query held connections
4. Why was query long-running? → Missing index on new column
5. Why was index missing? → Migration didn't include index; no query performance review in CI

→ **Root cause:** No automated query performance check in deployment pipeline
→ **Action:** Add query plan analysis to CI for migration PRs

**Fishbone / Ishikawa (complex incidents):**

```
Categories to investigate:
├── People: Training? Fatigue? Communication?
├── Process: Runbook? Escalation? Change management?
├── Technology: Bug? Config? Capacity? Dependency?
├── Environment: Network? Cloud provider? Third party?
├── Monitoring: Detection gap? Alert fatigue? Dashboard gap?
└── Testing: Test coverage? Load testing? Chaos testing?
```

**Contributing Factor Categories:**
| Category | Questions |
|----------|-----------|
| Trigger | What change or event started it? |
| Propagation | Why did it spread? Why wasn't it contained? |
| Detection | Why wasn't it caught earlier? |
| Resolution | What slowed the fix? |
| Process | What process gaps contributed? |

### Postmortem Review Meeting (60 min)

```
1. Timeline walk-through (15 min)
   - Author presents chronology
   - Attendees add context ("I remember seeing X at this point")

2. Root cause deep-dive (15 min)  
   - Do we agree on root cause?
   - Are there additional contributing factors?

3. Action item review (20 min)
   - Are these the RIGHT actions?
   - Are they prioritized correctly?
   - Do owners agree on deadlines?

4. Process improvements (10 min)
   - Could we have detected this sooner?
   - Could we have resolved this faster?
   - What would have prevented this entirely?
```

---

## Phase 7: Chaos Engineering

### Chaos Maturity Model

| Level | Name | Activities |
|-------|------|-----------|
| 0 | None | No chaos testing |
| 1 | Exploratory | Manual fault injection in staging |
| 2 | Systematic | Scheduled chaos experiments in staging |
| 3 | Production | Controlled chaos in production (Game Days) |
| 4 | Continuous | Automated chaos in production with safety controls |

### Chaos Experiment Template

```yaml
experiment:
  name: ""
  hypothesis: "When [fault], the system will [expected behavior]"
  
  steady_state:
    metrics:
      - name: ""
        baseline: ""
        acceptable_range: ""
  
  method:
    fault_type: ""  # network | compute | storage | dependency | data
    target: ""      # which service/component
    blast_radius: ""  # single pod | single AZ | percentage of traffic
    duration: ""
    
  safety:
    abort_conditions:
      - "SLO burn rate exceeds 10x"
      - "Customer-visible errors detected"
      - "Alert fires that we didn't expect"
    rollback_plan: ""
    required_approvals: []
    
  results:
    outcome: ""  # confirmed | disproved | inconclusive
    observations: []
    action_items: []
```

### Chaos Experiment Library

| Category | Experiment | Validates |
|----------|-----------|-----------|
| **Network** | Add 200ms latency to DB calls | Timeout handling, circuit breakers |
| **Network** | Drop 5% of packets to downstream | Retry logic, error handling |
| **Network** | DNS resolution failure | Caching, fallback, error messages |
| **Compute** | Kill random pod every 10 min | Auto-restart, load balancing |
| **Compute** | CPU stress to 95% on 1 node | Auto-scaling, graceful degradation |
| **Compute** | Fill disk to 95% | Disk monitoring, log rotation, alerts |
| **Storage** | Increase DB latency 5x | Connection pool handling, timeouts |
| **Storage** | Simulate cache failure (Redis down) | Cache-aside pattern, DB fallback |
| **Dependency** | Block external API (payment provider) | Circuit breaker, queuing, retry |
| **Dependency** | Return 429s from auth service | Rate limit handling, backoff |
| **Data** | Clock skew on subset of nodes | Timestamp handling, ordering |
| **Scale** | 10x traffic spike over 5 minutes | Auto-scaling speed, queue depth |

### Game Day Runbook

```
PRE-GAME (1 week before):
□ Experiment designed and reviewed
□ Steady-state metrics identified
□ Abort conditions defined
□ All participants briefed
□ Runbacks tested in staging
□ Stakeholders notified

GAME DAY:
□ Verify steady state (15 min baseline)
□ Announce in #engineering: "Chaos Game Day starting"
□ Inject fault
□ Observe and document
□ If abort condition hit → rollback immediately
□ Run for planned duration
□ Remove fault
□ Verify recovery to steady state

POST-GAME (same day):
□ Results documented
□ Surprises noted
□ Action items created
□ Share findings in team meeting
```

---

## Phase 8: Toil Management

### Toil Identification

**Definition:** Work that is manual, repetitive, automatable, tactical, without enduring value, and scales linearly with service growth.

### Toil Inventory Template

```yaml
toil_item:
  name: ""
  category: ""  # deployment | scaling | config | data | access | monitoring | recovery
  frequency: ""  # daily | weekly | monthly | per-incident
  time_per_occurrence_min: 0
  occurrences_per_month: 0
  total_hours_per_month: 0
  teams_affected: []
  automation_difficulty: ""  # low | medium | high
  automation_value: 0  # hours saved per month
  priority_score: 0  # value / difficulty
```

### Toil Reduction Priority Matrix

| | Low Effort | Medium Effort | High Effort |
|-|-----------|--------------|-------------|
| **High Value** (>10 hrs/mo) | DO FIRST | DO SECOND | PLAN |
| **Med Value** (2-10 hrs/mo) | DO SECOND | PLAN | EVALUATE |
| **Low Value** (<2 hrs/mo) | QUICK WIN | SKIP | SKIP |

### Common Toil Targets (Ranked by Impact)

1. **Manual deployments** → CI/CD pipeline + GitOps
2. **Access provisioning** → Self-service + auto-approval for low-risk
3. **Certificate renewals** → Auto-renewal (cert-manager, Let's Encrypt)
4. **Scaling decisions** → HPA + predictive auto-scaling
5. **Log investigation** → Structured logging + correlation + dashboards
6. **Data fixes** → Self-service admin tools + validation at ingestion
7. **Config changes** → Config-as-code + automated rollout
8. **Incident response** → Automated runbooks for known issues
9. **Capacity reporting** → Automated dashboards + forecasting
10. **On-call triage** → Noise reduction + auto-remediation for known patterns

### Toil Budget Rule
**Target: <25% of SRE time spent on toil.** Track monthly. If above 25%, prioritize automation over all feature work.

---

## Phase 9: Capacity Planning

### Capacity Model Template

```yaml
capacity_model:
  service: ""
  bottleneck_resource: ""  # CPU | memory | storage | connections | bandwidth
  
  current_state:
    peak_utilization_pct: 0
    headroom_pct: 0
    cost_per_month_usd: 0
    
  growth_forecast:
    metric: ""  # MAU | requests/sec | storage_gb
    current: 0
    monthly_growth_pct: 0
    projected_6mo: 0
    projected_12mo: 0
    
  scaling_strategy:
    type: ""  # horizontal | vertical | hybrid
    auto_scaling: true
    min_instances: 0
    max_instances: 0
    scale_up_threshold: 80  # % utilization
    scale_down_threshold: 30
    cooldown_seconds: 300
    
  cost_projection:
    current_monthly: 0
    projected_6mo_monthly: 0
    projected_12mo_monthly: 0
```

### Capacity Planning Cadence

| Frequency | Action |
|-----------|--------|
| Daily | Review auto-scaling events, check for anomalies |
| Weekly | Review utilization trends, spot-check headroom |
| Monthly | Update growth model, review cost projections |
| Quarterly | Full capacity review, budget planning, architecture check |
| Pre-launch | Load test to 2x expected peak, verify scaling |

### Load Testing Benchmarks

| Scenario | Method | Duration | Target |
|----------|--------|----------|--------|
| Baseline | Steady load at current peak | 30 min | Establish metrics |
| Growth | 2x current peak | 15 min | Verify scaling works |
| Spike | 10x normal in 60 seconds | 5 min | Circuit breakers hold |
| Soak | 1.5x normal load | 4 hours | No memory leaks, degradation |
| Stress | Ramp until failure | Until break | Find actual limits |

---

## Phase 10: On-Call Excellence

### On-Call Health Metrics

| Metric | Healthy | Warning | Critical |
|--------|---------|---------|----------|
| Pages per shift | <2 | 2-5 | >5 |
| Off-hours pages | <1/week | 1-3/week | >3/week |
| Time to acknowledge | <5 min | 5-15 min | >15 min |
| Time to mitigate | <30 min | 30-60 min | >60 min |
| False positive rate | <10% | 10-30% | >30% |
| Escalation rate | <20% | 20-40% | >40% |
| On-call satisfaction | >4/5 | 3-4/5 | <3/5 |

### On-Call Rotation Best Practices

1. **Minimum rotation size: 5 people** (one week on, four weeks off)
2. **No back-to-back weeks** unless team is too small (fix the team size)
3. **Follow-the-sun** for global teams (no one pages at 3 AM if avoidable)
4. **Primary + secondary** on-call always
5. **Handoff document** at rotation change — open issues, recent deploys, known risks
6. **Compensation** — on-call pay, time off in lieu, or equivalent

### On-Call Handoff Template

```
## On-Call Handoff: [Date]

### Open Issues
- [Issue]: [Status, next steps]

### Recent Changes (last 7 days)
- [Deployment/config change]: [Risk level, rollback plan]

### Known Risks
- [Event/condition]: [What to watch for]

### Scheduled Maintenance
- [When]: [What, duration, rollback plan]

### Runbook Updates
- [Any new/updated runbooks since last rotation]
```

### Runbook Template

```yaml
runbook:
  title: ""
  alert_name: ""  # exact alert that triggers this
  last_updated: ""
  owner: ""
  
  overview: |
    What this alert means in plain English.
    
  impact: |
    What users/systems are affected and how.
    
  diagnosis:
    - step: "Check service health"
      command: ""
      expected: ""
      if_unexpected: ""
    - step: "Check recent deployments"
      command: ""
      expected: ""
      if_unexpected: "Rollback: [command]"
    - step: "Check dependencies"
      command: ""
      expected: ""
      if_unexpected: ""
      
  mitigation:
    - option: "Rollback"
      when: "Recent deployment suspected"
      steps: []
    - option: "Scale up"
      when: "Traffic spike"
      steps: []
    - option: "Failover"
      when: "Single component failure"
      steps: []
      
  escalation:
    after_minutes: 30
    contact: ""
    context_to_provide: ""
```

---

## Phase 11: Reliability Review & Governance

### Weekly SRE Review (30 min)

```
1. SLO Status (5 min)
   - Budget remaining per service
   - Any burn rate alerts this week?

2. Incident Review (10 min)
   - Incidents this week: count, severity, duration
   - Open postmortem action items: status check

3. On-Call Health (5 min)
   - Pages this week (total, off-hours, false positives)
   - Any on-call feedback?

4. Reliability Work (10 min)
   - Automation shipped this week
   - Toil reduced (hours saved)
   - Chaos experiments run
   - Capacity concerns
```

### Monthly Reliability Report

```yaml
monthly_report:
  period: ""
  
  slo_summary:
    services_meeting_slo: 0
    services_breaching_slo: 0
    worst_performing: ""
    
  incidents:
    total: 0
    by_severity: { SEV1: 0, SEV2: 0, SEV3: 0, SEV4: 0 }
    mttr_minutes: 0
    mttd_minutes: 0
    repeat_incidents: 0
    
  error_budget:
    services_in_healthy: 0
    services_in_warning: 0
    services_in_critical: 0
    services_exhausted: 0
    
  toil:
    hours_spent: 0
    hours_automated_away: 0
    pct_of_sre_time: 0
    
  on_call:
    total_pages: 0
    off_hours_pages: 0
    false_positive_pct: 0
    avg_ack_time_min: 0
    
  action_items:
    open: 0
    completed_this_month: 0
    overdue: 0
    
  highlights: []
  concerns: []
  next_month_priorities: []
```

### Production Readiness Review Checklist

Before any new service goes to production:

| Category | Check | Status |
|----------|-------|--------|
| **SLOs** | SLIs defined and measured | |
| **SLOs** | SLO targets set with stakeholder agreement | |
| **SLOs** | Error budget policy documented | |
| **Monitoring** | Golden signals dashboarded | |
| **Monitoring** | Alerting configured with runbooks | |
| **Monitoring** | Structured logging implemented | |
| **Monitoring** | Distributed tracing enabled | |
| **Incidents** | On-call rotation established | |
| **Incidents** | Escalation paths documented | |
| **Incidents** | Runbooks for top 5 failure modes | |
| **Capacity** | Load tested to 2x expected peak | |
| **Capacity** | Auto-scaling configured and tested | |
| **Capacity** | Resource limits set (CPU, memory) | |
| **Resilience** | Graceful degradation implemented | |
| **Resilience** | Circuit breakers for dependencies | |
| **Resilience** | Retry with exponential backoff | |
| **Resilience** | Timeout configured for all external calls | |
| **Deploy** | Rollback tested and documented | |
| **Deploy** | Canary/blue-green deployment ready | |
| **Deploy** | Feature flags for risky features | |
| **Security** | Authentication and authorization | |
| **Security** | Secrets in vault (not env vars) | |
| **Security** | Dependencies scanned | |
| **Data** | Backup and restore tested | |
| **Data** | Data retention policy defined | |
| **Docs** | Architecture diagram current | |
| **Docs** | API documentation published | |
| **Docs** | Operational runbook complete | |

---

## Phase 12: Advanced Patterns

### Self-Healing Automation

```yaml
auto_remediation:
  - trigger: "pod_crash_loop"
    condition: "restart_count > 3 in 10 min"
    action: "Delete pod, let scheduler reschedule"
    escalate_if: "Still crashing after 3 auto-remediations"
    
  - trigger: "disk_usage_high"
    condition: "disk_usage > 85%"
    action: "Run log cleanup script, archive old data"
    escalate_if: "Still above 85% after cleanup"
    
  - trigger: "connection_pool_exhausted"
    condition: "available_connections = 0"
    action: "Kill idle connections, increase pool temporarily"
    escalate_if: "Pool exhausted again within 1 hour"
    
  - trigger: "certificate_expiring"
    condition: "days_until_expiry < 14"
    action: "Trigger cert renewal"
    escalate_if: "Renewal fails"
```

### Multi-Region Reliability

| Strategy | Complexity | RTO | Cost |
|----------|-----------|-----|------|
| Active-passive | Low | Minutes | 1.5x |
| Active-active read | Medium | Seconds | 1.8x |
| Active-active full | High | Near-zero | 2-3x |
| Cell-based | Very high | Per-cell | 2-4x |

**Decision guide:**
- SLO < 99.9% → Single region with good backups
- SLO 99.9-99.95% → Active-passive with automated failover
- SLO > 99.95% → Active-active (read or full)
- SLO > 99.99% → Cell-based architecture

### Reliability Culture Indicators

**Healthy signals:**
- Postmortems are blameless and well-attended
- Error budgets are respected (feature freeze actually happens)
- On-call is shared fairly and compensated
- Toil is tracked and reducing quarter-over-quarter
- Chaos experiments happen regularly
- Teams own their reliability (not just SRE)

**Warning signs:**
- "Hero culture" — same person always saves the day
- Postmortems are blame-focused or skipped
- Error budget exhaustion doesn't change behavior
- On-call is dreaded, same 2 people always paged
- "We'll fix reliability after this feature ships" (always)
- SRE team is just an ops team with a new name

---

## Quality Scoring Rubric (0-100)

| Dimension | Weight | 0-2 | 3-4 | 5 |
|-----------|--------|-----|-----|---|
| SLO Coverage | 20% | No SLOs | SLOs for critical services | All services with SLOs, error budgets, reviews |
| Monitoring | 15% | Basic health checks | Golden signals + dashboards | Full observability stack + anomaly detection |
| Incident Response | 15% | Ad-hoc, no process | ICS roles, runbooks, postmortems | Structured ICS, blameless culture, action tracking |
| Automation | 15% | Manual everything | CI/CD + some automation | Self-healing, GitOps, <25% toil |
| Chaos Engineering | 10% | None | Staging experiments | Continuous production chaos with safety |
| Capacity Planning | 10% | Reactive | Quarterly forecasting | Predictive, auto-scaling, cost-optimized |
| On-Call Health | 10% | Burnout, hero culture | Fair rotation, <5 pages/shift | Balanced, compensated, <2 pages/shift |
| Documentation | 5% | Nothing written | Runbooks exist | Complete, current, tested runbooks |

---

## Natural Language Commands

- "Assess reliability for [service]" → Run maturity assessment
- "Define SLOs for [service]" → Walk through SLI selection + SLO setting
- "Check error budget for [service]" → Calculate current budget status
- "Start incident for [description]" → Create incident channel, assign IC, begin workflow
- "Write postmortem for [incident]" → Generate structured postmortem
- "Plan chaos experiment for [service]" → Design experiment with hypothesis
- "Audit toil for [team]" → Inventory and prioritize toil
- "Review on-call health" → Analyze page volume, satisfaction, fairness
- "Production readiness review for [service]" → Run full checklist
- "Monthly reliability report" → Generate comprehensive report
- "Design runbook for [alert]" → Create structured runbook
- "Plan capacity for [service] growing at [X%]" → Build capacity model
