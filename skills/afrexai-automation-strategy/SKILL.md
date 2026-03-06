---
name: Business Automation Strategy — AfrexAI
description: Before building anything, map where time and money leak.
---

# Business Automation Strategy — AfrexAI

> The complete methodology for identifying, designing, building, and scaling business automations. Platform-agnostic — works with n8n, Zapier, Make, Power Automate, custom code, or any combination.

## Phase 1: Automation Audit — Find the Gold

Before building anything, map where time and money leak.

### Quick ROI Triage

Ask these 5 questions about any process:
1. How often does it happen? (frequency)
2. How long does it take? (duration per occurrence)
3. How many people touch it? (handoffs)
4. How error-prone is it? (failure rate)
5. How much does failure cost? (impact)

### Process Inventory Template

```yaml
process_inventory:
  process_name: "[Name]"
  department: "[Sales/Marketing/Ops/Finance/HR/Engineering]"
  owner: "[Person responsible]"
  frequency: "[X per day/week/month]"
  duration_minutes: [time per occurrence]
  monthly_volume: [total occurrences]
  monthly_hours: [volume × duration ÷ 60]
  hourly_cost: [fully loaded employee cost]
  monthly_cost: "$[hours × hourly cost]"
  error_rate: "[X%]"
  error_cost_per_incident: "$[average]"
  handoffs: [number of people involved]
  current_tools: ["tool1", "tool2"]
  automation_potential: "[Full/Partial/Assist/None]"
  complexity: "[Simple/Medium/Complex/Enterprise]"
  dependencies: ["system1", "system2"]
  notes: "[Pain points, workarounds, tribal knowledge]"
```

### Automation Potential Classification

| Level | Description | Human Role | Example |
|-------|------------|------------|---------|
| **Full** | End-to-end automated, no human needed | Monitor exceptions | Invoice processing, data sync |
| **Partial** | Automated with human approval gates | Review & approve | Contract generation, hiring workflow |
| **Assist** | Human does work, automation helps | Execute with AI assistance | Customer support, content creation |
| **None** | Requires human judgment/creativity | Full ownership | Strategy, relationship building |

### ROI Calculation

```
Annual savings = (monthly_hours × 12 × hourly_cost) + (error_rate × volume × 12 × error_cost)
Build cost = development_hours × developer_rate + tool_costs
Payback period = build_cost ÷ (annual_savings ÷ 12) months
ROI = ((annual_savings - annual_tool_cost) ÷ build_cost) × 100%
```

**Decision rules:**
- Payback < 3 months → Build immediately
- Payback 3-6 months → Build this quarter
- Payback 6-12 months → Evaluate against alternatives
- Payback > 12 months → Reconsider (unless strategic)

---

## Phase 2: Prioritization — The Automation Stack Rank

### ICE-R Scoring (0-10 each)

| Dimension | Weight | Scoring Guide |
|-----------|--------|--------------|
| **Impact** | 30% | 10=saves >$50K/yr, 7=saves >$20K/yr, 5=saves >$5K/yr, 3=saves >$1K/yr |
| **Confidence** | 20% | 10=proven pattern, 7=similar done before, 5=feasible but new, 3=uncertain |
| **Ease** | 25% | 10=<1 day, 7=<1 week, 5=<1 month, 3=<3 months, 1=>3 months |
| **Reliability** | 25% | 10=deterministic, 7=95%+ success, 5=80%+ success, 3=needs frequent fixes |

```
Score = (Impact × 0.30) + (Confidence × 0.20) + (Ease × 0.25) + (Reliability × 0.25)
```

### Quick Win Identification

**Automate FIRST** (highest ROI, lowest risk):
1. Data entry / copy-paste between systems
2. Notification routing (email → Slack → SMS based on rules)
3. Report generation and distribution
4. File organization and naming
5. Status updates across tools
6. Meeting scheduling and follow-ups
7. Invoice creation from templates
8. Lead capture → CRM entry
9. Onboarding checklists
10. Backup and archival

