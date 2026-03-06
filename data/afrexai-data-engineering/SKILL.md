---
name: Data Engineering Command Center
description: Complete methodology for designing, building, operating, and
  scaling data pipelines and infrastructure. Zero dependencies — pure agent
  skill.
---

# Data Engineering Command Center

Complete methodology for designing, building, operating, and scaling data pipelines and infrastructure. Zero dependencies — pure agent skill.

---

## Phase 1: Data Architecture Assessment

Before building anything, understand the landscape.

### Architecture Brief

```yaml
project_name: ""
business_context: ""
data_consumers:
  - team: ""
    use_case: ""          # analytics | ML | operational | reporting | reverse-ETL
    latency_requirement: ""  # real-time (<1s) | near-real-time (<5min) | batch (hourly+)
    query_pattern: ""     # ad-hoc | scheduled | API | dashboard

current_state:
  sources: []             # list every system producing data
  storage: []             # where data lives today
  pain_points: []         # what's broken, slow, unreliable
  data_volume:
    current_gb_per_day: 0
    growth_rate_percent: 0
    retention_months: 0

constraints:
  budget_monthly_usd: 0
  team_size: 0
  skill_level: ""         # junior | mid | senior | mixed
  compliance: []          # GDPR, HIPAA, SOX, PCI, none
  cloud_provider: ""      # AWS | GCP | Azure | multi | on-prem
```

### Architecture Pattern Decision Matrix

| Signal | Pattern | When to Use |
|--------|---------|-------------|
| All consumers need data hourly+ | **Batch ETL** | Reporting, warehousing, most analytics |
| Some need <5 min latency | **Micro-batch** | Dashboard freshness, near-real-time analytics |
| Events need <1s processing | **Streaming** | Fraud detection, real-time pricing, alerts |
| Need both batch + streaming | **Lambda** | When batch accuracy + real-time speed both matter |
| Want to simplify Lambda | **Kappa** | When you can reprocess from stream replay |
| Data lake + warehouse combined | **Lakehouse** | When you need both cheap storage + fast SQL |
| Sources change independently | **Data Mesh** | Large orgs, domain-owned data, >5 teams |
| ML is primary consumer | **Feature Store** | ML-heavy orgs with feature reuse needs |

### Technology Selection Guide

#### Orchestration

| Tool | Best For | Avoid When |
|------|----------|------------|
| **Airflow** | Complex DAGs, Python-native teams, mature ecosystem | Simple pipelines (<5 tasks) |
| **Dagster** | Software-defined assets, strong typing, dev experience | Legacy team resistant to new paradigms |
| **Prefect** | Dynamic workflows, cloud-native, Python-first | Need on-prem with no cloud dependency |
| **dbt** | SQL transformations, ELT, analytics engineering | Non-SQL transforms, streaming |
| **Temporal** | Long-running workflows, retry-heavy, microservices | Simple ETL, small teams |
| **Cron + scripts** | <3 pipelines, solo engineer, simple schedules | Anything with dependencies or retries |

#### Processing

| Tool | Best For | Avoid When |
|------|----------|------------|
| **Spark** | >100GB, complex transforms, ML pipelines | <10GB (overkill), real-time streaming |
| **DuckDB** | Local analytics, <100GB, SQL on files | Distributed processing, production streaming |
| **Polars** | Single-node, Rust-speed, <50GB, DataFrames | Distributed, need Spark ecosystem |
| **Pandas** | <1GB, quick analysis, prototyping | Production pipelines, anything >5GB |
| **Flink** | True streaming, event-time processing | Batch-only, small team (steep learning curve) |
| **SQL (warehouse)** | ELT in Snowflake/BigQuery/Redshift | Complex ML transforms, binary data |

#### Storage

| Tool | Best For | Avoid When |
|------|----------|------------|
| **Snowflake** | Analytics, separation of compute/storage, multi-cloud | Tight budget, real-time OLTP |
| **BigQuery** | GCP-native, serverless, large-scale analytics | Multi-cloud, need fine-grained cost control |
| **Redshift** | AWS-native, existing AWS ecosystem | Elastic scaling needs, multi-cloud |
| **Databricks** | ML + analytics unified, Spark-native, lakehouse | Pure SQL analytics, small data |
| **PostgreSQL** | OLTP + light analytics, <500GB, budget-conscious | >1TB analytics, real-time dashboards on large data |
| **S3/GCS/ADLS** | Raw data lake, cheap storage, any format | Direct SQL queries (need compute layer) |
| **Delta Lake/Iceberg** | Table format on data lake, ACID on files | Simple file storage, no lakehouse need |

