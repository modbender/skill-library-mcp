# Memory Optimization Guide

## 适用场景

- 长期运行的项目，需要保持上下文
- 频繁引用过去的决策和知识
- 大型代码库，需要更好的记忆检索
- 多会话协作，需要持久化重要信息

## 配置变更

本指南将修改以下文件：

1. `openclaw.json` - 启用 memorySearch 和优化 memoryFlush
2. `workspace/MEMORY.md` - 优化记忆存储结构
3. `workspace/AGENTS.md` - 添加记忆管理规则

## 功能说明

### Memory Search

启用向量搜索能力，让 AI 能够：

- 语义搜索过去的对话
- 快速定位相关决策
- 跨会话检索知识

### Memory Flush 优化

更智能的上下文压缩策略：

```
┌─────────────────────────────────────┐
│      Memory Flush Pipeline          │
│                                     │
│  1. Detect threshold (80%)          │
│     └─ Monitor context usage        │
│                                     │
│  2. Analyze content                 │
│     ├─ Identify critical info       │
│     ├─ Find repetitive content      │
│     └─ Extract decisions            │
│                                     │
│  3. Summarize                       │
│     ├─ Create concise summary       │
│     ├─ Preserve key context         │
│     └─ Store in MEMORY.md           │
│                                     │
│  4. Archive                         │
│     └─ Move to .memory/archive/     │
└─────────────────────────────────────┘
```

### Memory Storage

```
workspace/
├── MEMORY.md              # 当前会话记忆
├── .memory/
│   ├── archive/           # 历史会话归档
│   │   ├── 2026-02-27.md
│   │   └── 2026-02-26.md
│   ├── decisions/         # 重要决策
│   │   └── architecture.md
│   └── knowledge/         # 持久知识
│       ├── api-patterns.md
│       └── coding-standards.md
```

## 安装命令

### 1. 更新 openclaw.json

添加 memorySearch 配置：

```json
{
  "memoryFlush": {
    "enabled": true,
    "threshold": 0.8,
    "strategy": "summarize",
    "preserveContext": ["MEMORY.md", "AGENTS.md"]
  },
  "memorySearch": {
    "enabled": true,
    "indexDirectory": ".memory",
    "embeddingModel": "text-embedding-3-small",
    "topK": 5
  }
}
```

### 2. 创建记忆目录结构

```bash
mkdir -p ~/.openclaw/workspace/.memory/archive
mkdir -p ~/.openclaw/workspace/.memory/decisions
mkdir -p ~/.openclaw/workspace/.memory/knowledge
```

### 3. 更新 MEMORY.md 模板

```markdown
# MEMORY

## Current Session

### Active Context
- Project:
- Current Task:
- Status:

### Recent Decisions
_Updated automatically during memory flush_

### Key Information
_Critical data to preserve across sessions_

## Quick Reference

### Architecture Decisions
- [Link to decision docs]

### Important Patterns
- Code patterns used frequently

### External Resources
- Links to documentation
- API references

## Session History

### 2026-02-27
- Started work on...
- Decided to use...
- Learned that...

[Previous sessions archived in .memory/archive/]
```

### 4. 更新 AGENTS.md

添加记忆管理规则：

```markdown
## Memory Management

### Before Memory Flush
1. Identify critical information to preserve
2. Update MEMORY.md with key decisions
3. Archive completed tasks to .memory/archive/

### After Memory Flush
1. Verify important context is preserved
2. Review MEMORY.md for accuracy
3. Continue work seamlessly

### Memory Search Usage
When needing past context:
1. Use semantic search to find relevant info
2. Reference .memory/knowledge/ for patterns
3. Check .memory/decisions/ for rationale
```

## 验证步骤

### 1. 验证配置

```bash
cat ~/.openclaw/openclaw.json | grep -A 10 "memorySearch"
```

Expected:
```json
"memorySearch": {
  "enabled": true,
  "indexDirectory": ".memory",
  "embeddingModel": "text-embedding-3-small",
  "topK": 5
}
```

### 2. 测试 Memory Flush

创建长对话触发 flush：

```
Tell me a very long story about... [continue until context fills]
```

Expected:
- AI detects threshold approaching
- AI summarizes and preserves key info
- AI updates MEMORY.md
- Conversation continues smoothly

### 3. 测试 Memory Search

```
Search memory for "authentication" decisions
```

Expected:
- AI searches indexed content
- Returns relevant past decisions
- Provides context-aware results

## 使用示例

### 手动触发记忆存储

```
Remember this decision: We will use PostgreSQL for the database
```

AI will:
1. Add to MEMORY.md under "Recent Decisions"
2. Create entry in `.memory/decisions/`
3. Index for future search

### 搜索历史知识

```
What did we decide about the API architecture?
```

AI will:
1. Search `.memory/decisions/`
2. Retrieve relevant decisions
3. Provide context-aware answer

### 跨会话引用

在新的会话中：

```
Continue from where we left off with the user authentication feature
```

AI will:
1. Load MEMORY.md
2. Search for "authentication" context
3. Resume work seamlessly

## 进阶配置

### 自定义 Embedding 模型

```json
{
  "memorySearch": {
    "embeddingModel": "text-embedding-3-large",  // Better quality
    "chunkSize": 512,
    "overlap": 50
  }
}
```

### 调整 Flush 阈值

```json
{
  "memoryFlush": {
    "threshold": 0.7  // Flush earlier
  }
}
```

### 添加持久知识

在 `.memory/knowledge/` 创建文件：

```markdown
# API Patterns

## Authentication
- Use JWT tokens
- Refresh every 24 hours
- Store in httpOnly cookies

## Error Handling
- Use standardized error codes
- Include request ID in responses
- Log all errors with context
```

## 故障排除

### Memory Search 不工作

1. Check embedding API key
2. Verify `.memory/` directory exists
3. Run: `openclaw memory index`

### Flush 太频繁

1. Increase threshold to 0.85
2. Check for excessive logging
3. Review context usage patterns

### 丢失重要信息

1. Add to `preserveContext` array
2. Manually save to `.memory/decisions/`
3. Update MEMORY.md explicitly

## 相关指南

- [agent-swarm.md](agent-swarm.md) - Agent 协作需要良好记忆
- [monitor.md](monitor.md) - 监控记忆使用情况
- [cost-optimization.md](cost-optimization.md) - 优化记忆成本
