# Competitive Intelligence Research Patterns

This reference provides common search patterns and workflows for competitive intelligence research.

## Feature Comparison Searches

### Finding Feature Support

```bash
# Does competitor support X?
scripts/search_docs.py ./docs "<feature_name>" --full

# Compare multiple features
scripts/search_docs.py ./docs "snapshot" --max-results 20
scripts/search_docs.py ./docs "incremental" --max-results 20
```

### Finding Limitations

```bash
# Search for limitation language patterns
scripts/search_docs.py ./docs "not supported\|not available\|limitation" --mode regex

# Maximum values (scale limits)
scripts/search_docs.py ./docs "maximum\|max\s+\d+\|limit\s+\d+" --mode regex

# Prerequisites and requirements
scripts/search_docs.py ./docs "require\|prerequisite\|must have" --max-results 15
```

### Version-Specific Information

```bash
# Find version-specific docs
scripts/search_docs.py ./docs "version\s+11\." --mode regex

# What's new / changelog
scripts/search_docs.py ./docs "what's new\|release notes\|new in" --mode regex
```

## Architecture & Deployment

### Cloud Provider Support

```bash
# AWS
scripts/search_docs.py ./docs "AWS\|Amazon\|EC2\|S3" --mode regex --max-results 20

# Azure
scripts/search_docs.py ./docs "Azure\|Microsoft Cloud" --mode regex --max-results 20

# GCP
scripts/search_docs.py ./docs "GCP\|Google Cloud\|Google Kubernetes" --mode regex

# Multi-cloud
scripts/search_docs.py ./docs "multi.?cloud\|hybrid" --mode regex
```

### Kubernetes & Containers

```bash
scripts/search_docs.py ./docs "kubernetes\|k8s\|container" --mode regex --max-results 20

# Specific K8s features
scripts/search_docs.py ./docs "namespace\|persistent volume\|statefulset" --mode regex
```

### Database Support

```bash
# SQL databases
scripts/search_docs.py ./docs "SQL Server\|PostgreSQL\|MySQL\|Oracle" --mode regex

# NoSQL
scripts/search_docs.py ./docs "MongoDB\|Cassandra\|Couchbase" --mode regex
```

## Security & Compliance

### Security Features

```bash
scripts/search_docs.py ./docs "encryption\|RBAC\|authentication\|MFA" --mode regex

# Ransomware
scripts/search_docs.py ./docs "ransomware\|immutable\|air.?gap" --mode regex
```

### Compliance Certifications

```bash
scripts/search_docs.py ./docs "SOC\s*2\|ISO\s*27001\|GDPR\|HIPAA\|FedRAMP" --mode regex
```

## Licensing & Pricing Clues

```bash
# License types
scripts/search_docs.py ./docs "license\|licensing\|subscription" --max-results 15

# Capacity limits
scripts/search_docs.py ./docs "capacity\|TB\s+limit\|per\s+TB" --mode regex
```

## Integration & APIs

```bash
scripts/search_docs.py ./docs "API\|REST\|Webhook\|integration" --mode regex

# Specific integrations
scripts/search_docs.py ./docs "ServiceNow\|Terraform\|Ansible\|vCenter" --mode regex
```

## Reporting Findings

When documenting findings, use this structure:

```markdown
## [Topic] Research

### Key Findings
- Finding 1 with citation
- Finding 2 with citation

### Capabilities
- [x] Supported feature (Source: URL)
- [ ] Not mentioned/found

### Limitations
- Limitation 1 (Source: URL)

### Sources
1. Article Title - https://docs.vendor.com/path
2. Article Title - https://docs.vendor.com/path
```

## Cross-Reference Pattern

When comparing multiple competitors:

```bash
# Run same search across different doc sets
scripts/search_docs.py ./CommvaultDocs "kubernetes backup" --json > k8s_commvault.json
scripts/search_docs.py ./DattoDocs "kubernetes backup" --json > k8s_datto.json

# Then compare results programmatically or manually
```