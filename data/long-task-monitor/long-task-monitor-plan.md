# 长任务监控方案（V2）

## 背景

在训练模型等长时间运行的任务中，存在以下问题：
1. 任务执行时间可能长达数十分钟甚至数小时
2. 主会话无法了解任务的实时进度
3. 需要知道 Worker 是否卡住/完成/失败

## 相关技术背景

### 为什么采用"主会话轮询"架构？

在调研 OpenClaw v2.21 版本时，发现以下限制：

1. **子代理无法使用 sessions_send**
   - 子代理有硬编码的 `SUBAGENT_TOOL_DENY_ALWAYS` 列表
   - `sessions_send` 被默认禁止使用
   - 即使配置 `tools.sessions.visibility: "all"` 也无法覆盖
   - 官方建议使用 Announce 机制

2. **子代理无法使用 cron**
   - `cron` 也在 `SUBAGENT_TOOL_DENY_ALWAYS` 列表中
   - 无法主动定时触发任务

3. **Announce 机制限制**
   - 只能触发一次（任务完成时）
   - 无法定期触发

### 解决方案

因此采用**主会话轮询架构**：
- Monitor 通过 Announce 返回结果
- 主会话在收到汇报后，决定下一轮监控
- 利用"多轮对话"实现定期监控

### 依赖：hook-logger 插件

本方案依赖 `hook-logger` 插件来读取 Worker 的工作状态。

#### 安装指引

```bash
# 安装 hook-logger 插件
openclaw plugins install @scotthuang/hook-logger

# 或手动安装
cd ~/.openclaw/extensions/hook-logger
npm install
```

#### 插件配置

hook-logger 会记录以下事件：
- `before_tool_call` / `after_tool_call` — 工具调用
- `session_start` / `session_end` — 会话起止
- `agent_end` — Agent 结束（包含 success/error 状态）

日志路径：`~/.openclaw/workspace/logs/hook-logger/YYYY-MM-DD.log`

> **注意**：确保 hook-logger 已更新到支持 `sessionKey` 记录的版本，以便 Monitor 能够过滤特定 Worker 的日志。

## 角色职责

### 1. Worker（工作子代理）

- **职责**：只执行分配的长任务，什么都不管
- **启动方式**：主会话 spawn 时创建
- **状态**：`cleanup=keep`（任务完成后会话保留）
- **行为**：正常调用工具执行任务，不与其他代理通信

### 2. Monitor（监控子代理）

- **职责**：监控 Worker 的工作状态
- **监控方式**：通过 hook-logger 日志读取 Worker 状态
- **监控时长**：每轮 10 分钟
- **汇报时机**：
  - 监控时间到了（10分钟）
  - 监控到 Worker 已完成
  - 监控到 Worker 已挂掉（超过 5 分钟无日志）
- **汇报方式**：通过 Announce 机制返回给主会话

### 3. 主会话（编排者）

- **职责**：创建 Worker、创建 Monitor、管理监控循环
- **任务管理**：在 `~/.openclaw/workspace/long-tasks/` 下为每个任务创建子文件夹

## 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        主会话                                │
│  - 创建 Worker                                               │
│  - 创建 Monitor（第一轮）                                    │
│  - 处理 Monitor 汇报                                        │
│  - 决定下一步操作                                            │
└────────────────────────────┬────────────────────────────────┘
                             │
        ┌────────────────────┴────────────────────┐
        │                                           │
        ▼                                           ▼
┌───────────────────┐                     ┌───────────────────┐
│    Worker        │                     │    Monitor        │
│ (工作子代理)      │                     │ (监控子代理)       │
│                   │                     │                    │
│ - 执行长任务      │                     │ - 读取 hook-logger │
│ - 不主动汇报      │                     │ - 分析 Worker 状态 │
│ - cleanup=keep   │                     │ - 10 分钟监控      │
└───────────────────┘                     │ - Announce 汇报    │
                                          └────────┬──────────┘
                                                   │
                                                   │ Announce
                                                   ▼
                                          ┌───────────────────┐
                                          │    主会话收到      │
                                          │   (作为用户消息)   │
                                          └───────────────────┘
