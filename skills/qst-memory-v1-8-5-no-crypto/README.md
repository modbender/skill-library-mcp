# QST Memory - Universal Memory Management System for OpenClaw

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-v1.8.5-no-crypto-green.svg)](https://github.com/ZhuangClaw/qst-memory-skill/releases)
[![Skill](https://img.shields.io/badge/Type-Activity%20Skill-orange.svg)](SKILL.md)

## 🧪 About QST Memory

**QST Memory** is a universal memory management system for OpenClaw agents, providing intelligent storage, retrieval, and state awareness capabilities.

### 🌟 Key Features

| Feature | Description |
|---------|-------------|
| **Multi-Agent Support** | Support for qst, mengtian, lisi, and custom agents |
| **Agent State System** | "I'm Doing" state machine (IDLE/DOING/WAITING/PAUSED/COMPLETED/FAILED/BLOCKED) |
| **Subtask Management** ⭐ **NEW v1.8.4** | Multi-level subtasks with automatic progress calculation |
| **Auto-Completion Detection** ⭐ **NEW v1.8.4** | Automatic detection when all required subtasks are complete |
| **Progress Reminder** ⭐ **NEW v1.8.4** | 8-min stagnation detection with automatic priority adjustment |
| **Task Templates** ⭐ **NEW v1.8.4** | Predefined templates (Development, Research, Analytics, Support) |
| **User Priority Response** ⭐ **NEW v1.8.2** | Auto-skip heartbeats during user conversations (30-min window) |
| **Anti-Loop Protection** ⭐ **NEW v1.8.2** | 4-layer protection against infinite task loops |
| **Smart Search** | Tree-based, semantic, and hybrid search methods |
| **Auto-Classification** | AI-powered automatic keyword categorization |
| **Memory Encryption** | AES-128-CBC + HMAC for sensitive data |
| **Event Tracking** | Complete history with timeline visualization |

---

## 🚀 Installation

### Quick Install (GitHub Clone)

```bash
cd ~/.openclaw/workspace/skills
git clone https://github.com/ZhuangClaw/qst-memory-skill.git qst-memory
```

### Via ClawHub

```bash
# Install OpenClaw CLI
npm i -g clawhub

# Install QST Memory
clawhub install qst-memory-skill --version 1.8.4
```

### Verify Installation

```bash
cd ~/.openclaw/workspace/skills/qst-memory

# Save a test memory
python3 universal_memory.py --agent myagent save "Test memory: Hello QST!"

# List memories
python3 universal_memory.py --agent myagent list

# Search memories
python3 universal_memory.py --agent myagent search "QST"
```

---

## 📖 Usage

### Basic Commands

```bash
# Save memory
python3 universal_memory.py --agent qst save "[Tech] Important config info..."

# Search memory
python3 universal_memory.py --agent qst search "config"

# List all memories
python3 universal_memory.py --agent qst list

# Show stats
python3 universal_memory.py --agent qst stats
```

### State Management

```bash
# Start a task
python3 universal_memory.py --agent qst doing start --task "Research project" --type "Research"

# Start a task with a template (v1.8.4)
python3 universal_memory.py --agent qst doing start \
  --task "Develop new feature" \
  --type Development \
  --template Development

# Update progress
python3 universal_memory.py --agent qst doing update --progress 50

# Complete task
python3 universal_memory.py --agent qst doing complete --result "Task completed"

# Reset state
python3 universal_memory.py --agent qst doing reset
```

### Subtask Management (v1.8.4)

```bash
# Add a subtask
python3 universal_memory_v184.py --agent qst subtask add --title "Design API" --required

# List all subtasks
python3 universal_memory_v184.py --agent qst subtask list

# Update subtask status
python3 universal_memory_v184.py --agent qst subtask update --id st-xxx --status completed

# Delete a subtask
python3 universal_memory_v184.py --agent qst subtask delete --id st-xxx

# Show subtask details
python3 universal_memory_v184.py --agent qst subtask show --id st-xxx
```

### Template Management (v1.8.4)

```bash
# List available templates
python3 scripts/template_manager.py

# Use a template when starting a task
python3 universal_memory.py --agent qst doing start \
  --task "Data analysis project" \
  --type Analytics \
  --template Analytics
```

---

## 🎯 v1.8.4 New Features

### 1. Subtask Management System

**Features**:
- **Multi-level subtasks** (up to 3 levels deep)
- **Automatic progress calculation** based on required subtasks
- **Required vs Optional** subtasks marking
- **CRUD operations** for subtasks

**Usage**:
```bash
# Add subtasks
python3 universal_memory_v184.py --agent qst subtask add --title "Design API" --required
python3 universal_memory_v184.py --agent qst subtask add --title "Write tests" --required

# Update status
python3 universal_memory_v184.py --agent qst subtask update --id st-xxx --status completed

# View progress (automatically calculated)
python3 universal_memory_v184.py --agent qst subtask list
```

### 2. Auto-Completion Detection

**Features**:
- **Automatic detection** when all required subtasks are complete
- **Progress check** (must reach 100%)
- **Version check** (for Development tasks)
- **Heartbeat integration** (auto-detects in real-time)

**Configuration**:
```json
{
  "completion_criteria": {
    "all_required_subtasks_complete": true,
    "min_progress_percent": 100,
    "version_released": true
  }
}
```

### 3. Progress Reminder (8-min Stagnation)

**Features**:
- **8-minute stagnation detection** (configurable)
- **Automatic priority adjustment**:

| Stagnation Time | Action | Status |
|----------------|--------|--------|
| 8 minutes | Lower priority | ⚠️ priority downgrade |
| 15 minutes | Mark STAGNANT | ⏸️ mark_stagnant |
| 30 minutes | Mark BLOCKED | 🚫 mark_blocked |
| 60 minutes | Auto-complete | 🔄 auto_complete_if_possible |

**Configuration**:
```json
{
  "progress_reminder": {
    "enabled": true,
    "reminder_interval_minutes": 5,
    "stagnation_threshold_minutes": 8,
    "stagnation_actions": [
      {"stagnation_minutes": 8, "action": "lower_priority"},
      {"stagnation_minutes": 15, "action": "mark_stagnant"}
    ]
  }
}
```

### 4. Task Templates

**Available Templates**:

| Template | Subtasks | Required | Use Case |
|----------|----------|----------|----------|
| **Development** | 5 | 5 | Software development projects |
| **Research** | 4 | 3 | Research and analysis tasks |
| **Analytics** | 5 | 5 | Data analysis and reporting |
| **Support** | 4 | 4 | Technical support tasks |
| **Custom** | 0 | 0 | Custom task structure |

**Usage**:
```bash
# Start task with Development template
python3 universal_memory.py --agent qst doing start \
  --task " Develop QST Memory v1.8.4" \
  --type Development \
  --template Development

# This automatically creates 5 subtasks:
# 1. 需求分析和設計
# 2. 核心功能開發
# 3. 單元測試
# 4. 文檔編寫
# 5. 發布到生產環境
```

---

## 🎯 v1.8.2 New Features

### 1. User Priority Response Mechanism

- **Priority Window**: Skip heartbeats for 30 minutes after user interaction
- **Skip Counter**: Maximum 3 consecutive skips
- **Auto Reset**: Skip count resets on new user messages

**Configuration**:
```json
{
  "user_priority_override": {
    "enabled": true,
    "priority_window_minutes": 30,
    "max_skipped_heartbeats": 3
  }
}
```

### 2. Anti-Loop Protection

- **Throttling**: Minimum 30 seconds between heartbeats
- **Timeout Detection**: Automatic detection of stuck tasks (30-120 min)
- **Auto-Recovery**: Automatic downgrade to safe states

---

## 📊 Version History

### v1.8.4 (2026-02-16) ⭐ **LATEST**

**New Features**:
- ✨ Subtask Management System - Multi-level subtasks with automatic progress
- ✨ Auto-Completion Detection - Automatic detection when tasks are ready to complete
- ✨ Progress Reminder (8-min Stagnation) - Proactive stagnation detection
- ✨ Task Templates - Predefined templates for common task types
- 🔄 Heartbeat integration with subtasks and templates

**Bug Fixes**:
- 🐛 Fixed stagnation detection thresholds
- 🐛 Improved automatic progress calculation

### v1.8.5-no-crypto (2026-02-16) ⭐ **LATEST**

**Changes**:
- 🚫 Removed encryption module (crypto.py) to avoid ClawHub security scan false positive
- ✅ All other v1.8.4 features are retained

**Note**: This version has no encryption functionality. All data is stored as plain text. If you need encryption, use v1.8.4 or manually add crypto.py.

### v1.8.2 (2026-02-16)

**New Features**:
- ✨ User Priority Response - protect user conversations from interruptions
- 🛡️ Anti-Loop Protection - prevent infinite task loops
- 🔄 Heartbeat integration with state-driven checks
- 📝 Comprehensive documentation

**Bug Fixes**:
- 🐛 Fixed memory retrieval edge cases
- 🐛 Improved agent state transitions

### v1.8.1

**New Features**:
- Loop protection (throttling, timeout detection)
- Priority system for tasks
- Agent-specific configurations
- BLOCKED status handling

### v1.7.1

**New Features**:
- Agent State System ("I'm Doing")
- Heartbeat integration
- State-driven checking strategies

### v1.6.1

**New Features**:
- Multi-agent support
- Search function fixes
- Universal memory system

### Earlier versions

- v1.5.0: Hybrid search, auto-classification
- v1.2.2: Accelerated workflow
- v1.1.0: Initial release with semantic search

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [SKILL.md](SKILL.md) | OpenClaw Skill Definition (primary) |
| [INTEGRATION.md](INTEGRATION.md) | Integration Guide for v1.7.1 |
| [CHANGELOG-v1.6.md](CHANGELOG-v1.6.md) | Changelog for v1.6 |

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🔗 Links

- **GitHub**: https://github.com/ZhuangClaw/qst-memory-skill
- **Releases**: https://github.com/ZhuangClaw/qst-memory-skill/releases
- **ClawHub**: https://clawhub.ai/skills?q=qst (pending index)
- **Issues**: https://github.com/ZhuangClaw/qst-memory-skill/issues

---

## 🐲 About the Author

**QST Memory** is developed by **Zhuangzi** (the AI assistant inspired by Dragon Ball's Briefs family scientist).

For questions, suggestions, or support, please open an issue on GitHub or join the OpenClaw Discord community.

---

**Made with ❤️ by Zhuangzi & OpenClaw Community**
