---
name: memory-sync-enhanced
description: 增强版记忆系统 - Ebbinghaus 遗忘曲线 + Hebbian 共现图
metadata:
  openclaw:
    emoji: "🧠"
    category: "system"
    tags: ["memory", "cortexgraph", "hebbian", "ebbinghaus", "forgetting-curve"]
---

# 增强版记忆系统

结合 **Ebbinghaus 遗忘曲线** + **Hebbian 共现图** 的双层记忆架构。

## 架构

```
┌─────────────────────────────────────────────────────────┐
│                    记忆检索                              │
│  semantic_search() + co_occurrence_boost() + decay()    │
└─────────────────────────────────────────────────────────┘
                           │
           ┌───────────────┴───────────────┐
           ▼                               ▼
┌─────────────────────┐       ┌─────────────────────┐
│   Layer 1: 向量库   │       │  Layer 2: 共现图    │
│   (CortexGraph)     │       │  (Hebbian)          │
│                     │       │                     │
│ • 语义相似度        │◄─────►│ • 操作关联          │
│ • Ebbinghaus 衰减   │       │ • 边权重衰减        │
│ • use_count 追踪    │       │ • 跨域桥接          │
└─────────────────────┘       └─────────────────────┘
```

## 核心算法

### Layer 1: Ebbinghaus 遗忘曲线

```
score = (use_count)^β × e^(-λ × Δt) × strength
```

- **β** = 0.6（使用频率权重）
- **λ** = ln(2) / half_life（默认 3 天）
- **strength** = 1.0-2.0（重要性）

### Layer 2: Hebbian 共现图

```
effective_weight = weight × 2^(-age_days / 30)
```

- 每次记忆 A 和 B 同时被检索 → 边(A,B) 权重 +1
- 边权重 30 天半衰期
- **跨域桥接**：音乐记忆 ↔ 编码记忆（因为同时发生）

## 检索流程

```python
def retrieve_memory(query, top_k=10):
    # 1. 语义搜索
    semantic_results = cortexgraph.search(query, top_k * 2)
    
    # 2. 共现增强
    for mem in semantic_results:
        co_occur_boost = get_co_occurrence_score(mem.id, recent_context)
        mem.boosted_score = mem.semantic_score + co_occur_boost * 0.3
    
    # 3. 遗忘曲线过滤
    for mem in semantic_results:
        mem.final_score = mem.boosted_score * mem.decay_factor
    
    # 4. 返回 Top K
    return sorted(semantic_results, key=lambda x: x.final_score)[:top_k]
```

## 记忆类型

### STM (短期记忆)
- JSONL 格式
- 快速读写
- 高衰减率（3天 half-life）
- 存储日常日志

### LTM (长期记忆)
- Obsidian Markdown
- 永久存储
- 低衰减率（30天 half-life）
- 存储重要洞察

### Co-occurrence Graph
- SQLite 边表
- 30天 half-life
- 记录记忆之间的关联

## 数据结构

### CortexGraph 记录

```json
{
  "id": "uuid",
  "content": "记忆内容",
  "embedding": [0.1, 0.2, ...],
  "use_count": 5,
  "last_used": "2026-02-19",
  "strength": 1.5,
  "created_at": "2026-02-15",
  "tags": ["daily-log", "finding"]
}
```

### Co-occurrence 边

```sql
CREATE TABLE co_occurrence (
  memory_a TEXT,
  memory_b TEXT,
  weight REAL,
  last_updated TEXT,
  PRIMARY KEY (memory_a, memory_b)
);
```

## 使用方法

### 同步记忆

```bash
# 同步 MEMORY.md
./scripts/sync-memory.sh

# 同步每日日志
./scripts/sync-daily.sh 2026-02-19

# 记录共现
./scripts/record-co-occurrence.sh
```

### 检索记忆

```bash
# 语义搜索
./scripts/search.sh "量化交易"

# 增强搜索（语义 + 共现）
./scripts/search-enhanced.sh "量化交易"
```

### 记忆管理

```bash
# 查看记忆统计
./scripts/stats.sh

# 垃圾回收（删除低分记忆）
./scripts/gc.sh --threshold 0.1

# 晋升到长期记忆
./scripts/promote.sh <memory_id>
```

## 统计示例

```
=== 记忆系统统计 ===

总记忆数: 2,400
共现边: 803 (连接 366 个记忆)
平均每个记忆连接: 2.2 个

记忆分布:
- STM: 1,800 (75%)
- LTM: 600 (25%)

衰减状态:
- Danger zone (0.15-0.35): 120 个
- Healthy (0.35-0.65): 1,500 个
- Strong (>0.65): 780 个
```

## 与其他系统对比

| 系统 | 向量搜索 | 遗忘曲线 | 共现图 |
|------|---------|---------|--------|
| Markdown 文件 | ❌ | ❌ | ❌ |
| CortexGraph 原版 | ✅ | ✅ | ❌ |
| Zeph 的 Hebbian | ✅ | ❌ | ✅ |
| **本系统** | ✅ | ✅ | ✅ |

## 设计理念

1. **遗忘是功能** - 不是所有记忆都需要永久保存
2. **关联即记忆** - 两个记忆同时出现 = 它们有关联
3. **跨域桥接** - 穿衣服记录和调试记录可以关联
4. **个性在桥接中** - 跨域边是 personality 所在

## 参考

- [CortexGraph](https://github.com/prefrontal-systems/cortexgraph)
- @Zeph 的 Hebbian 共现图帖子 (The Colony)
- Ebbinghaus 遗忘曲线理论

---

*版本: 2.0.0*
*结合 Ebbinghaus 遗忘曲线 + Hebbian 共现图*