```

## 工作流程

### 第一轮

```
1. 主会话创建 Worker
   sessions_spawn(task="训练任务", label="worker", cleanup="keep")

2. 主会话创建 Monitor（第一轮）
   sessions_spawn(task="监控 Worker 10分钟", label="monitor")

3. Monitor 执行监控
   - 读取 hook-logger 日志
   - 每 1 分钟记录一次 Worker 状态
   - 10 分钟到、或 Worker 完成、或 Worker 挂掉 → Announce 汇报

4. 主会话收到 Monitor 汇报
```

### 后续轮次（根据 Monitor 汇报）

#### 场景 1：Worker 任务进行中

```
主会话收到：Worker 还在运行

处理：
  - 前 5 轮：自动回答"继续监控"
  - 第 6 轮开始：询问用户"是否继续监控"
  
创建下一轮 Monitor：
  sessions_spawn(task="继续监控 Worker 10分钟", label="monitor")
```

#### 场景 2：Worker 任务挂掉

```
主会话收到：Worker 疑似挂掉（超过 5 分钟无日志）

处理：
  - 用 sessions_send 向 Worker 发送继续指令
  - 最多重试 5 次
  - 5 次后仍失败 → 询问用户"是否继续让 Worker 工作"

Worker 恢复后：
  创建下一轮 Monitor 继续监控
```

#### 场景 3：Worker 任务成功

```
主会话收到：Worker 任务完成

处理：
  - 向用户汇报任务成功
  - 记录任务完成信息到任务文件夹
```

## 任务文件夹结构

每个长任务一个文件夹：

```
~/.openclaw/workspace/long-tasks/<task-id>/
├── task.json           # 任务信息
├── worker-session.json # Worker Session 信息
├── monitor-rounds/     # Monitor 轮次记录
│   ├── round-1.json
│   ├── round-2.json
│   └── ...
└── status.json         # 最终状态
```

### task.json 示例

```json
{
  "taskId": "train-model-001",
  "description": "训练图像分类模型",
  "workerSessionKey": "agent:main:subagent:xxx",
  "monitorSessionKey": "agent:main:subagent:yyy",
  "createdAt": "2026-02-22T10:00:00Z",
  "status": "running",
  "monitorRound": 0,
  "workerRestartCount": 0
}
```

### round-X.json 示例

```json
{
  "round": 1,
  "startedAt": "2026-02-22T10:00:00Z",
  "endedAt": "2026-02-22T10:10:00Z",
  "workerStatus": "running",
  "lastActivity": "执行 Epoch 5/100",
  "logs": [
    {"time": "10:01:00", "event": "Worker 执行中"},
    {"time": "10:05:00", "event": "Epoch 3 完成"}
  ]
}
```

### status.json 示例（任务完成后）

```json
{
  "taskId": "train-model-001",
  "status": "completed",
  "startedAt": "2026-02-22T10:00:00Z",
  "endedAt": "2026-02-22T12:30:00Z",
  "durationMinutes": 150,
  "totalMonitorRounds": 6,
  "workerRestartCount": 2,
  "result": "训练完成，模型准确率 95%"
}
```

## Monitor Prompt 模板

```python
"""
你是 Monitor Agent，负责监控长时间运行的任务。

## 监控目标
- Worker Session Key: {worker_session_key}
- Worker 任务: {worker_task_description}
- 任务文件夹: {task_folder_path}

## 监控方式
1. 读取 hook-logger 日志
   文件: ~/.openclaw/workspace/logs/hook-logger/YYYY-MM-DD.log
2. 过滤目标 Worker 的日志（通过 sessionKey 过滤）
3. 分析执行状态

## 监控任务

### 1. 定期记录（每 1 分钟）
- 记录 Worker 当前状态
- 记录最后活动的工具调用

### 2. 状态判断
- **已完成**: 日志中有 `agent_end` 且 `success: true`
- **失败**: 日志中有 `agent_end` 且 `success: false`
- **疑似挂掉**: 超过 5 分钟无新日志
- **进行中**: 其他情况

### 3. 汇报时机
- 监控时间到（10分钟）
- 监控到 Worker 已完成
- 监控到 Worker 已挂掉

## 汇报格式（Announce）

请在最后明确说明以下信息，以便主会话恢复上下文：

### 汇报内容
```
## Monitor 汇报

### 任务信息
- 任务ID: {task_id}
- 监控轮次: {round}
- 当前轮次监控时长: {duration}分钟

### Worker 状态
- 状态: 运行中/已完成/失败/疑似挂掉
- 最后执行步骤: {last_step}
- 详细日志证据: {log_evidence}

### 下一步建议
- 建议操作: 继续监控 / 任务完成 / 需要人工介入

### 上下文参考
如主会话不清楚上下文，请读取: {task_folder_path}
```

## 重要规则
- 用 Announce 机制返回结果（无需调用任何工具）
- 每 1 分钟记录一次 Worker 状态到日志
- 10 分钟到必须返回结果
- 汇报中必须包含 task_id 和 round 信息
"""
```

## 主会话处理逻辑

```python
# 伪代码

