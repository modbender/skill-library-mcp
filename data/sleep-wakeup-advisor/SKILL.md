---
name: sleep-wakeup-advisor
description: 'Calculate sleep-cycle-aligned wake-up times when the user says
  "晚安" or asks for best wake-up times. Use to recommend several wake-up options,
  put the best option first, and enforce top recommendation constraints: before
  09:00 on workdays and before 11:00 on weekends/China public holidays.'
---


# Sleep Wake-up Advisor

When user says "晚安", return wake-up suggestions immediately.

## Apply this workflow

1. Treat one sleep cycle as 90 minutes.
2. Add a 15-minute sleep-onset buffer from "now" (or from user-provided bedtime).
3. Generate candidate wake times at +3, +4, +5, +6 cycles.
4. Rank by recommended cycle count priority: 5 cycles > 4 cycles > 6 cycles > 3 cycles.
5. Determine day type:
   - Workday: Monday–Friday unless it is a China public holiday.
   - Holiday/Rest day: Saturday/Sunday or China public holiday.
6. Enforce top recommendation constraint:
   - Workday: top recommendation must be earlier than 09:00.
   - Holiday/Rest day: top recommendation must be earlier than 11:00.
7. If highest-priority candidate violates the limit, pick the next-best candidate that satisfies the limit.
8. Output:
   - First line: "最推荐：HH:mm（X 个周期）"
   - Then 2–4 alternative times in descending quality.
   - Keep response concise and practical.

## Sleep science defaults

- Adults usually complete ~4–6 full cycles per night.
- Deep sleep (N3) is concentrated in the first half of the night.
- Waking at cycle boundaries generally reduces sleep inertia versus waking mid-cycle.

Use these defaults unless user gives a personalized plan.

## Response template

- 最推荐：07:45（5 个周期）
- 备选：06:15（4 个周期）
- 备选：09:15（6 个周期）
- 备选：04:45（3 个周期）

Add one short sentence only when useful (e.g., "按你现在入睡，建议设置 07:45 闹钟").