# Vendor Security Assessment

## Vendor Risk Tiers

| Tier | Criteria | Assessment Level |
|------|----------|------------------|
| **Critical** | Access to sensitive data, core infrastructure | Full assessment + annual review |
| **High** | Access to internal systems, some sensitive data | Questionnaire + SOC 2 review |
| **Medium** | Limited system access, business data | Questionnaire |
| **Low** | No data access, commodity service | Basic due diligence |

## Vendor Assessment Process

### 1. Initial Screening

**Basic Due Diligence**
- [ ] Company registration verified
- [ ] Years in business
- [ ] Financial stability (if applicable)
- [ ] Public breach history
- [ ] Industry reputation

### 2. Security Questionnaire

**Infrastructure Security**
- How is customer data stored and encrypted?
- What cloud provider/data centers are used?
- What is your patch management process?
- How is access to production systems controlled?

**Access Controls**
- How do you manage employee access to customer data?
- Do you enforce MFA for all employees?
- What is your offboarding process?
- Do you perform background checks?

**Incident Response**
- Do you have a documented incident response plan?
- What is your breach notification timeline?
- Have you had any security incidents in the past 3 years?

**Compliance**
- What compliance certifications do you hold?
- When was your last SOC 2 audit?
- Are you GDPR compliant?
- Can you sign a DPA?

**Business Continuity**
- What is your uptime SLA?
- How often do you test backups?
- What is your disaster recovery RTO/RPO?

### 3. Documentation Review

**SOC 2 Report Review Checklist**
- [ ] Report type (I vs II) and period
- [ ] Trust service criteria covered
- [ ] Any exceptions noted?
- [ ] Opinion from auditor (unqualified?)
- [ ] Complementary user entity controls (CUECs)
- [ ] Subservice organizations used

**Red Flags in SOC 2 Reports**
- Qualified opinion
- Significant exceptions
- Missing controls for your data type
- Incomplete control descriptions
- Old report (>1 year)

### 4. Ongoing Monitoring

**Annual Review**
- [ ] Request updated SOC 2 report
- [ ] Review any incidents/changes
- [ ] Validate compliance status
- [ ] Check news for breaches

**Continuous Monitoring**
- Security rating services (BitSight, SecurityScorecard)
- Breach notification alerts
- Contract compliance tracking

## Vendor Security Requirements

### Data Processing Agreement (DPA) Requirements

- [ ] Clear data processing purposes
- [ ] Subprocessor notification requirements
- [ ] Audit rights
- [ ] Data deletion upon termination
- [ ] Breach notification timeline
- [ ] Data transfer mechanisms

### Contract Security Clauses

```
SECURITY REQUIREMENTS
1. Vendor shall maintain [SOC 2 Type II / ISO 27001] certification
2. Vendor shall notify Customer of security incidents within [24/48/72] hours
3. Vendor shall encrypt all Customer data at rest and in transit
4. Vendor shall perform annual penetration testing
5. Customer may audit Vendor's security controls with [30] days notice
6. Vendor shall maintain cyber liability insurance of at least [$X]
```

## Vendor Risk Register

| Vendor | Tier | Data Access | Last Review | SOC 2 Exp | Issues | Owner |
|--------|------|-------------|-------------|-----------|--------|-------|
| Example Co | Critical | PII | 2024-01 | 2024-06 | None | Security |
| Acme SaaS | High | Business | 2024-03 | 2024-12 | 1 medium | IT |

## Vendor Termination Checklist

- [ ] Data return/deletion confirmed in writing
- [ ] Access credentials revoked
- [ ] SSO/OAuth integrations removed
- [ ] DNS/network connections removed
- [ ] API keys rotated
- [ ] Data deletion certificate obtained
- [ ] Contract termination documented
