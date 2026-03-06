# Vendor Security Assessments

## Vendor Risk Tiers

| Tier | Criteria | Assessment Required |
|------|----------|---------------------|
| **Critical** | Access to production data, handles PII/PHI, infrastructure provider | Full assessment + annual review |
| **High** | Access to internal systems, processes business data | Standard assessment + annual review |
| **Medium** | Limited system access, no sensitive data | Lightweight assessment |
| **Low** | No data access, commodity service | Basic checks only |

## Quick Assessment Checklist

### Security Basics
- [ ] SOC 2 Type II report (current, < 12 months old)
- [ ] ISO 27001 certification (if claiming)
- [ ] Privacy policy published
- [ ] Security page/documentation available
- [ ] Bug bounty or responsible disclosure program

### Data Handling
- [ ] Data encryption at rest
- [ ] Data encryption in transit (TLS)
- [ ] Data residency options (if GDPR relevant)
- [ ] Data retention and deletion policies
- [ ] Subprocessor list available

### Access Control
- [ ] SSO/SAML support
- [ ] MFA available/required
- [ ] Role-based access control
- [ ] Audit logging of admin actions

### Incident Response
- [ ] Breach notification commitment (< 72 hours for GDPR)
- [ ] Incident response plan documented
- [ ] SLA for security issues

## Red Flags

🚩 **Immediate Concerns**:
- No SOC 2 and won't commit to timeline
- No encryption at rest
- No MFA option
- Shared credentials required
- No audit logging
- Can't provide subprocessor list
- Recent breach with poor response

⚠️ **Yellow Flags (dig deeper)**:
- SOC 2 Type I only (no Type II)
- New company (< 2 years)
- Single founder/maintainer
- No security page
- Generic privacy policy
- Slow response to security questions

## Security Questionnaire Response

When vendors send you questionnaires (SIG, CAIQ, custom):

### Efficient Response Strategy
1. **Maintain a master document** with pre-written answers
2. **Map to SOC 2 controls** — most questions map to existing controls
3. **Reference evidence** rather than re-explaining
4. **Use conditional answers** — "We do X when Y applies"
5. **Know your boundaries** — what applies vs. customer responsibility

### Common Question Categories
- Physical security (data centers)
- Network security (firewalls, segmentation)
- Application security (SDLC, testing)
- Data protection (encryption, classification)
- Access control (authentication, authorization)
- Incident management (response, notification)
- Business continuity (backups, DR)
- Compliance (certifications, audits)

## Contract Security Clauses

### Must-Have Clauses
- **Data processing agreement** (DPA) for GDPR
- **Breach notification timeline** (72 hours max)
- **Right to audit** or audit report provision
- **Data deletion upon termination**
- **Subprocessor approval rights**
- **Security incident notification**

### Nice-to-Have Clauses
- Penetration test report sharing
- Vulnerability disclosure
- Insurance requirements
- Background check requirements
- Specific encryption standards

## Vendor Review Cadence

| Tier | Initial | Ongoing |
|------|---------|---------|
| Critical | Full assessment | Annual review + continuous monitoring |
| High | Standard assessment | Annual review |
| Medium | Lightweight assessment | Biennial review |
| Low | Basic checks | Review on renewal |

## Integration Security Review

Before connecting a new vendor to your systems:

### Data Flow Documentation
- What data goes to vendor?
- What data comes back?
- How is data transmitted?
- Where is data stored?
- Who can access data at vendor?

### Permission Audit
- What OAuth scopes requested?
- Are all permissions necessary?
- Can permissions be reduced?
- Is there a service account option?

### Disconnection Plan
- How to revoke access quickly?
- How to export data before disconnection?
- What happens to data after disconnection?