---

## Phase 2: Data Modeling

### Modeling Methodology Decision

| Approach | Best For | Key Concept |
|----------|----------|-------------|
| **Kimball (Dimensional)** | BI/reporting, star schemas | Facts + Dimensions, business-process-centric |
| **Inmon (3NF)** | Enterprise data warehouse, single source of truth | Normalized, subject-area-centric |
| **Data Vault 2.0** | Agile warehousing, auditability, multiple sources | Hubs + Links + Satellites, insert-only |
| **One Big Table (OBT)** | Simple analytics, few joins, dashboard performance | Pre-joined, denormalized, fast queries |
| **Activity Schema** | Event analytics, product analytics | Entity + Activity + Feature columns |

### Dimensional Model Template

```yaml
fact_table:
  name: "fact_[business_process]"
  grain: ""                    # one row = one [what]?
  grain_statement: "One row per [transaction/event/snapshot] at [time grain]"
  measures:
    - name: ""
      type: ""                 # additive | semi-additive | non-additive
      aggregation: ""          # SUM | AVG | COUNT | MIN | MAX | COUNT DISTINCT
      business_definition: ""
  degenerate_dimensions: []    # IDs stored in fact (order_number, invoice_id)
  foreign_keys: []             # links to dimension tables

dimensions:
  - name: "dim_[entity]"
    type: ""                   # Type 1 (overwrite) | Type 2 (history) | Type 3 (previous value)
    natural_key: ""            # business key from source
    surrogate_key: ""          # warehouse-generated key
    attributes:
      - name: ""
        source: ""
        scd_type: ""           # 1 | 2 | 3
    hierarchy: []              # e.g., [country, region, city, store]
```

### SCD Type Decision Guide

| Scenario | SCD Type | Implementation |
|----------|----------|----------------|
| Don't care about history | **Type 1** | UPDATE in place |
| Need full history | **Type 2** | New row + valid_from/valid_to + is_current flag |
| Only need previous value | **Type 3** | Add previous_[column] |
| Track changes with timestamps | **Type 4** | Mini-dimension (history table) |
| Hybrid: some attrs Type 1, some Type 2 | **Type 6** | Combine 1+2+3 in one table |

**Default recommendation:** Type 2 for anything business-critical (customer status, product price, employee department). Type 1 for everything else.

### Naming Conventions

| Object | Convention | Example |
|--------|-----------|---------|
| Raw/staging tables | `raw_[source]_[table]` | `raw_stripe_payments` |
| Staging models | `stg_[source]__[entity]` | `stg_stripe__payments` |
| Intermediate models | `int_[entity]_[verb]` | `int_orders_pivoted` |
| Mart/fact tables | `fct_[business_process]` | `fct_orders` |
| Dimension tables | `dim_[entity]` | `dim_customers` |
| Metrics/aggregates | `mrt_[domain]_[metric]` | `mrt_sales_daily` |
| Snapshots | `snp_[entity]_[grain]` | `snp_inventory_daily` |
| Columns: boolean | `is_[state]` or `has_[thing]` | `is_active`, `has_subscription` |
| Columns: timestamp | `[event]_at` | `created_at`, `shipped_at` |
| Columns: date | `[event]_date` | `order_date` |
| Columns: ID | `[entity]_id` | `customer_id` |
| Columns: amount | `[thing]_amount` | `order_amount` |
| Columns: count | `[thing]_count` | `line_item_count` |

---

## Phase 3: Pipeline Design Patterns

### Universal Pipeline Template

```yaml
pipeline:
  name: ""
  owner: ""
  schedule: ""               # cron expression
  sla_minutes: 0             # max acceptable runtime
  tier: ""                   # 1 (critical) | 2 (important) | 3 (nice-to-have)

  extract:
    source_system: ""
    connection: ""
    strategy: ""             # full | incremental | CDC | log-based
    incremental_key: ""      # column for incremental (e.g., updated_at)
    watermark_storage: ""    # where to persist last-extracted position

  transform:
    engine: ""               # SQL | Spark | Python | dbt
    stages:
      - name: "clean"
        operations: []       # dedupe, null handling, type casting, trimming
      - name: "conform"
        operations: []       # standardize codes, currencies, timezones
      - name: "enrich"
        operations: []       # lookups, calculations, derived fields
      - name: "aggregate"
        operations: []       # rollups, pivots, window functions

  load:
    target_system: ""
    strategy: ""             # append | upsert | merge | truncate-reload | partition-swap
    merge_keys: []
    partition_key: ""
    clustering_keys: []

  quality_gates:
    pre_load: []             # checks before writing
    post_load: []            # checks after writing

  error_handling:
    strategy: ""             # fail-fast | dead-letter | retry | skip-and-alert
    max_retries: 3
    retry_delay_seconds: 300
    alert_channels: []
```

