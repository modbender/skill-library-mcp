# Legacy System Modernization Engine

Complete methodology for assessing, planning, and executing legacy system modernization — from monolith decomposition to cloud migration. Works for any tech stack, any scale.

---

## Phase 1: System Assessment

### Modernization Brief

```yaml
system_name: "[Name]"
age_years: 0
primary_language: ""
framework: ""
database: ""
deployment: "on-prem | VM | container | serverless"
lines_of_code: 0
team_size: 0
monthly_users: 0
annual_revenue_supported: "$0"
compliance_requirements: []
known_pain_points: []
business_driver: "cost | speed | talent | risk | compliance | scale"
timeline_pressure: "low | medium | high | critical"
budget_range: "$0-$0"
sponsor: ""
```

### Technical Debt Inventory

Score each dimension 1-5 (1=critical, 5=healthy):

| Dimension | Score | Evidence |
|-----------|-------|----------|
| **Code quality** — test coverage, complexity, duplication | | |
| **Architecture** — coupling, modularity, clear boundaries | | |
| **Infrastructure** — deployment automation, monitoring, scaling | | |
| **Dependencies** — outdated libraries, EOL frameworks, security vulns | | |
| **Data** — schema quality, migration history, backup/recovery | | |
| **Documentation** — accuracy, coverage, onboarding effectiveness | | |
| **Operations** — deployment frequency, MTTR, incident rate | | |
| **Security** — auth patterns, encryption, audit trail, compliance gaps | | |
| **Developer experience** — build time, local setup, debugging tools | | |
| **Business logic clarity** — documented rules, test coverage of logic | | |

**Total: /50**

- **40-50**: Healthy — incremental improvement
- **30-39**: Aging — targeted modernization
- **20-29**: Legacy — systematic modernization needed
- **10-19**: Critical — modernize or replace

### Dependency Risk Matrix

For each major dependency:

```yaml
dependency: ""
current_version: ""
latest_version: ""
eol_date: ""  # End of life
security_vulns: 0  # Known CVEs
upgrade_difficulty: "trivial | moderate | hard | rewrite"
business_risk: "low | medium | high | critical"
alternatives: []
```

**Priority rules:**
- EOL within 12 months → P0
- Known unpatched CVEs → P0
- 3+ major versions behind → P1
- No active maintainer → P1
- Everything else → P2

---

## Phase 2: Strategy Selection

### Modernization Strategy Decision Matrix

| Strategy | When to Use | Risk | Cost | Speed | Disruption |
|----------|-------------|------|------|-------|------------|
| **Rehost** (lift & shift) | Datacenter exit, minimal change | Low | Low | Fast | Low |
| **Replatform** (lift & optimize) | Cloud benefits without rewrite | Low-Med | Medium | Medium | Low-Med |
| **Refactor** (restructure) | Good code, bad architecture | Medium | Medium | Medium | Medium |
| **Re-architect** (rebuild patterns) | Monolith→services, new patterns | High | High | Slow | High |
| **Rebuild** (rewrite) | Small system, clear requirements | Very High | Very High | Very Slow | Very High |
| **Replace** (buy/SaaS) | Commodity functionality | Medium | Variable | Fast | High |
| **Retire** | No longer needed | None | Negative | Instant | Low |
| **Retain** (do nothing) | Working fine, other priorities | None | Ongoing | N/A | None |

### Strategy Selection Decision Tree

```
Is the system still needed?
├─ No → RETIRE
├─ Yes → Is it a commodity (CRM, email, etc.)?
│  ├─ Yes → REPLACE (buy SaaS)
│  └─ No → Is the code maintainable?
│     ├─ Yes → Is the architecture the problem?
│     │  ├─ Yes → RE-ARCHITECT (strangler fig)
│     │  └─ No → Is the infrastructure the problem?
│     │     ├─ Yes → REPLATFORM
│     │     └─ No → REFACTOR incrementally
│     └─ No → Is the system small (<50K LOC)?
│        ├─ Yes → Can requirements be clearly defined?
│        │  ├─ Yes → REBUILD
│        │  └─ No → REFACTOR + RE-ARCHITECT
│        └─ No → STRANGLER FIG (never big-bang rewrite)
```

### The Big Rewrite Anti-Pattern

**NEVER do a full rewrite of a large system.** It fails 70%+ of the time because:
1. The old system keeps getting features — moving target
2. Hidden business rules only exist in code — they get lost
3. Timeline always 2-3x longer than estimated
4. Two systems to maintain during transition
5. Team burns out before completion

