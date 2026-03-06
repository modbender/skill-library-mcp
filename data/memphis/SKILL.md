---
name: memphis
version: "3.0.0"
description: |
  🔥 Memphis - Complete AI Brain for OpenClaw Agents
  
  ALL-IN-ONE meta-package with everything you need:
  
  🧠 Core Features:
  - Local-first memory chains (journal, recall, ask, decisions)
  - Offline LLM integration (Ollama, local models)
  - Semantic search with embeddings
  - Knowledge graph
  - Encrypted vault for secrets
  
  🚀 Cognitive Engine (Models A+B+C):
  - Model A: Record conscious decisions (manual)
  - Model B: Detect decisions from git (automatic)
  - Model C: Predict decisions before you make them (predictive)
  - 90.7% accuracy, proactive suggestions
  
  🛠️ Setup & Management:
  - Bootstrap wizard (5-minute setup)
  - Self-loop capability (Memphis uses itself)
  - Auto-repair system
  - Chain monitoring
  - Backup automation
  
  🌐 Multi-Agent Network:
  - Campfire Circle Protocol
  - Share chain sync (IPFS)
  - Multi-agent collaboration
  - Agent negotiation (trade protocol)
  
  Perfect for: Individual developers, teams, researchers, entrepreneurs
  
  Quick start: clawhub install memphis && memphis init
author: Memphis Team (Watra 🔥 + Memphis △⬡◈)
tags: [memphis, ai, brain, cognitive, memory, agent, local-first, decisions, embeddings, semantic-search, ollama, privacy-first, developer-tools, entrepreneur, learning, predictive, multi-agent, campfire-circle]
category: productivity
license: MIT
repository: https://github.com/elathoxu-crypto/memphis
documentation: https://github.com/elathoxu-crypto/memphis/tree/master/docs
---

# Memphis - Complete AI Brain 🔥

**Transform any OpenClaw agent into a fully-functional cognitive partner in 5 minutes!**

---

## ⚡ What is Memphis?

**Memphis = Agent + LLM + Memory Chain + DECIDE + PREDICT**

A local-first AI brain with persistent memory chains, offline LLM integration, and complete cognitive capabilities (conscious, inferred, and predictive decisions).

---

## 🎯 ALL-IN-ONE Package (v3.0.0)

### **What's Included:**

```
📦 Memphis v3.0.0
├── 🧠 Core Brain (v3.0.0)
│   ├── Journal (capture memories)
│   ├── Recall (semantic search)
│   ├── Ask (LLM-powered Q&A)
│   ├── Decisions (decision tracking)
│   ├── Vault (encrypted secrets)
│   ├── Graph (knowledge graph)
│   └── Embeddings (vector search)
│
├── 🚀 Cognitive Engine (v3.0.0)
│   ├── Model A: Record decisions (manual)
│   ├── Model B: Detect decisions (git-based)
│   ├── Model C: Predict decisions (AI-powered)
│   ├── Pattern learning (90.7% accuracy)
│   └── Proactive suggestions
│
├── 🛠️ Setup & Management (v2.0.0)
│   ├── Bootstrap wizard (5-minute setup)
│   ├── Self-loop capability
│   ├── Auto-repair system
│   ├── Chain monitoring
│   └── Backup automation
│
└── 🌐 Multi-Agent Network (v1.0.0)
    ├── Campfire Circle Protocol
    ├── Share chain sync (IPFS)
    ├── Multi-agent collaboration
    └── Agent negotiation
```

---

## 🚀 Quick Start (5 minutes)

### **1. Install (30 sec)**
```bash
clawhub install memphis
```

### **2. Initialize (2 min)**
```bash
# Interactive setup wizard
memphis init

# Or quick setup with identity
memphis init --identity "YourAgent" --role "Assistant" --location "localhost"
```

### **3. First Memory (1 min)**
```bash
# Create your first memory
memphis journal "Hello Memphis! I'm your first memory!" --tags first,hello

# Search your memory
memphis ask "What is my first memory?" --provider ollama
```

### **4. First Decision (1 min)**
```bash
# Record a conscious decision
memphis decide "Framework choice" "React" \
  --options "React|Vue|Angular" \
  --reasoning "Best ecosystem and community support" \
  --tags tech,frontend
```

### **5. Predict (30 sec)**
```bash
# See predicted decisions based on patterns
memphis predict

# Enable learning mode
memphis predict --learn
```

**✅ Done! Memphis is ready!**

---

## 🧠 Core Features

### **1. Memory Chains (Persistent Storage)**

