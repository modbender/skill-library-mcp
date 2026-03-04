# FinOps Maturity Model

The FinOps maturity model uses a "Crawl, Walk, Run" approach that enables organizations to start small and grow in scale, scope, and complexity as business value warrants.

## Key Principles

1. **Business value drives maturity decisions** - Don't mature for maturity's sake
2. **Different capabilities mature at different rates** - Not everything needs to be "Run"
3. **Maturity is not a destination** - It's a continuous journey
4. **Quick action beats perfect analysis** - Start at Crawl, learn, then progress

## Maturity Levels

### Crawl

**Characteristics**:
- Very little reporting and tooling
- Measurements provide insight into benefits of maturing
- Basic KPIs set for measurement of success
- Basic processes and policies defined
- Capability understood but not followed by all major teams
- Plans to address "low hanging fruit"

**Typical Organization Profile**:
- New to cloud or FinOps
- Limited cloud spend
- Manual, reactive processes
- Siloed decision-making
- Basic visibility

**Sample KPIs**:
| Metric | Crawl Target |
|--------|--------------|
| Cost allocation | ~50% |
| RI/SP coverage | ~60% |
| Forecast variance | ~20% |
| Tagging compliance | ~50% |

### Walk

**Characteristics**:
- Capability understood and followed within the organization
- Difficult edge cases identified but decision made not to address them
- Automation and/or processes cover most capability requirements
- Critical edge cases identified with effort to resolve estimated
- Medium to high goals/KPIs set on measurement of success

**Typical Organization Profile**:
- Established FinOps practice
- Moderate to significant cloud spend
- Documented, proactive processes
- Cross-functional collaboration
- Detailed visibility and reporting

**Sample KPIs**:
| Metric | Walk Target |
|--------|-------------|
| Cost allocation | ~80% |
| RI/SP coverage | ~70% |
| Forecast variance | ~15% |
| Tagging compliance | ~80% |

### Run

**Characteristics**:
- Capability understood and followed by all teams
- Difficult edge cases are being addressed
- Very high goals/KPIs set on measurement of success
- Automation is the preferred approach

**Typical Organization Profile**:
- Mature FinOps practice
- Significant cloud spend
- Automated, continuous processes
- Embedded cost culture
- Real-time visibility and optimization

**Sample KPIs**:
| Metric | Run Target |
|--------|------------|
| Cost allocation | >90% |
| RI/SP coverage | ~80% |
| Forecast variance | ~12% |
| Tagging compliance | >95% |

## Maturity Assessment Framework

### Assessment Dimensions

For each capability, assess maturity across these dimensions:

| Dimension | Crawl | Walk | Run |
|-----------|-------|------|-----|
| **Process** | Ad-hoc, manual | Documented, regular | Automated, continuous |
| **People** | Limited involvement | Defined roles | Organization-wide adoption |
| **Tools** | Basic/native | Third-party tools | Integrated, automated |
| **Metrics** | Basic KPIs | Detailed tracking | Real-time optimization |
| **Coverage** | Partial | Majority | Comprehensive |

### Capability-Specific Maturity Examples

#### Cost Allocation Maturity

| Level | Characteristics |
|-------|-----------------|
| Crawl | Account-level allocation, inconsistent tagging, manual shared cost splits |
| Walk | Resource-level allocation, 80%+ tagging compliance, documented shared cost strategy |
| Run | Automated allocation, near-complete tagging, dynamic shared cost distribution |

#### Rate Optimization Maturity

| Level | Characteristics |
|-------|-----------------|
| Crawl | Ad-hoc RI purchases, no coverage targets, decentralized buying |
| Walk | Regular purchase cadence, 70% coverage target, centralized analysis |
| Run | Automated recommendations, 80%+ coverage, coordinated with workload optimization |

#### Forecasting Maturity

| Level | Characteristics |
|-------|-----------------|
| Crawl | Manual forecasts, historical trending only, 20%+ variance |
| Walk | Regular forecast updates, includes planned changes, 15% variance |
| Run | Driver-based models, real-time adjustments, 12% variance |

## Maturity Progression Guidance

### When to Progress from Crawl to Walk

Progress when:
- Basic KPIs consistently met
- Organization sees value in FinOps
- Quick wins have been captured
- Teams ready for more sophisticated practices
- Business value justifies investment

### When to Progress from Walk to Run

Progress when:
- Walk KPIs consistently met
- Automation ROI is positive
- Organization demands real-time insights
- Scale requires automation
- Cultural adoption is strong

### When NOT to Progress

Don't progress just for maturity's sake. Stay at current level when:
- Current maturity meets measurement of success
- Business value doesn't justify additional investment
- Other capabilities need attention first
- Organization isn't ready for change

## Prioritization Framework

### Value vs. Effort Matrix

```
High Value │   Quick Wins    │   Strategic
           │   (Do First)    │   (Plan for)
───────────┼─────────────────┼─────────────────
Low Value  │   Fill Ins      │   Reconsider
           │   (Do Later)    │   (Maybe Never)
           │                 │
           └─────────────────┴─────────────────
                Low Effort      High Effort
```

### Capability Prioritization

| Priority | Criteria |
|----------|----------|
| High | Large spend impact, quick ROI, foundational for other capabilities |
| Medium | Moderate impact, supports operations, improves efficiency |
| Low | Nice to have, limited ROI, not currently painful |

### Typical Prioritization Order

1. **Data Ingestion & Allocation** (Foundation for everything)
2. **Reporting & Analytics** (Enables visibility)
3. **Rate Optimization** (Quick financial wins)
4. **Workload Optimization** (Ongoing efficiency)
5. **Governance & Policy** (Scale and sustain)
6. **Advanced capabilities** (Benchmarking, unit economics, sustainability)

## Maturity Roadmap Template

### Sample 12-Month Roadmap

| Quarter | Focus | Target Maturity Changes |
|---------|-------|------------------------|
| Q1 | Foundation | Allocation: Crawl→Walk, Reporting: Crawl→Walk |
| Q2 | Optimization | Rate Optimization: Crawl→Walk, Workload Optimization: Crawl→Walk |
| Q3 | Operations | Governance: Crawl→Walk, Forecasting: Crawl→Walk |
| Q4 | Advancement | Rate Optimization: Walk→Run, Assessment: Walk |

### Progress Tracking

Track maturity progress using:
- Monthly maturity self-assessments
- Quarterly stakeholder reviews
- Annual comprehensive assessments
- Benchmark against industry peers (data.finops.org)

## Common Maturity Anti-Patterns

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Run everything | Wasted effort, no ROI | Prioritize by business value |
| Never progress | Miss optimization opportunities | Regular maturity reviews |
| Skip Walk | Implementation failures | Incremental progression |
| Ignore culture | Tools without adoption | Balance tech and people |
| No metrics | Can't measure progress | Define KPIs per capability |
