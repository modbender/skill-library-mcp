---
name: Enterprise
slug: enterprise
version: 1.0.0
description: Navigate enterprise software development with legacy integration, compliance requirements, stakeholder management, and architectural decisions at scale.
metadata: {"clawdbot":{"emoji":"🏢","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## When to Use

Working in corporate environments where decisions involve legacy systems, formal processes, compliance, multi-team coordination, or architectural trade-offs at scale.

## Quick Reference

| Topic | File |
|-------|------|
| Legacy patterns | `legacy.md` |
| Compliance rules | `compliance.md` |
| Architecture decisions | `architecture.md` |

## Core Rules

### 1. Legacy First Mindset
- Assume existing systems until proven otherwise
- Integration cost > development cost in most decisions
- "Replace vs wrap" analysis before any architecture change
- Document all integration points touched

### 2. Stakeholder Mapping
| Role | Cares About | Language |
|------|-------------|----------|
| Engineering | Technical debt, velocity | Patterns, trade-offs |
| Product | Features, timeline | User impact, scope |
| Security | Risk, compliance | Threat models, controls |
| Finance | Cost, ROI | TCO, licensing |
| Legal | Liability, data | Contracts, GDPR |

Translate technical decisions into each stakeholder's language.

### 3. Change Management
- No breaking changes without migration path
- Feature flags before hard switches
- Rollback plan for every deployment
- Document blast radius of failures

### 4. Compliance Awareness
- PCI, SOC2, HIPAA, GDPR implications in every data decision
- Audit trail requirements → logging design
- Data residency affects architecture
- Ask: "Who audits this? What do they need?"

### 5. Documentation as Deliverable
Enterprise code without docs = technical debt.
- ADRs (Architecture Decision Records) for major choices
- Runbooks for operations
- API contracts before implementation
- Dependency graphs updated with changes

### 6. Security by Default
- Principle of least privilege in all designs
- Secrets in vault, never in code or config files
- Network segmentation assumptions
- Zero trust between services

### 7. Observability Investment
- Logging, metrics, tracing from day one
- Correlation IDs across service boundaries
- SLI/SLO definitions before launch
- Alert fatigue is a system design failure

## Enterprise Traps

- Assuming greenfield when there's always legacy → scope explosion
- Optimizing for developer experience over ops burden → 3am pages
- Skipping security review for "internal tools" → breach vector
- Building before buying → reinventing solved problems
- Over-abstracting early → framework nobody understands
- Under-documenting decisions → knowledge silos
