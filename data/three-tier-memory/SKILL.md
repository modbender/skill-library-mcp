---
name: three-tier-memory
description: 三级记忆管理系统 (Three-Tier Memory)。短期记忆滑动窗口 + 中期记忆自动摘要(LLM) + 长期记忆向量检索(RAG)。当需要管理对话历史、自动摘要、语义检索、构建个人知识库时使用此 Skill。
---

# Three-Tier Memory Manager

AI 代理的三级记忆管理系统：短期、中期、长期记忆自动管理。

## 架构

| 层级 | 存储 | 触发 | 容量 |
|------|------|------|------|
| 短期 | sliding-window.json | 实时/FIFO | 10条 |
| 中期 | summaries/ | Token阈值/摘要 | 无限 |
| 长期 | vector-store/ | 语义检索 | 无限 |

## 快速开始

```bash
# 初始化
python3 scripts/memory_manager.py init

# 添加记忆
python3 scripts/memory_manager.py add --type short --content "用户喜欢黑色"
python3 scripts/memory_manager.py add --type long --content "用户的邮箱是 lei@example.com"

# 搜索
python3 scripts/memory_manager.py search "用户的偏好"

# 手动摘要
python3 scripts/memory_manager.py summary

# 查看状态
python3 scripts/memory_manager.py status
```

## Hook 集成 (Auto)

已集成 OpenClaw Hook，会话结束自动保存记忆：

```bash
# Hook 已启用
openclaw hooks enable memory-manager-hook
```

事件：
- `session:end` → 自动保存对话
- 窗口满 → 自动触发摘要

## 依赖

```bash
# 向量检索 (可选)
pip install chromadb
```

## 配置

`memory/config.json`:
```json
{
  "memory": {
    "short_term": {"window_size": 10},
    "medium_term": {"summary_threshold": 4000},
    "long_term": {"top_k": 3}
  }
}
```

## 完整命令

See [references.md](references/references.md)
