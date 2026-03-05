# PARA + Proactive Agent Workspace 🦞📁

[![OpenClaw](https://img.shields.io/badge/OpenClaw-Skill-blue)](https://clawhub.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PARA Method](https://img.shields.io/badge/PARA-Method-green)](https://fortelabs.com/blog/para/)

> A production-ready workspace template combining **PARA Method** by Tiago Forte with **Proactive Agent Architecture** for file organization, folder structure, productivity, knowledge management, second brain, and AI agent memory persistence.

---

## ✨ Features

- 🗂️ **PARA Method** - Battle-tested organization system by Tiago Forte
- 🧠 **Proactive Agent Memory** - Complete AI continuity architecture
- 🚀 **One-command setup** - Automated workspace initialization
- 📝 **Rich templates** - 19+ pre-configured files and directories
- 🔒 **Security-first** - Built-in security audit and best practices
- 🦞 **Agent-native** - Designed specifically for AI agent workflows

---

## 📸 Screenshots

### Complete Workspace Structure

![Workspace Structure](assets/screenshots/workspace-structure.png)

### PARA Method Organization

![PARA Structure](assets/screenshots/para-structure.png)

### Proactive Agent Memory System

![Agent Memory](assets/screenshots/agent-memory.png)

Visual overview of the workspace organization system.

---

## 🚀 Quick Start

### Option 1: Using OpenClaw (Recommended)

```bash
# Install the skill
npx clawhub install para-proactive-workspace

# Apply to your workspace
/skill para-proactive-workspace
```

### Option 2: Manual Setup

```bash
# Clone the template
git clone https://github.com/Cocoblood9527/para-proactive-workspace.git
cd para-proactive-workspace

# Run setup script
./scripts/setup-workspace.sh ~/my-workspace
```

### Option 3: Copy Manually

```bash
# Copy template files to your workspace
cp -r assets/templates/* ~/workspace/
```

---

## 📁 Directory Structure

```
workspace/
│
├── 📁 1-projects/          # Active projects with deadlines
│   └── example-project/
│       ├── README.md
│       ├── notes.md
│       ├── docs/
│       └── assets/
│
├── 📁 2-areas/             # Ongoing responsibilities
│   ├── health/
│   ├── finance/
│   └── learning/
│
├── 📁 3-resources/         # Reference materials
│   ├── articles/
│   ├── books/
│   └── templates/
│
├── 📁 4-archives/          # Completed items
│   └── 2024-projects/
│
├── 📁 +inbox/              # Temporary inbox (process weekly)
├── 📁 +temp/               # Scratch space
│
├── 📁 .agents/             # Agent configuration
│   └── state.json
│
├── 📁 .learnings/          # Learning logs
│   ├── ERRORS.md
│   ├── LEARNINGS.md
│   └── FEATURE_REQUESTS.md
│
├── 📁 memory/              # Daily logs
│   └── working-buffer.md
│
├── 📄 AGENTS.md            # Operating rules
├── 📄 HEARTBEAT.md         # Periodic checklist
├── 📄 MEMORY.md            # Long-term memory
├── 📄 ONBOARDING.md        # First-run setup
├── 📄 README.md            # This file
├── 📄 SESSION-STATE.md     # Active task state
├── 📄 SOUL.md              # Agent identity
├── 📄 TOOLS.md             # Tool configurations
├── 📄 USER.md              # Your profile
└── 📄 .gitignore           # Git ignore rules
```

---

## 🎯 What You Get

### PARA Structure

| Directory | Purpose | When to Move |
|-----------|---------|--------------|
| `1-projects/` | Active projects with goals & deadlines | To `4-archives/` when done |
| `2-areas/` | Ongoing responsibilities | To `4-archives/` when inactive |
| `3-resources/` | Reference materials & inspiration | To `4-archives/` when not needed |
| `4-archives/` | Inactive items from above | Keep for reference |
| `+inbox/` | Temporary capture (process weekly) | To PARA folders or trash |
| `+temp/` | Scratch space (safe to delete) | Clear daily |

### Proactive Agent Memory

| File | Purpose | Update Frequency |
|------|---------|------------------|
| `SESSION-STATE.md` | Active working memory | Every message (WAL protocol) |
| `memory/YYYY-MM-DD.md` | Daily raw logs | During session |
| `MEMORY.md` | Curated long-term wisdom | Periodically distill |
| `.learnings/` | Errors & learnings | When issues occur |
| `HEARTBEAT.md` | Periodic checklist | During heartbeats |

---

## 🔄 Workflows

### For You (Human)

```
Capture → Organize → Review
   ↓          ↓           ↓
+inbox/   PARA folders   Weekly
```

### For Your Agent

```
Read → Log → Review
  ↓      ↓       ↓
SOUL.md  memory/  HEARTBEAT.md
USER.md  .learnings/
```

---

## 🛠️ Requirements

- [OpenClaw](https://github.com/openclaw/openclaw) - AI agent framework
- Git (optional, for version control)
- Bash (for setup script)

---

## 📚 Documentation

- **SKILL.md** - Complete skill documentation
- **PARA Method** - [Building a Second Brain](https://fortelabs.com/blog/para/) by Tiago Forte
- **Proactive Agent** - [Hal Labs Architecture](https://github.com/hallabs/proactive-agent)

---

## 🤝 Contributing

Contributions welcome! Areas where help is needed:

- 🖼️ **Screenshots** - Real workspace examples
- 🌍 **Translations** - Multi-language support
- 📝 **Documentation** - Tutorials and guides
- 🐛 **Bug fixes** - Report issues via GitHub

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Tiago Forte** - Creator of PARA Method
- **Hal Labs** - Proactive Agent Architecture
- **OpenClaw Community** - Framework and ecosystem

---

## 🔗 Links

- 📦 [ClawHub Skill Page](https://clawhub.com)
- 🐙 [GitHub Repository](https://github.com/Cocoblood9527/para-proactive-workspace)
- 🦞 [OpenClaw](https://github.com/openclaw/openclaw)

---

<p align="center">
  Made with 🦞 by <a href="https://github.com/Cocoblood9527">Cocoblood9527</a>
</p>
