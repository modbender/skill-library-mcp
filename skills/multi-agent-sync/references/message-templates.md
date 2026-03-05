# Multi-agent sync message templates

## 1) Kickoff message

【任务启动】
- 目标：<一句话目标>
- 分工：
  - topic1/chat：<职责>
  - topic3/coding：<职责>
  - topic5/test：<职责>
- 技能约束：
  - coding 子任务：`openai-codex-operator`
  - 多agent协作流程：`multi-agent-sync`
- 交付：<文件/结论>

【主会话即时回执】
- 已完成任务分配，后续进度与最终结果将在群 topic 持续同步。
- 你可以继续在主会话下达其他任务（无需等待）。

## 2) Mid-progress message

【执行进度｜每个agent各自发】
- topic3（coding）：<状态>
- topic5（test）：<状态>
- 说明：若出现 timeout，仅表示等待窗口未返回，不等于失败；已继续追踪。
- 要求：由各 agent 在各自 topic 持续可见同步（`started` / `partial` / `done` 或 `blocked`）。
- 高密度模式：每个关键步骤都发“仍在执行/当前阶段”更新（started / command sent / partial output / waiting dependency / completed）。
- 缺失补偿：若未出现 `partial` 或 `done`，立即补发【状态修正】并说明原因。

## 2.5) Coordinator periodic rollup (topic1)

【协调者定期汇总】
- topic3：<latest status + latest evidence>
- topic5：<latest status + latest evidence>
- 总体：<on-track / blocked>
- 下一检查点：<time or milestone>

建议频率：活跃任务每 1–2 分钟一次；短任务可按关键里程碑汇总。
硬规则：每次巡检后立刻发一次汇总，不能只在内部看到状态。

## 2.6) Status-correction message

【状态修正】
- 发现问题：<agent 未按规则主动上报 done/partial>
- 原因：<timeout窗口/静默回复/上下文污染>
- 修复动作：<已催办 started ack / 已重发任务模板 / 已补发当前状态>
- 下一检查点：<time>

## 3) Final summary message

【最终汇总｜由1个汇总agent发在topic1】
- 实现：<核心结果>
- 测试：<通过情况/风险>
- 交付产物路径：<文件路径列表>
- 实现原理分析：<算法/架构/复杂度简述>
- 结论：<可交付状态>
- 下一步：<改进项>
- 可复现命令：<一键复跑>

说明：中间过程由各 agent 各自输出；最终再统一汇总。