**Always use Strangler Fig instead.** Replace piece by piece.

---

## Phase 3: Strangler Fig Pattern

### How It Works

1. **Identify a boundary** — a feature, page, or API endpoint
2. **Build the replacement** — new stack, new patterns
3. **Route traffic** — proxy/facade sends requests to new or old
4. **Verify parity** — same behavior, same data
5. **Cut over** — remove the proxy, retire the old code
6. **Repeat** — next boundary

### Strangler Facade YAML

```yaml
facade_name: "[API Gateway / Reverse Proxy / BFF]"
routing_rules:
  - path: "/api/users/*"
    target: "new-service"
    status: "migrated"
    migrated_date: "2025-01-15"
  - path: "/api/orders/*"
    target: "legacy"
    status: "planned"
    target_date: "2025-Q2"
  - path: "/api/reports/*"
    target: "legacy"
    status: "not-planned"
    notes: "Low priority, rarely used"
```

### Migration Sequence Rules

1. **Start with the easiest, most isolated module** — build confidence
2. **Then the highest-value business capability** — prove ROI early
3. **Leave the hardest, most coupled parts for last** — team learns patterns first
4. **Never migrate auth/identity early** — it touches everything
5. **Migrate data access layer before business logic** — clean data = clean migration
6. **Always keep the old system as fallback** until new is proven

### Dual-Write / Data Sync Patterns

| Pattern | When | Complexity | Risk |
|---------|------|-----------|------|
| **Dual write** | Both systems write simultaneously | High | Data inconsistency |
| **CDC (Change Data Capture)** | Stream changes from old→new DB | Medium | Lag, ordering |
| **ETL batch sync** | Periodic bulk sync | Low | Stale data |
| **Event sourcing bridge** | Events from old, replay in new | High | Schema mapping |
| **Read from new, write to old** | Transition period | Medium | Routing complexity |

**Golden rule:** Pick ONE source of truth. Never let both systems own the same data simultaneously.

---

## Phase 4: Monolith Decomposition

### Domain Discovery

Before splitting a monolith, identify bounded contexts:

1. **Event Storming** (preferred) — sticky notes for domain events, commands, aggregates
2. **Code analysis** — find clusters of related classes/tables
3. **Team analysis** — which teams own which features?
4. **Data coupling analysis** — which tables are joined together?

### Bounded Context YAML

```yaml
context_name: ""
description: ""
team: ""
entities: []
commands: []
events_published: []
events_consumed: []
database_tables: []
external_integrations: []
coupling_score: 0  # 0=independent, 10=deeply coupled
extraction_difficulty: "easy | moderate | hard | very-hard"
business_value: "low | medium | high | critical"
```

### Extraction Priority Matrix

Plot contexts on: **Business Value** (Y) × **Extraction Difficulty** (X)

| | Easy | Moderate | Hard |
|---|---|---|---|
| **High value** | 🟢 Do first | 🟡 Do second | 🟠 Plan carefully |
| **Medium value** | 🟢 Quick win | 🟡 Evaluate ROI | 🔴 Probably not worth it |
| **Low value** | 🟡 If easy, why not | 🔴 Skip | 🔴 Definitely skip |

### Service Extraction Checklist

For each service being extracted:

- [ ] Bounded context clearly defined
- [ ] API contract designed (OpenAPI spec)
- [ ] Database separated (no shared tables)
- [ ] Authentication/authorization integrated
- [ ] Event publishing for cross-service communication
- [ ] Circuit breaker for calls back to monolith
- [ ] Monitoring and alerting configured
- [ ] Deployment pipeline independent
- [ ] Feature flag for traffic routing
- [ ] Rollback plan documented
- [ ] Performance baseline captured (before/after)
- [ ] Data migration script tested
- [ ] Integration tests with monolith passing
- [ ] Runbook for on-call written

---

## Phase 5: Database Modernization

### Database Migration Strategies

| Strategy | Description | Downtime | Risk |
|----------|-------------|----------|------|
| **Parallel run** | New DB alongside old, sync both | Zero | High complexity |
| **Blue-green** | Full copy, switch DNS | Minutes | Medium |
| **Rolling** | Migrate table by table | Zero per table | Medium |
| **Big bang** | Stop, migrate, start | Hours | High |

### Schema Evolution Rules

1. **Always additive** — add columns/tables, never remove in the same release
2. **Two-phase removal** — Release 1: stop writing. Release 2: drop column (after backfill verified)
3. **Default values always** — every new column gets a default
4. **Backward compatible** — old code must work with new schema during rollout
5. **Index concurrently** — never lock production tables
6. **Test with production-scale data** — 100 rows ≠ 100M rows