### Extraction Strategy Decision Tree

```
Is the source database?
├── Yes → Does it support CDC?
│   ├── Yes → Use CDC (Debezium, AWS DMS, Fivetran)
│   │   Best for: high-volume, low-latency, minimal source impact
│   └── No → Does it have a reliable updated_at column?
│       ├── Yes → Incremental extraction on updated_at
│       │   ⚠️ Won't catch hard deletes — add periodic full reconciliation
│       └── No → Full extraction
│           Only viable for small tables (<1M rows)
├── Is it an API?
│   ├── Supports webhooks? → Event-driven ingestion
│   ├── Has cursor/pagination? → Incremental with cursor bookmark
│   └── No pagination? → Full pull with rate-limit handling
├── Is it files (S3, SFTP, email)?
│   └── Event-triggered (S3 notification, file watcher)
│       Validate: schema, completeness, filename pattern
└── Is it streaming (Kafka, Kinesis, Pub/Sub)?
    └── Consumer group with offset management
        Key decisions: at-least-once vs exactly-once, consumer lag alerting
```

### Load Strategy Decision

| Strategy | When | Trade-off |
|----------|------|-----------|
| **Append** | Event/log data, immutable facts | Simple but grows forever — partition + retain |
| **Upsert/Merge** | Dimension updates, SCD Type 1 | Handles updates but slower on large tables |
| **Truncate-Reload** | Small tables (<1M), reference data | Simple but window of missing data |
| **Partition Swap** | Large fact tables, daily loads | Atomic, fast, but needs partition alignment |
| **Soft Delete** | Need audit trail of deletions | Adds complexity to every downstream query |

### Idempotency Rules (NON-NEGOTIABLE)

Every pipeline MUST be re-runnable without side effects:

1. **Use MERGE/UPSERT, never blind INSERT** for mutable data
2. **Partition-swap for immutable data** — drop partition + reload
3. **Store watermarks externally** — not in the pipeline code
4. **Dedup at ingestion** — use source natural keys
5. **Test by running twice** — output must be identical both times

---

## Phase 4: Data Quality Framework

### Quality Dimensions

| Dimension | Definition | Example Check |
|-----------|-----------|---------------|
| **Completeness** | No missing values where required | `NOT NULL` on required fields, row count within range |
| **Uniqueness** | No unexpected duplicates | Primary key uniqueness, natural key uniqueness |
| **Validity** | Values within expected domain | Enum checks, range checks, regex patterns |
| **Accuracy** | Data matches real-world truth | Cross-system reconciliation, manual spot checks |
| **Freshness** | Data arrives on time | `MAX(loaded_at) > NOW() - INTERVAL '2 hours'` |
| **Consistency** | Same data agrees across systems | Sum reconciliation between source and target |

### Quality Check Templates

```sql
-- Completeness: Required fields not null
SELECT COUNT(*) AS null_violations
FROM {table}
WHERE {required_column} IS NULL;
-- Threshold: 0

-- Uniqueness: No duplicate primary keys
SELECT {pk_column}, COUNT(*) AS dupe_count
FROM {table}
GROUP BY {pk_column}
HAVING COUNT(*) > 1;
-- Threshold: 0

-- Freshness: Data arrived within SLA
SELECT CASE
  WHEN MAX({timestamp_col}) > CURRENT_TIMESTAMP - INTERVAL '{sla_hours} hours'
  THEN 'PASS' ELSE 'FAIL'
END AS freshness_check
FROM {table};

-- Volume: Row count within expected range
SELECT CASE
  WHEN COUNT(*) BETWEEN {min_expected} AND {max_expected}
  THEN 'PASS' ELSE 'FAIL'
END AS volume_check
FROM {table}
WHERE {partition_col} = '{run_date}';

-- Referential: FK integrity
SELECT COUNT(*) AS orphan_count
FROM {fact_table} f
LEFT JOIN {dim_table} d ON f.{fk} = d.{pk}
WHERE d.{pk} IS NULL;
-- Threshold: 0

-- Distribution: No unexpected skew
SELECT {column}, COUNT(*) AS cnt,
  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct
FROM {table}
GROUP BY {column}
ORDER BY cnt DESC;
-- Alert if any single value > {max_pct}%

-- Cross-system reconciliation
SELECT
  (SELECT SUM(amount) FROM source_system.orders WHERE date = '{date}') AS source_total,
  (SELECT SUM(amount) FROM warehouse.fct_orders WHERE order_date = '{date}') AS target_total,
  ABS(source_total - target_total) AS variance;
-- Threshold: variance < 0.01 * source_total (1%)
```