**Automate LAST** (complex, high risk):
1. Anything involving money transfers without approval
2. Customer-facing responses without review
3. Legal/compliance decisions
4. Hiring/firing workflows
5. Security-sensitive operations

---

## Phase 3: Platform Selection — Choose Your Weapons

### Platform Decision Matrix

| Factor | No-Code (Zapier/Make) | Low-Code (n8n/Power Automate) | Custom Code | AI Agent |
|--------|----------------------|------------------------------|-------------|----------|
| **Best for** | Simple integrations | Complex workflows | Unique logic | Judgment calls |
| **Build speed** | Hours | Days | Weeks | Days-weeks |
| **Maintenance** | Low | Medium | High | Medium |
| **Flexibility** | Limited | High | Unlimited | High |
| **Cost at scale** | Expensive | Moderate | Cheap | Varies |
| **Error handling** | Basic | Good | Full control | Variable |
| **Team skill needed** | Business user | Technical BA | Developer | AI engineer |
| **Vendor lock-in** | High | Medium | None | Low-medium |

### Selection Decision Tree

```
Is the process deterministic (same input → same output)?
├── YES: Does it involve >3 systems?
│   ├── YES: Does it need complex branching logic?
│   │   ├── YES → Low-code (n8n/Power Automate)
│   │   └── NO → No-code (Zapier/Make) if budget allows, else n8n
│   └── NO: Is it performance-critical?
│       ├── YES → Custom code
│       └── NO → No-code (simplest wins)
└── NO: Does it need judgment/reasoning?
    ├── YES: Is the judgment pattern learnable?
    │   ├── YES → AI agent with human review
    │   └── NO → Human-assisted automation
    └── NO → Partial automation with human gates
```

### Cost Comparison by Scale

| Monthly Tasks | Zapier | Make | n8n (self-hosted) | Custom Code |
|--------------|--------|------|-------------------|-------------|
| 1,000 | $30 | $10 | $5 (hosting) | $50+ (hosting) |
| 10,000 | $100 | $30 | $5 | $50+ |
| 100,000 | $500+ | $150 | $10 | $50+ |
| 1,000,000 | $2,000+ | $500+ | $20 | $100+ |

**Rule:** If you're spending >$200/mo on Zapier/Make, evaluate self-hosted n8n.

---

## Phase 4: Workflow Architecture — Design Before You Build

### Workflow Blueprint Template

```yaml
workflow_blueprint:
  name: "[Descriptive name]"
  id: "WF-[DEPT]-[NUMBER]"
  version: "1.0.0"
  owner: "[Person]"
  priority: "[P0-P3]"
  
  trigger:
    type: "[webhook/schedule/event/manual/condition]"
    source: "[System or schedule]"
    conditions: "[When to fire]"
    dedup_strategy: "[How to prevent double-processing]"
  
  inputs:
    - name: "[field]"
      type: "[string/number/date/object]"
      required: true
      validation: "[rules]"
      source: "[where it comes from]"
  
  steps:
    - id: "step_1"
      action: "[verb: fetch/transform/validate/send/create/update/delete]"
      system: "[target system]"
      description: "[what this step does]"
      input: "[from trigger or previous step]"
      output: "[what it produces]"
      error_handling: "[retry/skip/alert/abort]"
      timeout_seconds: 30
    
    - id: "step_2_branch"
      type: "condition"
      condition: "[expression]"
      true_path: "step_3a"
      false_path: "step_3b"
  
  error_handling:
    retry_policy:
      max_attempts: 3
      backoff: "exponential"
      initial_delay_seconds: 5
    on_failure: "[alert/queue-for-review/fallback]"
    alert_channel: "[Slack/email/SMS]"
    dead_letter_queue: true
  
  monitoring:
    success_metric: "[what defines success]"
    expected_duration_seconds: [max]
    alert_on_duration_exceeded: true
    log_level: "[info/debug/error]"
  
  testing:
    test_data: "[how to generate test inputs]"
    expected_output: "[what success looks like]"
    edge_cases: ["empty input", "duplicate", "malformed data"]
```

