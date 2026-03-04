# Workflow Patterns

## By User Mode

### Analyst Mode
```
User: "What's driving the drop in conversions?"

1. Query conversion data for relevant period
2. Compare to baseline period
3. Segment by key dimensions (source, device, region)
4. Identify segments with biggest delta
5. Drill into anomalous segment
6. Hypothesize cause
7. Present findings with supporting charts
```

### Engineer Mode
```
User: "Move this data from source A to warehouse B"

1. Connect to source, inspect schema
2. Design target schema (types, constraints)
3. Write extraction query
4. Transform to match target schema
5. Load incrementally (handle duplicates)
6. Validate row counts match
7. Schedule for recurring runs
8. Add quality checks
```

### Business Mode
```
User: "How are we doing this quarter?"

1. Identify relevant KPIs (revenue, users, churn)
2. Pull current values and trends
3. Compare to targets and prior period
4. Highlight wins and risks
5. Plain language summary, not jargon
6. One chart per key metric
7. Actionable recommendations
```

### Researcher Mode
```
User: "Is treatment group different from control?"

1. Load both group datasets
2. Check balance on covariates
3. Verify sample sizes adequate
4. Choose appropriate test
5. Check test assumptions
6. Run test, report p-value AND effect size
7. Interpret with confidence interval
8. Note limitations
```

### Developer Mode
```
User: "Generate TypeScript types from this API response"

1. Parse JSON response
2. Infer types from values
3. Handle optional fields (null values seen)
4. Generate interface definitions
5. Include JSDoc comments
6. Export as .d.ts file
```

## Common Workflows

### New Dataset Onboarding
```
Day 1: Schema discovery, sample data review
Day 2: Data quality assessment
Day 3: Clean and transform
Day 4: Build initial dashboards/queries
Day 5: Document and share with team
```

### Recurring Report Automation
```
1. Build report manually once
2. Parameterize dates and filters
3. Create data refresh script
4. Create chart generation script
5. Create delivery mechanism (email, Slack)
6. Schedule daily/weekly/monthly
7. Add alerting for failures
```

### Ad-Hoc Analysis Request
```
1. Clarify question and scope
2. Identify data sources needed
3. Quick EDA to understand data
4. Build analysis query/script
5. Generate visualizations
6. Write summary of findings
7. Share with requester
8. Save reusable components
```

### Data Migration
```
1. Inventory source data
2. Map source → target schema
3. Build transformation logic
4. Dry run on sample
5. Full migration to staging
6. Validate completeness and accuracy
7. Cutover to production
8. Deprecate old source
```

## Automation Patterns

### Incremental Loading
```python
# Track high watermark
last_loaded = get_last_watermark()
new_data = query(f"WHERE updated_at > '{last_loaded}'")
load(new_data)
set_watermark(new_data['updated_at'].max())
```

### Idempotent Writes
```python
# Delete + insert pattern
delete(target, where="date = '{date}'")
insert(target, data_for_date)
# Re-runnable without duplicates
```

### Monitoring Queries
```sql
-- Check data freshness
SELECT MAX(created_at), 
       NOW() - MAX(created_at) AS lag
FROM table;

-- Check volume
SELECT DATE(created_at), COUNT(*)
FROM table
GROUP BY 1
ORDER BY 1 DESC
LIMIT 7;
```

## Best Practices

### Code Organization
- One script/notebook per analysis
- Separate config from logic
- Version control everything
- Document dependencies (requirements.txt)
- Include README with purpose and usage

### Naming Conventions
- Files: `YYYYMMDD_analysis_name.py`
- Columns: snake_case, descriptive
- Variables: what it represents, not how computed
- Tables: singular nouns (user, order, event)

### Reproducibility
- Pin package versions
- Set random seeds
- Log parameters used
- Store raw data separately from derived
- Use relative paths