### Data Contract Template

```yaml
contract:
  name: ""
  version: ""
  owner: ""                    # team responsible for producing this data
  consumers: []                # teams consuming this data
  sla:
    freshness_hours: 0
    availability_percent: 99.9
    support_hours: ""          # business-hours | 24x7

  schema:
    - column: ""
      type: ""
      nullable: false
      description: ""
      business_definition: ""
      pii: false
      checks:
        - type: ""             # not_null | unique | range | enum | regex | custom
          params: {}

  breaking_change_policy: ""   # notify-30-days | version-bump | never-break
  notification_channel: ""
```

### Quality Severity Levels

| Level | Definition | Response |
|-------|-----------|----------|
| **P0 — Critical** | Data corruption, wrong numbers in production dashboards, compliance data wrong | Stop pipeline, alert immediately, rollback if possible |
| **P1 — High** | Missing data for key reports, SLA breach, >5% of records affected | Alert team, fix within 4 hours, post-mortem required |
| **P2 — Medium** | Non-critical field quality, <1% records affected, no downstream impact | Fix in next sprint, add monitoring to prevent recurrence |
| **P3 — Low** | Cosmetic issues, edge cases, non-critical data | Backlog, fix when convenient |

---

## Phase 5: Performance Optimization

### SQL Optimization Checklist

| Problem | Fix | Impact |
|---------|-----|--------|
| Full table scan | Add/use partition pruning | 10-100x faster |
| Large joins | Pre-aggregate before joining | 5-50x faster |
| SELECT * | Select only needed columns | 2-10x faster (columnar stores) |
| Correlated subquery | Rewrite as JOIN or window function | 10-100x faster |
| DISTINCT on large result | Fix upstream duplication instead | 2-5x faster |
| ORDER BY without LIMIT | Add LIMIT or remove if not needed | Prevents memory spills |
| String operations in WHERE | Pre-compute, use lookup table | Enables index usage |
| Multiple passes over same data | Combine with CASE WHEN + GROUP BY | 2-5x faster |
| NOT IN with NULLs | Use NOT EXISTS or LEFT JOIN IS NULL | Correctness + performance |

### Spark Optimization Guide

| Problem | Solution |
|---------|----------|
| Shuffle-heavy joins | Broadcast small table (`broadcast(df)`) if <100MB |
| Data skew | Salt the skewed key: add random prefix, join on salted key, aggregate |
| Small files | Coalesce output: `.coalesce(target_files)` or use adaptive query execution |
| Too many partitions | `spark.sql.shuffle.partitions` = 2-3x cluster cores |
| OOM errors | Increase `spark.executor.memory`, reduce partition size, spill to disk |
| Slow writes | Use Parquet with snappy, partition by date, avoid small writes |
| Repeated computation | `.cache()` or `.persist()` DataFrames used >1 time |
| Complex transformations | Push down predicates, filter early, select early |

### Partitioning Strategy

| Data Type | Partition Key | Why |
|-----------|--------------|-----|
| Transactional/event | Date (daily or monthly) | Most queries filter by time range |
| Multi-tenant | Tenant ID + date | Isolate tenant queries, time-range pruning |
| Geospatial | Region + date | Regional queries are common |
| Log data | Date + hour | High volume needs finer partitions |
| Reference/dimension | Don't partition | Too small, full scan is fine |

**Rules:**
- Target 100MB-1GB per partition (compressed)
- <10,000 total partitions per table
- Never partition on high-cardinality columns (user_id)
- Always include partition key in WHERE clauses

---

## Phase 6: Data Governance & Cataloging

### Data Classification

| Level | Examples | Controls |
|-------|---------|----------|
| **Public** | Product catalog, published stats | No restrictions |
| **Internal** | Aggregated metrics, non-PII analytics | Auth required, audit logging |
| **Confidential** | Customer PII, financial records, HR data | Encryption, column-level access, masking |
| **Restricted** | SSN, payment cards, health records, passwords | Encryption at rest + transit, tokenization, audit every access, retention limits |

