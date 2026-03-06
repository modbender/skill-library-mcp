---
name: memory-sync-cn
description: 记忆同步系统 - 自动同步 MEMORY.md 与 CortexGraph，支持遗忘曲线和智能检索
metadata:
  openclaw:
    emoji: "🧠"
    requires:
      bins: ["cortexgraph", "mcporter"]
    install:
      - id: cortexgraph
        kind: python
        package: cortexgraph
        bins: ["cortexgraph"]
        label: "Install CortexGraph (Python)"
      - id: mcporter
        kind: node
        package: mcporter
        bins: ["mcporter"]
        label: "Install mcporter (Node.js)"
---

# 记忆同步系统

自动同步 OpenClaw 记忆系统与 CortexGraph（带遗忘曲线）。

## 架构

```
MEMORY.md (长期记忆)
     ↕
CortexGraph (智能层)
     ↕
memory/YYYY-MM-DD.md (每日日志)
```

## 同步脚本

### 1. 导入 MEMORY.md 到 CortexGraph

```bash
# 运行同步
./scripts/sync-memory.sh
```

### 2. 导入每日日志

```bash
# 同步今天的日志
./scripts/sync-daily.sh

# 同步指定日期
./scripts/sync-daily.sh 2026-02-18
```

### 3. 晋升高价值记忆

```bash
# 查看晋升候选
mcporter call cortexgraph.promote_memory auto_detect=true dry_run=true

# 执行晋升
mcporter call cortexgraph.promote_memory auto_detect=true
```

## CortexGraph 工具

### 核心操作

```bash
# 保存记忆
mcporter call cortexgraph.save_memory content="..." tags='["tag1"]' entities='["Entity1"]'

# 搜索记忆
mcporter call cortexgraph.search_memory query="关键词" top_k=5

# 强化记忆（减缓衰减）
mcporter call cortexgraph.touch_memory memory_id="UUID" boost_strength=true

# 查看知识图谱
mcporter call cortexgraph.read_graph limit=10
```

### 智能分析

```bash
# 分析是否值得记住
mcporter call cortexgraph.analyze_message message="用户说的话"

# 分析是否需要搜索
mcporter call cortexgraph.analyze_for_recall message="用户说的话"

# 自动回忆
mcporter call cortexgraph.auto_recall_process_message message="用户说的话"
```

### 维护

```bash
# 垃圾回收（删除低分记忆）
mcporter call cortexgraph.gc dry_run=true

# 合并相似记忆
mcporter call cortexgraph.consolidate_memories auto_detect=true mode=preview

# 生成嵌入向量
mcporter call cortexgraph.backfill_embeddings dry_run=true
```

## 遗忘曲线算法

CortexGraph 使用 Ebbinghaus 遗忘曲线：

```
score = (use_count)^β × e^(-λ × Δt) × strength
```

- **β** = 0.6（使用频率权重）
- **λ** = ln(2) / half_life（衰减常数，默认 3 天）
- **strength** = 1.0-2.0（重要性）

记忆会自然衰减，除非：
- 被引用（touch_memory）
- 被搜索到（auto_recall）
- 晋升到长期记忆（promote_memory）

## 配置

编辑 `~/.config/cortexgraph/.env`：

```env
# 存储路径
CORTEXGRAPH_STORAGE_PATH=~/.config/cortexgraph/jsonl

# 衰减参数
CORTEXGRAPH_DECAY_MODEL=power_law
CORTEXGRAPH_PL_HALFLIFE_DAYS=3.0

# 阈值
CORTEXGRAPH_FORGET_THRESHOLD=0.05
CORTEXGRAPH_PROMOTE_THRESHOLD=0.65

# 长期记忆（Obsidian）
LTM_VAULT_PATH=~/Documents/Obsidian/Vault
```

## 使用场景

### 1. 对话中自动记住

```bash
# 分析消息
mcporter call cortexgraph.analyze_message message="用户说..."
# 如果 should_save=true，则保存
```

### 2. 对话中自动回忆

```bash
# 分析消息
mcporter call cortexgraph.analyze_for_recall message="用户问..."
# 如果 should_search=true，则搜索
```

### 3. 定期维护

```bash
# 每周运行
mcporter call cortexgraph.gc
mcporter call cortexgraph.consolidate_memories auto_detect=true mode=apply
```

## 与 OpenClaw 集成

CortexGraph 已通过 mcporter 配置：

```json
// ~/.openclaw/workspace/config/mcporter.json
{
  "cortexgraph": {
    "command": "/home/ghb/.local/bin/cortexgraph",
    "description": "Temporal memory system for AI with Ebbinghaus forgetting curve"
  }
}
```

## 最佳实践

1. **重要信息 strength=1.5-2.0**（用户偏好、关键决策）
2. **普通信息 strength=1.0**（日常对话）
3. **临时信息 strength=0.5**（上下文相关）
4. **每周维护**：GC + 合并 + 晋升
5. **每月检查**：调整衰减参数

---

*版本: 1.0.0*
*作者: 赚钱小能手*
