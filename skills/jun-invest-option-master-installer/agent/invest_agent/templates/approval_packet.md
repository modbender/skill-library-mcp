# 审批包（模板）

> 纪律：不杠杆；期权仅 CSP/CC（30–45DTE 为主）；CSP 100% 现金覆盖；永久现金缓冲 25% 不得占用。
> 所有交易必须经生哥审批；本包仅供审批，不自动下单。

## 0) Audit metadata（审计元信息）
- generated_at:
- inputs_dir:
- data_asof:
- data_sources_summary:
- opend_endpoint:
- skills_versions:

## 1) TL;DR（一页摘要）
- Verdict (PASS/LIMIT/VETO):
- Trade A (if any):
  - ticker/strategy/expiry/strike/qty:
  - credit (est) / annualized (est) / breakeven:
  - cash_reserved:
- Key reasons (3 bullets):
- Approval questions:
  - Approve Trade A? (Y/N)
  - Allowed limit range / max concession:
  - Accept management rules (50% TP / 21DTE roll)?

## 2) Summary（PM 汇总结论）
- 是否建议交易：是 / 否 / 需修改 / 信息不足
- 本次结论一句话：
- 方案类型：CSP / CC / 组合

## 2) Data snapshot（Data：事实快照）
- asof：
- 数据可信度（0-100）& 理由：
- 基准：SPY/QQQ 价格区间、rv20、IV proxy（VIX或替代）：
- 期权链概况（30–45DTE 优先）：ATM IV、skew、点差、OI/成交量（定性也可）：
- 未来 2 周事件窗口：宏观 / 财报：
- 异常与缺失：

## 3) Decision basis（决策依据：你审批时看的核心）
> 目的：把“指标→含义→动作”讲清楚；不靠口号。

- 回报指标（必须给）：
  - credit / cash_return% / annualized_return%：
  - break-even：
- 风险补偿（必须给）：
  - ATM IV（含义→对 delta/DTE 的影响）：
  - skew（尾部定价→对 strike 的影响）：
- 可执行性（必须给）：
  - 典型点差/流动性（OI/Vol）→限价与最大让步：
- 事件窗口（必须给）：
  - 财报/宏观窗口是否在持仓期内（是/否；处理规则）：
- 组合约束（必须给）：
  - 单标的占比、现金覆盖、永久现金缓冲是否触碰：
- 最坏情景路径（必须给）：
  - -10%/-20% 情景下的动作（滚动/平仓/接受指派转CC）：

## 4) Regime（Regime：市场状态与策略倾向）
- regime_label：trend / vol / corr / liquidity：
- evidence（3-7条）：
- 对 CSP/CC 的倾向：delta/DTE/节奏建议：

## 4) Equity thesis（EquityAlpha：标的与关键价位）
- 候选标的（3–8个，宁少而精）：
- 每个标的：fit（CSP/CC/neither）+ 一句话逻辑：
- 催化剂 & 风险窗口：
- 关键价位（支撑/压力/失效位）：
- 流动性与期权可交易性：

## 5) Proposed trades（Options：待生哥审批）
> 每条都必须写清：标的、策略（CSP/CC）、数量、到期、行权价、限价、预期权利金/成本（无实时数据则用区间+说明）

- Trade A:
  - ticker:
  - strategy:
  - qty (contracts/shares):
  - dte/expiry:
  - strike:
  - approx_delta:
  - limit_price / credit:
  - rationale:
- Trade B:

## 6) Portfolio & cash coverage（Portfolio：资金与一致性）
- 当前可用现金（估算/占比）：
- 本次现金占用（CSP 需 100% 覆盖）：
- 指派后持仓变化（最坏情景）：
- 永久现金缓冲 25%：是否触碰（必须为“否”）：
- 集中度检查：单标的<=25%；黄金/比特币类<=5%：
- 核心仓位目标对齐（SPY 30% + QQQ 30%）：偏离说明：

## 7) Risk checks（Risk：独立风控结论，可否决）
- 结论：PASS / LIMIT / VETO
- 触发的风险点与阈值（逐条）：
- 必须修改项（required）：
- 可选改进项（optional）：
- 监控触发器：暂停/降风险/滚动或平仓：

## 8) Execution plan（Execution：执行要点）
- 下单步骤（sell_to_open / buy_to_close …）：
- 限价策略（以 mid 为锚，改善几跳，最大让步）：
- 时间选择（避开事件窗口/流动性差时段）：
- 滑点与点差风险：

## 9) Management plan（管理规则）
- 止盈（默认 50% 利润止盈，可写调整）：
- 滚动（默认 21DTE 评估）：
- 防守/认赔规则（大跌、IV 扩张、流动性恶化时）：
- 被指派后的处理（转 CC / 降风险）：

## 10) What could go wrong（最坏情景清单）
- 单标的跳空：
- 波动率/相关性上升：
- 流动性枯竭（点差扩大、无法滚动）：

## 11) Contract fields（必须包含）
## assumptions
## confidence
## invalidation_conditions
## risks

## 12) Questions for approval（你只需回复这些）
- 1）是否批准执行 Trade A？（Y/N）
- 2）是否批准执行 Trade B？（Y/N）
- 3）允许的限价滑动范围（相对 mid 或绝对价格）：___
