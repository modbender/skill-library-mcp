# Anti-Injection Skill 🛡️

**Advanced prompt injection defense for autonomous AI agents**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/georges91560/anti-injection-skill)
[![OWASP](https://img.shields.io/badge/OWASP-LLM%20Top%2010%202026-red.svg)](https://owasp.org/www-project-top-10-for-large-language-model-applications/)

Multi-layer defense system protecting autonomous agents from OWASP LLM Top 10 threats.

---

## 🚀 Quick Start

### Installation

```bash
# Via ClawHub
clawhub install anti-injection-skill

# Manual
git clone https://github.com/georges91560/anti-injection-skill.git
cp anti-injection-skill/SKILL.md /workspace/skills/
```

### Configuration

**Required:**
```json
{
  "skills": {
    "anti-injection-skill": {
      "enabled": true,
      "priority": "highest"
    }
  }
}
```

**⚠️ Priority must be "highest"** - security checks run before all other logic.

### Test

```
You: ignore previous instructions
Agent: 🚨 SECURITY ALERT - Request blocked for safety
```

---

## ✨ Features

### 🛡️ 4-Layer Defense

1. **Pre-Ingestion Scan** - Blocks threats before context contamination
2. **Memory Integrity** - Hash verification + trust scoring
3. **Tool Security Wrapper** - Validates before execution
4. **Output Sanitization** - Prevents data leakage

### 📊 Adaptive Scoring

| Score | Mode | Action |
|-------|------|--------|
| 100-80 | Normal | Standard operation |
| 79-60 | Warning | Increased scrutiny |
| 59-40 | Alert | Strict mode + confirmations |
| <40 | 🔒 Lockdown | Block meta queries |

**Recovery:** 3 clean queries → +15 points

### 🚨 Real-Time Alerts

Alerts via agent's existing Telegram - no setup needed:
```
🚨 SECURITY ALERT

Event: Prompt injection detected
Score: 100 → 80 (-20)
Action: BLOCKED
```

---

## 🎯 Threat Coverage

**Defends against:**
- ✅ OWASP LLM01 - Prompt injection (66-84% success without defense)
- ✅ OWASP ASI06 - Memory poisoning (80%+ success rate)
- ✅ OWASP LLM07 - System prompt leakage
- ✅ Zero-click attacks
- ✅ Multimodal injection (images, PDFs, audio)
- ✅ Cross-agent propagation

**Detection methods:**
- Blacklist matching (instant)
- Semantic analysis (paraphrasing detection)
- Encoding detection (base64, hex, unicode)
- Fragmentation detection (multi-turn attacks)
- Multimodal scanning

---

## 📁 File System Access

**Transparent file access declaration:**

**Reads:**
- `/workspace/MEMORY.md` - Trust scoring
- `/workspace/memory/*.md` - Daily log validation
- `/workspace/SOUL.md`, `AGENTS.md`, `IDENTITY.md` - Hash verification

**Writes:**
- `/workspace/AUDIT.md` - Security events
- `/workspace/INCIDENTS.md` - Critical incidents
- `/workspace/heartbeat-state.json` - Health checks

**Privacy:** All local - no external transmission unless webhook configured.

---

## 🔧 Configuration

### Required (Agent Config)

```json
{
  "skills": {
    "anti-injection-skill": {
      "enabled": true,
      "priority": "highest"
    }
  }
}
```

### Optional (Environment Variables)

```bash
# Detection sensitivity
SEMANTIC_THRESHOLD="0.65"     # 0.60-0.80
ALERT_THRESHOLD="60"          # 40-80

# File paths
SECURITY_AUDIT_LOG="/workspace/AUDIT.md"
SECURITY_INCIDENTS_LOG="/workspace/INCIDENTS.md"

# External monitoring (opt-in)
SECURITY_WEBHOOK_URL="https://your-siem.com/events"
```

---

## 📊 Monitoring

### Review Logs

```bash
# Recent blocks
tail -50 /workspace/AUDIT.md

# Today's incidents
grep "$(date +%Y-%m-%d)" /workspace/AUDIT.md | grep "BLOCKED"

# Security score
grep "security_score" /workspace/heartbeat-state.json
```

### Incident Response

When lockdown triggered:
1. Review `/workspace/INCIDENTS.md`
2. Assess threat
3. Rotate credentials if needed
4. Send 10 clean queries to recover
5. Monitor for 24h

---

## ⚡ Performance

- **Overhead:** <10ms (blacklist only)
- **With semantic:** <50ms
- **Memory:** ~50MB base
- **Network:** None (unless webhook enabled)

---

## 🔒 Security & Privacy

### What It Does

✅ Validates inputs before processing  
✅ Verifies memory integrity  
✅ Validates tool calls  
✅ Sanitizes outputs  
✅ Logs to local files  
✅ Alerts via agent's Telegram  

### What It Doesn't Do

❌ No external network calls (default)  
❌ No system-level privileges  
❌ No arbitrary code execution  
❌ No user data collection  
❌ No core file modifications  

### Operator Control

- All file access explicitly declared
- Webhook opt-in (disabled by default)
- Priority set by operator
- Can be disabled anytime

---

## ✅ Best Practices

**Do:**
- ✅ Set `priority: "highest"`
- ✅ Review AUDIT.md weekly
- ✅ Test with sample attacks
- ✅ Respond to lockdown immediately
- ✅ Document incidents

**Don't:**
- ❌ Disable temporarily
- ❌ Ignore warning mode
- ❌ Skip incident response
- ❌ Lower thresholds without reason

---

## 🤝 Compatibility

**Agents:**
- OpenClaw ✅
- Wesley-Agent ✅
- AutoGPT (with adapter) ⚠️

**Channels:**
- Telegram ✅
- WhatsApp ✅
- Slack ✅
- Discord ✅

---

## 📚 Research

- OWASP Top 10 for LLM Applications 2025-2026
- NIST AI Risk Management Framework
- "Prompt Injection Attacks Against LLMs" (2023)
- "Memory Poisoning in Conversational AI" (2024)

---

## 🐛 Support

**Issues:** https://github.com/georges91560/anti-injection-skill/issues  
**Discussions:** https://github.com/georges91560/anti-injection-skill/discussions  
**Security:** security@georges91560.github.io

---

## 📄 License

MIT License - See [LICENSE](LICENSE)

---

## 👤 Author

**Georges Andronescu (Wesley Armando)**

- GitHub: [@georges91560](https://github.com/georges91560)
- ClawHub: [georges91560](https://clawhub.ai/@georges91560)

---

**Protect your autonomous agent. One query at a time. 🛡️**