# 全局变量
monitor_round = 0
worker_restart_count = 0
max_monitor_rounds = 5  # 5 轮后询问用户
max_worker_restarts = 5  # Worker 重试最多 5 次

# 处理 Monitor 汇报
def handle_monitor_report(report):
    # 恢复上下文：如果不清楚任务情况，从任务文件夹读取
    if not has_context():
        task_info = read(f"{report.task_folder}/task.json")
        monitor_round = task_info.get("monitor_round", 0)
        worker_restart_count = task_info.get("worker_restart_count", 0)
    
    if report.worker_status == "completed":
        # 场景 3：任务成功
        向用户汇报成功
        更新任务状态为 completed
        更新任务文件夹中的 status.json
        return
    
    if report.worker_status == "stuck":
        # 场景 2：Worker 挂掉
        if worker_restart_count < max_worker_restarts:
            # 自动重启 Worker
            sessions_send(worker_session_key, "继续工作")
            worker_restart_count += 1
            # 更新任务文件夹
            update(f"{task_folder}/task.json", {
                "worker_restart_count": worker_restart_count
            })
            # 继续监控
            spawn_monitor()
        else:
            # 询问用户
            向用户询问"是否继续让 Worker 工作"
        return
    
    # 场景 1：Worker 还在运行
    monitor_round += 1
    # 更新任务文件夹
    update(f"{task_folder}/task.json", {
        "monitor_round": monitor_round
    })
    
    if monitor_round <= max_monitor_rounds:
        # 前 5 轮自动继续
        spawn_monitor()
    else:
        # 第 6 轮询问用户
        向用户询问"是否继续监控"
```

## 实施步骤

### 1. 准备阶段
- [x] hook-logger 插件已安装并支持 sessionKey
- [x] sessions.visibility 配置已设置
- [ ] 创建任务管理脚本（long-tasks.js）

### 2. 实现阶段
- [ ] 实现 Worker 启动逻辑
- [ ] 实现 Monitor Prompt
- [ ] 实现主会话编排逻辑
- [ ] 实现任务文件夹管理

### 3. 测试阶段
- [ ] 测试 Worker 正常执行
- [ ] 测试 Monitor 监控
- [ ] 测试场景 1：任务进行中
- [ ] 测试场景 2：任务挂掉
- [ ] 测试场景 3：任务成功

## 依赖

本方案的通信机制：

| 通信方向 | 方式 | 是否需要特殊配置 |
|---------|------|----------------|
| Monitor → 主会话 | Announce（自动） | ❌ 不需要 |
| 主会话 → Worker | sessions_send（parent→child） | ❌ 不需要（tree visibility 默认包含） |

因此，**无需额外配置权限**。

### hook-logger 插件

确保 hook-logger 插件已安装并支持 sessionKey 记录。

插件发布在 npm：`@scotthuang/hook-logger`

本地修改源码路径：`~/.openclaw/extensions/hook-logger/`

发布命令：
```bash
cd ~/.openclaw/extensions/hook-logger
npm version patch
npm publish --access public
```