### Data Quality Gates

Before migrating data:

```yaml
table: ""
row_count_source: 0
row_count_target: 0
count_match: false
checksum_match: false
null_analysis: "pass | fail"
referential_integrity: "pass | fail"
business_rule_validation: "pass | fail"
sample_manual_review: "pass | fail"
performance_benchmark: "pass | fail"
rollback_tested: false
```

**Rule: All gates must pass before cutover.** No exceptions.

---

## Phase 6: Cloud Migration

### Cloud Readiness Assessment

Score each workload:

| Factor | Score (1-5) | Notes |
|--------|-------------|-------|
| Stateless design | | |
| Configuration externalized | | |
| Logging to stdout | | |
| Health check endpoint | | |
| Graceful shutdown | | |
| Horizontal scalability | | |
| Secret management | | |
| 12-factor compliance | | |

**35-40**: Cloud-native ready
**25-34**: Minor modifications needed
**15-24**: Significant refactoring
**8-14**: Major redesign required

### Cloud Migration Checklist

- [ ] Network architecture designed (VPC, subnets, security groups)
- [ ] Identity and access management configured
- [ ] Data residency requirements verified
- [ ] Compliance mapping (cloud controls ↔ requirements)
- [ ] Cost estimation completed (TCO comparison)
- [ ] Disaster recovery plan updated
- [ ] Monitoring and alerting migrated
- [ ] DNS and certificate management planned
- [ ] CDN configuration
- [ ] Load testing in cloud environment
- [ ] Security scanning pipeline
- [ ] Backup and restore verified
- [ ] Runbooks updated for cloud operations
- [ ] Team trained on cloud platform
- [ ] Vendor lock-in assessment

### Cost Optimization from Day 1

- **Right-size instances** — start small, scale up with data
- **Reserved/committed use** — only after 3 months of usage data
- **Spot/preemptible** — for batch jobs, CI/CD, dev/test
- **Auto-scaling** — scale down at night, weekends
- **Storage tiers** — hot/warm/cold/archive based on access patterns
- **Tag everything** — cost allocation by team, service, environment
- **Monthly review** — unused resources, oversized instances

---

## Phase 7: API Modernization

### API Wrapping Pattern

For legacy systems without APIs:

1. **Screen scraping adapter** — parse HTML/mainframe screens
2. **Database tap** — read directly from legacy DB (read-only!)
3. **File-based integration** — watch folders, parse files
4. **Message queue bridge** — legacy writes to queue, new reads
5. **RPC wrapper** — expose existing functions via REST/gRPC

### API Contract-First Migration

```yaml
endpoint: "/api/v2/orders"
legacy_source: "stored_procedure: sp_GetOrders"
new_implementation: "orders-service"
migration_status: "legacy | dual-run | new-only"
contract_changes:
  - field: "order_date"
    old_format: "MM/DD/YYYY string"
    new_format: "ISO 8601"
    adapter: "date_format_adapter"
  - field: "status"
    old_values: ["A", "C", "P"]
    new_values: ["active", "completed", "pending"]
    adapter: "status_code_mapper"
parity_tests: 47
parity_passing: 47
```

---

## Phase 8: Testing Strategy

### Migration Testing Pyramid

```
         /  Smoke Tests  \           ← Whole system alive?
        / Parity Tests    \          ← Same behavior old vs new?
       / Integration Tests \         ← Services work together?
      / Contract Tests      \        ← API contracts honored?
     / Performance Tests     \       ← Not slower than before?
    / Data Validation Tests   \      ← Data migrated correctly?
   /  Unit Tests               \     ← New code works?
```

### Parity Testing Framework

For EVERY migrated feature:

```yaml
feature: ""
test_type: "api_parity | ui_parity | data_parity"
method: "shadow traffic | replay | parallel run"
sample_size: 0
match_rate: "0%"  # Target: 99.9%+
mismatches_investigated: 0
mismatches_accepted: 0  # Known intentional differences
mismatches_bugs: 0
sign_off: false
```

