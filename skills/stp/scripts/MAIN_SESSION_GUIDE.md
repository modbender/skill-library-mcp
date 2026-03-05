# STP V2 主会话执行指南

## 完整流程

当你收到一个 STP 任务时，按照以下步骤执行：

---

### 第一步：生成计划书

用户输入任务后，你需要：

1. **分析任务**，生成计划书（Markdown 格式）
2. **保存到 task-list**： `~/.openclaw/workspace/task-list/<任务名>-<日期>.md`
3. **展示给用户确认**

**计划书模板**：

```markdown
# 任务名称

## 任务描述
用户需求的简要描述

## 技术方案
- 使用的工具/库/API

## 全局设置
- 步骤超时时间：[无超时 / N 分钟]

## 核心执行步骤
- [ ] 步骤 1：xxx
    - **执行 Prompt**: 给执行子代理的具体指令
    - **检验标准**: 给检验子代理的验证条件
- [ ] 步骤 2：xxx
    - **执行 Prompt**: xxx
    - **检验标准**: xxx

## 预期产出
- xxx
```

---

### 第二步：等待用户确认

展示计划书后，询问用户：

```
📋 任务计划书已生成

任务名称：xxx
步骤数：N
超时设置：xxx

请确认：
- 输入 "ok" 或 "确认" → 开始执行
- 输入 "取消" → 放弃
- 输入 "修改" → 调整计划
- 输入 "超时 30" → 设置步骤超时 30 分钟
```

---

### 第三步：启动任务

用户确认后：

```bash
# 1. 初始化任务目录
python3 ~/.openclaw/workspace/skills/stp/scripts/stp_orchestrator.py start <计划书路径>

# 获取返回的 task_id，例如：20
```

---

### 第四步：执行步骤循环

对于每个步骤，执行以下流程：

#### 4.1 获取下一个待执行步骤

```bash
python3 ~/.openclaw/workspace/skills/stp/scripts/stp_orchestrator.py status <task_id>
```

找到状态为"待执行"的步骤。

#### 4.2 创建执行子代理

```bash
sessions_spawn(
  task="<步骤的执行 Prompt>

工作目录：~/.openclaw/workspace/tasks/task-<ID>/temp

完成后请用英文返回：
- SUCCESS: <简要说明> - 如果成功
- FAILED: <失败原因> - 如果失败",
  label="task-<ID>-step-<N>-exec",
  cleanup="keep",
  mode="run"
)
```

#### 4.3 更新步骤状态

```bash
python3 ~/.openclaw/workspace/skills/stp/scripts/stp_orchestrator.py update <task_id> <步骤号> 执行中 "<子代理sessionKey>" "<runId>"
```

#### 4.4 ⚠️ 关键：立即返回，不要轮询等待！

```
✅ 任务已启动 (task-<ID>)
步骤 <N>：<步骤描述> (执行中)
你可以继续做其他事，我会通过消息通知你进度
```

**❌ 错误做法**：
```python
# 不要这样等待！
while True:
    time.sleep(10)
    history = sessions_history(...)
    if done:
        break
```

**✅ 正确做法**：
创建子代理后**立即返回**，然后继续与用户对话。当收到子代理的 **announce 消息** 时，系统会自动推送给你，你再继续处理。

---

#### 4.5 处理子代理完成（收到 announce）

当子代理完成时，你会收到系统消息：
> `[System Message] A subagent task "task-XX-step-N-exec" just completed successfully.`

然后你需要：
1. 解析执行结果
2. 更新状态为"待检验"
3. 创建检验子代理
4. **再次立即返回**（不要等待检验子代理完成）

---

### 第五步：处理执行完成（收到 announce）⚠️

当执行子代理完成任务，会收到系统消息（不是立即自动回复，是系统推送给你）：

> `[System Message] A subagent task "task-XX-step-N-exec" just completed successfully.`

**这时候再继续处理**，不要提前轮询等待！

#### 5.1 解析执行结果

从消息中提取：
- 执行结果（SUCCESS / FAILED）
- 执行的输出内容

#### 5.2 如果执行失败

直接询问用户：