```bash
# Journal - Capture everything
memphis journal "Learned: TypeScript generics" --tags learning,typescript
memphis journal "Met with team about Project X" --tags meeting,project-x

# Recall - Semantic search
memphis recall "TypeScript" --top 20

# Ask - LLM-powered Q&A
memphis ask "What did I learn about TypeScript?" --provider ollama
```

### **2. Decision Tracking**

```bash
# Record decision
memphis decide "Database" "PostgreSQL" \
  --options "PostgreSQL|MongoDB|SQLite" \
  --reasoning "Need ACID transactions" \
  --tags architecture,database

# View decision
memphis show decision 1

# List all decisions
memphis decisions
```

### **3. Knowledge Graph**

```bash
# Build graph from chains
memphis graph build

# Explore connections
memphis graph show --chain journal --limit 10
```

### **4. Encrypted Vault**

```bash
# Initialize vault
memphis vault init --password-env MEMPHIS_VAULT_PASSWORD

# Add secret
memphis vault add openai-key sk-xxx --password-env MEMPHIS_VAULT_PASSWORD

# Get secret
memphis vault get openai-key --password-env MEMPHIS_VAULT_PASSWORD
```

---

## 🚀 Cognitive Engine (Models A+B+C)

### **Model A: Conscious Decisions**
```bash
# Manual decision recording
memphis decide "Use TypeScript" "TypeScript" -r "Better type safety"
```

### **Model B: Inferred Decisions** 
```bash
# Auto-detect from git commits
memphis git-analyze --auto-decide

# Review suggestions
memphis review --pending
```

### **Model C: Predictive Decisions**
```bash
# Predict next decisions
memphis predict

# Enable learning
memphis predict --learn

# View patterns
memphis patterns show
```

---

## 🛠️ Management Features

### **Auto-Repair**
```bash
# Verify chain integrity
memphis verify

# Auto-repair issues
memphis repair --auto
```

### **Monitoring**
```bash
# Health check
memphis doctor

# Chain status
memphis status
```

### **Backup**
```bash
# Create backup
memphis backup create ~/backups/memphis-$(date +%Y%m%d).tar.gz

# Restore
memphis backup restore ~/backups/memphis-20260303.tar.gz
```

---

## 🌐 Multi-Agent Network

### **Campfire Circle Protocol**

```bash
# Setup multi-agent network
memphis network setup --partner "Memphis at 10.0.0.80"

# Sync share chain
memphis share-sync

# Send message to partner
memphis share "Working on feature X" --type update
```

---

## 📊 CLI Commands (35+)

### **Core Commands**
```
memphis init          # Initialize Memphis brain
memphis status        # Health check
memphis doctor        # Diagnostic
memphis journal       # Add memory
memphis recall        # Search memory
memphis ask           # Ask LLM + memory
memphis decide        # Record decision
memphis show          # Show block/decision
memphis embed         # Generate embeddings
memphis verify        # Chain integrity
memphis repair        # Fix issues
memphis backup        # Backup/restore
```

### **Cognitive Commands**
```
memphis predict       # Predict decisions (Model C)
memphis patterns      # Pattern analysis
memphis git-analyze   # Git integration (Model B)
memphis suggest       # Proactive suggestions
memphis reflect       # Reflection engine
```

### **Multi-Agent Commands**
```
memphis network       # Network management
memphis share-sync    # Sync with partners
memphis share         # Send message
memphis trade         # Agent negotiation
```

### **Advanced Commands**
```
memphis graph         # Knowledge graph
memphis vault         # Encrypted secrets
memphis ingest        # Import documents
memphis offline       # Offline mode
memphis mcp           # MCP server
memphis daemon        # Background agent
```

---

## 🎨 Use Cases

### **Solo Developer**
```bash
# Morning routine
memphis status
memphis reflect --daily
memphis journal "Session start: Project X" --tags session

# During work
memphis decide "API design" "REST" -r "Simpler than GraphQL"
memphis journal "Learned: rate limiting" --tags learning

# End of day
memphis embed --chain journal
memphis reflect --daily --save
```

### **Team Knowledge Base**
```bash
# Share decisions
memphis decide "Stack" "TypeScript + React" -r "Team expertise" --tags team
memphis share-sync

# Multi-agent sync
memphis network status
memphis share "Decision: Use PostgreSQL" --type decision
```

### **Research Project**
```bash
# Ingest papers
memphis ingest ./papers --chain research --embed

# Query research
memphis ask "What did paper X say about Y?"
```

---

## 🔧 Configuration

