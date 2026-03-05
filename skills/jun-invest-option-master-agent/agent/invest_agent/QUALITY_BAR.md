# Invest Agent 质量门槛（Quality Bar）

目标：把每次输出变成“可审批、可审计、可复盘”的专业交付。

## A. 事实与数据（Data）
- 所有关键数值必须带：source + timestamp
- 缺失/异常必须显式列出，并下调 data_quality_score
- 不允许“拍脑袋填数”；宁可 unknown + 影响评估

## B. 可证伪（All roles）
- 每个结论必须给出：invalidation_conditions（何时判错/重评）
- 证据写成：观察 → 含义 → 阈值/触发

## C. 章程一致性（Policy）
- 杠杆：禁止
- 期权：仅 CSP / Covered Call
- CSP：100% 现金覆盖
- 永久现金缓冲 25%：不得占用
- 最大回撤上限：30%
- 集中度：单标的<=8%，黄金/比特币类<=5%

## D. 风控优先（Risk）
- Risk 的 verdict 为 VETO 或 LIMIT：PM 必须降级，不得绕过
- 任何“最坏情景”都要落到可执行动作（暂停/减仓/滚动/平仓）

## E. 执行可操作（Execution）
- 订单写到可下单的粒度（动作、品种、数量、限价、最大让步）
- 明确避免追价与流动性薄时段

## F. 复盘闭环（Postmortem）
- 归因要区分：过程错误 vs 运气
- 每次复盘必须产出：模板/参数/监控项的具体更新建议