### 7 Workflow Design Principles

1. **Idempotent by default** — Running the same workflow twice with the same input should produce the same result, not duplicates
2. **Fail loudly** — Silent failures are worse than crashes. Every error must notify someone
3. **Checkpoint progress** — Long workflows should save state so they can resume, not restart
4. **Validate early** — Check inputs at the start, not after 10 expensive API calls
5. **Separate concerns** — One workflow, one job. Chain workflows, don't build monoliths
6. **Log everything** — Timestamps, inputs, outputs, decisions. You WILL need to debug
7. **Human escape hatch** — Every automated workflow needs a manual override path

### Common Workflow Patterns

| Pattern | When to Use | Example |
|---------|------------|---------|
| **Sequential** | Steps depend on each other | Lead → Enrich → Score → Route |
| **Parallel fan-out** | Independent steps | Send email + Update CRM + Log analytics |
| **Conditional branch** | Different paths by data | High value → Sales, Low value → Nurture |
| **Loop/batch** | Process collections | For each row in CSV, create record |
| **Approval gate** | Human judgment needed | Contract review before sending |
| **Event-driven chain** | Workflow triggers workflow | Order placed → Fulfillment → Shipping → Notification |
| **Retry with fallback** | Unreliable external APIs | Try API → Retry 3x → Use cached data → Alert |
| **Scheduled sweep** | Periodic cleanup/sync | Nightly: sync CRM → accounting |

---

## Phase 5: Integration Architecture — Connect Everything

### Integration Quality Checklist

For every system integration:
- [ ] API documentation reviewed
- [ ] Authentication method confirmed (OAuth2/API key/JWT)
- [ ] Rate limits documented (requests/min, requests/day)
- [ ] Webhook support checked (push vs poll)
- [ ] Error response format understood
- [ ] Pagination handling planned
- [ ] Data format confirmed (JSON/XML/CSV)
- [ ] Field mapping documented
- [ ] Test environment available
- [ ] Sandbox/production separation configured

### Data Mapping Template

```yaml
data_mapping:
  source_system: "[System A]"
  target_system: "[System B]"
  sync_direction: "[one-way/bidirectional]"
  sync_frequency: "[real-time/5min/hourly/daily]"
  conflict_resolution: "[source wins/target wins/newest wins/manual]"
  
  field_mappings:
    - source_field: "contact.email"
      target_field: "customer.email_address"
      transform: "lowercase"
      required: true
    - source_field: "contact.company"
      target_field: "customer.organization"
      transform: "trim"
      default: "Unknown"
    - source_field: "contact.created_at"
      target_field: "customer.signup_date"
      transform: "ISO8601 → YYYY-MM-DD"
```

### Rate Limit Strategy

| Approach | When | Implementation |
|----------|------|---------------|
| **Queue + throttle** | Predictable volume | Process queue at 80% of rate limit |
| **Exponential backoff** | Burst traffic | Wait 1s, 2s, 4s, 8s on 429 errors |
| **Batch API calls** | High volume CRUD | Group 50-100 records per call |
| **Cache responses** | Repeated lookups | Cache for TTL matching data freshness needs |
| **Off-peak scheduling** | Non-urgent syncs | Run heavy syncs at 2-4 AM |

---

## Phase 6: Error Handling & Reliability — Build It Unbreakable

### Error Classification

| Type | Example | Response | Priority |
|------|---------|----------|----------|
| **Transient** | API timeout, 503 | Retry with backoff | Auto-handle |
| **Rate limit** | 429 Too Many Requests | Queue + throttle | Auto-handle |
| **Data validation** | Missing required field | Log + skip + alert | Review daily |
| **Auth failure** | Token expired | Refresh + retry, else alert | P1 — fix within 1h |
| **Logic error** | Unexpected state | Halt + alert + queue | P0 — fix immediately |
| **External change** | API schema changed | Halt + alert | P0 — fix immediately |
| **Capacity** | Queue overflow | Scale + alert | P1 — fix within 4h |

### Dead Letter Queue Pattern

