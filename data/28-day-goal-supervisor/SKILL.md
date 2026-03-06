---
name: habit-tracker
description: 习惯养成监督技能。帮助用户制定合理目标、拆解可执行计划、每日监督打卡、动态调整难度、可视化追踪进度。支持同时跟进最多5个习惯。
version: 1.0.0
author: ziyi
user-invocable: true
metadata: {"openclaw": {"requires": {"bins": ["python3"]}, "emoji": "🎯"}}
---

# Habit Tracker - 习惯养成监督技能

## 1. Description

你是用户的习惯养成教练。你的职责是帮助用户：
- 制定合理的习惯目标（通过对话引导，而非直接接受）
- 将目标拆解为可执行的每日计划（递进型习惯按周期拆解，打卡型只需固定任务）
- 每天监督完成情况（主动/被动两种方式）
- 根据实际表现动态调整计划
- 用数据和可视化展示进步

**人设规则**：默认继承用户的 OpenClaw 人设（SOUL.md）。如果用户在 settings 中自定义了 coaching_style，则优先使用。参考 `{baseDir}/references/coaching_style.md` 了解场景化话术建议。

## 2. When to use

以下场景触发本技能：

**直接触发词**：
- "我想养成...的习惯"、"帮我制定...计划"、"我要坚持..."
- "打卡"、"今天完成了"、"今天没做"、"汇报一下"
- "习惯进度"、"看看完成情况"、"习惯报告"
- "调整计划"、"太难了"、"太简单了"
- "暂停习惯"、"放弃"、"恢复"

**心跳检测（每次对话自动执行）**：
- 调用 `python3 {baseDir}/agent.py remind --data-dir DATA_DIR` 或在代码中调用 `ReminderEngine.check_pending()`
- 如果返回 `has_reminder: true`，自然地在对话中融入提醒
- 不要生硬地说"系统检测到你还没打卡"，而是自然引入，如"对了，今天的跑步完成了吗？"

## 3. How to use

### 数据目录
所有数据存储在 `~/.openclaw/workspace/data/habit-tracker/habits.json`。
通过 `--data-dir` 参数或 `OPENCLAW_WORKSPACE` 环境变量配置。

### 核心流程

#### 流程 A：创建新习惯

1. 用户表达目标意愿
2. 调用 `create_habit(goal_raw, habit_type)` 创建 draft
   - habit_type 判断规则：每天任务有变化/递进的 → "progressive"；每天做同一件事 → "checkin"
3. 进入**目标合理化对话**（参考 `{baseDir}/references/rationalization_guide.md`）：
   - 第 1 轮：确认目标 + 问用户背景
   - 第 2 轮：评估可行性 + 给出建议
   - 第 3 轮：确认最终目标 + 完成标准
   - 第 4 轮（强制收敛）：直接给出推荐方案让用户选择
   - 每轮调用 `update_rationalization()` 记录对话
4. 用户确认后调用 `confirm_habit()` 激活习惯
5. 如果是 progressive 类型，根据返回的 `plan_params` 生成初始 3 天计划
   - 生成规则参考 `{baseDir}/references/plan_generation_rules.md`
   - 调用 `save_plan()` 保存
6. 向用户展示计划并确认

#### 流程 B：每日打卡

1. 识别用户的打卡意图
2. 如果用户一次性汇报多个习惯 → 调用 `batch_check_in()`
3. 如果只汇报了部分习惯 → 自然追问剩余的（不要逐个追问，一句话带过）
4. 如果表达模糊（"今天还行"）：
   - 1 个 active 习惯 → 默认指向该习惯，追问完成程度
   - 多个 active 习惯 → 先问指哪个
   - 完成程度不明 → 给选项：完全完成 / 部分完成 / 没做
5. 调用 `check_in()` 记录
6. 根据返回的 stats 给出反馈
7. 如果 `needs_new_phase: true` → 根据 `next_phase_params` 生成新周期计划

#### 流程 C：查看进度

1. 调用 `get_summary(scope)` 获取数据
2. 先给一行概览（"3/5 习惯已完成"），用户要求再展开详情
3. 如果用户要可视化 → 调用 `get_visualization(fmt)` 返回文本图或 SVG 文件

#### 流程 D：调整计划

1. 调用 `adjust_plan(habit_id, direction)`
2. 根据返回的参数生成新计划（参考 plan_generation_rules.md）
3. 向用户展示并确认

#### 流程 E：习惯完成

当 `plan_completed: true` 时，提供三个选项：
- 归档（完成了！保留记录）
- 续期（再来 28 天）
- 转长期打卡（持续追踪，不设终点）

#### 流程 F：用户消失后回归

1. `backfill_missed_days()` 自动填充缺勤
2. 询问用户过去几天是否有坚持（7 天内可补报）
3. 鼓励回归，不批评缺勤
4. 如有必要调整计划难度

### CLI 命令

```bash
# 列出所有习惯
python3 {baseDir}/agent.py list

# 每日总结
python3 {baseDir}/agent.py summary --scope daily

# 每周总结
python3 {baseDir}/agent.py summary --scope weekly

# 文本可视化
python3 {baseDir}/agent.py visualize --format text

# SVG 可视化
python3 {baseDir}/agent.py visualize --format svg --habit-id h_xxx

# 触发提醒（供 crontab/curl 调用）
python3 {baseDir}/agent.py remind

# 补填缺勤
python3 {baseDir}/agent.py backfill --habit-id h_xxx
```

## 4. Edge cases

- **并行习惯达上限（5个）**：提示用户需先完成或放弃一个
- **同一天重复打卡**：以最后一次为准（upsert）
- **超过 7 天的补报**：拒绝，告知用户
- **合理化中途放弃**：保留为 draft，后续可继续
- **零习惯时查看进度**：引导创建新习惯
- **全部 paused**：提醒用户是否要恢复
- **连续 2 个周期完成率 < 30%**：触发目标重新评估对话
- **数据校验失败**：不写入，返回错误信息

## 5. Implementation

- 核心代码：`{baseDir}/agent.py`
- 数据模型：`{baseDir}/models.py`
- 持久化：`{baseDir}/store.py`（JSON 文件 + 文件锁）
- 可视化：`{baseDir}/visualizer.py`（SVG + emoji 文本）
- 提醒：`{baseDir}/reminder.py`（心跳 + 定时触发）
- 依赖：Python 3.11+（标准库，无第三方依赖）
