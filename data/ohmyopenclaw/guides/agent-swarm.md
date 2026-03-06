# Agent Swarm Architecture Guide

## 适用场景

- 复杂项目，需要并行处理多个任务
- 想要利用不同 AI 模型的专长（Codex、Claude Code、Gemini）
- 需要任务追踪和监控机制
- 希望实现自动化工作流

## 配置变更

本指南将修改以下文件：

1. `workspace/AGENTS.md` - 添加任务追踪规则
2. `openclaw.json` - 配置 subagents 和 heartbeat
3. `workspace/.tasks/` - 创建任务目录结构

## 架构说明

### Orchestrator vs Workers

```
┌─────────────────────────────────────┐
│        Orchestrator Agent           │
│  (Main context, task distribution)  │
│                                     │
│  - Context: ~100K tokens            │
│  - Role: Plan, delegate, review     │
│  - Model: claude-sonnet-4           │
└──────────┬──────────────────────────┘
           │
           │ spawn workers
           │
    ┌──────┴──────┬──────────┬──────────┐
    │             │          │          │
┌───▼────┐  ┌────▼───┐  ┌───▼────┐  ┌──▼─────┐
│ Codex  │  │ Claude │  │Gemini  │  │ Custom │
│ Worker │  │  Code  │  │ Worker │  │ Worker │
│        │  │        │  │        │  │        │
│ Code   │  │CLI     │  │Research│  │Special │
│ Gen    │  │Tasks   │  │Analysis│  │Tasks   │
└────────┘  └────────┘  └────────┘  └────────┘
```

### Context Window 分工策略

| Agent Type | Context Size | Best For |
|------------|--------------|----------|
| Orchestrator | 100K-200K tokens | Planning, coordination, review |
| Codex Worker | 8K-32K tokens | Code generation, file editing |
| Claude Code Worker | 32K-100K tokens | CLI tasks, system operations |
| Gemini Worker | 32K-128K tokens | Research, analysis, multimodal |

### Task Tracking Format

任务文件存储在 `.tasks/active/<task-id>.json`:

```json
{
  "id": "task-20260227-001",
  "status": "in_progress",
  "agent": "codex-worker-1",
  "agentType": "codex",
  "created": "2026-02-27T10:00:00Z",
  "updated": "2026-02-27T10:05:00Z",
  "description": "Implement user authentication API",
  "prompt": "Create authentication endpoints with JWT support...",
  "context": {
    "files": ["src/auth/*.ts"],
    "dependencies": ["jsonwebtoken", "bcrypt"]
  },
  "result": null,
  "error": null,
  "retryCount": 0
}
```

### Definition of Done

任务完成标准：

- [ ] 功能实现完成
- [ ] 单元测试通过
- [ ] 代码审查完成
- [ ] 文档更新
- [ ] 部署/合并完成

### Ralph Loop V2

监控和恢复循环：

```
┌─────────────────────────────────────┐
│         Ralph Loop V2               │
│                                     │
│  1. Heartbeat (every 5 min)         │
│     ├─ Check .tasks/active/*.json   │
│     ├─ Update task status           │
│     └─ Scan for new issues          │
│                                     │
│  2. Task Recovery                   │
│     ├─ Detect failed tasks          │
│     ├─ Analyze failure              │
│     ├─ Improve prompt               │
│     └─ Retry with better context    │
│                                     │
│  3. Proactive Work                  │
│     ├─ Scan for TODOs in code       │
│     ├─ Check for open issues        │
│     └─ Spawn agents autonomously    │
└─────────────────────────────────────┘
```

### Agent Selection Guide

选择合适的 Worker：

| Task Type | Recommended Agent | Reason |
|-----------|-------------------|--------|
| 代码生成 | Codex | 专注代码，快速响应 |
| CLI 操作 | Claude Code | 原生 CLI 支持 |
| 研究分析 | Gemini | 大上下文，多模态 |
| 复杂推理 | Claude Sonnet | 强推理能力 |
| 快速原型 | Claude Haiku | 低延迟，低成本 |

