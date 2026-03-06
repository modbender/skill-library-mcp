# Analytics and BI Platforms

## Platform Selection Criteria

| Criterion | Questions |
|-----------|-----------|
| **Scale** | How many users? Data volume? Query complexity? |
| **Self-service** | Can business users build their own reports? |
| **Governance** | Row-level security? Certification? Usage tracking? |
| **Integration** | Connects to your data stack? Embedding options? |
| **Cost model** | Per-user, per-query, or capacity-based? |
| **Semantic layer** | Built-in metrics layer or external (dbt, Cube)? |

## Platform Comparison

| Platform | Strengths | Best For |
|----------|-----------|----------|
| **Looker** | Semantic layer, governance | Enterprise, embedded analytics |
| **Tableau** | Visualization depth, community | Analyst-heavy teams |
| **Power BI** | Microsoft integration, cost | Microsoft shops |
| **Metabase** | Simple, open source option | Startups, internal tools |
| **Superset** | Open source, customizable | Technical teams |
| **Sigma** | Spreadsheet UX, cloud-native | Finance, self-service |

## Semantic Layer Strategy

### Why Semantic Layer Matters
- Single definition of metrics
- Business users get consistent numbers
- Reduces "my numbers don't match yours"
- Enables true self-service

### Options
- **In-BI tool** — Looker LookML, Tableau data models
- **Standalone** — dbt Semantic Layer, Cube.dev, Metricflow
- **Data platform** — Databricks Unity Catalog, Snowflake metrics

## Dashboard Standards

### Layout Principles
- Key metrics at top (KPIs)
- Filters clearly visible
- Drill-down paths obvious
- Mobile-friendly design

### Performance Guidelines
- Load time < 5 seconds
- No more than 10 visuals per dashboard
- Pre-aggregate when possible
- Cache hot dashboards

### Governance Rules
- Certified vs exploratory clearly marked
- Owner and last updated visible
- Deprecation process defined
- Naming conventions enforced
