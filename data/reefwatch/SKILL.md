---
name: reefwatch
version: 1.3.0
description: "Continuous local security monitoring daemon for Linux and macOS. Detects brute-force attacks, malware, privilege escalation, suspicious processes, file tampering, cryptominers, and network anomalies using YARA, Sigma, and custom detection rules. Runs as a background process and alerts only when real threats are found. Use when the user wants host-level intrusion detection, security monitoring, threat scanning, or asks about suspicious activity on their machine."
metadata:
  openclaw:
    requires:
      bins: ["python3", "pip3"]
      env: ["OPENCLAW_HOOKS_TOKEN"]
    os: ["linux", "darwin"]
---

# ReefWatch 🪸

## What it does
ReefWatch is a lightweight host-based intrusion detection system (HIDS) that runs as a background daemon on the same machine as OpenClaw. It continuously monitors the local system for security threats and alerts the user through OpenClaw's messaging channels ONLY when something suspicious is detected.

## Architecture
ReefWatch runs as an **independent Python process** (not consuming LLM tokens) and communicates with OpenClaw via the local webhook endpoint (`/hooks/wake`) to alert the user.

```
[Collectors] → [Detection Engines] → [Alert Manager] → [OpenClaw Webhook] → [User]
```

## Detection Engines
- **YARA**: File and process scanning for malware, webshells, miners, ransomware
- **Sigma**: Log-based detection for brute-force, privilege escalation, lateral movement
- **Custom Rules**: System-specific checks (file integrity, process anomalies, network connections)

## Commands

### Start monitoring
When the user asks to start ReefWatch or enable security monitoring:

1. Verify dependencies are installed:
   ```bash
   pip3 install -r ~/.openclaw/workspace/skills/reefwatch/requirements.txt --quiet
   ```

2. Download initial rulesets (first time only):
   ```bash
   python3 ~/.openclaw/workspace/skills/reefwatch/setup_rules.py
   ```

3. Start the daemon:
   ```bash
   nohup python3 ~/.openclaw/workspace/skills/reefwatch/reefwatch_daemon.py \
     --webhook-url "http://127.0.0.1:18789/hooks/wake" \
     --webhook-token "${OPENCLAW_HOOKS_TOKEN}" \
     --config ~/.openclaw/workspace/skills/reefwatch/reefwatch_config.yaml \
     > ~/.openclaw/logs/reefwatch.log 2>&1 &
   echo $! > /tmp/reefwatch.pid
   ```

4. Confirm to the user: "🪸 ReefWatch is now active. I'll alert you if any threats are detected."

### Stop monitoring
```bash
kill $(cat /tmp/reefwatch.pid 2>/dev/null) 2>/dev/null && rm -f /tmp/reefwatch.pid
```
Confirm: "🪸 ReefWatch stopped."

### Check status
```bash
if kill -0 $(cat /tmp/reefwatch.pid 2>/dev/null) 2>/dev/null; then
  echo "ReefWatch is running (PID: $(cat /tmp/reefwatch.pid))"
  tail -5 ~/.openclaw/logs/reefwatch.log
else
  echo "ReefWatch is not running"
fi
```

### View recent alerts
```bash
tail -20 ~/.openclaw/workspace/skills/reefwatch/alert_history.jsonl | python3 -c "import sys,json; [print(json.dumps(json.loads(l),indent=2)) for l in sys.stdin]"
```

### Update rules
```bash
python3 ~/.openclaw/workspace/skills/reefwatch/setup_rules.py --update
```

### Run manual scan
When the user asks to scan a specific file or directory:
```bash
python3 ~/.openclaw/workspace/skills/reefwatch/manual_scan.py --target <path>
```

## Alert Format
When ReefWatch detects a threat, it wakes OpenClaw with a message like:

```
🔴 REEFWATCH ALERT
━━━━━━━━━━━━━━━━━━
Type: Brute-force SSH attempt
Severity: HIGH
Source: auth.log
Detail: 47 failed login attempts from 192.168.1.105 in 2 minutes
Rule: sigma/ssh_brute_force
Time: 2026-02-22 15:43:21
━━━━━━━━━━━━━━━━━━
```

Forward this alert to the user immediately through their active messaging channel. If the user asks for more details, check the full log at `~/.openclaw/logs/reefwatch.log`.

## Important Notes
- ReefWatch does NOT consume LLM tokens while monitoring. It only triggers OpenClaw when alerting.
- On macOS, some collectors require granting Full Disk Access or specific permissions.
- YARA scanning can be CPU-intensive; default config scans changed files only, not full disk.
- The daemon auto-recovers if a collector fails; it logs the error and continues with remaining collectors.
- All data stays local. ReefWatch never sends system data to external servers (only to OpenClaw's local webhook).
