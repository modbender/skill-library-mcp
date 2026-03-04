# MEMORY.md - Long-Term Memory Template

> [!IMPORTANT]
> **Storage Architecture**: Most long-term memories are stored in SQLite database.
> **Database Path**: `/home/node/.openclaw/database/insight.db`
> **Query Method**: `python3 scripts/db_query.py [keyword] [--category CATEGORY]`
> **Auto-Extraction**: `python3 scripts/extract_memory.py` (runs daily via heartbeat/cron)

---

## L0 - Abstract (One-Line Summary)

> Core memory in one sentence: [Brief description of what this memory system tracks - e.g., "CheeInsight operational memory covering A-share quant strategies, toolchain configs, security policies, and communication channel agreements."]

---

## L1 - Overview (Category Index)

### 🖥️ System
Session configuration, model aliases, compatibility rules, and OpenClaw settings.

### 🛠️ Skills
Installed skills, API configurations, known issues, and tool policies.

### 📊 Projects
Active projects, strategy parameters, backtest results, and TODOs.

### 🌍 Environment
Workspace paths, backup configurations, Python/UV policies, and directory structure.

### 💬 Communication
Channel mappings, notification rules, bot configurations, and Discord/Telegram settings.

### 🔒 Security
Access control principles, credential storage policies, and audit guidelines.

---

## L2 - Details Index (Database Categories)

| Category | Database Filter | Key Contents |
|----------|-----------------|--------------|
| System | `--category System` | Model aliases, session config, compat rules |
| Skill | `--category Skill` | Tool configs, API endpoints, installation notes |
| Project | `--category Project` | Strategy params, project status, decisions |
| Environment | `--category Environment` | Paths, backup rules, UV policy |
| Comm | `--category Comm` | Channel IDs, bot configs, notifications |
| Security | `--category Security` | Access rules, credential policies |

---

## 📅 Recent Extraction Log

| Date | Source File | Extracted Content |
|------|-------------|-------------------|
| [DATE] | `memory/[FILE].md` | [CATEGORY]: [Brief summary] |

---

*Last updated: [DATE] | Next auto-extraction: during heartbeat check*
