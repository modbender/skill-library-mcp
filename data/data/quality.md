# Quality & Validation

## Data Quality Dimensions

| Dimension | Definition | Check |
|-----------|------------|-------|
| Completeness | No missing required values | Null counts, coverage % |
| Accuracy | Values match reality | Cross-reference, spot check |
| Consistency | Same value = same meaning | Duplicates, conflicting records |
| Timeliness | Data is current enough | Last update, lag calculation |
| Validity | Values within allowed ranges | Constraints, domain rules |
| Uniqueness | No unintended duplicates | Key uniqueness checks |

## Validation Rules

### Schema Validation
```
- Column exists
- Column type matches expected (INT, VARCHAR, DATE)
- Column is not null (if required)
- Column length within bounds
- Foreign key references valid
```

### Range Validation
- Numeric: min ≤ value ≤ max
- Date: within expected range, not in future (if applies)
- Categorical: value in allowed set
- Text: pattern matching (regex for emails, phones, etc.)

### Cross-Field Validation
- Start date ≤ end date
- Calculated fields match components
- Mutually exclusive flags
- Hierarchical consistency (child belongs to parent)

## Anomaly Detection

### Volume Checks
```
Expected: ~10,000 rows/day
Received: 2,500 rows
Alert: Volume drop >50%
```

### Distribution Drift
- Compare current distribution to baseline
- KS test, PSI (Population Stability Index)
- Alert thresholds: PSI > 0.1 (some change), > 0.25 (significant)

### Value Drift
- Track metric averages over time
- Moving window comparison
- Control charts (upper/lower bounds)

## Data Quality Reports

### Daily Health Check
```
□ Row counts vs expected
□ Null rates per critical column
□ Value distribution summary
□ Latest timestamp (freshness)
□ Duplicate detection results
□ Validation rule failures
```

### Quality Score
```python
# Example scoring
completeness = 1 - (null_count / total_rows)
validity = 1 - (invalid_count / total_rows)
uniqueness = 1 - (duplicate_count / total_rows)

quality_score = (completeness + validity + uniqueness) / 3
```

## Data Contracts

### Between Systems
- Define expected schema (columns, types)
- Define freshness SLA (updated by X time)
- Define volume bounds (±30% of average)
- Define validation rules
- Define escalation path when violated

### Testing Pipeline
```
1. Load data to staging
2. Run all validation rules
3. If all pass → promote to production
4. If any fail → alert, hold in staging
5. Log all checks with pass/fail
```

## Lineage Tracking

### What to Track
- Source system
- Extraction timestamp
- Transformations applied
- Who/what made changes
- Version of processing code

### Documentation Format
```yaml
column: revenue_usd
source: billing.invoices.amount
transformations:
  - currency conversion from EUR to USD
  - null replaced with 0
last_updated: 2024-01-15T10:30:00Z
owner: data-team
```

## Recovery Procedures

### When Quality Fails
1. Stop downstream consumption if critical
2. Identify scope of bad data
3. Find root cause (source, transformation, timing)
4. Fix pipeline or reject bad input
5. Backfill if possible
6. Communicate to stakeholders
7. Add checks to prevent recurrence