Every workflow should have a DLQ:
1. **Capture** — Failed items go to DLQ with full context (input, error, timestamp, step)
2. **Alert** — Notify on DLQ growth (>10 items or >1% failure rate)
3. **Review** — Daily check of DLQ items
4. **Replay** — Ability to reprocess DLQ items after fix
5. **Expire** — Auto-archive items older than 30 days with summary

### Circuit Breaker Pattern

```
States: CLOSED (normal) → OPEN (failing) → HALF-OPEN (testing)

CLOSED: Process normally, track failures
  → If failure_count > threshold in window → OPEN

OPEN: Reject all requests, return cached/default
  → After cool_down_period → HALF-OPEN

HALF-OPEN: Allow 1 test request
  → If success → CLOSED
  → If failure → OPEN (reset cool_down)
```

**Thresholds:**
- Simple integrations: 5 failures in 60 seconds
- Critical paths: 3 failures in 30 seconds
- Non-critical: 10 failures in 300 seconds

---

## Phase 7: Testing & Validation — Trust But Verify

### Automation Test Pyramid

| Level | What | How | When |
|-------|------|-----|------|
| **Unit** | Individual step logic | Mock inputs, verify output | Every change |
| **Integration** | System connections | Test with sandbox APIs | Weekly + after changes |
| **End-to-end** | Full workflow path | Run with test data | Before deploy + weekly |
| **Chaos** | Failure scenarios | Kill steps, corrupt data | Monthly |
| **Load** | Volume handling | 10x normal volume | Before scaling |

### Test Scenario Checklist

For every workflow, test:
- [ ] Happy path (normal input, expected output)
- [ ] Empty/null input (missing required fields)
- [ ] Duplicate input (same event twice)
- [ ] Malformed input (wrong types, encoding issues)
- [ ] Boundary values (max length, zero, negative)
- [ ] API down (target system unavailable)
- [ ] Slow response (timeout handling)
- [ ] Partial failure (step 3 of 5 fails)
- [ ] Concurrent execution (two runs at same time)
- [ ] Clock skew / timezone issues
- [ ] Large payload (oversized data)
- [ ] Permission denied (auth issues)

### Validation Before Go-Live

```yaml
go_live_checklist:
  functionality:
    - [ ] All test scenarios pass
    - [ ] Edge cases documented and handled
    - [ ] Error messages are actionable
  
  reliability:
    - [ ] Retry logic tested
    - [ ] Circuit breaker configured
    - [ ] Dead letter queue active
    - [ ] Idempotency verified (run twice, same result)
  
  monitoring:
    - [ ] Success/failure alerts configured
    - [ ] Duration alerts set
    - [ ] Log retention configured
    - [ ] Dashboard created
  
  documentation:
    - [ ] Workflow blueprint updated
    - [ ] Runbook written
    - [ ] Team trained on manual override
  
  rollback:
    - [ ] Previous version preserved
    - [ ] Rollback procedure tested
    - [ ] Data cleanup plan for partial runs
```

---

## Phase 8: Monitoring & Observability — See Everything

### Automation Health Dashboard

```yaml
automation_dashboard:
  period: "weekly"
  
  summary:
    total_workflows: [count]
    total_executions: [count]
    success_rate: "[X%]"
    avg_duration: "[X seconds]"
    errors_this_period: [count]
    time_saved_hours: [calculated]
    cost_saved: "$[calculated]"
  
  by_workflow:
    - name: "[Workflow name]"
      executions: [count]
      success_rate: "[X%]"
      avg_duration: "[X seconds]"
      p95_duration: "[X seconds]"
      errors: [count]
      error_types: ["type1: count", "type2: count"]
      dlq_items: [count]
      status: "[healthy/degraded/failing]"
  
  alerts_fired: [count]
  manual_interventions: [count]
  
  top_issues:
    - "[Issue 1: description + fix status]"
    - "[Issue 2: description + fix status]"
  
  cost:
    platform_cost: "$[monthly]"
    api_calls_cost: "$[monthly]"
    compute_cost: "$[monthly]"
    total: "$[monthly]"
    cost_per_execution: "$[calculated]"
```

