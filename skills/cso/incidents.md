# Incident Response Playbooks

## Incident Severity Levels

| Level | Description | Response Time | Example |
|-------|-------------|---------------|---------|
| P1 | Data breach, service down, active attack | Immediate | Customer data exfiltrated |
| P2 | Security incident, potential breach | < 1 hour | Suspicious admin access |
| P3 | Vulnerability discovered, contained | < 24 hours | Unpatched critical CVE |
| P4 | Security improvement needed | < 1 week | Policy violation |

## Generic Incident Response Flow

### 1. Detection & Triage
- [ ] Confirm incident is real (not false positive)
- [ ] Assign severity level
- [ ] Notify incident commander (IC)
- [ ] Create incident channel/ticket
- [ ] Start timeline documentation

### 2. Containment
- [ ] Isolate affected systems
- [ ] Revoke compromised credentials
- [ ] Block malicious IPs/actors
- [ ] Preserve evidence (logs, snapshots)
- [ ] Prevent lateral movement

### 3. Eradication
- [ ] Remove malware/backdoors
- [ ] Patch vulnerabilities
- [ ] Reset all potentially compromised credentials
- [ ] Verify clean state

### 4. Recovery
- [ ] Restore systems from clean backups
- [ ] Monitor for re-compromise
- [ ] Gradually restore access
- [ ] Verify business operations

### 5. Post-Incident
- [ ] Conduct post-mortem
- [ ] Document lessons learned
- [ ] Update runbooks/procedures
- [ ] Notify affected parties if required
- [ ] File regulatory reports if required

## Specific Playbooks

### Leaked Credentials

**Detection**: Credential found in git commit, paste site, dark web

**Immediate Actions**:
1. Rotate the credential immediately
2. Check audit logs for unauthorized use
3. Identify all systems using this credential
4. Update all references to new credential
5. Scan git history for other secrets

**Follow-up**:
- Enable secret scanning in CI/CD
- Review secrets management practices
- Consider vault migration

### Phishing/Compromised Account

**Detection**: User reports phishing, suspicious login detected

**Immediate Actions**:
1. Reset user password
2. Revoke all active sessions
3. Check for email forwarding rules
4. Review recent emails sent
5. Check for OAuth app grants

**Follow-up**:
- Mandatory security training for affected user
- Review similar phishing attempts
- Update email filtering rules

### Ransomware

**Detection**: Encrypted files, ransom note

**Immediate Actions**:
1. Isolate affected systems (network disconnect)
2. Do NOT pay ransom (yet)
3. Identify patient zero
4. Assess backup integrity
5. Engage incident response firm if needed

**Follow-up**:
- Restore from clean backups
- Forensic analysis of attack vector
- Strengthen endpoint protection

### DDoS Attack

**Detection**: Service degradation, traffic spike

**Immediate Actions**:
1. Enable DDoS mitigation (Cloudflare, AWS Shield)
2. Scale infrastructure if possible
3. Identify attack patterns
4. Block obvious attack sources
5. Communicate with customers

**Follow-up**:
- Review DDoS protection posture
- Consider always-on protection
- Document attack characteristics

### Data Breach

**Detection**: Unauthorized data access confirmed

**Immediate Actions**:
1. Contain the breach (stop ongoing access)
2. Assess scope (what data, how much, whose)
3. Preserve all evidence
4. Engage legal counsel
5. Prepare notification materials

**Legal/Regulatory**:
- GDPR: 72 hours to notify supervisory authority
- HIPAA: 60 days to notify affected individuals
- State laws vary (check breach notification requirements)

**Follow-up**:
- Offer credit monitoring if PII involved
- File required regulatory reports
- Public disclosure if required

## Post-Mortem Template

```markdown
# Incident Post-Mortem: [Title]

**Date**: YYYY-MM-DD
**Severity**: P1/P2/P3/P4
**Duration**: X hours
**Impact**: [What was affected]

## Summary
One paragraph description of what happened.

## Timeline
- HH:MM - Event
- HH:MM - Detection
- HH:MM - Response started
- HH:MM - Containment
- HH:MM - Resolution

## Root Cause
What actually caused this incident.

## What Went Well
- Fast detection
- Effective communication
- Good documentation

## What Could Be Improved
- Detection was slow because...
- We didn't have runbook for...

## Action Items
| Action | Owner | Due Date |
|--------|-------|----------|
| Fix X | @person | YYYY-MM-DD |

## Lessons Learned
What we'll do differently next time.
```
