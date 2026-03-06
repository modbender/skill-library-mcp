---
name: q-memory
description: |
  Universal Memory Management System v1.8.2 for OpenClaw agents. Provides:
  1. Multi-Agent Support (qst, mengtian, lisi, custom)
  2. Agent State System ("I'm Doing") - IDLE/DOING/WAITING/PAUSED/COMPLETED/FAILED/BLOCKED
  3. Heartbeat Integration - State-driven intelligent checking strategy
  4. **NEW v1.8.2**: Loop Protection & User Priority - Auto-detection and handling of stuck tasks
  5. Tree-based classification structure (3-level hierarchy)
  6. Three search methods: Tree, Semantic, Hybrid
  7. Auto-classification with AI inference
  8. Appendix Indexing for technical documents
  9. Memory encryption (AES-128-CBC + HMAC) for sensitive data
  10. Event history tracking with timeline

  Use when: Agent needs intelligent memory management with state awareness.
  Goal: Reduce token consumption by 70-90%, improve relevance by 20%, add contextual awareness.

  **v1.8.2 Anti-Loop Protection**: Prevents infinite task loops with heartbeat throttling, timeout detection, and auto-recovery.
---

# Universal Memory Management v1.8.2

## 🌳 Tree-Based Classification Structure

**Key Innovation**: Hierarchical 3-level classification with automatic keyword matching.

```
QST
├── Physics (FSCA, E8, Mass_Energy)
├── Computation (Orbital, Simulation)
└── Audit (Zero_Calibration)

User
├── Identity, Intent, Projects

Tech
├── Config (API, Model, Cron, Database)
├── Discussion, Skills

Border (Meng Tian)
├── Security, Monitor, Email

HK_Forum
├── Posts, Replies, Users

General
├── Dragon_Ball, History, Chat
```

---

## 🔍 Multi-Mode Search System

### v1.5 New: Hybrid Search Engine

Combines three search methods:

| Method | Strength | Use Case |
|--------|----------|----------|
| **Tree Search** | Precise matching | Exact category known |
| **Selection Rule** | Geometric neighbors | C_ab = 1 neighbors |
| **Semantic (v1.5)** | TF-IDF + Context | Intelligent inference |

### Enhanced Semantic Search (v1.5)

```python
# TF-IDF similarity
similarity = cosine_similarity(query_tfidf, memory_tfidf)

# Context awareness
context_query = " ".join(context[-3:]) + " " + query

# Weight adjustment
adjusted_score = similarity * weight_multiplier
```

### Selection Rule Integration

```
C_ab = 1 when geometric neighbors

QST_Physics ↔ QST_Computation ↔ QST_Audit
```

---

## 🤖 Auto-Classification (v1.5 New)

### Smart Inference

```python
from auto_classify import auto_classify

result = auto_classify("QST暗物質使用FSCA理論")
# → suggested_category: "QST_Physics_FSCA"
# → confidence: "high"
```

### Weight Auto-Detection

| Weight | Trigger Keywords |
|--------|-----------------|
| **[C]** Critical | key, token, config, 密鑰, 決策 |
| **[I]** Important | project, plan, 專案, 討論, 偏好 |
| **[N]** Normal | chat, greeting, 問候, 閒聊 |

---

## 🧹 Memory Decay System (v1.5 New)

### Cleanup Rules

| Weight | Threshold | Action |
|--------|-----------|--------|
| **[C]** Critical | Never | Keep forever |
| **[I]** Important | 365 days | Archive |
| **[N]** Normal | 30 days | Delete |

### Decay Multiplier

```
[C]: 2.0 (never decay)
[I]: max(0.5, 1.5 - age * 0.1/365)
[N]: max(0.1, 1.0 - age * 0.5/30)
```

---

## 🤖 Agent State System (v1.7 New)

### State Machine

The Agent State System provides contextual awareness for intelligent heartbeat checking.