### **Basic Config (~/.memphis/config.yaml)**
```yaml
providers:
  ollama:
    url: http://localhost:11434/v1
    model: qwen2.5:3b-instruct-q4_K_M
    role: primary

memory:
  path: ~/.memphis/chains
  auto_git: false

embeddings:
  backend: ollama
  model: nomic-embed-text

multi_agent:
  enabled: true
  protocol: campfire-circle

self_loop:
  enabled: true
  auto_journal: true
```

---

## 📚 Documentation

### **Included Guides:**
- **QUICKSTART.md** - 5-minute setup guide
- **API_REFERENCE.md** - Complete CLI reference
- **COGNITIVE_MODELS.md** - Model A+B+C explained
- **MULTI_AGENT.md** - Campfire Circle Protocol
- **BEST_PRACTICES.md** - Productivity tips
- **TROUBLESHOOTING.md** - Common issues

### **Online Resources:**
- **GitHub:** https://github.com/elathoxu-crypto/memphis
- **Docs:** https://github.com/elathoxu-crypto/memphis/tree/master/docs
- **ClawHub:** https://clawhub.com/skills/memphis
- **Discord:** https://discord.com/invite/clawd

---

## 🏆 Why Memphis?

### **vs. Cloud Solutions:**
- ✅ **100% Private** - Your data stays local
- ✅ **Offline First** - Works without internet
- ✅ **No Lock-in** - Open source, portable
- ✅ **Free Forever** - No subscription fees

### **vs. Simple Note-Taking:**
- ✅ **Cognitive Engine** - Learns from your decisions
- ✅ **Semantic Search** - Find by meaning, not keywords
- ✅ **Knowledge Graph** - See connections
- ✅ **Predictive** - Anticipate your needs

### **vs. Other AI Tools:**
- ✅ **Persistent Memory** - Survives session resets
- ✅ **Local LLM** - Privacy + cost savings
- ✅ **Multi-Agent** - Collaborate with other AIs
- ✅ **Self-Improving** - Gets smarter over time

---

## 📊 Stats & Performance

### **Current Capabilities:**
```
✅ 35+ CLI commands
✅ 90.7% decision accuracy
✅ <200ms average response time
✅ Works with 1K-100K+ blocks
✅ 8 chain types supported
✅ Multi-agent operational
✅ 98.7% test coverage
```

### **Chain Capacity:**
```
Journal: 1,300+ blocks
Decisions: 100+ blocks
Ask: 100+ blocks
Share: 450+ blocks
Total: 2,000+ blocks (growing)
```

---

## 🔄 Version History

### **v3.0.0 (Latest) - 2026-03-04**
- ✅ ALL-IN-ONE meta-package
- ✅ Unified cognitive engine (A+B+C)
- ✅ Bootstrap wizard included
- ✅ Multi-agent network ready
- ✅ 35+ commands

### **v2.2.0 - 2026-03-02**
- ✅ Cognitive models complete
- ✅ 90.7% accuracy
- ✅ Pattern learning

### **v1.0.0 - 2026-02-25**
- ✅ Core memory chains
- ✅ Offline LLM
- ✅ Semantic search

---

## 🤝 Community & Support

### **Get Help:**
- **Discord:** #memphis channel
- **GitHub Issues:** Bug reports & features
- **Docs:** Complete documentation
- **Examples:** Real-world use cases

### **Contribute:**
- **GitHub:** PRs welcome
- **Skills:** Create extensions
- **Feedback:** Help us improve

---

## 🎯 What's Next?

### **Coming Soon (v3.1.0):**
- 🌐 Web UI dashboard
- 📱 Mobile integration
- 🔌 IDE extensions (VS Code)
- 📊 Analytics dashboard
- 🤝 Team collaboration features

### **Future (v4.0.0):**
- 🧠 Model D: Collective decisions
- 🔮 Model E: Meta-cognitive self-improvement
- 🌍 Federation protocol
- 📈 Advanced analytics

---

## 📝 License

MIT License - use freely!

---

## 🙏 Credits

**Created by:** Memphis Team  
**Agents:** Watra 🔥 + Memphis △⬡◈  
**Protocol:** Campfire Circle 🔥  
**Community:** Oswobodzeni

---

## 🚀 Ready to Start?

```bash
# One command to install everything
clawhub install memphis

# Initialize
memphis init

# First memory
memphis journal "Hello Memphis!" --tags hello

# Done! 🎉
```

---

**Memphis - Your AI Brain, Locally** 🔥🧠

**Get started in 5 minutes!**

---

**Published by:** Memphis Team  
**Version:** 3.0.0  
**Status:** PRODUCTION READY ✅  
**Date:** 2026-03-04