```
⚠️ 步骤 <N> 执行失败

失败原因：<xxx>

请选择：
1. 调整方案 → 修改后续步骤计划
2. 重试 → 重新创建执行子代理
3. 终止 → 结束整个任务
```

#### 5.3 如果执行成功

更新状态并创建检验子代理：

```bash
# 更新为待检验
python3 ~/.openclaw/workspace/skills/stp/scripts/stp_orchestrator.py update <task_id> <步骤号> 待检验
```

```bash
# 创建检验子代理
sessions_spawn(
  task="请根据以下检验标准判断步骤是否成功完成。

检验标准：<步骤的检验标准>

执行结果：
<执行子代理的输出>

请严格按以下格式返回：
PASS - <原因> - 如果检验通过
FAIL - <原因> - 如果检验不通过>",
  label="task-<ID>-step-<N>-verify",
  cleanup="keep",
  mode="run"
)
```

更新状态：

```bash
python3 ~/.openclaw/workspace/skills/stp/scripts/stp_orchestrator.py update <task_id> <步骤号> 检验中 "<子代理sessionKey>" "<runId>"
```

**然后立即返回**，等检验子代理的 announce 消息再继续。

---

### 第六步：处理检验完成（收到 announce）⚠️

#### 6.1 解析检验结果

从 announce 消息中提取：
- PASS / FAIL
- 原因

#### 6.2 如果检验失败

询问用户：

```
⚠️ 步骤 <N> 检验不通过

检验反馈：<xxx>

请选择：
1. 调整方案 → 修改后续步骤计划
2. 重试 → 重新执行当前步骤
3. 终止 → 结束整个任务
```

#### 6.3 如果检验通过

标记步骤完成，继续下一步：

```bash
python3 ~/.openclaw/workspace/skills/stp/scripts/stp_orchestrator.py update <task_id> <步骤号> 已完成
```

然后回到 **4.1**，继续执行下一个步骤。

如果所有步骤完成：

```
✅ 任务完成！task-<ID>

最终结果：
<结果汇总>
```

---

### Heartbeat 检查

当主会话收到 heartbeat poll 时：

```bash
# 检查任务状态
python3 ~/.openclaw/workspace/skills/stp/scripts/stp_orchestrator.py heartbeat <task_id>
```

返回活跃子代理列表后，对每个子代理：

```bash
# 获取子代理历史
sessions_history(sessionKey="<子代理sessionKey>", limit=5)
```

检查最后一条消息：
- 如果是 tool 类型且执行时间 > 30 分钟 → 增加超时计数
- 如果超时计数 >= 2 → 通知用户可能挂死

```
⚠️ 步骤 <N> 可能已挂死

执行子代理已等待 30+ 分钟无响应
Tool: <tool名称>

请选择：
1. 继续等待 → 再次等待 10 分钟
2. 重试 → 终止当前子代理，重新执行
3. 终止 → 结束整个任务
```

---

### 任务中断

用户输入：`中断 task-<ID>` 或 `中断 <任务名>`

```bash
# 中断任务
python3 ~/.openclaw/workspace/skills/stp/scripts/stp_orchestrator.py interrupt <task_id>
```

然后使用 `subagents` 工具 kill 所有子代理。

```
🛑 任务已中断
```

---

## 快速参考命令

```bash
# 启动任务
python3 ~/.openclaw/workspace/skills/stp/scripts/stp_orchestrator.py start <计划书>

# 查看状态
python3 ~/.openclaw/workspace/skills/stp/scripts/stp_orchestrator.py status <task_id>

# 检查 heartbeat
python3 ~/.openclaw/workspace/skills/stp/scripts/stp_orchestrator.py heartbeat <task_id>

# 更新步骤状态
python3 ~/.openclaw/workspace/skills/stp/scripts/stp_orchestrator.py update <task_id> <步骤> <状态> [exec_subagent] [exec_runid]

# 增加超时计数
python3 ~/.openclaw/workspace/skills/stp/scripts/stp_orchestrator.py timeout <task_id> <步骤> <exec|verify>

# 中断任务
python3 ~/.openclaw/workspace/skills/stp/scripts/stp_orchestrator.py interrupt <task_id>
```