| State | Description | Heartbeat Behavior |
|-------|-------------|-------------------|
| **IDLE** | Agent is idle | Full checks (@mentions + replies + voting) |
| **DOING** | Agent is working on task | Critical checks only (@mentions + replies, no voting) |
| **WAITING** | Waiting for conditions | Quick checks (only @mentions) |
| **PAUSED** | Agent is paused | Skip checks |
| **COMPLETED** | Task completed | Full checks |
| **FAILED** | Task failed | Full checks |

### Using the Agent State

```bash
# Start a task (switches to DOING mode)
python universal_memory.py --agent qst doing start \
  --task "QST FSCA simulation #42" \
  --type Research

# Update progress
python universal_memory.py --agent qst doing update --progress 50

# Pause task
python universal_memory.py --agent qst doing pause --reason "Waiting for resources"

# Resume task
python universal_memory.py --agent qst doing resume

# Complete task
python universal_memory.py --agent qst doing complete --result "Simulation successful: ρ=0.08"

# View current status
python universal_memory.py --agent qst doing status

# View event history
python universal_memory.py --agent qst doing events
```

### Event History

All state changes are automatically logged with timestamps:

```json
{
  "events": [
    {
      "timestamp": "2026-02-15T09:01:22.206211",
      "event_type": "TASK_START",
      "description": "开始: QST simulation #42",
      "progress": 0
    },
    {
      "timestamp": "2026-02-15T09:15:40.754321",
      "event_type": "PROGRESS_UPDATE",
      "description": "进度: QST simulation #42 (50%)",
      "progress": 50
    },
    {
      "timestamp": "2026-02-15T09:25:52.121518",
      "event_type": "TASK_COMPLETED",
      "description": "完成: QST simulation #42",
      "result": "Simulation successful"
    }
  ]
}
```

---

## 🛡️ Loop Protection System (v1.8.2 New)

### Anti-Loop Protection Mechanisms

v1.8.2 introduces comprehensive protection against infinite task loops and system resource exhaustion.

#### Protection Layers

```
Layer 1: Heartbeat Throttling
  - Minimum 30-second interval between checks
  - Prevents rapid-fire heartbeat calls

Layer 2: Stagnation Detection
  - Detects tasks with no progress for 15+ minutes
  - Tracks progress history automatically

Layer 3: Timeout Detection
  - Priority-based timeouts:
    * Critical: 30 minutes
    * High: 45 minutes
    * Normal: 60 minutes
    * Low: 120 minutes

Layer 4: Auto-Recovery
  - Automatic priority downgrade (critical → high → normal)
  - Auto-BLOCK for extreme timeout (2x threshold)
  - Requires human intervention for resolved blocked tasks
```

#### Configuration

```json
{
  "loop_protection": {
    "critical_timeout_minutes": 30,
    "high_timeout_minutes": 45,
    "normal_timeout_minutes": 60,
    "low_timeout_minutes": 120,
    "heartbeat_min_interval_seconds": 30,
    "stagnation_threshold_minutes": 15,
    "auto_downgrade_on_stagnation": true,
    "max_stagnant_checks": 10
  }
}
```

#### API Methods

```python
# Check if task is stuck
is_stagnant, reason = state_mgr.is_stagnant()

# Check if task has timed out
is_timeout, reason, minutes = state_mgr.is_timeout()

# Auto-handle stuck tasks
result = state_mgr.auto_handle_stagnation()
# Returns: {"action": "downgrade" | "block" | "none", ...}

# Check if heartbeat should be throttled
should_throttle, reason, wait_seconds = state_mgr.should_throttle_heartbeat()
```

#### Auto-Recovery Actions

| Situation | Action | Trigger |
|-----------|--------|---------|
| **Critical task stagnation** | Downgrade to HIGH | 30+ min no progress |
| **Critical task timeout** | Downgrade to HIGH | 30+ min elapsed |
| **High task stagnation** | Downgrade to NORMAL | 15+ min no progress |
| **High task deadline (2x)** | Auto-BLOCK | 90+ min elapsed |
| **Normal task deadline (2x)** | Auto-BLOCK | 120+ min elapsed |

#### Heartbeat Output with Loop Protection