## 安装命令

执行以下步骤：

### 1. 更新 openclaw.json

```bash
# AI will update openclaw.json with:
# - subagents.maxConcurrent: 3
# - heartbeat.enabled: true
# - heartbeat.interval: 300000 (5 minutes)
# - cron.enabled: true
```

### 2. 创建任务目录

```bash
mkdir -p ~/.openclaw/workspace/.tasks/active
mkdir -p ~/.openclaw/workspace/.tasks/completed
```

### 3. 更新 AGENTS.md

将以下内容追加到 `workspace/AGENTS.md`:

```markdown
## Agent Swarm Configuration

### Worker Spawning

When delegating tasks to workers:
1. Create task file in `.tasks/active/<task-id>.json`
2. Use `sessions_spawn` to create worker
3. Pass task-id as parameter
4. Monitor via heartbeat

### Task Management

- **Active Tasks**: `.tasks/active/*.json`
- **Completed Tasks**: `.tasks/completed/*.json`
- **Task ID Format**: `task-YYYYMMDD-NNN`

### Worker Types

- **codex**: Code generation and editing
- **claude-code**: CLI and system operations
- **gemini**: Research and analysis

### Monitoring

Heartbeat runs every 5 minutes:
- Check active task status
- Recover failed tasks
- Discover new work
```

## 验证步骤

### 1. 验证配置

```bash
# Check openclaw.json
cat ~/.openclaw/openclaw.json | grep -A 5 "subagents\|heartbeat"
```

Expected output:
```json
"subagents": {
  "maxConcurrent": 3,
  "timeout": 600000
},
"heartbeat": {
  "enabled": true,
  "interval": 300000
}
```

### 2. 验证目录结构

```bash
ls -la ~/.openclaw/workspace/.tasks/
```

Expected:
```
drwxr-xr-x  active/
drwxr-xr-x  completed/
```

### 3. 测试 Worker Spawn

Tell the AI:
```
Spawn a codex worker to create a simple hello world function
```

Expected behavior:
- AI creates task file in `.tasks/active/`
- AI spawns worker agent
- Worker completes task
- Task moved to `.tasks/completed/`

### 4. 测试 Heartbeat

```bash
# Trigger heartbeat manually
openclaw heartbeat
```

Expected:
- AI checks active tasks
- AI updates task status
- AI reports any issues

## 示例用法

### 并行代码生成

```
I need to implement 3 API endpoints:
1. GET /users - list users
2. POST /users - create user
3. DELETE /users/:id - delete user

Spawn separate workers for each endpoint.
```

### 任务监控

```
Show me all active tasks and their status
```

### 错误恢复

```
Check if any tasks failed and retry them
```

## 进阶配置

### 自定义 Worker 模板

在 `workspace/.workers/` 创建模板：

```
.workspace/.workers/
├── codex-template.md
├── claude-code-template.md
└── gemini-template.md
```

### 调整并发数

修改 `openclaw.json`:
```json
{
  "subagents": {
    "maxConcurrent": 5  // Increase for more parallelism
  }
}
```

### 调整监控频率

```json
{
  "heartbeat": {
    "interval": 60000  // Check every minute
  }
}
```

## 故障排除

### Worker 无响应

1. Check task file: `cat .tasks/active/<task-id>.json`
2. Check OpenClaw logs
3. Kill stuck worker and retry

### 任务堆积

1. Check maxConcurrent setting
2. Clear completed tasks: `mv .tasks/active/* .tasks/completed/`
3. Restart OpenClaw

### Context Overflow

1. Reduce worker context size
2. Use haiku for simple tasks
3. Implement task chunking

## 相关指南

- [memory-optimized.md](memory-optimized.md) - 增强记忆能力
- [monitor.md](monitor.md) - 详细监控配置
- [cost-optimization.md](cost-optimization.md) - 优化成本
