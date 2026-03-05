---
name: linkedin-human-warmup
description: Human-like LinkedIn warmup for new/cold accounts via AdsPower+CDP. Features non-deterministic behavior scripts, connect preconditions based on browsing intent, strict stop-on-risk, and session memory. Use when running LinkedIn daily warmup sessions.
---

# linkedin-human-warmup

面向 LinkedIn 新号/冷号的「拟人化养号」Skill。

目标：让账号行为更像真实用户的长期分布（意图链路、犹豫/返回/走神、被动增长），而不是每天稳定产出 connect。

## Inputs

- `user_id`：AdsPower profile id（也是 browser profile 名称）
- `cdp_port`：CDP 调试端口

## Core workflow

按以下顺序执行，在剧本选择和具体行为上自主决策。

### 1) 读取记忆

- 读 `memory/linkedin/MEMORY.md`（账号全貌：状态、累计数据、风控记录、当前约束、内容偏好）
- 读最近 5 天的 `memory/linkedin/YYYY-MM-DD.md`（含今天，用于判断近期剧本分布和 connect 频率）
- **首次运行**：若 `memory/linkedin/` 不存在或为空，视为全新账号，默认选择保守剧本（PureFeed / DistractedWander），本次 0 connect

> 记忆决定行为边界：如果记忆显示近期风险偏高或处于冷却期，本次强制 0 connect。

### 2) 选择剧本

- 从 `references/behavior-scripts.md` 自主选择一个剧本
- 选择时综合考虑：记忆中的近期行为分布、距上次 connect 的天数、风险状态
- 允许"本次什么都不做就退出"（这是拟人化的一部分）

### 3) 写 plan

- 用自然语言写 5-10 步 plan
- plan 中**停留/滚动/hover/返回/中断**至少出现一种
- plan 允许以"什么都不做"或"只看不动"结束

### 4) 启动浏览器 → 执行 → 关闭浏览器

- **必须先通过脚本启动 AdsPower 浏览器**，再连接 CDP、检测登录、按 plan 行动、最后关闭浏览器
- **重要：所有 browser 工具调用必须全程指定 `profile=<USER_ID>`，确保操作始终在目标实例中执行**
- 具体操作步骤见 `references/browser-ops.md`
- 任何一步出现风控信号：立刻停止（见 `references/risk-signals.md`）

### 5) 写入记忆

- 每次执行结束都写 `memory/linkedin/YYYY-MM-DD.md`（哪怕 0 操作）
- 用 **自然语言** 写两三句话，像日记不像工单（严格参照 `references/memory-spec.md` 中的日志示例格式）
- `memory/linkedin/MEMORY.md` 自主判断是否需要更新

### 6) 输出报告

简短汇报即可，包含：你的名字、剧本、做了什么、connect 数、风控状态、浏览器是否已关闭。不要反问用户下次该怎么做——你自主决策。

## Hard rules（不可违反）

- **风控优先**：出现验证码/身份验证/异常活动警告 → 立即停止并关闭浏览器
- **禁止 KPI 行为**：不要为了完成 connect 指标去找人加
- **Connect 需要证据链**：connect 前必须有浏览意图（内容/推荐触发 → profile 浏览 → 决策）
- **Note 不强制**：遇到限制就记录，不用纠结

## References（按需读取）

- `references/browser-ops.md`：浏览器启动/连接/登录/关闭操作（执行 Step 4 时读）
- `references/behavior-scripts.md`：剧本库（选择剧本时读）
- `references/risk-signals.md`：风控信号与停止策略（执行前或遇到异常时读）
- `references/memory-spec.md`：记忆写法规范与日志示例（写日志时读）
