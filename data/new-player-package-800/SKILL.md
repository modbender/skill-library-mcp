---
name: new-player-package-800
description: OpenClaw deployment optimization guide based on 800 RMB (100 USD) of real-world experience. Helps new users quickly complete skill installation, configuration optimization, and system tuning to solve common deployment issues.
metadata:
  {
    "openclaw":
      {
        "emoji": "🎁",
        "requires": { "bins": ["python3", "uv", "git"] }
      }
  }
---

# New Player Package 800 - OpenClaw Deployment Optimization Guide

## 💰 Background Story

This is a valuable lesson learned by a "poor developer" who spent 800 RMB (approximately 100 USD) on real-world OpenClaw deployment and debugging. This comprehensive optimization guide helps new users avoid common pitfalls and get started quickly.

## 🎯 Core Problems Solved

- **Missing Skills**: New OpenClaw installations have limited functionality and need key skills installed
- **Complex Configuration**: Authentication, security, and plugin configuration are error-prone  
- **Incomplete Features**: Missing core capabilities like documentation search, filesystem operations, and knowledge management
- **Lack of Monitoring**: Unable to view token consumption and session status
- **Task Interruption**: Gateway restarts cause task loss with no recovery mechanism
- **Vector Search**: Missing semantic search and knowledge organization capabilities

## 📋 Complete Optimization Checklist

### Phase 1: Essential Skill Installation

1. **clawhub** - Official skill repository manager
   - Function: Search, install, update, and publish skills
   - Command: `clawhub install <skill-name>`

2. **Find Skills** - Skill recommendation assistant  
   - Function: Automatically recommend suitable skills based on needs
   - Solves: Not knowing which skills to install

3. **skill-creator** - Skill creation toolkit
   - Function: Create and package custom skills
   - Use: Extend OpenClaw functionality

4. **clawddocs** - Official documentation retrieval
   - Function: Quickly find OpenClaw configuration details and best practices
   - Solves: Documentation lookup difficulties

5. **openclaw-anything** - System management operations
   - Function: Execute official OpenClaw management and deployment operations
   - Use: System maintenance and configuration management

6. **clawdbot-filesystem** - Advanced filesystem operations
   - Function: Batch renaming, directory analysis, file search, content extraction
   - Solves: Complex file operation requirements

7. **Ontology** - Knowledge graph construction
   - Function: Relationship and structure organization, vector semantic search, relationship analysis
   - Use: Knowledge management and intelligent retrieval

### Phase 2: Enhanced Features

8. **session-monitor** - Session status monitoring ⭐
   - Function: Automatically display token consumption, model info, context usage rate
   - Command: `/token on|off` to toggle
   - Format: `[🧠 qwen3-max | 📥123k/📤420 | Context: 47%]`

9. **task-persistence** - Task persistence ⭐
   - Function: Task continuation, state snapshots, gateway restart notifications
   - Solves: Task loss and no feedback after restarts
   - Features: Auto-recover incomplete tasks, proactive restart status notifications

### Phase 3: System Optimization

10. **Vector Search Configuration**
    - Enable memory-core plugin
    - Configure embedding models and vector database
    - Implement semantic search functionality

11. **Security Hardening**
    - Fix gateway authentication token mismatch
    - Disable insecure HTTP authentication
    - Set plugin allow list

12. **Performance Optimization**
    - Configure context compression strategy
    - Optimize memory usage
    - Set reasonable session timeouts

## 🛠️ One-Click Optimization Script

```bash
# Install all required CLI tools
npm install -g clawhub uv

# Clone and install core skills
mkdir -p ~/.openclaw/skills
cd ~/.openclaw/skills

# Install official skills
clawhub install clawhub find-skills skill-creator clawddocs openclaw-anything clawdbot-filesystem ontology

# Install enhanced skills  
clawhub install session-monitor task-persistence

# Configure vector search
mkdir -p ~/.openclaw/memory
# Enable memory-core plugin in openclaw.json

# Apply security configuration
# Fix gateway.auth.token and gateway.remote.token consistency
```

## 🔧 Common Problem Solutions

### Issue 1: Gateway token mismatch
**Symptom**: `unauthorized: gateway token mismatch`
**Solution**:
```json
{
  "gateway": {
    "auth": {
      "token": "your-consistent-token"
    }
  }
}
```
Set environment variable: `export OPENCLAW_GATEWAY_TOKEN="your-consistent-token"`

### Issue 2: Skills show as missing
**Cause**: Required tools not installed or environment variables not set
**Solution**:
- Install Python 3.8+
- Install uv or pip
- Set `OPENCLAW_WORKSPACE` environment variable

### Issue 3: Context full (100%)
**Symptom**: Cannot load new skills, slow responses
**Solution**:
- Enable context compression: `agents.defaults.compaction.mode = "safeguard"`
- Start new session
- Use `/status` to monitor token usage

### Issue 4: No feedback after gateway restart
**Solution**: Enable task-persistence skill
- Automatically monitor gateway status
- Proactively send status reports after restart
- Restore incomplete tasks

## 📊 Verification Checklist

✅ All 9 core skills installed and enabled  
✅ session-monitor displays token information  
✅ task-persistence monitors gateway status  
✅ Vector search configured and working  
✅ Security configuration applied  
✅ Performance optimization implemented  

## 💡 Best Practices

1. **Regular Updates**: `clawhub update --all`
2. **Resource Monitoring**: Use `/status` to check token usage
3. **Configuration Backup**: Regularly backup `openclaw.json`
4. **Feature Testing**: Test key features after each configuration change
5. **Experience Documentation**: Record problems and solutions in MEMORY.md

## 🎁 Value Summary

This "New Player Package 800" includes:
- **7 core functional skills**: Extend OpenClaw's basic capabilities
- **2 enhanced monitoring skills**: Solve visibility and task persistence issues  
- **Complete configuration templates**: Avoid security and performance pitfalls
- **Real-world problem solutions**: Based on actual deployment experience
- **One-click optimization script**: Quickly complete all configurations

Helps new users complete in 30 minutes what would normally take days, achieving a truly "out-of-the-box" experience.

## 📚 Related Skills

- **clawhub**: Skill management
- **find-skills**: Skill discovery  
- **session-monitor**: Status monitoring
- **task-persistence**: Task persistence
- **ontology**: Knowledge management
- **healthcheck**: Security auditing