### Alert Rules

| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| Success rate | <95% | <90% | Investigate + fix |
| Duration | >2x average | >5x average | Check for bottleneck |
| DLQ size | >10 items | >50 items | Review + reprocess |
| Error spike | 5 errors/hour | 20 errors/hour | Pause + investigate |
| Queue depth | >100 pending | >1000 pending | Scale + investigate |
| Cost spike | >150% of average | >300% of average | Audit + optimize |

### Weekly Review Questions

1. Which workflows had the lowest success rate? Why?
2. Are any workflows consistently slow? What's the bottleneck?
3. How many manual interventions were needed? Can we eliminate them?
4. What's in the DLQ? Patterns?
5. Are we approaching any rate limits?
6. Total cost vs total time saved — still positive ROI?

---

## Phase 9: Scaling & Optimization — Go From 10 to 10,000

### Scaling Checklist

Before scaling any automation:
- [ ] Load tested at 10x current volume
- [ ] Rate limits mapped for all APIs
- [ ] Queue-based architecture (not synchronous chains)
- [ ] Database indexes optimized
- [ ] Caching layer in place
- [ ] Monitoring alerts adjusted for new thresholds
- [ ] Cost projections at scale calculated
- [ ] Fallback/degradation plan documented

### Performance Optimization Priority

1. **Eliminate unnecessary API calls** — Cache lookups, batch operations
2. **Parallelize independent steps** — Don't wait when you don't have to
3. **Optimize data payloads** — Only fetch/send fields you need
4. **Use webhooks over polling** — Real-time + fewer API calls
5. **Batch processing** — Group operations (50-100 per batch)
6. **Async where possible** — Don't block on non-critical steps
7. **CDN/cache for static lookups** — Country codes, categories, templates
8. **Database query optimization** — Indexes, query plans, connection pooling

### When to Migrate Platforms

| Signal | From | To |
|--------|------|----|
| Spending >$500/mo on Zapier/Make | No-code | Self-hosted n8n |
| Need custom logic in >50% of workflows | No-code | Low-code or code |
| >100K executions/day | Any hosted | Self-hosted or custom |
| Complex branching breaking visual tools | Low-code | Custom code |
| Multiple teams building automations | Single tool | Platform + governance |
| AI judgment needed in workflows | Traditional | AI agent integration |

---

## Phase 10: Governance & Documentation — Keep It Manageable

### Automation Registry

Every automation must be registered:

```yaml
automation_registry_entry:
  id: "WF-[DEPT]-[NUMBER]"
  name: "[Descriptive name]"
  description: "[What it does in one sentence]"
  owner: "[Person]"
  team: "[Department]"
  platform: "[n8n/Zapier/Make/custom]"
  status: "[active/paused/deprecated/testing]"
  created: "[date]"
  last_modified: "[date]"
  last_reviewed: "[date]"
  review_frequency: "[monthly/quarterly]"
  
  business_impact:
    time_saved_monthly_hours: [X]
    cost_saved_monthly: "$[X]"
    error_reduction: "[X%]"
    
  technical:
    trigger: "[type]"
    systems_connected: ["system1", "system2"]
    avg_daily_executions: [X]
    success_rate: "[X%]"
    
  dependencies:
    upstream: ["WF-XXX"]
    downstream: ["WF-YYY"]
    
  documentation:
    blueprint: "[link]"
    runbook: "[link]"
    test_plan: "[link]"
```

### Naming Conventions

```
Pattern: [DEPT]-[ACTION]-[OBJECT]-[QUALIFIER]
Examples:
  SALES-sync-leads-from-typeform
  FINANCE-generate-invoice-monthly
  HR-onboard-employee-new-hire
  MARKETING-post-content-social-scheduled
  OPS-backup-database-nightly
```

### Change Management for Automations

