---
name: agent-memory-continuity
description: Solve the "agent forgot everything" problem with search-first protocol, automated memory sync, and context preservation. No more conversation restarts!
homepage: https://sapconet.co.za
metadata: {"clawhub": {"emoji": "🧠", "tags": ["memory", "continuity", "agent-management", "enterprise"], "author": "SAPCONET", "version": "1.0.0"}}
---

# Agent Memory Continuity 🧠

## The Problem
Does your OpenClaw agent suffer from "conversation amnesia"? Starting fresh every session? Forgetting previous discussions, decisions, and context? You're not alone - this is the #1 frustration with AI agents.

## The Solution
**Agent Memory Continuity** solves fragmented conversations through a battle-tested **search-first protocol** that ensures agents never forget previous context.

## Why This Skill?
- ✅ **Solves universal pain point** - Every OpenClaw user faces memory issues
- ✅ **Battle-tested solution** - Proven in production environment
- ✅ **Immediate impact** - No more "agent broke and forgot everything"
- ✅ **Enterprise-grade** - Professional memory management system

## Use When
- Agent conversations keep "starting fresh"
- Previous context gets lost between sessions
- Users complain "we already discussed this"
- Enterprise environments requiring conversation continuity
- Multi-session agent workflows

## Don't Use When  
- Single-use, stateless interactions
- Agents with no conversation history requirements
- Simple query/response scenarios

## Features

### 🔍 Search-First Protocol
- Mandatory memory search before responding to ongoing topics
- Red flag detection for conversation continuity breaks
- Automatic context reconstruction from memory files

### 📝 Automated Memory Sync
- 6-hourly memory context synchronization
- Daily memory file creation and updates
- Cross-referencing of ongoing projects and conversations

### 🧠 Context Preservation
- Daily memory logging discipline
- Persistent insight tracking
- Conversation thread continuity maintenance

### 🚨 Break Detection
- Identifies when agent "forgets" previous context
- Automatic recovery through memory search
- User frustration prevention system

## Installation

```bash
# Install via ClawHub
npx clawhub install agent-memory-continuity

# Or clone directly
git clone https://github.com/sapconet/agent-memory-continuity.git
cd agent-memory-continuity
bash install.sh
```

## Quick Start

### 1. Initialize Memory Protocol
```bash
# Set up memory structure
bash scripts/init-memory-protocol.sh

# Creates:
# - AGENT_MEMORY_PROTOCOL.md (search-first rules)
# - memory/YYYY-MM-DD.md (daily context files)
# - Memory sync cron jobs
```

### 2. Configure Search-First Behavior
```bash
# Configure mandatory memory search
bash scripts/configure-search-first.sh

# Enables:
# - Pre-response memory searches
# - Context continuity checks
# - Automatic break recovery
```

### 3. Activate Memory Sync
```bash
# Start automated memory synchronization  
bash scripts/activate-memory-sync.sh

# Schedules:
# - 6-hourly context updates
# - Daily memory file creation
# - Ongoing project cross-referencing
```

## Usage

### Basic Memory Protocol
The skill automatically:
1. **Searches memory** before responding to ongoing topics
2. **Detects red flags** ("we discussed this", "remember when")
3. **Reconstructs context** from memory files when breaks detected
4. **Logs decisions** to daily memory files
5. **Syncs context** across sessions

### Advanced Configuration

#### Custom Memory Search Patterns
```bash
# Add custom search patterns
echo "project_name meeting decision" >> config/search-patterns.txt

# Configure search sensitivity
export MEMORY_SEARCH_THRESHOLD=0.7
```

#### Memory Archival Rules
```bash
# Configure archival timing
export MEMORY_ARCHIVE_DAYS=30
export MEMORY_RETENTION_MONTHS=12

# Set up automatic archival
bash scripts/setup-memory-archival.sh
```

## File Structure

```
agent-memory-continuity/
├── SKILL.md
├── install.sh
├── scripts/
│   ├── init-memory-protocol.sh
│   ├── configure-search-first.sh
│   ├── activate-memory-sync.sh
│   ├── setup-memory-archival.sh
│   └── test-memory-continuity.sh
├── templates/
│   ├── AGENT_MEMORY_PROTOCOL.md
│   ├── daily-memory-template.md
│   └── cron-jobs-template.txt
├── config/
│   ├── search-patterns.txt
│   └── memory-config.json
└── docs/
    ├── troubleshooting.md
    └── enterprise-setup.md
```

## Real-World Results

**Before Agent Memory Continuity:**
- ❌ "Billy broke and forgot everything" 
- ❌ Constant conversation restarts
- ❌ Lost context and decisions
- ❌ User frustration and lost productivity

**After Agent Memory Continuity:**
- ✅ Perfect conversation continuity
- ✅ Context preserved across sessions  
- ✅ Decisions and discussions remembered
- ✅ User satisfaction and trust restored

## Enterprise Features

### Production Deployment
- Multi-agent memory synchronization
- Team conversation continuity
- Enterprise memory governance
- Audit trails and compliance

### Professional Support
- Implementation consulting
- Custom memory pattern development
- Enterprise integration services
- 24/7 technical support

## Troubleshooting

### Common Issues

**Agent still forgetting conversations:**
```bash
# Check memory search frequency
bash scripts/test-memory-continuity.sh

# Increase search sensitivity  
export MEMORY_SEARCH_THRESHOLD=0.5
```

**Memory files growing too large:**
```bash
# Enable automatic archival
bash scripts/setup-memory-archival.sh

# Configure retention policies
nano config/memory-config.json
```

**Cron jobs not running:**
```bash
# Check cron status
crontab -l | grep memory

# Reinstall cron jobs
bash scripts/activate-memory-sync.sh --force
```

## Support

### Community Support
- GitHub Issues: https://github.com/sapconet/agent-memory-continuity/issues
- Documentation: https://docs.sapconet.co.za/memory-continuity
- Examples: https://github.com/sapconet/agent-memory-continuity/examples

### Enterprise Support  
- Email: support@sapconet.co.za
- Professional Services: https://sapconet.co.za/openclaw-consulting
- Phone: +27 (0)53 123 4567

## About SAPCONET

Leading OpenClaw enterprise specialists with 6+ months of production experience. We solve the problems others are still discovering.

**Services:**
- Enterprise OpenClaw deployments
- Custom skill development
- Agent workforce consulting
- 24/7 technical support

**Website:** https://sapconet.co.za
**Contact:** hello@sapconet.co.za

---

*Stop agent amnesia. Start agent continuity. Built by the team that solved it first.*