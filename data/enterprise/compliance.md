# Compliance — Enterprise

## Quick Reference

| Framework | Scope | Key Requirements |
|-----------|-------|------------------|
| SOC 2 | Service orgs | Access control, encryption, monitoring |
| PCI DSS | Payment data | Network segmentation, encryption, audit |
| HIPAA | Health data | Access logs, encryption, BAAs |
| GDPR | EU personal data | Consent, deletion, portability |
| SOX | Public companies | Financial controls, audit trails |

## Design Implications

### Data Classification
Before building, classify data:

| Level | Examples | Requirements |
|-------|----------|--------------|
| Public | Marketing content | None |
| Internal | Employee docs | Authentication |
| Confidential | Customer data | Encryption, audit |
| Restricted | PII, PHI, PCI | All controls, DLP |

### Audit Trail Requirements
Every compliance framework needs:
- Who (authenticated identity)
- What (action performed)
- When (timestamp, timezone)
- Where (source IP, service)
- Result (success/failure)

### Data Residency
GDPR, China, Russia have data localization rules.

```
Before: [Single Global DB]
After:  [EU DB] [US DB] [APAC DB] + routing layer
```

## Common Mistakes

- Logging PII in plaintext → compliance violation
- No retention policy → storing data forever
- Assuming "internal" means "no compliance" → wrong
- Consent buried in ToS → GDPR violation
- Audit logs deletable → defeats purpose