**Shadow traffic** — copy production requests to new system, compare responses (don't serve new responses to users yet).

### Performance Regression Rules

- P95 latency must not increase >10% vs legacy
- Throughput must meet or exceed legacy under same load
- Database query count must not increase per request
- Memory usage must not increase >20%
- If ANY metric regresses → investigate before proceeding

---

## Phase 9: Team & Process

### Modernization Team Structure

| Role | Responsibility | When Needed |
|------|---------------|-------------|
| **Modernization Lead** | Strategy, sequencing, blockers | Full-time |
| **Legacy Expert** | Knows where the bodies are buried | Part-time, on-call |
| **New Platform Engineer** | Builds target architecture | Full-time |
| **Data Engineer** | Migration, sync, validation | Phase-dependent |
| **QA/Test Engineer** | Parity testing, automation | Full-time |
| **DevOps/Platform** | CI/CD, infrastructure | Part-time |
| **Product Owner** | Business priority, acceptance | Part-time |

### Knowledge Mining from Legacy

The most dangerous part of modernization is **losing undocumented business rules**.

1. **Code archaeology** — git blame, find oldest unchanged code, understand why
2. **Interview stakeholders** — "What would break if we changed X?"
3. **Production log analysis** — what edge cases actually occur?
4. **Error handling review** — each catch block is a documented business rule
5. **Test suite review** — tests describe expected behavior
6. **Configuration review** — magic numbers, feature flags, overrides

### Communication Plan

| Audience | Frequency | Content |
|----------|-----------|---------|
| Executive sponsor | Bi-weekly | Progress, risks, budget, timeline |
| Engineering team | Weekly | Sprint goals, technical decisions, blockers |
| Dependent teams | Monthly | Upcoming changes, migration dates, API changes |
| End users | Per migration | What's changing, when, how it affects them |

---

## Phase 10: Risk Management

### Top 10 Modernization Risks (Pre-Built)

| # | Risk | Likelihood | Impact | Mitigation |
|---|------|-----------|--------|------------|
| 1 | Undocumented business rules lost | High | Critical | Code archaeology + stakeholder interviews + parity tests |
| 2 | Timeline underestimation | Very High | High | 2x initial estimate, phase-gated checkpoints |
| 3 | Data migration corruption | Medium | Critical | Checksums, parallel runs, rollback plans |
| 4 | Feature parity gaps | High | High | Shadow traffic testing, user acceptance testing |
| 5 | Team knowledge loss (people leave) | Medium | High | Document everything, pair programming, knowledge sharing |
| 6 | Legacy system changes during migration | High | Medium | Feature freeze or dual-write contract |
| 7 | Performance regression | Medium | High | Load testing at every phase, performance budgets |
| 8 | Scope creep (improve while migrating) | Very High | Medium | Strict "migrate, don't improve" rule for Phase 1 |
| 9 | Integration failures | Medium | High | Contract testing, circuit breakers, fallback routing |
| 10 | Stakeholder fatigue | High | Medium | Quick wins early, visible progress dashboard |

### Kill Criteria

Stop the modernization if:
- Budget exceeds 2x initial estimate with <50% complete
- Key business rules can't be verified after migration
- Team attrition >30% during project
- Legacy system stability degrades due to migration work
- Business context changes (M&A, pivot, sunset)

**If kill criteria triggered:** Stabilize what's done, document learnings, reassess in 6 months.

---

## Phase 11: Patterns & Playbooks

### Language/Framework Migration Patterns

**Java → Modern Java (8→17+)**
- Records, sealed classes, pattern matching
- Virtual threads (Project Loom) for thread-per-request
- Migrate build: Maven→Gradle or update Maven plugins
- Spring Boot 2→3: javax→jakarta namespace

**Python 2→3**
- Use `2to3` tool for automated conversion
- Fix: print(), division, unicode, dict methods
- Upgrade dependencies (check py3 compat)

**jQuery→React/Vue**
- Extract components from page sections
- State management replaces DOM manipulation
- Event handlers become component methods
- Ajax calls become API service layer

**Monolith→Microservices**
- Strangler fig (see Phase 3)
- Start with read models (reporting, search)
- Extract stateless services first
- Shared database → database-per-service last

**On-Prem→Cloud**
- Rehost first (lift & shift)
- Then replatform (managed services)
- Then re-architect (cloud-native patterns)
- Never skip steps — each proves value

### COBOL/Mainframe Modernization

1. **API wrapping** — expose CICS/IMS transactions as REST APIs
2. **Screen scraping** — automate 3270 terminal interactions
3. **Gradual extraction** — one transaction at a time
4. **Data replication** — DB2/VSAM → PostgreSQL/cloud DB
5. **Rule extraction** — COBOL paragraphs → business rule engine
6. **Never rewrite all at once** — decades of business logic = decades of edge cases

### Microservices Anti-Patterns to Avoid

| Anti-Pattern | Symptom | Fix |
|-------------|---------|-----|
| Distributed monolith | Services must deploy together | Identify and break coupling |
| Shared database | Multiple services write same tables | Database-per-service |
| Synchronous chains | A calls B calls C calls D | Async events, choreography |
| Nano-services | Hundreds of tiny services | Merge related services |
| Shared libraries for business logic | Library update breaks consumers | Duplicate code > shared coupling |
| No API versioning | Breaking changes cascade | Semantic versioning, deprecation policy |

---

## Phase 12: Metrics & Reporting

### Modernization Health Dashboard

```yaml
project: ""
assessment_date: ""
overall_health: "green | yellow | red"

progress:
  modules_total: 0
  modules_migrated: 0
  modules_in_progress: 0
  percent_complete: "0%"
  
velocity:
  modules_per_sprint: 0
  estimated_completion: ""
  on_track: true

quality:
  parity_test_pass_rate: "0%"
  production_incidents_from_migration: 0
  rollbacks: 0
  
risk:
  open_risks: 0
  p0_risks: 0
  blocked_items: 0

cost:
  budget_total: "$0"
  budget_spent: "$0"
  budget_remaining: "$0"
  burn_rate_monthly: "$0"
```

### 100-Point Modernization Quality Rubric

| Dimension | Weight | Score (0-10) | Weighted |
|-----------|--------|-------------|----------|
| Strategy clarity | 15% | | |
| Risk management | 15% | | |
| Testing rigor | 15% | | |
| Data integrity | 15% | | |
| Architecture quality | 10% | | |
| Team capability | 10% | | |
| Stakeholder alignment | 10% | | |
| Documentation | 10% | | |
| **Total** | **100%** | | **/100** |

**90-100**: Exemplary — reference project
**70-89**: Strong — minor improvements
**50-69**: Adequate — address gaps
**Below 50**: At risk — pause and reassess

### Weekly Status Template

```markdown
## Modernization Status — Week of [DATE]

### Progress
- Modules migrated this week: [N]
- Total migrated: [N]/[TOTAL] ([X]%)
- On track for [TARGET DATE]: [Yes/No]

### Completed
- [What shipped this week]

### In Progress
- [What's being worked on]

### Blockers
- [What's stuck and what's needed]

### Risks
- [New or changed risks]

### Next Week
- [Plan for next sprint]
```

---

## Edge Cases

### "We need to modernize but can't stop adding features"
- **Strangler fig** — modernize around new features
- Feature freeze on legacy module ONLY when that module is being migrated
- New features build in new stack from day 1

### "We don't know what the system does"
- Start with observability: instrument logging, tracing, metrics
- Run for 2-4 weeks to understand actual usage patterns
- Code coverage analysis shows what code is actually executed
- Interview longest-tenured team members

### "Multiple systems need modernizing simultaneously"
- Sequence by dependency order — downstream first
- Shared services (auth, data) get modernized once, reused
- Never parallelize more than 2 modernization streams

### "The original developers are gone"
- Treat code as the documentation
- Invest 2-4 weeks in code archaeology before any migration work
- Pair new developers with business stakeholders
- Write tests for existing behavior before changing anything

### "We're being acquired / merging systems"
- Map overlapping functionality first
- Pick "winner" system per domain — don't merge codebases
- API integration layer between systems
- 18-month realistic timeline for full consolidation

### "Compliance requires the old system"
- Maintain compliance evidence chain during migration
- Dual-audit period with both systems
- Get compliance team involved in migration planning from Day 1
- Document control mapping: old control → new implementation

---

## Natural Language Commands

| Command | Action |
|---------|--------|
| "Assess this system for modernization" | Run full Technical Debt Inventory |
| "Which modernization strategy should we use?" | Walk through Strategy Decision Tree |
| "Plan a strangler fig migration" | Generate Strangler Facade YAML + sequence |
| "Decompose this monolith" | Domain discovery + Bounded Context mapping |
| "Migrate this database" | Data Quality Gates + migration strategy |
| "Check cloud readiness" | Run Cloud Readiness Assessment |
| "Create a migration testing plan" | Build Testing Pyramid with parity tests |
| "What are the risks?" | Generate Top 10 risk register |
| "How do we migrate from [X] to [Y]?" | Pattern-specific playbook |
| "Status update for modernization" | Generate Weekly Status Template |
| "Score this modernization project" | Run 100-Point Quality Rubric |
| "Should we kill this modernization?" | Evaluate Kill Criteria |
