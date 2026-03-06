---
name: task-persistence
description: Task continuity, session snapshots, and gateway restart recovery. Use when starting long-running tasks (register them), after gateway restart (check for interrupted tasks), or when user asks about task status/recovery. Trigger on "resume", "任务恢复", "重启后", "未完成任务", or before/after any multi-step operation.
metadata:
  {
    "openclaw":
      {
        "emoji": "🔄",
        "requires": { "bins": ["python3"] }
      }
  }
---

# Task Persistence

会话状态管理、任务持久化和网关重启恢复。

## 核心场景

| 触发条件 | 动作 |
|---------|------|
| 网关刚重启 | 运行 `check-restart`，汇报恢复状态 |
| 开始长时间任务 | 用 `task_manager.py add` 注册任务 |
| 用户问"有没有未完成的任务" | 运行 `task_manager.py list` |
| 任务完成 | 运行 `task_manager.py complete` |
| 任务被中断 | 运行 `task_manager.py recover` |

## 变量说明

所有脚本中的 `{baseDir}` = 本技能的目录路径（SKILL.md 所在目录）。
工作区路径从环境变量 `OPENCLAW_WORKSPACE` 读取，默认 `/workspace`。

## 快速命令

### 网关重启后检查（每次重启后必须执行）
```bash
python3 {baseDir}/scripts/main.py --mode check-restart --workspace /workspace
```

### 查看所有活跃任务
```bash
python3 {baseDir}/scripts/task_manager.py --action list --workspace /workspace
```

### 注册新任务（开始长时间操作前）
```bash
python3 {baseDir}/scripts/task_manager.py \
  --action add \
  --task-id "task_$(date +%s)" \
  --task-type "file_processing" \
  --description "处理大量文件" \
  --priority normal \
  --workspace /workspace
```

### 标记任务完成
```bash
python3 {baseDir}/scripts/task_manager.py \
  --action complete \
  --task-id <task_id> \
  --workspace /workspace
```

### 从崩溃/重启中恢复任务
```bash
python3 {baseDir}/scripts/task_manager.py \
  --action recover \
  --workspace /workspace
```

### 任务队列状态
```bash
python3 {baseDir}/scripts/task_manager.py --action status --workspace /workspace
```

### 会话快照（保存当前状态）
```bash
python3 {baseDir}/scripts/session_snapshot.py \
  --workspace /workspace \
  --action list
```

### 网关监控状态
```bash
python3 {baseDir}/scripts/main.py --mode status --workspace /workspace
```

## 重启后工作流

当 heartbeat 或用户提到"网关重启"时，执行：

1. `python3 {baseDir}/scripts/main.py --mode check-restart --workspace /workspace`
2. 解析输出中的 `active_tasks` 和 `recovered_tasks`
3. 向用户汇报：哪些任务被恢复、哪些需要手动继续

## 文件结构

```
/workspace/
  tasks/
    task_queue.json       # 任务队列
    completed/            # 已完成任务
    failed/               # 失败任务
  memory/
    session_snapshots/    # 会话快照
  persistence/
    active_tasks.json     # 持久化任务
    gateway_state.json    # 网关状态
```

## 注意事项

- 脚本使用标准库，无需额外安装依赖
- 所有数据持久化在 workspace 目录下，重启后不会丢失
- `task_manager.py` 是统一入口，推荐优先使用
- `gateway_monitor.py` 的后台监控模式（`full` mode）在沙箱中不适用，用 `check-restart` 代替