| Change Type | Approval | Testing | Rollback Plan |
|-------------|----------|---------|---------------|
| **Config change** (threshold, timing) | Owner | Quick smoke test | Revert config |
| **Logic change** (new branch, new step) | Owner + reviewer | Full test suite | Previous version |
| **Integration change** (new API, new system) | Owner + tech lead | Integration + E2E | Disconnect + manual |
| **New workflow** | Owner + stakeholder | Full test + pilot | Disable workflow |
| **Deprecation** | Owner + affected teams | Verify replacements | Re-enable |

### Quarterly Automation Review

1. **Inventory check** — Are all automations in the registry? Any rogue workflows?
2. **ROI validation** — Is each automation still delivering value?
3. **Health review** — Success rates, error trends, DLQ patterns
4. **Cost audit** — Platform costs trending up? Optimization opportunities?
5. **Security review** — API keys rotated? Permissions still appropriate?
6. **Deprecation candidates** — Any automations that should be retired?
7. **Opportunity scan** — New processes to automate? Existing ones to improve?

---

## Phase 11: AI-Powered Automations — The Next Level

### When to Add AI to Automations

| Scenario | AI Type | Example |
|----------|---------|---------|
| Classify unstructured text | LLM | Categorize support tickets |
| Extract data from documents | LLM + OCR | Parse invoices, contracts |
| Generate content from templates | LLM | Personalized emails, reports |
| Make judgment calls | LLM + rules | Lead scoring, risk assessment |
| Summarize information | LLM | Meeting notes, research briefs |
| Route based on intent | LLM | Customer request → right team |

### AI Integration Best Practices

1. **Always validate AI output** — LLMs hallucinate. Add validation checks
2. **Set confidence thresholds** — Below threshold → human review queue
3. **Log AI decisions** — Input, output, confidence, model version
4. **A/B test AI vs rules** — Prove AI adds value before committing
5. **Cost-control AI calls** — Cache similar inputs, batch where possible
6. **Fallback to rules** — If AI is unavailable, have deterministic backup
7. **Review AI decisions weekly** — Spot check for quality drift

### AI Agent Integration Pattern

```yaml
ai_agent_step:
  type: "ai_judgment"
  model: "[model name]"
  
  input:
    context: "[relevant data from previous steps]"
    task: "[specific instruction — be precise]"
    output_format: "[JSON schema or structured format]"
    constraints: ["must not", "must always", "if unsure"]
  
  validation:
    confidence_threshold: 0.85
    required_fields: ["field1", "field2"]
    value_ranges:
      score: [0, 100]
      category: ["A", "B", "C"]
    
  on_low_confidence:
    action: "route_to_human"
    queue: "[review queue name]"
    
  on_failure:
    action: "fallback_to_rules"
    rules_engine: "[rule set name]"
    
  monitoring:
    log_all_decisions: true
    sample_rate_for_review: 0.10
    alert_on_confidence_drop: true
```

---

## Phase 12: Automation Maturity Model

### 5 Levels of Automation Maturity

| Level | Name | Description | Indicators |
|-------|------|------------|------------|
| **1** | Ad Hoc | Manual processes, maybe a few scripts | No registry, tribal knowledge |
| **2** | Reactive | Automate pain points as they arise | Some workflows, no standards |
| **3** | Systematic | Planned automation program | Registry, testing, monitoring |
| **4** | Optimized | Continuous improvement, governance | ROI tracking, quarterly reviews |
| **5** | Intelligent | AI-augmented, self-healing | Adaptive workflows, predictive |

### Maturity Assessment (Score 1-5 per dimension)

```yaml
automation_maturity:
  dimensions:
    strategy: [1-5]  # Planned roadmap vs ad hoc
    architecture: [1-5]  # Patterns, standards, reuse
    reliability: [1-5]  # Error handling, monitoring, uptime
    governance: [1-5]  # Registry, change management, reviews
    testing: [1-5]  # Test coverage, validation, chaos
    documentation: [1-5]  # Blueprints, runbooks, training
    optimization: [1-5]  # Performance, cost, continuous improvement
    ai_integration: [1-5]  # AI-powered decisions, self-healing
  
  total: [sum ÷ 8]
  grade: "[A/B/C/D/F]"
  # A: 4.5+ | B: 3.5-4.4 | C: 2.5-3.4 | D: 1.5-2.4 | F: <1.5
  
  top_gap: "[lowest scoring dimension]"
  next_action: "[specific improvement for top gap]"
```

