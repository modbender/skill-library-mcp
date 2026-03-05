# Documentation Search Patterns

This reference provides common search patterns for documentation research.

## Feature Research

### Finding Feature Support

```bash
# Does the product support X?
docs.py search "<feature_name>" --max 10

# Compare multiple features
docs.py search "snapshot OR incremental"
docs.py search "backup AND restore"
```

### Finding Limitations

```bash
# Search for limitation language patterns
docs.py search "not supported OR limitation OR restriction"

# Maximum values (scale limits)
docs.py search "maximum OR limit"

# Prerequisites and requirements
docs.py search "requirement OR prerequisite"
```

### Version-Specific Information

```bash
# Find version-specific docs
docs.py search '"version 11"'

# What's new / changelog
docs.py search "release notes OR \"what's new\""
```

## Architecture & Deployment

### Cloud Provider Support

```bash
# AWS
docs.py search "AWS OR Amazon OR EC2 OR S3"

# Azure
docs.py search "Azure"

# GCP
docs.py search "GCP OR \"Google Cloud\""

# Multi-cloud
docs.py search "multi-cloud OR hybrid"
```

### Kubernetes & Containers

```bash
docs.py search "kubernetes OR k8s OR container"

# Specific K8s features
docs.py search "namespace OR \"persistent volume\""
```

### Database Support

```bash
# SQL databases
docs.py search "PostgreSQL OR MySQL OR Oracle"

# NoSQL
docs.py search "MongoDB OR Cassandra"
```

## Security & Compliance

### Security Features

```bash
docs.py search "encryption OR RBAC OR authentication"

# Ransomware protection
docs.py search "ransomware OR immutable OR \"air gap\""
```

### Compliance Certifications

```bash
docs.py search "SOC OR ISO OR GDPR OR HIPAA"
```

## Licensing & Pricing

```bash
# License types
docs.py search "license OR licensing OR subscription"

# Capacity limits
docs.py search "capacity OR TB"
```

## Integration & APIs

```bash
docs.py search "API OR REST OR Webhook"

# Specific integrations
docs.py search "Terraform OR Ansible OR vCenter"
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
1. Article Title - https://docs.example.com/path
2. Article Title - https://docs.example.com/path
```

## Cross-Reference Pattern

When comparing multiple documentation sources:

```bash
# Run same search across different doc sets
cd ~/docs/VendorA && docs.py search "kubernetes backup" --json > results_a.json
cd ~/docs/VendorB && docs.py search "kubernetes backup" --json > results_b.json

# Then compare results programmatically or manually
```