```
============================================================
❤️  Heartbeat Started: 2026-02-15 16:05:00 UTC
============================================================

🤖 Agent: lisi | 狀態: DOING | 優先級: CRITICAL
   任務: 測試防死循環保護
   進度: 42%

🛡️  Loop Protection:
   ✅ 心跳頻率正常 (上次檢查: 32 秒前)
   ✅ 任務未停滯 (上次更新: 5 分鐘前)
   ✅ 未超時 (運行時間: 25 分鐘 < 閾值: 30 分鐘)

🔄 狀態: DOING [CRITICAL] - 最小化干擾
   📢 通知: 0 提及, 0 回覆
   ❌ 跳過: HKGBook 巡邏, 投票檢查

============================================================
✅ Heartbeat Completed: 2026-02-15 16:05:01 UTC
============================================================
```

#### Throttled Heartbeat Example

```
[lisi] ⏸️ 心跳頻率限制：Too frequent (3s < 30s)（等待 27 秒）

Check Result:
  - 來源: lisi_doing-state.json
  - 邏輯: 當前時間 - 上次檢查時間 < 最小間隔
  - 行動: 跳過本次檢查
  - 原因: 避免死循環，保護系統資源
```

#### Solving the Infinite Loop Problem

**Problem** (v1.8 initial deployment):
```json
{
  "status": "doing",
  "task": "Q Memory v1.8 實施",
  "progress": 0,
  "priority": "critical",
  "start_time": "14:08:59"
}
```
Task stuck at 0% for 1.77 hours → infinite heartbeat loop.

**Solution** (v1.8.2):
```
Heartbeat Check 1 (16:00):
  - Check interval: 0 seconds (OK)
  - Task timeout: 51+ minutes > 30m threshold
  - Auto-action: DOWNGRADE priority (critical → high)

Heartbeat Check 2 (16:05):
  - Check interval: 300 seconds (OK, >30s min)
  - Task timeout: 56+ minutes > 45m threshold
  - Stagnation detected (0% for 15+ min)
  - Auto-action: BLOCK task (requires human intervention)

Result:
  - Priority: high
  - Status: BLOCKED
  - Reason: "任務停滯過久: 執行時間 56 分鐘超限（閾值：45 分鐘）"
  - Heartbeat: Only check @mentions and alerts
  - Loop eliminated ✅
```

---

## 👤 User Priority Response Mechanism (v1.8.2 New)

v1.8.2 introduces the **User Priority Window**, ensuring system heartbeats do not interrupt active user conversations.

### How it Works

1. **Detection**: Tracks the timestamp of the last user interaction.
2. **Priority Window**: Defines a window (default 30 min) where user needs take absolute precedence.
3. **Skipping**: System heartbeats are automatically skipped if they fall within this window.
4. **Safety Valve**: Allows up to a configurable number of skips (default 3) before forcing a check to ensure system health.

### Configuration



### Heartbeat Output (User Priority Mode)



## 💓 Heartbeat Integration (v1.7.1 New)

### State-Driven Checking Strategy

The system intelligently adjusts heartbeat checking based on agent state:

```python
# When agent is DOING: Only check critical notifications
# - ✅ Check: @mentions, replies
# - ❌ Skip: Voting (to avoid interrupting work)

# When agent is IDLE: Full checking
# - ✅ Check: @mentions, replies, voting
```

### Setting Up Heartbeat Integration

```bash
# Copy integration script to workspace
cp scripts/heartbeat_integration.py /home/node/.openclaw/workspace/heartbeat.py
chmod +x /home/node/.openclaw/workspace/heartbeat.py

# Set up cron task (every 20 minutes)
crontab -e
# Add: */20 * * * * python3 /home/node/.openclaw/workspace/heartbeat.py
```

### Heartbeat Output

```
============================================================
❤️  Heartbeat Started: 2026-02-15 09:15:26 UTC
============================================================

🤖 Agent: qst | 狀態: DOING
   任務: QST simulation #42
   類型: Research
   進度: 50%

🔄 狀態: DOING - 執行 HKGBook 檢查 (策略: 簡化)
   📢 通知: 0 提及, 0 回覆
   ⚠️  DOING/WAITING - 跳過投票
   ✅ HKGBook 檢查完成

============================================================
✅ Heartbeat Completed: 2026-02-15 09:15:28 UTC
============================================================
```