### PII Handling Rules

1. **Identify:** Scan all sources for PII columns (name, email, phone, SSN, DOB, address, IP)
2. **Classify:** Tag each with sensitivity level
3. **Minimize:** Only ingest PII you actually need
4. **Protect:** 
   - Hash or tokenize in staging (SHA-256 with salt for pseudonymization)
   - Dynamic masking for non-privileged users
   - Column-level encryption for restricted data
5. **Retain:** Auto-delete after retention period
6. **Audit:** Log every query touching PII columns
7. **Right to delete:** Build a deletion pipeline that propagates across all derived tables

### Data Catalog Entry Template

```yaml
dataset:
  name: ""
  description: ""
  owner_team: ""
  steward: ""                  # person responsible for quality
  domain: ""                   # sales | marketing | finance | product | engineering
  tier: ""                     # gold (trusted) | silver (cleaned) | bronze (raw)
  
  lineage:
    sources: []                # upstream datasets/systems
    transformations: ""        # brief description of key transforms
    downstream: []             # who consumes this
  
  refresh:
    schedule: ""
    sla_hours: 0
    last_successful_run: ""
  
  quality:
    tests: []                  # list of quality checks
    last_score: 0              # 0-100
    known_issues: []
  
  access:
    classification: ""         # public | internal | confidential | restricted
    pii_columns: []
    access_request_process: "" # how to get access
  
  usage:
    avg_daily_queries: 0
    top_consumers: []
    cost_monthly_usd: 0
```

---

## Phase 7: Pipeline Monitoring & Alerting

### Pipeline Health Dashboard

```yaml
dashboard:
  pipeline_metrics:
    - metric: "Pipeline Success Rate"
      formula: "successful_runs / total_runs * 100"
      target: ">99%"
      alert_threshold: "<95%"

    - metric: "Average Runtime"
      formula: "avg(end_time - start_time) over 7 days"
      target: "<SLA"
      alert_threshold: ">80% of SLA"

    - metric: "Data Freshness"
      formula: "NOW() - MAX(loaded_at)"
      target: "<SLA hours"
      alert_threshold: ">SLA"

    - metric: "Data Volume Variance"
      formula: "abs(today_rows - avg_7d_rows) / avg_7d_rows * 100"
      target: "<20%"
      alert_threshold: ">50%"

    - metric: "Quality Check Pass Rate"
      formula: "passed_checks / total_checks * 100"
      target: "100%"
      alert_threshold: "<95%"

    - metric: "Failed Pipeline Count"
      formula: "count where status = failed in last 24h"
      target: "0"
      alert_threshold: ">0"

    - metric: "Backfill Queue"
      formula: "count of pending backfill requests"
      target: "0"
      alert_threshold: ">5"

    - metric: "Infrastructure Cost"
      formula: "compute + storage + egress"
      target: "<budget"
      alert_threshold: ">110% budget"
```

### Alert Severity

| Severity | Condition | Response Time | Example |
|----------|-----------|---------------|---------|
| **P0** | Revenue/compliance impacting | 15 min | Payment pipeline down, regulatory report delayed |
| **P1** | Business-critical dashboard stale | 1 hour | Executive dashboard >4h stale |
| **P2** | Non-critical pipeline failed | 4 hours | Marketing attribution delayed |
| **P3** | Warning/degradation | Next business day | Pipeline 80% of SLA, minor quality drift |

### Structured Logging Standard

Every pipeline run MUST log:

```json
{
  "pipeline_name": "",
  "run_id": "",
  "started_at": "",
  "completed_at": "",
  "status": "success|failed|partial",
  "stage": "",
  "rows_extracted": 0,
  "rows_transformed": 0,
  "rows_loaded": 0,
  "rows_rejected": 0,
  "quality_checks_passed": 0,
  "quality_checks_failed": 0,
  "duration_seconds": 0,
  "error_message": "",
  "watermark_before": "",
  "watermark_after": ""
}
```

---

## Phase 8: Testing Strategy

### Pipeline Test Pyramid

| Layer | What to Test | How | When |
|-------|-------------|-----|------|
| **Unit** | Individual transforms, business logic | pytest with fixtures, dbt unit tests | Every PR |
| **Integration** | Source connectivity, schema compatibility | Test against staging/dev environment | Daily + PR |
| **Contract** | Schema hasn't changed, data types stable | Schema registry, contract tests | Every pipeline run |
| **Data Quality** | Completeness, uniqueness, freshness, validity | Quality framework checks | Every pipeline run |
| **E2E** | Full pipeline produces correct output | Golden dataset comparison | Weekly + release |
| **Performance** | Runtime within SLA, no regression | Benchmark against historical runs | Weekly |

