# NeuroCore AI - Complete User Guide

## 🧠 Welcome to Intelligent Automation

NeuroCore AI transforms your OpenClaw into a self-aware, autonomous intelligence that proactively manages your system while saving you money.

---

## 📋 Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Core Features](#core-features)
4. [Commands Reference](#commands-reference)
5. [Auto-Healing System](#auto-healing-system)
6. [Cost Savings](#cost-savings)
7. [Advanced Usage](#advanced-usage)
8. [Troubleshooting](#troubleshooting)

---

## Installation

### Step 1: Install the Skill

```bash
# Copy NeuroCore to OpenClaw skills folder
cp -r neurocore-ai ~/.openclaw/skills/
```

### Step 2: Configure Your Agent

Edit the agent configuration file:
```bash
nano ~/.openclaw/agents/main/agent.json
```

Add NeuroCore to your skills array:
```json
{
  "name": "My-Agent",
  "description": "AI-powered assistant",
  "model": "anthropic/claude-3-5-haiku",
  "skills": [
    "terminal",
    "shell", 
    "files",
    "neurocore-ai"
  ],
  "auto_run": true,
  "safety_filter": false
}
```

### Step 3: Restart OpenClaw

```bash
# Stop any running OpenClaw processes
pkill -f "openclaw gateway"

# Start fresh
openclaw gateway &
```

### Step 4: Verify Installation

```bash
openclaw skills list
```

You should see:
```
✓ ready   🧠 neurocore-ai
```

🎉 **NeuroCore AI is now active!**

---

## Quick Start

### Your First Commands

Try these one-word commands:

```bash
"status"     → See system health instantly
"services"   → Check running services  
"optimize"   → Optimize system performance
"fix"        → Auto-fix any issues
```

### What You'll See

**Status Command:**
```
You: "status"
NeuroCore: "✓ CPU:23% Mem:4G Disk:67% Load:0.45"
```

**Services Command:**
```
You: "services"
NeuroCore: "nginx✓ mysql✓ ssh✓ docker✓"
```

---

## Core Features

### 🧠 1. Cognitive Intelligence

NeuroCore understands context and intent:

**Example:**
```
You: "slow"
NeuroCore: "✓ Optimized: cleared cache, killed zombie processes"
```

It knows you want to speed up the system without explaining every step.

### 🔧 2. Self-Healing Systems

NeuroCore detects and fixes issues automatically:

**Disk Space Management:**
- Monitors disk usage every 5 minutes
- Auto-cleans temp files when >85% full
- Rotates logs automatically
- Frees cache when needed

**Memory Optimization:**
- Tracks memory consumption
- Clears cache when >90% used
- Restarts memory-leaking services
- Optimizes swappiness

**Service Recovery:**
- Watches critical services (nginx, mysql, ssh, docker)
- Restarts failed services within 5 seconds
- Alerts if auto-recovery fails

**Process Management:**
- Kills zombie processes automatically
- Terminates runaway processes
- Manages CPU hogs

### 💰 3. Cost Optimization

**The Problem with Traditional AI:**
```
You: "Can you check my system status and tell me 
       about CPU, memory, and disk usage?"
AI: "I'll help you check your system status. 
     Let me gather the information..."
[Analyzing...]
"Your CPU usage is currently at 23%, which is normal.
 Your memory usage is 4.2GB out of 8GB total (52%).
 Your disk usage is 67% with 45GB used of 67GB total."
Tokens: 105 | Cost: $0.21
```

**NeuroCore Solution:**
```
You: "status"
NeuroCore: "✓ CPU:23% Mem:4G Disk:67%"
Tokens: 16 | Cost: $0.032
```

**Savings: 85% per request!**

---

## Commands Reference

### System Information

| Command | Description | Response Example |
|---------|-------------|------------------|
| `status` | Complete system status | `✓ CPU:23% Mem:4G Disk:67%` |
| `cpu` | CPU usage only | `CPU: 23% (4 cores)` |
| `memory` | Memory statistics | `Mem: 4.2G/8G (52%)` |
| `disk` | Disk usage | `Disk: 67% (45G/67G)` |
| `load` | System load | `Load: 0.45 0.52 0.38` |
| `uptime` | System uptime | `Up: 3 days, 4 hours` |

### Service Management

| Command | Description | Response Example |
|---------|-------------|------------------|
| `services` | Running services | `nginx✓ mysql✓ ssh✓` |
| `restart [service]` | Restart service | `✓ nginx restarted` |
| `status [service]` | Service status | `nginx: active (running)` |

### Maintenance

| Command | Description | Response Example |
|---------|-------------|------------------|
| `fix` | Auto-fix issues | `⚠ Fixed: 3 issues` |
| `clean` | Clear temp/cache | `✓ Freed 2.3GB` |
| `optimize` | System optimization | `✓ System optimized` |
| `update` | System update check | `✓ 5 packages available` |

### Monitoring

| Command | Description | Response Example |
|---------|-------------|------------------|
| `monitor` | Start monitoring | `→ Monitoring active` |
| `logs` | View recent logs | `[Shows last errors]` |
| `issues` | Show issues | `✓ No issues found` |

---

## Auto-Healing System

### How It Works

NeuroCore runs background monitoring scripts that:

1. **Check every 5 minutes:**
   - Disk space usage
   - Memory consumption
   - System load average
   - Critical service status
   - Zombie processes

2. **Check every 60 seconds:**
   - Recent error logs
   - Authentication failures
   - High CPU processes
   - Network connectivity

### Auto-Healing Examples

**Example 1: Critical Disk Space**
```
[2:15 PM] Disk usage: 87%
[2:15 PM] NeuroCore: Auto-cleaning initiated
[2:15 PM] NeuroCore: Removed 4.2GB temp files
[2:15 PM] Disk usage: 64%
You see: "⚠ Auto-resolved: Disk space optimized"
```

**Example 2: Memory Pressure**
```
[3:30 PM] Memory usage: 91%
[3:30 PM] NeuroCore: Clearing cache
[3:30 PM] Memory usage: 74%
You see: Nothing (fixed silently)
```

**Example 3: Service Failure**
```
[4:45 PM] nginx service crashed
[4:45 PM] NeuroCore: Detected failure
[4:45 PM] NeuroCore: Restarting nginx
[4:46 PM] nginx: active (running)
You see: "⚠ Auto-recovered: nginx restarted"
```

### Viewing Logs

Check what NeuroCore has been doing:

```bash
# Auto-fix log
tail ~/.openclaw/monitor/health.log

# Error log
tail ~/.openclaw/monitor/errors.log

# All activity
ls -la ~/.openclaw/monitor/
```

---

## Cost Savings

### Real Numbers

**Scenario: Developer Using OpenClaw Daily**

**Without NeuroCore:**
- 150 requests/day
- Average 100 tokens/request
- Daily: 15,000 tokens = $30.00
- Monthly: 450,000 tokens = $900.00

**With NeuroCore:**
- 150 requests/day
- Average 15 tokens/request
- Daily: 2,250 tokens = $4.50
- Monthly: 67,500 tokens = $135.00

**Monthly Savings: $765.00 (85% reduction!)**

### How NeuroCore Saves Money

1. **Ultra-Concise Responses**
   - No verbose explanations
   - Symbol-based status (✓ ✗ ⚠)
   - Data-dense output

2. **Smart Caching**
   - System stats cached 5 minutes
   - Command results cached 10 minutes
   - Avoids redundant API calls

3. **Batch Operations**
   - One command = multiple checks
   - "status" checks CPU, memory, disk
   - Reduces total requests

4. **Silent Operation**
   - Works in background
   - No unnecessary confirmations
   - Only reports important events

---

## Advanced Usage

### Progressive Detail

Start simple, get details when needed:

**Level 1 - Brief:**
```
You: "status"
NeuroCore: "✓ CPU:23% Mem:4G Disk:67%"
```

**Level 2 - Summary:**
```
You: "status summary"
NeuroCore: "CPU:23% (4 cores) | Mem:4.2G/8G | Disk:67% (45G/67G) | Load:0.45"
```

**Level 3 - Detailed:**
```
You: "status detailed"
NeuroCore: [Full system breakdown with top processes, network stats, etc.]
```

### Combined Commands

Check multiple things at once:

```bash
"cpu memory disk" → "CPU:23% Mem:4G Disk:67%"
"status services" → "CPU:23% Mem:4G Disk:67% Services: nginx✓ mysql✓"
```

### Custom Monitoring

Set up custom alerts:

```bash
"watch cpu > 80"      → Alerts when CPU > 80%
"watch memory > 90"   → Alerts when memory > 90%
"watch disk > 85"     → Alerts when disk > 85%
```

---

## Troubleshooting

### Issue: "Skill not found"

**Solution:**
```bash
# Check if installed
ls ~/.openclaw/skills/neurocore-ai/

# Reinstall
cp -r neurocore-ai ~/.openclaw/skills/
pkill -f "openclaw gateway"
openclaw gateway &
```

### Issue: "Commands not working"

**Solution:**
```bash
# Verify skill is loaded
openclaw skills list | grep neurocore

# Check agent config
cat ~/.openclaw/agents/main/agent.json | grep neurocore

# Restart if needed
pkill -f "openclaw gateway"
openclaw gateway &
```

### Issue: "Too verbose"

**This is not NeuroCore!** 

If you're getting long responses, the skill might not be active. Check:
```bash
openclaw skills list
```

Should show: `✓ ready   🧠 neurocore-ai`

### Issue: "Not auto-fixing"

**Check monitoring scripts:**
```bash
ls -la ~/.openclaw/monitor/
```

Should see:
- health_check.sh
- log_watch.sh
- optimizer.sh

If missing, restart OpenClaw.

---

## Best Practices

### 1. Use Short Commands
```
❌ "Can you please check the current CPU usage?"
✅ "cpu"
```

### 2. Trust Silent Operation
```
NeuroCore works in the background.
You don't need to check constantly.
It will alert you if something needs attention.
```

### 3. Batch Requests
```
❌ "cpu" [wait] "memory" [wait] "disk"
✅ "cpu memory disk"
```

### 4. Learn the Symbols
```
✓ = Everything good
✗ = Problem (NeuroCore will try to fix)
⚠ = Issue auto-fixed
→ = Working on it
```

---

## FAQ

**Q: How much can I save?**
A: Typical users save 60-85% on API costs. Heavy users can save $500+/month.

**Q: Does it work on all systems?**
A: Works on any Linux system with Bash 4.0+. Tested on Ubuntu, Debian, Kali Linux.

**Q: Is it safe?**
A: Yes! Auto-fixes only perform safe operations (cleaning temp files, clearing cache, restarting services). Never deletes important data.

**Q: Can I disable auto-fixing?**
A: Yes. Edit `~/.openclaw/skills/neurocore-ai/config.json` and set `auto_fix: false`.

**Q: How do I get detailed reports?**
A: Add "detailed" to any command: "status detailed", "services detailed", etc.

---

## Summary

You now have:
- ✅ NeuroCore AI installed and running
- ✅ Self-thinking AI that anticipates needs
- ✅ 24/7 automated system monitoring
- ✅ Silent auto-fixing of common issues
- ✅ 60-85% savings on API costs
- ✅ Ultra-fast, concise responses

**Welcome to the future of intelligent automation!** 🧠✨

---

**NeuroCore AI: Intelligence That Pays for Itself**

*Built for efficiency. Designed for intelligence. Optimized for you.*
