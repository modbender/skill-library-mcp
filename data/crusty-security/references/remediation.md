# Threat Remediation Guide

## Severity Response Matrix

| Severity | Detection Signal | Immediate Action |
|----------|-----------------|------------------|
| **False Positive** | ClamAV detection, known safe source | Verify, whitelist if safe |
| **Low** | ClamAV detection, unknown source | Quarantine, monitor |
| **Medium** | ClamAV detection + suspicious origin | Quarantine, investigate origin |
| **High** | ClamAV detection + skill audit critical findings | Quarantine, check for compromise |
| **Critical** | Multiple detections, active compromise indicators | Quarantine, full incident response |

## Step 1: Immediate Containment

```bash
# Quarantine the file
bash scripts/scan_file.sh --quarantine /path/to/infected_file

# Kill suspicious processes
kill -9 <pid>

# Block outbound to suspicious IP (if root)
iptables -A OUTPUT -d <suspicious_ip> -j DROP
```

## Step 2: Verify the Threat

```bash
# Check agent integrity
bash scripts/monitor_agent.sh

# Full host audit
bash scripts/host_audit.sh --deep
```

**Interpreting ClamAV results:**
- Single detection from known safe source = likely false positive
- Detection + suspicious file origin = treat as real threat
- Detection + skill audit findings = confirmed threat

## Step 3: Assess Scope

Was the file executed?
```bash
# Check shell history
history | grep <filename>
cat ~/.bash_history | grep <filename>

# Check if process is running
ps aux | grep <filename>

# Check recent process tree
pstree -p | head -50
```

Did it modify other files?
```bash
# Find recently modified files
find /data/workspace -type f -mmin -60 -ls
find /tmp -type f -mmin -60 -ls
find ~ -type f -mmin -60 -ls
```

## Step 4: Check Persistence Mechanisms

```bash
# Cron jobs
crontab -l
ls -la /etc/cron.d/ /etc/cron.daily/ /etc/cron.hourly/

# Shell profiles (look for additions)
tail -5 ~/.bashrc ~/.profile ~/.zshrc 2>/dev/null

# SSH keys (look for unauthorized entries)
cat ~/.ssh/authorized_keys

# Systemd services
systemctl list-units --type=service --state=running | grep -v systemd

# Running listeners
ss -tlnp
```

## Step 5: Check for Data Exfiltration

```bash
# Recent outbound connections
ss -tnp | grep ESTAB

# DNS cache (if available)
journalctl -u systemd-resolved --since "1 hour ago" 2>/dev/null

# Check if API keys were accessed
# Look for reads of .env files, environment variables
bash scripts/monitor_agent.sh --hours 1
```

## Step 6: Rotate Credentials

If compromise is confirmed or suspected:

- [ ] API keys: OpenAI, Anthropic, Google, any service keys
- [ ] SSH keys: generate new, revoke old authorized_keys entries
- [ ] Database passwords
- [ ] Service tokens (Slack, Discord, Telegram bots)
- [ ] Cloud provider credentials (AWS, GCP, Railway)
- [ ] Git credentials
- [ ] Any credentials stored in .env files

## Step 7: Full Scan

```bash
# Full system scan
bash scripts/scan_file.sh -r /

# All skills audit
for d in /data/workspace/skills/*/; do
    echo "=== $d ==="
    bash scripts/audit_skill.sh "$d"
done

# Generate incident report
bash scripts/generate_report.sh --output incident_report.md
```

## Step 8: Document

Record in the security report:
- What was detected and when
- What files/systems were affected
- What credentials were rotated
- Root cause (how did the threat get in?)
- Preventive measures added

## Quarantine Management

```bash
# View quarantined files
cat /tmp/clawguard_quarantine/manifest.json | python3 -m json.tool

# Restore false positive
mv /tmp/clawguard_quarantine/<file> /original/path/

# Permanently delete all quarantined files
rm -rf /tmp/clawguard_quarantine/*
```

## Reporting Malicious Skills

If a malicious OpenClaw skill is found:

1. Document: skill name, source, malicious behavior, evidence
2. `bash scripts/audit_skill.sh /path/to/skill/ > evidence.json`
3. Report to OpenClaw team
4. Remove: `rm -rf /path/to/malicious/skill`
5. Check if other agents installed it

## Recovery Severity Levels

### Minimal (file found, never executed)
1. Delete the file → done
2. Run full scan to confirm no other artifacts

### Moderate (file was executed)
1. Kill processes
2. Remove persistence mechanisms
3. Rotate all API keys and tokens
4. Full scan
5. Monitor for 48 hours

### Severe (data exfiltration confirmed)
1. Immediately rotate ALL credentials
2. Revoke all API keys, tokens, SSH keys
3. Consider rebuilding environment from scratch
4. Audit all connected services for unauthorized access
5. Notify affected parties if user data was involved
6. Review access logs on external services

## False Positive Handling

1. Check the file's origin (known source = lower risk)
2. Submit to ClamAV: https://www.clamav.net/reports/fp
3. Add to local allowlist if confirmed safe
4. Document the false positive for future reference