### dbt Testing Checklist

```yaml
# For every model, define at minimum:
models:
  - name: fct_orders
    columns:
      - name: order_id
        tests:
          - unique
          - not_null
      - name: customer_id
        tests:
          - not_null
          - relationships:
              to: ref('dim_customers')
              field: customer_id
      - name: order_amount
        tests:
          - not_null
          - dbt_utils.accepted_range:
              min_value: 0
              max_value: 1000000
      - name: order_status
        tests:
          - accepted_values:
              values: ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']
      - name: ordered_at
        tests:
          - not_null
          - dbt_utils.recency:
              datepart: day
              field: ordered_at
              interval: 2
```

### Backfill Protocol

When you need to reprocess historical data:

1. **Scope:** Define exact date range and affected tables
2. **Impact assessment:** What downstream models/dashboards will be affected?
3. **Communication:** Notify consumers of temporary data inconsistency
4. **Isolation:** Run backfill in separate compute to avoid impacting current pipelines
5. **Validation:** Compare row counts and key metrics pre/post backfill
6. **Execution:** Process in reverse-chronological order (most recent first)
7. **Monitoring:** Watch for resource spikes, duplicate creation
8. **Verification:** Reconcile against source after completion
9. **Documentation:** Log what was backfilled, why, and any anomalies found

---

## Phase 9: Cost Optimization

### Cloud Cost Reduction Strategies

| Strategy | Savings | Effort |
|----------|---------|--------|
| Right-size compute (auto-scaling) | 20-40% | Low |
| Use spot/preemptible instances for batch | 60-80% | Medium |
| Compress data (Parquet + Snappy/Zstd) | 50-80% storage | Low |
| Lifecycle policies (hot → warm → cold → archive) | 40-70% storage | Low |
| Eliminate unused tables/pipelines | 10-30% | Low |
| Optimize query patterns (partition pruning) | 30-60% compute | Medium |
| Reserved capacity for steady-state | 30-50% | Medium |
| Cache expensive queries | 20-50% compute | Medium |

### Cost Allocation Template

```yaml
cost_tracking:
  by_pipeline:
    - pipeline: ""
      compute_monthly_usd: 0
      storage_monthly_usd: 0
      egress_monthly_usd: 0
      total: 0
      cost_per_row: 0        # total / rows_processed
      business_value: ""     # what revenue/decision does this enable?
      roi_justified: true    # is the cost worth it?

  optimization_opportunities:
    - description: ""
      estimated_savings_usd: 0
      effort: ""             # low | medium | high
      priority: 0            # 1 = do now
```

### Cost Red Flags

- Single pipeline >30% of total spend
- Cost per row increasing month-over-month
- Tables with 0 queries in 30 days
- Dev/staging environments running 24/7
- Full table scans on >1TB tables
- Uncompressed data in cloud storage
- Cross-region data transfer

---

## Phase 10: Operational Runbooks

### Pipeline Failure Triage

```
Pipeline failed →
1. Check error message in logs
   ├── Connection timeout → Check source availability, network, credentials
   ├── Schema mismatch → Source schema changed → update extract + notify
   ├── Data quality check failed → Investigate source data, check for anomalies
   ├── Out of memory → Increase resources or optimize query
   ├── Permission denied → Check IAM roles, token expiry
   ├── Duplicate key violation → Check idempotency, investigate source dupes
   └── Timeout (SLA breach) → Check data volume spike, query plan, cluster health

2. Determine impact
   ├── What dashboards/reports are affected?
   ├── What's the data freshness SLA?
   └── Who needs to be notified?

3. Fix
   ├── Transient (network, timeout) → Retry
   ├── Data issue → Fix source data, re-run with quality gate override if safe
   ├── Schema change → Update pipeline, backfill if needed
   └── Infrastructure → Scale up, file ticket with cloud provider

4. Post-fix
   ├── Verify data correctness
   ├── Update runbook with new failure mode
   └── Add monitoring/alerting to catch earlier next time
```

### Schema Change Management

When a source system changes schema:

