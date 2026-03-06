# ReefWatch 🪸 — Threat Catalog

## Threats Covered

### Authentication Attacks
| Threat | Engine | Severity | Notes |
|--------|--------|----------|-------|
| SSH brute-force | Sigma | HIGH | Detects repeated failed SSH logins |
| PAM auth failures | Sigma | HIGH | Failed authentication via PAM |
| Sudo abuse | Sigma + Custom | HIGH | Failed sudo, unauthorized sudo usage |
| Invalid user login attempts | Sigma | MEDIUM | Attempts with non-existent usernames |

### Malware
| Threat | Engine | Severity | Notes |
|--------|--------|----------|-------|
| Known malware signatures | YARA | HIGH-CRITICAL | Community + custom signatures |
| Webshells (PHP/Python/Perl) | YARA | CRITICAL | Generic webshell patterns |
| Cryptominers (XMRig, cpuminer) | YARA + Custom | HIGH | File signatures + process monitoring |
| Ransomware indicators | YARA | CRITICAL | Ransom note patterns, encryption behaviors |
| Reverse shells | YARA + Sigma | CRITICAL | Bash/Python/Perl/Ruby/NC reverse shells |

### Privilege Escalation
| Threat | Engine | Severity | Notes |
|--------|--------|----------|-------|
| SUID/SGID abuse | Sigma | HIGH | auditd-based detection |
| Sudo CVE exploits | Sigma | HIGH | Known sudo vulnerabilities |
| Crontab modification (as root) | Sigma + Custom | HIGH | Unauthorized scheduled tasks |
| Systemd service creation | Sigma | HIGH | New services (persistence) |

### Persistence
| Threat | Engine | Severity | Notes |
|--------|--------|----------|-------|
| New cron jobs | Custom (inotify) | HIGH | Monitored via file watcher |
| New systemd services | Custom (inotify) | HIGH | Linux only |
| LaunchAgent/LaunchDaemon | Custom (inotify) | HIGH | macOS only |
| SSH authorized_keys changes | Custom (inotify) | HIGH | New SSH keys added |
| init.d script changes | Custom (inotify) | MEDIUM | Legacy init scripts |

### Network Threats
| Threat | Engine | Severity | Notes |
|--------|--------|----------|-------|
| C2 callback (known ports) | Custom | HIGH | Connections to 4444, 1337, etc. |
| Known malicious IPs | Custom (IOC list) | CRITICAL | Checked against blocklist |
| High connection rate | Custom | MEDIUM | Possible scanning/exfiltration |
| Port scanning (outbound) | Custom | MEDIUM | Nmap-like patterns |

### File Integrity
| Threat | Engine | Severity | Notes |
|--------|--------|----------|-------|
| /etc/passwd modification | Custom | HIGH | User account changes |
| /etc/shadow modification | Custom | CRITICAL | Password hash changes |
| /etc/sudoers modification | Custom | CRITICAL | Privilege changes |
| /etc/hosts modification | Custom | MEDIUM | DNS hijacking |
| Binary replacement | YARA | HIGH | Changes to system binaries |

### OpenClaw-Specific
| Threat | Engine | Severity | Notes |
|--------|--------|----------|-------|
| Config tampering | Custom | CRITICAL | Changes to openclaw.json |
| Memory/prompt poisoning | Custom | CRITICAL | Injection in HEARTBEAT.md, SOUL.md |
| Skill supply chain attack | Custom | HIGH | Patterns from ClawHavoc campaign |
| Identity modification | Custom | HIGH | Changes to IDENTITY.md |

### Process Anomalies
| Threat | Engine | Severity | Notes |
|--------|--------|----------|-------|
| Suspicious process names | Custom | HIGH | nc, ncat, socat, xmrig, etc. |
| Sustained high CPU | Custom | MEDIUM | >90% for >2 minutes |
| Known offensive tools | YARA + Custom | HIGH | Metasploit, Cobalt Strike, Mimikatz |

## Platform Support

| Feature | Linux (Debian/Ubuntu) | macOS |
|---------|----------------------|-------|
| Log monitoring (syslog) | ✅ auth.log, syslog, kern.log | ✅ system.log |
| journald | ✅ | ❌ |
| File watching | ✅ /etc/, systemd, init.d | ✅ LaunchAgents, LaunchDaemons |
| Process monitoring | ✅ | ✅ |
| Network monitoring | ✅ | ✅ (may need permissions) |
| YARA scanning | ✅ | ✅ |
| Sigma rules | ✅ (full support) | ⚠️ (limited log sources) |

## Rule Update Sources

- **YARA**: [signature-base](https://github.com/Neo23x0/signature-base), [YARA-Rules](https://github.com/Yara-Rules/rules)
- **Sigma**: [SigmaHQ](https://github.com/SigmaHQ/sigma)
- **IOCs**: User-managed blocklist, compatible with abuse.ch feeds
