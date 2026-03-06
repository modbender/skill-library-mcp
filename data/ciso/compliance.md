# Compliance Frameworks

## SOC 2

### Trust Service Criteria

| Category | Focus |
|----------|-------|
| **Security** | Protection against unauthorized access |
| **Availability** | System availability for operation |
| **Processing Integrity** | System processing is complete and accurate |
| **Confidentiality** | Information designated confidential is protected |
| **Privacy** | Personal information handling |

### SOC 2 Type I vs Type II

| Type | What it covers | Timeline |
|------|----------------|----------|
| **Type I** | Controls design at a point in time | Snapshot |
| **Type II** | Controls operating effectiveness over time | 6-12 months |

### Evidence Collection Checklist

**Security**
- [ ] Access control policy
- [ ] User provisioning/deprovisioning records
- [ ] MFA enrollment evidence
- [ ] Firewall configuration
- [ ] Encryption configuration
- [ ] Penetration test results
- [ ] Vulnerability scan reports

**Availability**
- [ ] Uptime metrics/SLA reports
- [ ] Incident response records
- [ ] Backup verification tests
- [ ] Disaster recovery test results
- [ ] Capacity monitoring

**Confidentiality**
- [ ] Data classification policy
- [ ] Encryption evidence
- [ ] Access logs
- [ ] NDA templates

### Common SOC 2 Gaps

| Gap | Fix |
|-----|-----|
| No formal security policy | Draft and approve policy document |
| Missing access reviews | Implement quarterly access reviews |
| No background checks | Add to hiring process |
| Incomplete offboarding | Create offboarding checklist with IT |
| No penetration testing | Schedule annual pentest |
| Missing vendor assessment | Create vendor security questionnaire |

## GDPR

### Key Requirements

| Requirement | Implementation |
|-------------|----------------|
| **Lawful basis** | Document legal basis for each data processing |
| **Data minimization** | Only collect what's necessary |
| **Purpose limitation** | Use data only for stated purposes |
| **Storage limitation** | Define and enforce retention periods |
| **Right to access** | Process for users to request their data |
| **Right to deletion** | Process for users to request deletion |
| **Data portability** | Export user data in standard format |
| **Breach notification** | 72-hour notification process |

### Data Mapping Template

```
DATA ELEMENT: [Name]
- Category: Personal / Sensitive
- Source: [How collected]
- Purpose: [Why collected]
- Legal basis: [Consent / Contract / Legitimate interest]
- Storage location: [Where stored]
- Retention period: [How long kept]
- Access: [Who can access]
- Transfers: [Any cross-border transfers]
- Deletion process: [How deleted]
```

### GDPR Compliance Checklist

- [ ] Privacy policy updated and accessible
- [ ] Cookie consent mechanism
- [ ] Data processing records maintained
- [ ] DPA signed with all processors
- [ ] Data subject request process
- [ ] Breach response procedure
- [ ] DPIA for high-risk processing
- [ ] DPO appointed (if required)

## ISO 27001

### Core Domains

| Domain | Focus Area |
|--------|------------|
| Information security policies | Policy documents |
| Organization of information security | Roles and responsibilities |
| Human resource security | Hiring, training, termination |
| Asset management | Inventory, classification |
| Access control | Authentication, authorization |
| Cryptography | Encryption policies |
| Physical security | Data centers, offices |
| Operations security | Change management, monitoring |
| Communications security | Network security |
| System acquisition | Secure development |
| Supplier relationships | Third-party security |
| Incident management | Response procedures |
| Business continuity | DR/BCP planning |
| Compliance | Legal and regulatory |

### Statement of Applicability

Document which controls apply and why others don't:

| Control | Applicable | Justification |
|---------|------------|---------------|
| A.8.1 Asset inventory | Yes | Required for all assets |
| A.11.1 Physical security | Partial | Cloud-only, no physical DC |

## HIPAA

### Key Safeguards

**Administrative**
- Risk assessment
- Workforce training
- Contingency planning
- Business associate agreements

**Physical**
- Facility access controls
- Workstation security
- Device controls

**Technical**
- Access controls
- Audit controls
- Integrity controls
- Transmission security

### PHI Handling Rules

- [ ] Access limited to minimum necessary
- [ ] Encryption at rest and in transit
- [ ] Audit logging for all PHI access
- [ ] BAA signed with all vendors handling PHI
- [ ] Breach notification process (60 days)
