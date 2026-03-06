# Compliance Framework Reference

## SOC 2 Overview

### Trust Service Criteria
| Category | Focus |
|----------|-------|
| Security | Protection against unauthorized access |
| Availability | System uptime and recovery |
| Processing Integrity | Accurate and complete processing |
| Confidentiality | Data protection |
| Privacy | Personal information handling |

### SOC 2 Type I vs Type II
- **Type I**: Point-in-time assessment of control design
- **Type II**: Assessment over 3-12 months of control effectiveness

### Common SOC 2 Evidence
- Access control lists and reviews
- Change management logs (PR approvals)
- Vulnerability scan reports
- Penetration test results
- Security training records
- Incident response documentation
- Backup verification tests
- MFA enrollment reports

## GDPR Compliance

### Key Requirements
1. **Lawful basis** for processing personal data
2. **Data minimization** — collect only what's needed
3. **Purpose limitation** — use data only for stated purposes
4. **Storage limitation** — delete when no longer needed
5. **Data subject rights** — access, rectification, erasure, portability
6. **Breach notification** — 72 hours to supervisory authority

### Required Documentation
- Privacy policy (public)
- Data processing records (Article 30)
- Data protection impact assessments (DPIA)
- Data processing agreements with vendors
- Breach response procedures

### Technical Controls for GDPR
- Encryption at rest and in transit
- Access controls and audit logs
- Data retention automation
- Consent management
- Right to erasure implementation

## ISO 27001

### Key Control Domains
- Information security policies
- Organization of information security
- Human resource security
- Asset management
- Access control
- Cryptography
- Physical security
- Operations security
- Communications security
- System acquisition and development
- Supplier relationships
- Incident management
- Business continuity
- Compliance

## PCI-DSS (Payment Card)

### Key Requirements
1. Install and maintain firewall
2. No vendor-supplied default passwords
3. Protect stored cardholder data
4. Encrypt transmission of cardholder data
5. Use and update antivirus
6. Develop secure systems
7. Restrict access to cardholder data
8. Assign unique ID to each user
9. Restrict physical access
10. Track and monitor network access
11. Test security systems regularly
12. Maintain security policy

## HIPAA (Healthcare)

### Administrative Safeguards
- Security officer designation
- Workforce security training
- Access management
- Security incident procedures
- Contingency planning

### Technical Safeguards
- Access controls
- Audit controls
- Integrity controls
- Transmission security

### Physical Safeguards
- Facility access controls
- Workstation security
- Device and media controls

## Compliance Calendar Template

| Month | SOC 2 | GDPR | Other |
|-------|-------|------|-------|
| Jan | Q4 evidence review | DPIA review | Security training kickoff |
| Feb | Penetration test | Data mapping update | |
| Mar | Access review | Privacy policy review | |
| Apr | Q1 evidence collection | DPA renewals | |
| May | Vulnerability scan | | |
| Jun | Security training check | Data retention audit | Mid-year audit prep |
| Jul | Q2 evidence collection | | |
| Aug | Vendor assessments | | |
| Sep | Access review | Consent audit | |
| Oct | Q3 evidence collection | DPIA review | |
| Nov | Policy reviews | | Audit prep |
| Dec | Year-end evidence | Year-end cleanup | Compliance report |
