# Data Migration Planner

Plan, execute, and validate data migrations between systems. Covers schema mapping, ETL pipeline design, rollback strategies, and post-migration validation.

## What It Does

Given source and target system details, this skill:
1. Maps source → target schemas with field-level transformation rules
2. Generates an ETL pipeline plan with staging, transform, and load phases
3. Creates validation queries (row counts, checksum, referential integrity)
4. Builds a rollback plan with point-of-no-return criteria
5. Produces a migration runbook with go/no-go gates

## Usage

Tell your agent:
- "Plan a migration from Salesforce to HubSpot CRM"
- "Create a data migration runbook for moving from MySQL to PostgreSQL"
- "Map our legacy ERP data to the new system schema"

## Migration Framework

### Phase 1: Discovery
- Inventory all source tables/objects and record counts
- Document data types, constraints, and relationships
- Identify data quality issues (nulls, duplicates, orphans)
- Map business rules that affect data interpretation

### Phase 2: Schema Mapping
For each source entity, document:
| Source Field | Type | Target Field | Type | Transform | Notes |
|---|---|---|---|---|---|
| (field) | (type) | (field) | (type) | (rule) | (edge cases) |

### Phase 3: ETL Pipeline
```
Extract → Stage (raw) → Clean → Transform → Validate → Load → Verify
```
- **Extract**: Full vs incremental, API vs direct DB, rate limits
- **Stage**: Raw landing zone, no transforms, audit trail
- **Clean**: Dedup, null handling, encoding fixes
- **Transform**: Type conversions, lookups, calculated fields
- **Validate**: Pre-load checks (counts, checksums, business rules)
- **Load**: Batch size, parallelism, error handling
- **Verify**: Post-load reconciliation

### Phase 4: Validation
- Row count match (source vs target, per table)
- Checksum validation on key columns
- Referential integrity checks
- Business rule validation (e.g., all active accounts migrated)
- User acceptance sampling (random 5% manual review)

### Phase 5: Cutover
- Go/no-go criteria checklist
- Point-of-no-return definition
- Rollback procedure and time estimate
- Communication plan (users, stakeholders)
- Parallel run period (if applicable)

## Risk Factors
- **Data volume**: >10M rows = batch strategy required
- **Downtime window**: Zero-downtime needs CDC/dual-write
- **Data quality**: Garbage in = garbage out. Clean BEFORE migrating
- **Dependencies**: Other systems reading from source during migration
- **Compliance**: GDPR/HIPAA data handling during transit

## Output Format
Deliver a migration runbook as structured markdown with:
1. Executive summary (what, why, when, risk level)
2. Schema mapping tables
3. ETL pipeline specification
4. Validation test suite
5. Cutover runbook with rollback
6. Timeline with milestones

## Cost Estimation
Typical migration costs by complexity:
- Simple (1-5 tables, <1M rows): $5K-$15K or 1-2 weeks internal
- Medium (10-50 tables, 1-10M rows): $25K-$75K or 1-2 months
- Complex (50+ tables, 10M+ rows, multiple systems): $100K-$500K or 3-6 months

---

**Built by [AfrexAI](https://afrexai-cto.github.io/context-packs/)** — AI Context Packs for business automation.

Calculate your AI automation ROI: [Revenue Calculator](https://afrexai-cto.github.io/ai-revenue-calculator/)
