---
name: Threat Modeling Expert
description: Expert in threat modeling methodologies, security architecture
  review, and risk assessment using STRIDE, PASTA, attack trees, and security
  requirement extraction.
---

# Threat Modeling Expert

Expert in threat modeling methodologies, security architecture review, and risk assessment using STRIDE, PASTA, attack trees, and security requirement extraction.

## Description

USE WHEN:
- Designing new systems or features (secure-by-design)
- Reviewing architecture for security gaps
- Preparing for security audits
- Identifying attack vectors and threat actors
- Prioritizing security investments
- Creating security documentation
- Training teams on security thinking

DON'T USE WHEN:
- Lack scope or authorization for security review
- Need legal compliance certification (consult legal)
- Only need automated scanning (use vulnerability-scanner)

---

## Core Process

### 1. Define Scope
- System boundaries
- Assets to protect
- Trust boundaries
- Regulatory requirements

### 2. Create Data Flow Diagram
```
[User] → [Web App] → [API Gateway] → [Backend] → [Database]
                ↓
          [External API]
```

### 3. Identify Assets & Entry Points
- **Assets**: User data, credentials, business logic, infrastructure
- **Entry Points**: APIs, forms, file uploads, admin panels

### 4. Apply STRIDE
- **S**poofing: Can someone impersonate?
- **T**ampering: Can data be modified?
- **R**epudiation: Can actions be denied?
- **I**nformation Disclosure: Can data leak?
- **D**enial of Service: Can availability be affected?
- **E**levation of Privilege: Can access be escalated?

### 5. Build Attack Trees
```
Goal: Access Admin Panel
├── Steal admin credentials
│   ├── Phishing
│   ├── Brute force
│   └── Session hijacking
├── Exploit vulnerability
│   ├── SQL injection
│   └── Auth bypass
└── Social engineering
    └── Support desk compromise
```

### 6. Score & Prioritize
Use DREAD or CVSS:
- **D**amage potential
- **R**eproducibility
- **E**xploitability
- **A**ffected users
- **D**iscoverability

### 7. Design Mitigations
Map threats to controls and validate coverage.

### 8. Document Residual Risks
What's accepted vs. mitigated.

---

## STRIDE Analysis Template

| Component | Spoofing | Tampering | Repudiation | Info Disclosure | DoS | EoP |
|-----------|----------|-----------|-------------|-----------------|-----|-----|
| Web App | Auth bypass | XSS, CSRF | Missing logs | Error messages | Rate limit | Broken access |
| API | Token theft | Input manip | No audit | Data exposure | Resource exhaust | Privilege escalation |
| Database | Credential theft | SQL injection | No audit trail | Backup exposure | Connection flood | Direct access |

---

## Threat Categories by Layer

### Application Layer
- Injection (SQL, XSS, command)
- Broken authentication
- Sensitive data exposure
- Broken access control
- Security misconfiguration
- Using vulnerable components

### Network Layer
- Man-in-the-middle
- Eavesdropping
- Replay attacks
- DNS spoofing
- DDoS

### Infrastructure Layer
- Unauthorized access
- Misconfigured services
- Unpatched systems
- Weak credentials
- Exposed admin interfaces

### Human Layer
- Phishing
- Social engineering
- Insider threats
- Credential sharing

---

## Data Flow Diagram Elements

| Element | Symbol | Description |
|---------|--------|-------------|
| External Entity | Rectangle | Users, external systems |
| Process | Circle | Application logic |
| Data Store | Parallel lines | Database, cache, files |
| Data Flow | Arrow | Data movement |
| Trust Boundary | Dashed line | Security perimeter |

---

## Risk Prioritization Matrix

```
              LOW IMPACT    HIGH IMPACT
HIGH LIKELIHOOD   MEDIUM        HIGH
LOW LIKELIHOOD    LOW           MEDIUM
```

### DREAD Scoring (1-10 each)

| Factor | Question |
|--------|----------|
| Damage | How bad if exploited? |
| Reproducibility | How easy to reproduce? |
| Exploitability | How easy to attack? |
| Affected Users | How many impacted? |
| Discoverability | How easy to find? |

**Score**: Sum / 5 = Risk Level

---

## Mitigation Strategies

### Input Validation
- Whitelist validation
- Parameterized queries
- Output encoding
- Content-Type enforcement

### Authentication
- MFA where possible
- Strong password policies
- Account lockout
- Secure session management

### Authorization
- Principle of least privilege
- Role-based access control
- Resource ownership checks
- Regular permission audits

### Cryptography
- TLS 1.2+ everywhere
- Strong key management
- Secure password hashing
- Encrypted data at rest

### Monitoring
- Security event logging
- Anomaly detection
- Alert thresholds
- Incident response plan

---

## Best Practices

1. **Involve developers** in threat modeling sessions
2. **Focus on data flows**, not just components
3. **Consider insider threats**
4. **Update models** with architecture changes
5. **Link threats** to security requirements
6. **Track mitigations** to implementation
7. **Review regularly**, not just at design time
8. **Keep models living documents**

---

## Output Template

```markdown
# Threat Model: [System Name]

## Scope
- Components in scope
- Out of scope

## Assets
- Critical assets list

## Trust Boundaries
- Internal vs external
- Admin vs user

## Data Flow Diagram
[DFD here]

## STRIDE Analysis
[Table here]

## Prioritized Threats
1. [High] Description - Mitigation
2. [Medium] Description - Mitigation

## Residual Risks
- Accepted risks with justification

## Review Schedule
- Next review date
```
