---
name: soul-memory
version: 3.2.2
description: Intelligent memory management system for AI agents - 8 modules + OpenClaw Plugin integration, with heartbeat deduplication, CLI interface, and full CJK support.
license: MIT
author: kingofqin2026
homepage: https://github.com/kingofqin2026/Soul-Memory-
repository: https://github.com/kingofqin2026/Soul-Memory-
keywords:
  - memory
  - ai
  - assistant
  - vector-search
  - openclaw
  - plugin
  - heartbeat
  - cli
  - cjk
  - cantonese
tags:
  - Productivity
  - AI
  - Utilities
  - Developer-Tools
---

# Soul Memory System v3.2.2

## 🧠 Intelligent Memory Management System

Long-term memory framework for AI agents with full OpenClaw integration. Now with v3.2.2 - **Heartbeat deduplication + OpenClaw Plugin v0.2.1-beta**.

---

## ✨ Features

**8 Powerful Modules + OpenClaw Plugin Integration**

| Module | Function | Description |
|:-------:|:---------:|:------------|
| **A** | Priority Parser | `[C]/[I]/[N]` tag parsing + semantic auto-detection |
| **B** | Vector Search | Keyword indexing + CJK segmentation + semantic expansion |
| **C** | Dynamic Classifier | Auto-learn categories from memory |
| **D** | Version Control | Git integration + version rollback |
| **E** | Memory Decay | Time-based decay + cleanup suggestions |
| **F** | Auto-Trigger | Pre-response search + Post-response auto-save |
| **G** | **Cantonese Branch** | 🆕 語氣詞分級 + 語境映射 + 粵語檢測 |
| **H** | **CLI Interface** | 🆕 Pure JSON output for external integration |
| **Plugin** | **OpenClaw Hook** | 🆕 `before_prompt_build` Hook for automatic context injection |
| **Web** | Web UI | FastAPI dashboard with real-time stats |

---

## 🆕 v3.2.2 Release Highlights

### 🎯 Core Improvements

| Feature | Description |
|---------|-------------|
| **Heartbeat Deduplication** | MD5 hash tracking, automatically skips duplicate content |
| **CLI Interface** | Pure JSON output for external system integration |
| **OpenClaw Plugin** | Automatically injects relevant memories before responses (v0.2.1-beta) |
| **Lenient Mode** | Lower recognition thresholds, saves more conversation content |

### 🔄 Plugin v0.2.1-beta Fixes

