# Incident Response

## Incident Classification

| Severity | Definition | Response Time |
|----------|------------|---------------|
| **Critical** | Active breach, data exfiltration, service down | Immediate |
| **High** | Confirmed compromise, vulnerability exploitation | < 4 hours |
| **Medium** | Suspicious activity, potential exposure | < 24 hours |
| **Low** | Policy violation, minor security event | < 72 hours |

## Incident Response Phases

### 1. Detection & Identification

**Initial Triage Questions**
- What was detected and when?
- What systems/data are affected?
- Is the incident ongoing?
- What is the potential impact?
- Who reported it?

**Evidence Preservation**
- [ ] Screenshot the alert/indicator
- [ ] Preserve logs before rotation
- [ ] Document timeline of events
- [ ] Identify affected systems

### 2. Containment

**Short-term Containment**
- Isolate affected systems (don't power off)
- Block malicious IPs/domains
- Disable compromised accounts
- Revoke exposed credentials

**Long-term Containment**
- Patch vulnerable systems
- Implement additional monitoring
- Segment affected networks

**Containment Decisions**

| Option | When to Use |
|--------|-------------|
| Isolate system | Active threat, need evidence |
| Wipe and rebuild | Rootkit, deep compromise |
| Keep running + monitor | Need to understand scope |
| Take offline | Service degradation acceptable |

### 3. Eradication

- [ ] Remove malware/backdoors
- [ ] Close attack vector
- [ ] Rotate all potentially compromised credentials
- [ ] Patch vulnerabilities
- [ ] Verify no persistence mechanisms

### 4. Recovery

- [ ] Restore from known-good backups
- [ ] Rebuild compromised systems
- [ ] Validate system integrity
- [ ] Gradual service restoration
- [ ] Enhanced monitoring period

### 5. Lessons Learned

**Post-Incident Review**
- What happened (timeline)
- What worked well
- What could improve
- Action items with owners and deadlines

## Specific Incident Playbooks

### Credential Leak

1. **Identify scope** — What credentials, where exposed?
2. **Rotate immediately** — All exposed credentials
3. **Audit access** — Review logs for unauthorized use
4. **Notify affected users** — If customer credentials
5. **Search for reuse** — Check if creds used elsewhere
6. **Source remediation** — How did they leak?

### Ransomware

1. **Isolate** — Disconnect from network immediately
2. **Identify variant** — Check No More Ransom project
3. **Assess scope** — What's encrypted, what's clean?
4. **Preserve evidence** — Don't wipe yet
5. **Restore from backup** — If backups are clean
6. **Report** — Law enforcement if required
7. **Do not pay** — Funds criminal enterprise

### Phishing Compromise

1. **Reset credentials** — User and any shared accounts
2. **Review email rules** — Check for forwarding rules
3. **Check OAuth apps** — Revoke suspicious grants
4. **Review sent mail** — Did attacker send from account?
5. **Check for persistence** — Device compromise possible
6. **Awareness training** — Reinforce for affected user

### Data Breach

1. **Scope assessment** — What data, how much, how sensitive?
2. **Legal notification** — 72 hours for GDPR, varies by jurisdiction
3. **Customer notification** — If PII exposed
4. **Credit monitoring** — Offer if SSN/financial data
5. **Regulatory reporting** — HHS for HIPAA, etc.
6. **Public statement** — Coordinate with legal/PR

## Communication Templates

### Internal Alert

```
SECURITY INCIDENT ALERT
Severity: [Critical/High/Medium/Low]
Time detected: [Timestamp]
Summary: [One sentence description]
Current status: [Investigating/Contained/Resolved]
Impact: [What's affected]
Actions required: [If any]
Next update: [Time]
```

### Customer Notification

```
Subject: Important Security Notice

We are writing to inform you of a security incident that may have affected your data.

What happened: [Brief, factual description]
What information was involved: [Specific data types]
What we are doing: [Steps taken]
What you can do: [Recommended actions]
For more information: [Contact details]
```

## Incident Log Template

```
INCIDENT ID: INC-[YYYY]-[###]
Status: Open / Contained / Resolved

TIMELINE
[Timestamp] - [Event]
[Timestamp] - [Event]

AFFECTED SYSTEMS
- System 1
- System 2

ACTIONS TAKEN
- [ ] Action 1
- [ ] Action 2

EVIDENCE
- [Link to preserved logs]
- [Link to screenshots]

ASSIGNEE: [Name]
NEXT STEPS: [Description]
```
