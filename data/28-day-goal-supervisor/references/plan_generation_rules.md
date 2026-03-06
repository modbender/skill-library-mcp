# 计划生成规则

## 适用范围

本规则仅适用于 **progressive（递进型）** 习惯。checkin（打卡型）习惯不需要生成计划。

## 核心生成原则

### 1. 渐进原则
- 难度必须逐步递增，不能跳跃
- 每天的增量不超过前一天的 20%
- 新周期第一天的难度不高于上周期平均水平

### 2. 具体原则
- 每个任务必须有**量化指标**
  - ✅ "慢跑 2.5 公里" 
  - ❌ "多跑一点"
- 必须有明确的**动作描述**
  - ✅ "阅读《原子习惯》第 3-4 章（约 30 页）"
  - ❌ "读书"

### 3. 可恢复原则
- 如果上周期完成率低，新周期要适当降低起点
- 允许"缓冲日"：每个周期的第一天可以略低于目标节奏

### 4. 多样性原则
- 避免连续多天完全相同的任务（即使是递进型）
- 可以变换方式达成同一目标
  - 例如跑步：周一慢跑、周三间歇跑、周五配速跑

## 生成时的输入参数

AI 会从 `next_phase_params` 获取以下参数：

```json
{
  "phase_number": 2,
  "phase_length": 3,
  "start_day": 4,
  "difficulty_direction": "maintain",  // harder | maintain | easier | much_easier | needs_reevaluation
  "previous_completion_rate": 0.83,
  "remaining_days": 25,
  "goal_refined": "每天晨跑，从 2 公里逐步提升到 5 公里",
  "completion_criteria": "完成当天计划的跑步距离"
}
```

## difficulty_direction 含义

| 方向 | 含义 | 生成策略 |
|------|------|----------|
| harder | 上周期完成率 ≥ 90% | 增加 10-20% 难度 |
| maintain | 60-89% | 保持与上周期末相近的难度 |
| easier | 30-59% | 降低 10-20% 难度 |
| much_easier | < 30% | 大幅降低，回到用户能完成的水平 |
| needs_reevaluation | 连续 2 周期 < 30% | 不生成计划，先触发目标重新评估对话 |

## 输出格式

生成后必须调用 `save_plan()` 保存，格式为：

```json
{
  "phase_number": 2,
  "phase_length": 3,
  "start_day": 4,
  "daily_tasks": [
    {"day": 4, "description": "慢跑 2.5 公里"},
    {"day": 5, "description": "间歇跑 2.5 公里（跑 3 分钟走 1 分钟）"},
    {"day": 6, "description": "慢跑 3 公里"}
  ]
}
```

## 示例：跑步习惯的 28 天计划进程

```
Phase 1 (Day 1-3): 基础建立
  Day 1: 快走 + 慢跑交替 2 公里
  Day 2: 慢跑 2 公里
  Day 3: 慢跑 2.5 公里

Phase 2 (Day 4-6): 巩固（假设 Phase 1 完成率 83%）
  Day 4: 慢跑 2.5 公里
  Day 5: 间歇跑 2.5 公里
  Day 6: 慢跑 3 公里

Phase 3 (Day 7-11): 提升（假设连续两周期 ≥90%，周期延长到 5 天）
  Day 7: 慢跑 3 公里
  Day 8: 配速跑 2.5 公里
  Day 9: 慢跑 3.5 公里
  Day 10: 间歇跑 3 公里
  Day 11: 慢跑 3.5 公里

... 依此递进
```