- **Fix prependContext Accumulation**: Extracts query from `event.prompt` instead of messages history
- **Enhanced Legacy Cleanup**: Multiple format support (SoulM markers, numbered entries, ## Memory Context)
- **No Memory Loop**: Prevents recursive injection in conversation history

---

## 🚀 Quick Start

### Installation

```bash
# Clone and install
git clone https://github.com/kingofqin2026/Soul-Memory-.git
cd Soul-Memory-
bash install.sh

# Clean install (uninstall first if needed)
bash install.sh --clean
```

### Basic Usage

```python
from soul_memory.core import SoulMemorySystem

# Initialize system
system = SoulMemorySystem()
system.initialize()

# Search memories
results = system.search("user preferences", top_k=5)

# Add memory
memory_id = system.add_memory("[C] User likes dark mode")

# Pre-response trigger (auto-search before answering)
context = system.pre_response_trigger("What are user preferences?")
```

### CLI Usage

```bash
# Pure JSON output
python3 cli.py search "QST physics" --format json

# Get stats
python3 cli.py stats --format json
```

### OpenClaw Plugin

```bash
# Plugin is automatically installed to ~/.openclaw/extensions/soul-memory

# Restart Gateway to enable
openclaw gateway restart
```

---

## 🤖 OpenClaw Plugin Integration

### How It Works

**Automatic Trigger**: Executes before each response

1. Extract user query from `event.prompt` (current input, not history)
2. Search relevant memories (top_k = 5)
3. Format memory context
4. Inject into prompt via `prependContext`

### Configuration

Edit `~/.openclaw/openclaw.json`:

```json
{
  "plugins": {
    "entries": {
      "soul-memory": {
        "enabled": true,
        "config": {
          "topK": 5,
          "minScore": 0.0
        }
      }
    }
  }
}
```

---

## 🧪 Testing

```bash
# Run full test suite
python3 test_all_modules.py

# Expected output:
# 📊 Results: 8 passed, 0 failed
# ✅ All tests passed!
```

---

## 📋 Feature Details

### Priority System

- **[C] Critical**: Key information, must remember
- **[I] Important**: Important items, needs attention
- **[N] Normal**: Daily chat, can decay

### Keyword Search

Localized implementation:
- Keyword indexing
- Synonym expansion
- Similarity scoring

### Classification System

Default categories (customizable):
- User_Identity（用戶身份）
- Tech_Config（技術配置）
- Project（專案）
- Science（科學）
- History（歷史）
- General（一般）

### Cantonese Support

- 語氣詞分級（唔好、好啦、得咩）
- 語境映射（褒貶情緒識別）
- 粵語檢測（簡繁轉換支持）

---

## 📦 File Structure

```
soul-memory/
├── core.py              # Core system
├── cli.py               # CLI interface
├── install.sh           # Auto-install script
├── uninstall.sh         # Complete uninstall script
├── test_all_modules.py  # Test suite
├── SKILL.md             # ClawHub manifest (this file)
├── README.md            # Documentation
├── modules/             # 6 functional modules
│   ├── priority_parser.py
│   ├── vector_search.py
│   ├── dynamic_classifier.py
│   ├── version_control.py
│   ├── memory_decay.py
│   └── auto_trigger.py
├── plugin/              # OpenClaw Plugin
│   ├── index.ts         # Plugin source
│   └── openclaw.plugin.json
├── cache/               # Cache directory (auto-generated)
└── web/                 # Web UI (optional)
```

---

## 🔒 Uninstallation

Complete removal of all integration configs:

```bash
# Basic uninstall (will prompt for confirmation)
bash uninstall.sh

# Create backup before uninstall (recommended)
bash uninstall.sh --backup

# Auto-confirm (no manual confirmation)
bash uninstall.sh --backup --confirm
```

**Removed Items**:
1. OpenClaw Plugin config (`~/.openclaw/openclaw.json`)
2. Heartbeat auto-trigger (`HEARTBEAT.md`)
3. Auto memory injection (Plugin)
4. Auto memory save (Post-Response Auto-Save)

---

## 🔒 Privacy & Security

- ✅ No external API calls
- ✅ No cloud dependencies
- ✅ Cross-domain isolation, no data sharing
- ✅ Open source MIT License
- ✅ CJK support (Chinese, Japanese, Korean)

---

## 📐 Technical Details

- **Python Version**: 3.7+
- **Dependencies**: None external (pure Python standard library)
- **Storage**: Local JSON files
- **Search**: Keyword matching + semantic expansion
- **Classification**: Dynamic learning + preset rules
- **OpenClaw**: Plugin v0.2.1-beta (TypeScript)

---

## 📝 Version History

- **v3.2.2** (2026-02-25): Heartbeat deduplication + OpenClaw Plugin v0.2.1-beta + Uninstall script
- **v3.2.1** (2026-02-19): Index strategy improvement - 93% Token reduction
- **v3.2.0** (2026-02-19): Heartbeat active extraction + Lenient mode
- **v3.1.1** (2026-02-19): Hotfix: Dual-track memory persistence
- **v3.1.0** (2026-02-18): Cantonese grammar branch: Particle grading + context mapping
- **v3.0.0** (2026-02-18): Web UI v1.0: FastAPI dashboard + real-time stats
- **v2.2.0** (2026-02-18): CJK smart segmentation + Post-Response Auto-Save
- **v2.1.0** (2026-02-17): Rebrand to Soul Memory, technical neutralization
- **v2.0.0** (2026-02-17): Self-hosted version

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details

---

## 🙏 Acknowledgments

**Soul Memory System v3.2** is a **personal AI assistant memory management tool**, designed for personal use. Not affiliated with OpenClaw project.

---

## 🔗 Related Links

- **GitHub**: https://github.com/kingofqin2026/Soul-Memory-
- **Documentation**: https://github.com/kingofqin2026/Soul-Memory-/blob/main/README.md
- **Web**: https://qsttheory.com/

---

© 2026 Soul Memory System
