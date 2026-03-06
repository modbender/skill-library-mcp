# Security Policy - EvidenceOps

## Overview

EvidenceOps is designed with security as a primary concern. This document outlines the security architecture, threat model, and operational security guidelines.

## Security Architecture

### Defense in Depth

```
┌─────────────────────────────────────────────────────────────────┐
│                      SECURITY LAYERS                             │
├─────────────────────────────────────────────────────────────────┤
│ Layer 1: Channel Validation                                      │
│   - Allowlist/Denylist enforcement                              │
│   - Pairing requirements for DMs                                │
│   - Untrusted channel blocking                                  │
├─────────────────────────────────────────────────────────────────┤
│ Layer 2: Input Validation                                        │
│   - Path traversal prevention                                   │
│   - Filename sanitization                                       │
│   - MIME type verification                                      │
│   - Size limit enforcement                                      │
├─────────────────────────────────────────────────────────────────┤
│ Layer 3: Storage Security                                        │
│   - Append-only storage mode                                    │
│   - Cryptographic hashing (SHA-256)                             │
│   - Hash chain for integrity                                    │
│   - Read-only original files                                    │
├─────────────────────────────────────────────────────────────────┤
│ Layer 4: Audit & Monitoring                                      │
│   - JSONL audit logging                                         │
│   - Secret redaction in logs                                    │
│   - Access tracking                                             │
│   - Integrity verification                                      │
└─────────────────────────────────────────────────────────────────┘
```

## Threat Model

### High-Risk Threats

#### T01: Path Traversal Attack

**Description:** Attacker attempts to access files outside the vault directory using `../` sequences or similar.

**Mitigation:**
- All paths canonicalized before validation
- Base path boundary enforcement
- Rejection of any path containing traversal patterns
- Pattern blocking: `../`, `~/`, null bytes

**Code Reference:** `src/utils/path.ts:sanitizePath()`

#### T02: Evidence Tampering

**Description:** Modification of evidence after ingest to alter forensic value.

**Mitigation:**
- Files stored with read-only permissions
- Append-only storage mode for filesystem driver
- S3 Object Lock support (when available)
- Hash chain for detecting modifications
- Regular integrity verification

**Detection:** Run `evidence.verify()` to detect tampering

#### T03: Secret Exfiltration

**Description:** Sensitive data (API keys, passwords, PII) logged or stored in manifests.

**Mitigation:**
- Automatic regex-based redaction in logs
- No secrets in manifest files
- Redaction of email addresses, phone numbers, credit cards
- Configurable redaction patterns

**Code Reference:** `src/utils/redaction.ts`

### Medium-Risk Threats

#### T04: Malicious Skill Abuse

**Description:** A compromised or malicious skill attempts to access evidence tools.

**Mitigation:**
- Tool permission scoping in skill definition
- Channel-based access control
- Session isolation
- Audit logging of all tool calls

#### T05: Unauthorized Channel Access

**Description:** Evidence ingestion from untrusted channels.

**Mitigation:**
- Deny-by-default policy
- Explicit allowlist configuration
- DM pairing requirements
- Blocked channel enforcement

#### T06: Resource Exhaustion

**Description:** Large files (zip bombs, etc.) causing system impact.

**Mitigation:**
- Configurable size limits
- MIME type validation
- Magic byte verification
- Processing timeouts

## Security Configuration

### Recommended Production Configuration

```yaml
plugins:
  evidence-vault:
    driver: filesystem
    
    security:
      channelAllowlist:
        - "whatsapp:+1234567890"
        - "telegram:trusted_bot"
        - "slack:secure_channel"
      channelDenylist:
        - "discord:public_server"
      requirePairing: true
      
    limits:
      maxFileSizeBytes: 524288000
      allowedMimeTypes:
        - image/jpeg
        - image/png
        - video/mp4
        - audio/mpeg
        - application/pdf
        
    audit:
      enabled: true
      logRetention: 2555d
      redactPatterns:
        - "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}"
```

### S3 Security Configuration

```yaml
plugins:
  evidence-vault:
    driver: s3
    s3:
      bucket: evidence-vault-prod
      region: us-east-1
      objectLock: true
      # Use IAM roles, not static credentials
      # accessKeyId: (from environment or IAM)
      # secretAccessKey: (from environment or IAM)
```

## Security Checklist

### Deployment

- [ ] Configure channel allowlist with only trusted sources
- [ ] Enable pairing requirement for DM channels
- [ ] Set appropriate file size limits
- [ ] Configure allowed MIME types
- [ ] Enable audit logging
- [ ] Review redaction patterns
- [ ] Test path traversal protections
- [ ] Verify file permissions (read-only originals)

### Operations

- [ ] Regular integrity verification (automated)
- [ ] Audit log review schedule
- [ ] Incident response procedures documented
- [ ] Backup procedures for vault
- [ ] Retention policy compliance check

### S3-Specific

- [ ] Bucket encryption enabled
- [ ] Object Lock enabled (if available)
- [ ] Bucket policy restricts access
- [ ] No public access
- [ ] IAM roles for authentication
- [ ] Versioning enabled

## Security Best Practices

### 1. Principle of Least Privilege

Only grant the minimum permissions required:
- Skills should only have access to tools they need
- Channels should be explicitly allowed
- Users should have minimal vault access

### 2. Defense in Depth

Multiple security layers ensure single point of failure doesn't compromise security:
- Input validation at ingest
- Storage-level protections
- Audit logging for detection
- Integrity verification for assurance

### 3. Immutability

Original evidence must never be modified:
- Read-only file permissions
- Append-only storage mode
- Hash chain for detection
- Derivatives in separate folders

### 4. Transparency

All operations must be auditable:
- JSONL audit log for all events
- Redacted logs to protect PII
- Chain of custody documentation
- Export functionality with hashes

## Incident Response

### Evidence Tampering Detected

1. **Immediate:** Isolate affected case
2. **Document:** Record detection in audit log
3. **Investigate:** Review access logs for case
4. **Escalate:** Notify security team
5. **Preserve:** Create backup before investigation
6. **Report:** Generate incident report with chain analysis

### Unauthorized Access Detected

1. **Block:** Add source to denylist
2. **Audit:** Review all actions by source
3. **Assess:** Determine data exposure
4. **Report:** Generate access report
5. **Remediate:** Update access controls

### Secret Exposure Detected

1. **Rotate:** Immediately rotate exposed credentials
2. **Audit:** Review logs for exposure scope
3. **Redact:** Update redaction patterns
4. **Notify:** Inform affected parties per policy

## Vulnerability Reporting

**DO NOT** open public issues for security vulnerabilities.

Report security issues to: security@openclaw.ai

Include:
- Description of vulnerability
- Steps to reproduce
- Potential impact
- Suggested mitigation (if any)

## Security Updates

Security updates are released as patch versions and announced via:
- GitHub Security Advisories
- Release notes (marked as SECURITY)
- Discord security channel

## Compliance

EvidenceOps supports compliance with:
- **Chain of Custody:** Hash-based integrity chain
- **Audit Requirements:** JSONL audit logging
- **Data Protection:** PII redaction, retention policies
- **Legal Hold:** Retention policy enforcement

## Related Documents

- [PRIVACY.md](./PRIVACY.md) - Privacy and data protection
- [DESIGN.md](../../docs/DESIGN.md) - Architecture and threat model
- [README.md](../../README.md) - Setup and usage
