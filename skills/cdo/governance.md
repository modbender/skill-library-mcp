# Data Governance and Quality

## Governance Operating Model

### Roles

| Role | Responsibility |
|------|----------------|
| **Data Owner** | Business leader accountable for data domain |
| **Data Steward** | Day-to-day quality and standards enforcement |
| **Data Custodian** | Technical implementation and access control |
| **Data Governance Council** | Cross-functional body for policy decisions |

### Policy Areas

1. **Data Classification** — Public, internal, confidential, restricted
2. **Access Control** — Role-based, need-to-know, audit trails
3. **Retention** — How long, where stored, deletion procedures
4. **Quality Standards** — Completeness, accuracy, timeliness thresholds
5. **Lineage** — Source tracking, transformation documentation

## Data Quality Dimensions

| Dimension | Definition | Measurement |
|-----------|------------|-------------|
| **Completeness** | No missing required values | % fields populated |
| **Accuracy** | Values reflect reality | Error rate on validation |
| **Consistency** | Same data, same meaning everywhere | Cross-system match rate |
| **Timeliness** | Data available when needed | Freshness lag |
| **Uniqueness** | No unintended duplicates | Duplicate detection rate |
| **Validity** | Values conform to rules | Rule violation count |

## Data Catalog Requirements

- Automated schema discovery
- Business glossary integration
- Lineage visualization
- Usage analytics
- Access request workflow
- Data quality scores displayed
- Search across all assets

## Governance Implementation Phases

### Phase 1: Foundation (0-6 months)
- Identify critical data domains
- Assign initial owners
- Basic classification
- Catalog deployment

### Phase 2: Operationalize (6-12 months)
- Quality monitoring automated
- Stewardship workflows
- Lineage documentation
- Training programs

### Phase 3: Mature (12-24 months)
- Self-service data marketplace
- Automated policy enforcement
- Metrics-driven governance
- Continuous improvement cycle