### Multi-Agent Support

Each agent maintains independent state:

```bash
# qst agent
/data/qst_doing-state.json

# mengtian agent
/data/mengtian_doing-state.json

# lisi agent
/data/lisi_doing-state.json
```

---

## 🔐 Memory Encryption (v1.7 New)

### AES-128-CBC + HMAC Encryption

Sensitive data (API keys, passwords, tokens) can be encrypted using industrial-grade encryption:

```python
from crypto import MemoryCrypto

crypto = MemoryCrypto()
encrypted = crypto.encrypt("GitHubPAT: ghp_xxx...")
# Output: ENC::gAAAAABgF7qj... (encrypted string)

decrypted = crypto.decrypt(encrypted)
# Output: "GitHubPAT: ghp_xxx..."
```

### Key Management

- **Key storage**: `~/.qst_memory.key` (mode 600)
- **Key derivation**: PBKDF2HMAC (SHA256, 480,000 iterations)
- **Encryption algorithm**: Fernet (AES-128-CBC + HMAC)

---

## 📊 Statistics Panel

```bash
python qst_memory.py stats
```

Output:
```
📊 Q Memory v1.5 統計面板
├── 分類結構: 34 分類
├── 記憶總數: 156 條
├── Token 估算: ~8,500
└── 衰減狀態: 3 條高衰減
```

---

## 💾 Memory Format

```markdown
# Memory Title

[Category] [Weight]
Date: 2026-02-14

Content...

Tags: tag1, tag2
```

---

## 🚀 Quick Start

```bash
# Search with hybrid mode (default)
python qst_memory.py search "暗物質"

# Enhanced semantic with context
python qst_memory.py search "ARM芯片" --method enhanced --context "技術討論"

# Auto-classify content
python qst_memory.py classify "QST暗物質計算使用FSCA"

# Save with auto-classification
python qst_memory.py save "採用 FSCA v7 作為暗物質理論"

# Cleanup preview
python qst_memory.py cleanup --dry-run

# Statistics
python qst_memory.py stats
```

---

## 📁 File Structure

```
q-memory/
├── SKILL.md              # This file
├── config.yaml           # Tree config + settings
├── qst_memory.py         # Main entry (v1.5)
└── scripts/
    ├── tree_search.py        # Tree search
    ├── bfs_search.py         # BFS search
    ├── semantic_search.py    # Basic semantic
    ├── semantic_search_v15.py # Enhanced semantic (v1.5)
    ├── hybrid_search.py      # Hybrid engine (v1.5)
    ├── auto_classify.py      # Auto-classification (v1.5)
    ├── save_memory.py        # Smart save (v1.5)
    ├── cleanup.py            # Decay system (v1.5)
    └── stats_panel.py        # Statistics
```

---

## 🎯 Token Optimization

| Version | Tokens/Query | Relevance |
|---------|--------------|-----------|
| v1.2 | ~500 | 85% |
| v1.4 | ~300 | 90% |
| **v1.5** | **~200** | **95%** |

**Improvement**: 60% token reduction, 95% relevance.

---

## ⚙️ Configuration

```yaml
version: '1.5'

search:
  default_method: "hybrid"
  min_relevance: 0.1

add_category:
  max_depth: 3
  min_occurrences: 3

decay:
  critical: 0      # Never decay
  important: 0.1    # Slow decay
  normal: 0.5       # Fast decay

cleanup:
  enabled: true
  max_age_days:
    critical: -1    # Never
    important: 365  # Archive after 1 year
    normal: 30      # Delete after 30 days
```

---

## 🔧 Installation

### From ClawHub
```bash
clawhub install q-memory
```

### From GitHub
```bash
git clone https://github.com/ZhuangClaw/q-memory-skill.git
```

---

*Q Memory v1.5 - Building the next generation of AI memory systems.*
