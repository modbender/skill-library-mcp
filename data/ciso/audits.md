# Infrastructure Security Audits

## Cloud Configuration Audit

### AWS Security Checklist

**IAM**
- [ ] Root account has MFA enabled
- [ ] Root account has no access keys
- [ ] IAM users have MFA enabled
- [ ] No inline policies (use managed policies)
- [ ] Password policy enforces complexity
- [ ] Unused credentials removed (90+ days)
- [ ] Cross-account access reviewed

**S3**
- [ ] No public buckets (unless intentional)
- [ ] Bucket policies reviewed
- [ ] Encryption at rest enabled
- [ ] Versioning enabled for critical data
- [ ] Access logging enabled
- [ ] Block public access settings enabled

**Network**
- [ ] Security groups follow least privilege
- [ ] No 0.0.0.0/0 on SSH/RDP
- [ ] VPC flow logs enabled
- [ ] Default VPC not used for production
- [ ] Network ACLs reviewed

**Compute**
- [ ] EC2 instances use IAM roles, not keys
- [ ] IMDSv2 required (no IMDSv1)
- [ ] EBS volumes encrypted
- [ ] Patch management in place

**Monitoring**
- [ ] CloudTrail enabled (all regions)
- [ ] CloudTrail logs sent to S3 + CloudWatch
- [ ] GuardDuty enabled
- [ ] Config rules active

### GCP Security Checklist

**IAM**
- [ ] Organization-level policies set
- [ ] No primitive roles (Owner/Editor) in production
- [ ] Service accounts follow least privilege
- [ ] No user-managed service account keys
- [ ] Domain-restricted sharing enabled

**Storage**
- [ ] No public buckets
- [ ] Uniform bucket-level access enabled
- [ ] Encryption with CMEK where required

**Network**
- [ ] Firewall rules reviewed
- [ ] VPC flow logs enabled
- [ ] Private Google Access enabled
- [ ] Cloud NAT for egress

### Docker/Kubernetes Audit

**Images**
- [ ] Base images from trusted registries
- [ ] No latest tag in production
- [ ] Vulnerability scanning in CI/CD
- [ ] Images signed

**Runtime**
- [ ] No root containers
- [ ] Read-only root filesystem
- [ ] Resource limits set
- [ ] No privileged mode
- [ ] Security contexts defined

**Kubernetes**
- [ ] RBAC enabled and reviewed
- [ ] Network policies in place
- [ ] Pod security standards enforced
- [ ] Secrets encrypted at rest
- [ ] Audit logging enabled
- [ ] No default namespace for workloads

## Application Security Audit

### Authentication
- [ ] Strong password policy enforced
- [ ] MFA available and encouraged
- [ ] Session timeout configured
- [ ] Secure password reset flow
- [ ] Account lockout after failed attempts
- [ ] OAuth/OIDC configured correctly

### Authorization
- [ ] Role-based access control implemented
- [ ] Principle of least privilege
- [ ] Direct object reference protection
- [ ] API authorization on all endpoints

### Data Protection
- [ ] Encryption in transit (TLS 1.2+)
- [ ] Encryption at rest for sensitive data
- [ ] PII handling documented
- [ ] Data retention policies defined
- [ ] Backup encryption verified

### Input Validation
- [ ] SQL injection protected (parameterized queries)
- [ ] XSS protected (output encoding)
- [ ] CSRF tokens implemented
- [ ] File upload validation
- [ ] Rate limiting in place

## Audit Report Template

```
SECURITY AUDIT REPORT
Date: [Date]
Scope: [What was audited]
Auditor: [Name/Agent]

EXECUTIVE SUMMARY
- Critical findings: X
- High findings: X
- Medium findings: X
- Low findings: X

CRITICAL FINDINGS
1. [Finding]
   - Risk: [Impact description]
   - Remediation: [Specific fix]
   - Priority: Immediate

HIGH FINDINGS
[Same format]

RECOMMENDATIONS
1. [Short-term actions]
2. [Medium-term improvements]
3. [Long-term security roadmap]

APPENDIX
- Tools used
- Full scan results
- Evidence screenshots
```
