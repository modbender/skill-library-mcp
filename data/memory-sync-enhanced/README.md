# Memory Sync Enhanced

增强版记忆系统 - Ebbinghaus 遗忘曲线 + Hebbian 共现图。

## 架构

```
Layer 1: CortexGraph (语义搜索 + 遗忘曲线)
Layer 2: Co-occurrence Graph (操作关联)
```

## 核心概念

1. **Ebbinghaus 遗忘曲线** - 管理记忆生命周期
2. **Hebbian 共现图** - 记录记忆之间的关联
3. **双层检索** - 语义相似 + 操作相关

## 使用

```bash
# 同步记忆
./scripts/sync-memory.sh

# 搜索记忆（增强版）
python3 scripts/co_occurrence_tracker.py
```

## 参考

- @Zeph 的 Hebbian 共现图帖子 (The Colony)
- CortexGraph 遗忘曲线

## 许可证

MIT
