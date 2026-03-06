# 🛡️ AgentGuard

**Security Monitoring for AI Agents**

[![ClawdHub](https://img.shields.io/badge/ClawdHub-Skill-00e5cc)](https://clawdhub.com)
[![Version](https://img.shields.io/badge/version-1.0.0-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()

---

## What is AgentGuard?

AgentGuard is a comprehensive security monitoring skill that watches over your AI agent's operations. It detects suspicious behavior, logs all external communications, and provides actionable security reports.

**Think of it as a security camera for your AI agent.**

---

## 🎯 Key Features

### 📁 File Access Monitoring
- Tracks all file read/write operations
- Detects access to sensitive files (.env, credentials, secrets)
- Identifies bulk read patterns that may indicate data exfiltration

### 🌐 API Call Detection  
- Monitors all outbound HTTP requests
- Flags calls to unknown or untrusted endpoints
- Detects credential exposure in request payloads

### 📝 Communication Logging
- Complete audit trail of external communications
- Covers emails, messages, webhooks, API calls
- Sanitized logs with hashed sensitive data

### 🚨 Anomaly Detection
- Learns baseline behavior patterns
- Alerts on deviations from normal operations
- Time-aware (knows what's normal for time of day)

### 📊 Daily Security Reports
- Comprehensive activity summaries
- Alert breakdown by severity
- Actionable security recommendations

---

## 🚀 Quick Start

### 1. Install
```bash
clawdhub install agentguard
```

### 2. Configure
Edit `~/.agentguard/config.yaml` with your preferences.

### 3. Start Monitoring
```bash
agentguard start
```

### 4. Check Status
```bash
agentguard status
```

---

## 📸 Screenshots

```
┌─────────────────────────────────────────────────────────┐
│ 🛡️ AgentGuard Security Dashboard                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Threat Level: 🟢 LOW                                   │
│                                                         │
│  Active Monitors                                        │
│  ├─ 📁 File Access    ✓ Running                        │
│  ├─ 🌐 API Calls      ✓ Running                        │
│  ├─ 📝 Comm Logger    ✓ Running                        │
│  └─ 🔍 Anomaly Detect ✓ Running                        │
│                                                         │
│  Last 24 Hours                                          │
│  ├─ File Operations: 1,247                              │
│  ├─ API Calls: 89                                       │
│  ├─ Alerts: 3 (2 LOW, 1 MEDIUM)                        │
│  └─ Communications: 12                                  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 Configuration

```yaml
# ~/.agentguard/config.yaml

monitoring:
  enabled: true
  file_watch_dirs:
    - ~/clawd
    - ~/.clawdbot

alerts:
  sensitivity: medium
  channels:
    - telegram
  
api_monitoring:
  trusted_domains:
    - api.anthropic.com
    - api.openai.com

reporting:
  auto_daily_report: true
  report_time: "09:00"
```

---

## 📈 Alert Levels

| Level | Icon | When It Triggers |
|-------|------|------------------|
| INFO | 🔵 | Normal logged activity |
| LOW | 🟢 | Minor pattern deviation |
| MEDIUM | 🟡 | Notable anomaly detected |
| HIGH | 🟠 | Potential security threat |
| CRITICAL | 🔴 | Immediate action required |

---

## 🔐 Security & Privacy

- **100% Local** - No data leaves your machine
- **Hashed Secrets** - Credentials never logged in plain text
- **Configurable Retention** - Auto-delete old logs
- **Optional Encryption** - AES-256 for stored logs

---

## 📋 Requirements

- Clawdbot v1.0+
- Python 3.10+
- ~50MB disk space for logs

---

## 🤝 Support

- **Issues:** [GitHub Issues](https://github.com/manas-ai/agentguard/issues)
- **Docs:** [Full Documentation](https://docs.clawdhub.com/skills/agentguard)
- **Discord:** [Manas AI Community](https://discord.gg/manas-ai)

---

## 📜 License

MIT License - Use freely, modify freely, just keep the attribution.

---

## 🏢 About

Built by **Manas AI** for the ClawdHub ecosystem.

*Because if you can't see what your agent is doing, how do you know it's safe?*
