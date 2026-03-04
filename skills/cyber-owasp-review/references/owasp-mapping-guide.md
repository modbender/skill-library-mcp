# OWASP Mapping Guide

## Input Model

Each finding should include:
- `id`
- `title`
- `severity`

## Mapping Heuristics

- Access/authorization keywords map to `A01 Broken Access Control`.
- Injection keywords map to `A03 Injection`.
- Misconfiguration indicators map to `A05 Security Misconfiguration`.
- Outdated dependency indicators map to `A06 Vulnerable Components`.
- Logging/monitoring gaps map to `A09 Security Logging and Monitoring Failures`.

## Output Requirements

- Category counts
- Normalized finding rows
- Remediation checklist per category
