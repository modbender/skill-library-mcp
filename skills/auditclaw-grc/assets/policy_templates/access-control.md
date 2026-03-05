# Access Control Policy

**Version:** {{VERSION}}
**Effective Date:** {{EFFECTIVE_DATE}}
**Last Reviewed:** {{REVIEW_DATE}}
**Owner:** {{POLICY_OWNER}}
**Classification:** {{CLASSIFICATION}}

---

## 1. Purpose

This policy establishes requirements for controlling access to {{ORGANIZATION_NAME}}'s information systems, applications, and data. It ensures that access is granted based on business need, least privilege, and proper authorization.

**Related Controls:** A9.1.1, A9.2.1–A9.4.5, CC6.1, CC6.2, CC6.3

---

## 2. Scope

This policy applies to:
- All information systems, applications, databases, and network resources
- All users including employees, contractors, vendors, and temporary staff
- All access methods including local, remote, API, and service accounts
- Cloud services and third-party systems used for business purposes

---

## 3. Access Control Principles

1. **Least Privilege:** Users receive only the minimum access necessary for their role
2. **Need-to-Know:** Access to information is restricted to those who require it
3. **Separation of Duties:** Critical functions divided to prevent fraud or error
4. **Default Deny:** Access is denied unless explicitly granted
5. **Defense in Depth:** Multiple layers of access controls

---

## 4. Authentication Requirements

### Password Requirements

| Requirement | Standard |
|-------------|----------|
| Minimum length | {{MIN_PASSWORD_LENGTH}} characters |
| Complexity | Mix of uppercase, lowercase, numbers, and symbols |
| Maximum age | {{PASSWORD_MAX_AGE}} days |
| History | Last {{PASSWORD_HISTORY}} passwords cannot be reused |
| Lockout | After {{LOCKOUT_ATTEMPTS}} failed attempts |
| Lockout duration | {{LOCKOUT_DURATION}} minutes |

### Multi-Factor Authentication (MFA)

MFA is **required** for:
- All remote access connections
- Administrative and privileged accounts
- Access to systems containing Restricted or Confidential data
- Cloud management consoles
- Source code repositories with production access

MFA is **recommended** for:
- All user accounts (organization-wide)
- Email access from untrusted devices

### Service Accounts
- Service accounts must use strong, unique credentials
- Credentials stored in approved secrets management systems (not in code)
- Service accounts reviewed {{SERVICE_ACCOUNT_REVIEW_FREQUENCY}}
- Interactive login disabled where possible

---

## 5. Authorization and Provisioning

### Access Request Process

1. User or manager submits access request via {{ACCESS_REQUEST_SYSTEM}}
2. Data/system owner reviews and approves based on business need
3. IT provisions access according to approved request
4. User acknowledges access policies and responsibilities
5. Access logged in central access management system

### Role-Based Access Control (RBAC)

| Role Category | Description | Approval Required |
|---------------|-------------|-------------------|
| Standard User | Basic business application access | Manager |
| Power User | Extended application features | Manager + System Owner |
| Developer | Development and staging environments | Manager + Tech Lead |
| Administrator | System/infrastructure administration | Manager + CISO |
| Emergency Access | Break-glass for critical situations | CISO + documented justification |

---

## 6. Access Reviews

| Review Type | Frequency | Scope | Reviewer |
|-------------|-----------|-------|----------|
| User access recertification | {{ACCESS_REVIEW_FREQUENCY}} | All user accounts | System/Data Owners |
| Privileged access review | {{PRIV_ACCESS_REVIEW_FREQUENCY}} | All admin/elevated accounts | CISO + System Owners |
| Service account review | {{SERVICE_ACCOUNT_REVIEW_FREQUENCY}} | All non-human accounts | IT Operations + Owners |
| Orphaned account cleanup | Monthly | Accounts without active owners | IT Operations |
| Third-party access review | {{VENDOR_REVIEW_FREQUENCY}} | All vendor/contractor access | Vendor Manager + CISO |

### Review Process
1. Generate access report for review scope
2. Owner reviews each access grant for continued need
3. Unnecessary access flagged for removal
4. IT removes flagged access within {{REMOVAL_SLA}} business days
5. Review completion documented and retained

---

## 7. Privileged Access Management

- Privileged accounts maintained separately from standard user accounts
- Just-in-time (JIT) access preferred over standing privileges
- All privileged sessions logged and monitored
- Privileged access requires explicit business justification
- Emergency (break-glass) access:
  - Requires post-use justification within {{BREAKGLASS_JUSTIFICATION_HOURS}} hours
  - All actions during emergency access logged
  - Reviewed by CISO within {{BREAKGLASS_REVIEW_HOURS}} hours

---

## 8. Remote Access

- Remote access only through approved channels (VPN, zero-trust proxy)
- MFA required for all remote connections
- Split tunneling {{SPLIT_TUNNEL_POLICY}} (allowed/prohibited)
- Remote devices must meet minimum security requirements:
  - [ ] Operating system up to date
  - [ ] Endpoint protection active
  - [ ] Disk encryption enabled
  - [ ] Screen lock configured
- Remote access monitored and logged

---

## 9. Access Removal and Offboarding

### Triggers for Access Removal
- Employment termination (voluntary or involuntary)
- Contract completion
- Role change (adjust access within {{ROLE_CHANGE_SLA}} business days)
- Extended leave (disable after {{LEAVE_DISABLE_DAYS}} days)
- Account inactivity (disable after {{INACTIVE_DISABLE_DAYS}} days)

### Termination Process
- Involuntary termination: Access disabled **immediately** upon notification
- Voluntary termination: Access disabled on last working day
- Shared credentials rotated upon departure of any user with access
- Return of all organizational devices and access tokens

---

## 10. Account Types and Standards

| Account Type | Naming Convention | MFA | Expiry | Monitoring |
|--------------|-------------------|-----|--------|------------|
| Employee | {{EMPLOYEE_FORMAT}} | Required | None (active employment) | Standard |
| Contractor | {{CONTRACTOR_FORMAT}} | Required | Contract end date | Enhanced |
| Service | svc-{{SERVICE_FORMAT}} | N/A (no interactive) | Annual review | Enhanced |
| Admin | adm-{{ADMIN_FORMAT}} | Required | Annual recertification | Full logging |
| Emergency | brk-{{BREAKGLASS_FORMAT}} | Required | Single use | Full logging + alert |

---

## 11. Monitoring and Logging

Access-related events that **must** be logged:
- Successful and failed authentication attempts
- Account creation, modification, and deletion
- Privilege escalation events
- Access to Restricted data
- Administrative actions

Logs retained for minimum {{LOG_RETENTION_PERIOD}} and protected from tampering.

---

## 12. Violations and Enforcement

| Violation | Response |
|-----------|----------|
| Sharing credentials | Immediate password reset, written warning |
| Unauthorized access attempt | Account suspended, investigation |
| Circumventing access controls | Account suspended, disciplinary action |
| Failure to complete access review | Escalation to management |

---

## 13. Review and Maintenance

- This policy reviewed {{REVIEW_FREQUENCY}} or after significant security events
- Changes require approval from CISO and Executive Management
- All employees notified of policy changes

---

**Approval:**

| Role | Name | Signature | Date |
|------|------|-----------|------|
| CISO / Security Lead | {{CISO_NAME}} | | |
| IT Director | {{IT_DIRECTOR_NAME}} | | |
| HR Director | {{HR_DIRECTOR_NAME}} | | |
