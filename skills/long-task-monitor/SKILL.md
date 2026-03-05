---
name: long-task-monitor
description: 长任务监控方案 V2。实现 Worker-Monitor 架构，Monitor 通过 hook-logger 日志监控 Worker 状态，每轮 10 分钟通过 Announce 汇报。采用主会话轮询机制（因子代理 sessions_send 限制）。推荐 OpenClaw 2.21+。触发词：长任务、监控任务、任务监控。
---

> **注意**：本 Skill 依赖 **hook-logger** 插件读取 Worker 状态，必须先安装。

当用户说"长任务"、"监控任务"、"执行训练"等需要长时间运行任务时使用此技能。

## 功能

实现长任务监控方案（V2）：
- 创建 Worker 执行长任务
- 创建 Monitor 监控 Worker 状态（每轮 10 分钟）
- 主会话轮询处理 Monitor 汇报
- 任务完成时自动清理 Worker/Monitor sessions

## English Description

**Long-running task monitoring solution (V2).** Implements Worker-Monitor architecture: Monitor tracks Worker status via hook-logger logs, reports to main session every 10 minutes via Announce. Uses main session polling mechanism due to subagent sessions_send limitation. Recommended for OpenClaw v2.21+.

**Note:** This skill is primarily designed for Chinese users, but the monitor/worker mechanism can be implemented independently by referring to `long-task-monitor-plan.md` in the skill folder.

**Trigger:** "长任务", "监控任务", "任务监控"

## 使用前提

### 1. 安装 hook-logger 插件

本方案依赖 hook-logger 插件读取 Worker 状态，必须先安装：

```bash
# 安装 hook-logger 插件
openclaw plugins install @scotthuang/hook-logger

# 或手动安装
cd ~/.openclaw/extensions/hook-logger
npm install
```

**注意**：确保 hook-logger 已更新到支持 `sessionKey` 记录的版本（用于过滤特定 Worker 的日志）。

### 2. 无需额外权限配置

- Monitor → 主会话：Announce（自动）
- 主会话 → Worker：sessions_send（parent→child 默认允许）

## 使用方式

### 启动长任务流程

```bash
# 1. 创建任务
node ~/.openclaw/workspace/skills/long-task-monitor/long-task.js start "任务描述" "worker命令"

# 2. 启动 Worker（获取 session key 后）
sessions_spawn(task="...", label="worker-xxx", cleanup="keep")

# 3. 更新 Worker Session Key
node long-task.js update <task_id> worker "<sessionKey>"

# 4. 启动 Monitor
sessions_spawn(task="...", label="monitor-xxx", cleanup="delete")

# 5. 更新 Monitor Session Key
node long-task.js update <task_id> monitor "<sessionKey>"

# 6. 任务完成时手动清理
node long-task.js complete <task_id> "结果描述"
```

### 快捷命令

```bash
# 创建任务
node long-task.js start "描述" "worker任务"

# 更新 Worker Session Key
node long-task.js update <task_id> worker "<sessionKey>"

# 更新 Monitor Session Key
node long-task.js update <task_id> monitor "<sessionKey>"

# 生成 Worker 启动命令
node long-task.js worker-command <task_id> "worker任务"

# 生成 Monitor 启动命令
node long-task.js monitor-command <task_id> <worker_session_key> 1

# 标记任务完成并清理 sessions
node long-task.js complete <task_id> "结果描述"

# 查看任务状态
node long-task.js status
```

## 任务文件夹结构

```
~/.openclaw/workspace/long-tasks/<task-id>/
├── task.json             # 任务信息（包含 workerSessionKey, monitorSessionKey）
├── status.json           # 最终状态（完成后）
└── monitor-rounds/       # Monitor 轮次记录
    ├── current-round.json # 当前轮次记录
    └── round-1.json      # 第一轮记录
```

## task.json 字段说明

```json
{
  "taskId": "task-xxx",
  "description": "任务描述",
  "workerTask": "pip install torch",
  "workerSessionKey": "agent:main:subagent:xxx",
  "monitorSessionKey": "agent:main:subagent:yyy",
  "createdAt": "2026-02-22T10:00:00Z",
  "status": "running",
  "monitorRound": 1,
  "workerRestartCount": 0
}
```

## Monitor 行为

1. **定期记录** - 写入 monitor-rounds/current-round.json（注：实际取决于执行频率）
2. **10 分钟到** - Announce 返回结果
3. **检测完成** - 发现 Worker agent_end 事件时返回
4. **检测挂掉** - 超过 5 分钟无日志时返回

## 轮询逻辑

| 轮次 | 行为 |
|------|------|
| 1-5 | 自动继续下一轮监控 |
| 6+ | 询问用户是否继续 |

## 注意事项

### 1. 任务完成时需要手动清理

当前版本需要手动执行 `complete` 命令清理 sessions：
```bash
node long-task.js complete <task_id> "结果描述"
```

### 2. Monitor 轮次日志

Monitor 尝试每分钟记录状态，但实际频率取决于 Worker 执行速度。如果 Worker 执行很快，可能只记录 1-2 次。

### 3. Session Key 更新

spawn Worker/Monitor 后，必须手动更新 task.json：
- 获取 Worker Session Key → 更新
- 获取 Monitor Session Key → 更新

### 4. 任务完成判断

- Monitor 会检测 `agent_end` 事件判断 Worker 是否完成
- 如果 Worker 已完成，Monitor 会返回"已完成"状态
- 主会话收到后需要手动执行 `complete` 清理

## 已知限制

1. **complete 命令有 bug** - 当前版本可能报 ReferenceError，需手动清理 sessions
2. **无法自动检测 Worker 完成** - 需要等待 Monitor 下一轮汇报
3. **Session Key 需要手动更新** - 无法自动获取

## 发布更新

如果修改了 skill：
```bash
cd ~/.openclaw/workspace/skills/long-task-monitor
# 未来如有 npm 包需求
```

## ⚠️ 安全说明

本 skill 已做安全加固：
- 使用 `execFile` + 参数数组防止命令注入
- 所有用户输入经过过滤（只允许安全字符，包含 `:` 用于 session keys）
- 依赖 `hook-logger` 插件，请确保来源可信

## ⚠️ 已知限制

- Monitor Agent 需要使用 exec 工具执行 shell 命令（写入监控日志），这是架构固有限制
- Session Key 必须包含 `:` 字符（如 `agent:main:subagent:xxx`），已修复过滤函数允许此字符
