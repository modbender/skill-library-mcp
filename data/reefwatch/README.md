<p align="center">
  <img src="reefwatch.png" alt="ReefWatch Logo" width="400">
</p>

<h1 align="center">ReefWatch</h1>
<p align="center">By Yassin Naeim · X: <a href="https://x.com/yasnaeim">@yasnaeim</a></p>
<p align="center"><strong>Continuous local security monitoring for OpenClaw hosts.</strong></p>

ReefWatch is an OpenClaw skill that turns your assistant into a lightweight host-based intrusion detection system (HIDS). It runs as a background daemon, monitors your local machine for threats, and only alerts you through OpenClaw when something suspicious is found.

## What it detects

- **Authentication attacks** -- SSH brute-force, sudo abuse, PAM failures
- **Malware** -- Known signatures via YARA (webshells, miners, ransomware, RATs)
- **Privilege escalation** -- SUID abuse, sudo exploits, unauthorized root access
- **Persistence** -- New cron jobs, systemd services, LaunchAgents, SSH keys
- **Network threats** -- C2 callbacks, known malicious IPs/domains, suspicious ports
- **File integrity** -- SHA256-based change detection, critical path monitoring
- **OpenClaw-specific** -- Config tampering, memory/prompt poisoning (Unicode-aware), skill supply chain attacks
- **Process anomalies** -- Suspicious processes, cryptominers, sustained high CPU

## Platforms

| | Linux (Debian/Ubuntu) | macOS |
|---|---|---|
| **Support** | Full | Full (some features need permissions) |

## Architecture

```
reefwatch/                     Python package
    daemon.py                  Orchestrator + main entry point
    config.py                  Config loading + validation
    alert_manager.py           Dedup, batch, webhook delivery
    _common.py                 Shared constants/utilities
    collectors/
        log_collector.py       Tails syslog/auth.log + journald
        file_watcher.py        Polling + SHA256 integrity + dir mtime cache
        process_monitor.py     Pattern matching + sustained CPU detection
        network_monitor.py     Port/IOC checking + domain resolution
    engines/
        yara_engine.py         File scanning (realtime + scheduled)
        sigma_engine.py        Log rule evaluation (condition parser)
        custom_rules.py        JSON rules + OpenClaw integrity + poisoning detection
```

**Data flow:**

```
Collectors (log, file, process, network)
         |
         v
Detection Engines (YARA, Sigma, Custom JSON rules)
         |
         v  (only on detection)
Alert Manager (severity filter, dedup, batch, history rotation)
         |
         v
OpenClaw Webhook --> Your messaging channel
```

## Quick Start

```bash
# Install dependencies
pip3 install -r requirements.txt

# Download YARA/Sigma rules
python3 setup_rules.py

# Run the daemon
python3 reefwatch_daemon.py --webhook-url http://127.0.0.1:18789/hooks/wake
```

### As a system service

**Linux (systemd):**
```bash
cp service/reefwatch.service ~/.config/systemd/user/
systemctl --user enable --now reefwatch
```

**macOS (launchd):**
```bash
cp service/com.reefwatch.daemon.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.reefwatch.daemon.plist
```

## Commands (via OpenClaw chat)

- **"Start ReefWatch"** -- Activate monitoring
- **"Stop ReefWatch"** -- Deactivate monitoring
- **"ReefWatch status"** -- Check daemon health (reads `/tmp/reefwatch_status.json`)
- **"Update ReefWatch rules"** -- Download latest YARA/Sigma rules
- **"Scan /path/to/something"** -- Manual YARA scan of a file/directory
- **"Show ReefWatch alerts"** -- View alert history

## Configuration

Edit `reefwatch_config.yaml` to customize:

| Section | Key settings |
|---------|-------------|
| `collectors.logs` | `interval_seconds`, `use_journald`, `sources` |
| `collectors.files` | `watched_paths`, `scan_extensions`, `hash_threshold_kb` |
| `collectors.processes` | `suspicious_patterns`, `cpu_threshold_percent` |
| `collectors.network` | `suspicious_ports`, `ioc_blocklist`, `connection_rate_threshold` |
| `engines.yara` | `mode` (realtime/scheduled), `scheduled_interval_hours` |
| `engines.sigma` | `rules_dir` |
| `engines.custom` | `rules_dir`, `integrity_interval_seconds` |
| `alerting` | `min_severity`, `dedup_window_seconds`, `batch_alerts` |
| `webhook` | `url`, `retry_attempts`, `allow_external` |
| `general` | `status_file`, `log_max_bytes`, `log_backup_count` |

Config is validated at startup -- invalid values produce warnings in the log.

## Custom Rules (JSON)

Place `.json` files in `rules/custom/`:

```json
{
    "id": "detect_shadow_change",
    "name": "Shadow file modification",
    "severity": "CRITICAL",
    "source_type": "file_change",
    "conditions": {
        "path": "/etc/shadow",
        "type": "file_modified"
    }
}
```

`source_type` can be `file_change`, `process`, or `network`. All conditions must match (AND logic, case-insensitive substring).

## Rule Sources

| Engine | Source | Auto-update |
|--------|--------|-------------|
| YARA | [signature-base](https://github.com/Neo23x0/signature-base), [YARA-Rules](https://github.com/Yara-Rules/rules) | Via `setup_rules.py --update` |
| Sigma | [SigmaHQ](https://github.com/SigmaHQ/sigma) | Via `setup_rules.py --update` |
| Custom | Built-in + user-defined JSON | Manual |
| IOCs | User-managed blocklist (IPs + domains) | Manual |

## Testing

```bash
pip3 install -r requirements-dev.txt
python3 -m pytest tests/ -v
```

## License

MIT