1. **Detect:** Schema comparison check in extraction pipeline (hash schema, compare to registered)
2. **Classify:**
   - **Additive** (new column): Usually safe — add to pipeline, backfill if needed
   - **Rename**: Map old → new in transform, update downstream
   - **Type change**: Assess compatibility, may need cast or historical rebuild
   - **Column removed**: Critical — breaks queries, need immediate attention
3. **Test:** Run pipeline in dry-run mode with new schema
4. **Deploy:** Update transforms, quality checks, documentation
5. **Communicate:** Notify downstream consumers via data contract channel

### Disaster Recovery

| Scenario | RPO | RTO | Recovery Steps |
|----------|-----|-----|----------------|
| Pipeline code lost | 0 (git) | 1h | Redeploy from git, restore orchestrator state |
| Warehouse data corrupted | Varies | 4h | Restore from Time Travel/snapshot, re-run affected pipelines |
| Source system down | N/A | Wait | Queue extractions, catch up with incremental once restored |
| Cloud region outage | 24h | 8h | Failover to DR region if configured, else wait |
| Credential compromise | 0 | 2h | Rotate all credentials, audit access logs, re-run affected pipelines |

---

## Phase 11: Advanced Patterns

### Slowly Changing Dimension Type 2 (SQL Template)

```sql
-- Merge pattern for SCD Type 2
MERGE INTO dim_customer AS target
USING (
  SELECT * FROM stg_customers
  WHERE updated_at > (SELECT MAX(valid_from) FROM dim_customer)
) AS source
ON target.customer_natural_key = source.customer_id
   AND target.is_current = TRUE

-- Update: close old record
WHEN MATCHED AND (
  target.customer_name != source.name OR
  target.customer_status != source.status
  -- list all Type 2 tracked columns
) THEN UPDATE SET
  is_current = FALSE,
  valid_to = CURRENT_TIMESTAMP

-- Insert: new record (both new customers and changed ones)
WHEN NOT MATCHED THEN INSERT (
  customer_natural_key, customer_name, customer_status,
  valid_from, valid_to, is_current
) VALUES (
  source.customer_id, source.name, source.status,
  CURRENT_TIMESTAMP, '9999-12-31', TRUE
);

-- Then insert new versions of changed records
INSERT INTO dim_customer (
  customer_natural_key, customer_name, customer_status,
  valid_from, valid_to, is_current
)
SELECT customer_id, name, status,
  CURRENT_TIMESTAMP, '9999-12-31', TRUE
FROM stg_customers s
WHERE EXISTS (
  SELECT 1 FROM dim_customer d
  WHERE d.customer_natural_key = s.customer_id
    AND d.is_current = FALSE
    AND d.valid_to = CURRENT_TIMESTAMP
);
```

### CDC with Debezium (Architecture Pattern)

```
Source DB → Debezium Connector → Kafka Topic → 
  ├── Stream processor (Flink/Spark Streaming) → Target DB
  ├── S3 sink connector → Data Lake (raw)
  └── Elasticsearch sink → Search index
```

Key decisions:
- **Topic per table** or **single topic**: Per table (easier routing, independent scaling)
- **Schema registry**: Always use (Confluent Schema Registry or AWS Glue)
- **Serialization**: Avro (compact + schema evolution) or Protobuf (strict + fast)
- **Offset management**: Connector manages; monitor consumer lag

### Feature Store Pattern

```yaml
feature_store:
  entity: "customer"
  entity_key: "customer_id"
  
  features:
    - name: "total_orders_30d"
      description: "Total orders in last 30 days"
      type: "INT"
      source: "fct_orders"
      computation: "batch"      # batch | streaming | on-demand
      freshness: "daily"
      ttl_hours: 48
    
    - name: "avg_order_value_90d"
      description: "Average order value last 90 days"
      type: "FLOAT"
      source: "fct_orders"
      computation: "batch"
      freshness: "daily"
      ttl_hours: 48
    
    - name: "last_login_minutes_ago"
      description: "Minutes since last login event"
      type: "INT"
      source: "events_stream"
      computation: "streaming"
      freshness: "real-time"
      ttl_hours: 1
  
  serving:
    online: true               # low-latency feature serving (Redis/DynamoDB)
    offline: true              # batch feature retrieval for training
    point_in_time_correct: true  # prevent feature leakage in ML training
```

### Data Mesh Principles

If operating at scale (>5 data teams):

1. **Domain ownership**: Each business domain owns its data products (not central data team)
2. **Data as a product**: Treat datasets like products — SLAs, documentation, discoverability
3. **Self-serve platform**: Central team builds the platform, domains build on top
4. **Federated governance**: Standards and interoperability maintained centrally, implementation decentralized

