---
name: context-guard
description: "防遗忘防卡顿的context管理协议。自动监控水位、分区管理、压缩前存档、压缩后恢复。适用于所有OpenClaw agent和sub-agent。在heartbeat或session启动时触发。"
version: 1.0.0
---

# Context Guard

全自动context管理 — 防遗忘、防卡顿、防token浪费。

融合了 context-sentinel（自动监控）、context-budgeting（分区+checkpoint）、context-recovery（压缩后恢复）三个方案的优点，去掉了它们的缺陷。

---

## 1. Context分区预算

每次session的context是有限资源，按以下比例分配：

| 分区 | 占比 | 内容 |
|------|------|------|
| 核心指令 | 10% | SOUL.md + USER.md + 当前任务目标 |
| 近期对话 | 40% | 最近5-10轮对话 |
| 决策日志 | 20% | "试了X，因为Y失败" 这类关键记录 |
| 背景知识 | 20% | MEMORY.md中与当前任务相关的片段 |
| 缓冲区 | 10% | 留给工具输出和突发需求 |

**原则：** 大段工具输出（JSON、网页内容等）提取关键信息后不要保留原文。Browser snapshot用完即弃。

---

## 2. 水位监控与行动

在每次回复前，agent应评估当前context水位并执行对应动作：

### 水位线

| 水位 | 状态 | 动作 |
|------|------|------|
| 0-40% | 🟢 安全 | 正常工作 |
| 40-50% | 🟡 注意 | 精简回复，避免大段输出，重活spawn sub-agent |
| 50-55% | 🟠 预警 | **立即执行存档流程**（见第3节） |
| 55-60% | 🔴 危险 | 存档完成 → 通知Russ执行 `/new` |
| 60%+ | 🚨 禁区 | 停止一切非存档操作，立即存档+通知 |

### 自动检查方法

在heartbeat或感觉context变大时，运行：

```
session_status
```

读取返回的context百分比，按上表行动。

### Model降级（可选）

如果Russ暂时无法 `/new`，agent可以自行降级model减缓context增长：

| 当前model | context > 50% | context > 60% |
|-----------|--------------|--------------|
| opus-4-6 | 切换到 sonnet | 停止工作，等reset |
| sonnet | 继续 | 停止工作，等reset |

降级命令：`session_status model=<model_name>`

---

## 3. 存档流程（Checkpoint）

到50%水位时**必须执行**，不需要等Russ确认：

### Step 1: STATUS.md — 任务断点

```markdown
# STATUS.md
Updated: YYYY-MM-DD HH:MM

## 当前任务
[在做什么]

## 进度
[做到哪了，关键步骤完成情况]

## 阻塞
[卡在哪 / 无]

## 下一步
[接下来该做什么，越具体越好]

## 关键数据
[地址/金额/TX hash/URL等，任何重启后需要的具体数据]
```

### Step 2: memory/YYYY-MM-DD.md — 当天日志

追加写入，不覆盖：
- 今天做了什么（关键决策和结果）
- 新发现的信息（合约地址、API endpoint等）
- 犯的错误和教训
- 只写重启后需要的信息，不写废话

### Step 3: MEMORY.md — 长期记忆（如有）

只在有长期价值的信息时更新：
- 新策略、新工具、新教训
- 钱包余额重大变动
- 重要决策和原因
- 人物关系、偏好变化

### Step 4: 通知Russ

存档完成后发一条消息：

> "总裁，context到X%了，已存好档（STATUS.md + memory已更新）。帮我 `/new` 🙏"

**注意：** Agent不能自己reset，必须Russ手动 `/new`。

### Step 5: 压缩后通知（必须）

如果context被系统自动压缩了，**恢复后第一条消息必须告诉Russ**：

> "刚刷新了，context从X%压缩了。记忆已从文件恢复，没丢东西。"

**这条规则没有例外。** 每次刷新都要通知。

---

## 4. 压缩后恢复（Recovery）

当新session启动或检测到context被压缩时，执行恢复流程：

### 触发条件
- Session以 `<summary>` 标签开始（自动压缩）
- 用户说"继续"、"刚才做到哪了"
- Agent感觉缺少上下文

### 恢复步骤

1. **读文件**（标准启动流程）：
   - `SOUL.md` → 我是谁
   - `USER.md` → 我服务谁
   - `MEMORY.md` → 长期记忆（仅主session）
   - `memory/YYYY-MM-DD.md` → 今天+昨天日志
   - `STATUS.md` → 进行中的任务
   - `HEARTBEAT.md` → 待检查事项

2. **读channel历史**（如果文件不够还原上下文）：
   ```
   message action=read limit=20
   ```
   从最近20条消息中提取：最后的用户请求、未完成的操作、关键URL/地址

3. **合成上下文**，用一句话内部确认：
   > "上次做到[X]，当前状态是[Y]，下一步是[Z]"

4. **继续工作**，不需要问用户"我们刚才在做什么"

---

## 5. Sub-Agent规则

### 什么时候spawn
- 浏览器操作（吃context最快）
- 长时间research / 大量网页抓取
- 任何预计消耗 >20% context的任务

### Sub-Agent也遵守本协议
- 同样的水位线和存档流程
- 做完任务 → 结果写文件 → 汇报主session → 结束
- **失败3次就停**，上报原因，不死循环

### 资源互斥
- 同一时间只有一个agent用browser profile "openclaw"
- 多个browser任务 → 排队执行，不并行

---

## 6. 绝对禁止

1. ❌ **只在聊天里说重要信息不写文件** — 聊天会压缩/丢失
2. ❌ **Context超60%还在做重操作** — 先存档先reset
3. ❌ **Sub-agent无限重试** — 3次失败就停
4. ❌ **说"我记住了"但没写文件** — 没写 = 没记
5. ❌ **多agent同时用同一个browser profile**
6. ❌ **大段JSON/HTML原文留在context里** — 提取关键信息后丢弃

---

## 7. Heartbeat集成

在 `HEARTBEAT.md` 中加入：

```markdown
### 🛡️ Context Guard（每次heartbeat必查）
1. `session_status` 检查context水位
2. 按水位线执行对应动作
3. 如果 >50%，执行存档流程
```

---

*v1.0.0 — 2026-02-12 by Echo*
*适用于所有OpenClaw agent及sub-agent*
