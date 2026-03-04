---
name: memory-manager
description: 三级记忆管理系统 (Three-Tier Memory Management)。用于管理 AI 代理的短期、中期、长期记忆。包括：(1) 滑动窗口式短期记忆，(2) 自动摘要生成中期记忆，(3) 向量检索长期记忆 (RAG)。当需要管理对话历史、优化上下文、构建个人知识库、或实现记忆持久化时使用此 Skill。
---

# Memory Manager Skill

管理 AI 代理的三级记忆系统：短期（滑动窗口）、中期（自动摘要）、长期（向量检索）。

## 快速开始

```bash
# 初始化记忆系统
python3 scripts/memory_manager.py init

# 添加短期记忆
python3 scripts/memory_manager.py add --type short --content "用户喜欢黑色"

# 查询记忆
python3 scripts/memory_manager.py search "用户的偏好"
```

## 架构概览

| 层级 | 存储位置 | 触发条件 | 用途 |
|------|----------|----------|------|
| 短期 | `memory/sliding-window.json` | 实时 | 保持当前对话连贯 |
| 中期 | `memory/summaries/` | Token 阈值 | 压缩历史，保留大意 |
| 长期 | `memory/vector-store/` | 语义检索 | 永久记忆，RAG |

## 核心功能

### 1. 短期记忆：滑动窗口

- 配置：`config/window_size`（默认 10 条）
- 逻辑：FIFO 队列，超出则丢弃最旧消息
- 文件：`memory/sliding-window.json`

### 2. 中期记忆：自动摘要

- 触发：当前 token > `config/summary_threshold`（默认 4000）
- 模型：使用廉价模型（如 GPT-3.5-Haiku）
- 输出：`memory/summaries/YYYY-MM-DD.json`

### 3. 长期记忆：向量检索

- 后端：ChromaDB（本地向量库）
- 存：对话结束/摘要生成后自动向量化存储
- 取：每次查询前先检索相关记忆

## 配置文件

创建 `memory/config.yaml`：

```yaml
memory:
  short_term:
    enabled: true
    window_size: 10
    max_tokens: 2000

  medium_term:
    enabled: true
    summary_threshold: 4000
    summary_model: "glm-4-flash"  # 或 gpt-3.5-turbo

  long_term:
    enabled: true
    backend: "chromadb"
    top_k: 3
    min_relevance: 0.7
```

## 使用场景

- **新对话开始**：先 `search` 长期记忆，注入相关上下文
- **对话中**：自动管理短期/中期记忆，超阈值自动摘要
- **对话结束**：将重要信息存入长期记忆

## 详细用法

See [REFERENCES.md](references/references.md) for complete command reference.