**When NOT to use Data Mesh:**
- <5 data producers/consumers
- Small team (<20 engineers total)
- Single business domain
- Early-stage company (over-engineering)

---

## Quality Scoring Rubric (0-100)

| Dimension | Weight | Scoring |
|-----------|--------|---------|
| **Pipeline Reliability** | 20 | 0=frequent failures, 10=some failures with manual recovery, 20=99.5%+ success rate with auto-retry |
| **Data Quality** | 20 | 0=no checks, 10=basic null/unique checks, 20=comprehensive quality framework with contracts |
| **Performance** | 15 | 0=regularly breaches SLA, 8=meets SLA, 15=well under SLA with optimization |
| **Documentation** | 10 | 0=none, 5=basic README, 10=full catalog entries with lineage and business definitions |
| **Monitoring** | 15 | 0=no alerts, 8=failure alerts only, 15=proactive monitoring with dashboards and anomaly detection |
| **Testing** | 10 | 0=no tests, 5=basic smoke tests, 10=full test pyramid (unit+integration+contract+E2E) |
| **Cost Efficiency** | 10 | 0=no cost tracking, 5=tracked, 10=optimized with ROI justification per pipeline |

**Scoring guide:**
- 0-40: Critical gaps — prioritize pipeline reliability and data quality
- 41-60: Functional but fragile — add monitoring, testing, documentation
- 61-80: Solid — optimize performance, cost, governance
- 81-100: Excellent — maintain, innovate, mentor

---

## Edge Cases & Gotchas

### Timezone Traps
- Store everything in UTC. Convert only at presentation layer
- Event timestamps: use event time, not processing time
- Daylight saving: `TIMESTAMP WITH TIME ZONE`, never `WITHOUT`
- Late-arriving data: watermark strategy + allowed lateness window

### Late-Arriving Data
- Define maximum acceptable lateness per source
- Reprocess affected partitions when late data arrives
- Track late arrival rate as a quality metric
- Consider separate "late data" pipeline that patches in

### Exactly-Once Processing
- True exactly-once is expensive. Most systems need at-least-once + idempotent writes
- Use transaction IDs or natural keys for deduplication
- Kafka: use idempotent producer + transactional consumer
- Database: MERGE/UPSERT on natural key

### Schema Evolution
- **Forward compatible**: New code reads old data (safe to deploy new readers first)
- **Backward compatible**: Old code reads new data (safe to deploy new writers first)
- **Full compatible**: Both directions (safest, most restrictive)
- Use Avro or Protobuf with schema registry for streaming data

### Multi-Tenant Data
- Tenant ID in every table, every query, every log
- Row-level security in warehouse
- Separate compute per tenant (or at least isolation)
- Never join across tenants without explicit business reason
- Tenant-aware backfill (don't rebuild all tenants for one tenant's issue)

### Data Lake Anti-Patterns
- "Data Swamp": ingesting everything with no organization or catalog → only ingest what has a known consumer
- Small files: thousands of <1MB files → compact regularly (target 100MB-1GB)
- No table format: raw Parquet/CSV without Delta/Iceberg → loses ACID, schema evolution, time travel
- No access controls: single bucket, everyone admin → implement IAM per domain/team

---

## Natural Language Commands

Say any of these to activate specific workflows:

1. **"Design a data pipeline for [source] to [target]"** → Full pipeline template with extraction strategy, transforms, load pattern, quality checks
2. **"Model [entity/domain] for analytics"** → Dimensional model with fact/dimension tables, grain, measures, SCD types
3. **"Optimize this query/pipeline"** → Performance analysis with specific recommendations
4. **"Set up data quality for [table/pipeline]"** → Quality framework with checks, contracts, monitoring
5. **"Audit our data infrastructure"** → Full assessment using scoring rubric
6. **"Help with [Spark/Airflow/dbt/Kafka] issue"** → Troubleshooting with technology-specific guidance
7. **"Design a data catalog for our org"** → Catalog template with governance, classification, lineage
8. **"Plan a data migration from [old] to [new]"** → Migration plan with validation, rollback, parallel-run
9. **"Set up monitoring for our pipelines"** → Dashboard template with alerts, logging standards, runbooks
10. **"Review our data costs"** → Cost analysis with optimization strategies and ROI framework
11. **"Handle schema change in [source]"** → Change management protocol with impact assessment
12. **"Backfill [table] for [date range]"** → Backfill protocol with validation and communication plan