---

## 100-Point Quality Rubric

| Dimension | Weight | 0-2 (Poor) | 3-5 (Basic) | 6-8 (Good) | 9-10 (Excellent) |
|-----------|--------|------------|-------------|------------|-------------------|
| **Design** | 15% | No blueprint, ad hoc | Basic flow documented | Full blueprint with error handling | Blueprint + edge cases + optimization |
| **Reliability** | 20% | No error handling | Basic retries | DLQ + circuit breaker + fallback | Self-healing + auto-scaling |
| **Testing** | 15% | No tests | Happy path only | Full test pyramid | Chaos testing + load testing |
| **Monitoring** | 15% | No visibility | Basic success/fail logs | Dashboard + alerts | Predictive monitoring |
| **Documentation** | 10% | None | README exists | Blueprint + runbook | Full docs + training materials |
| **Security** | 10% | Hardcoded credentials | Encrypted secrets | Least privilege + rotation | Zero-trust + audit trail |
| **Performance** | 10% | Works but slow | Acceptable speed | Optimized + cached | Auto-scaling + sub-second |
| **Governance** | 5% | No registry | Listed somewhere | Full registry + reviews | Change management + compliance |

**Score: (weighted sum) → Grade: A (90+) B (80-89) C (70-79) D (60-69) F (<60)**

---

## 10 Automation Killers

| # | Mistake | Fix |
|---|---------|-----|
| 1 | Automating a broken process | Fix the process FIRST, then automate |
| 2 | No error handling | Every step needs a failure path |
| 3 | Silent failures | If it fails and nobody knows, it's worse than manual |
| 4 | Not testing edge cases | Test empty, duplicate, malformed, concurrent |
| 5 | Hardcoded values | Use config/environment variables for everything |
| 6 | No monitoring | You can't fix what you can't see |
| 7 | Building monolith workflows | One workflow, one job. Chain them together |
| 8 | Ignoring rate limits | Design for API limits from day one |
| 9 | No documentation | Future-you will hate present-you |
| 10 | Over-automating | Not everything should be automated. Human judgment exists for a reason |

---

## Edge Cases

### Small Team / Solo Founder
- Start with Zapier/Make — speed over flexibility
- Automate the 3 most time-consuming tasks first
- Graduate to n8n when spending >$100/mo on no-code

### Regulated Industry
- Add approval gates at every decision point
- Log all automated actions for audit trail
- Review automations quarterly with compliance team
- Document data flow for privacy impact assessments

### Legacy Systems
- Use middleware/iPaaS for legacy integration
- Build adapters that normalize legacy data formats
- Plan for eventual migration, not permanent workarounds

### Multi-Team / Enterprise
- Establish automation Center of Excellence (CoE)
- Standardize on 1-2 platforms max
- Shared component library for common patterns
- Governance board for cross-team automations

### AI-Heavy Workflows
- Always keep human-in-the-loop for high-stakes decisions
- Monitor AI output quality continuously
- Budget for AI API costs separately (they scale differently)
- Version-pin AI models — don't auto-upgrade in production

---

## Natural Language Commands

Use these to invoke specific phases:

1. `audit my processes for automation opportunities` → Phase 1
2. `prioritize automations by ROI` → Phase 2
3. `recommend automation platform for [process]` → Phase 3
4. `design workflow blueprint for [process]` → Phase 4
5. `plan integration between [system A] and [system B]` → Phase 5
6. `design error handling for [workflow]` → Phase 6
7. `create test plan for [automation]` → Phase 7
8. `set up monitoring for [workflow]` → Phase 8
9. `optimize [workflow] for scale` → Phase 9
10. `review automation governance` → Phase 10
11. `add AI to [workflow]` → Phase 11
12. `assess automation maturity` → Phase 12
