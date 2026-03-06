---
name: a-share-metrics-card
description: 获取并生成 A股单只股票的关键指标“体检卡”（估值/盈利质量/现金流/负债/分红/交易活跃度等），输出为统一 Markdown，便于对比与持续跟踪。用在："帮我查600406关键指标"、"做一张国电南瑞体检卡"。
user-invocable: true
metadata: {"openclaw": {"emoji": "🩺"}}
---

# A-Share Metrics Card

## Inputs
- symbol（必填）：如 "600406" / "000733"
- name（可选）：中文名（若不提供则尽量自动识别）
- focus（可选）："balanced" | "value" | "growth" | "dividend"（默认 balanced）
- outputPath（可选）：默认 `notes/stocks/cards/{symbol}.md`

## Steps
1. 校验参数：必须有 symbol。
2. 选择数据源：
   - 优先：Python + AkShare（覆盖广、适配A股）
   - 备选：公开网页/API（轻量但不保证稳定）
3. 拉取数据并标注“口径/时间”（能拿到就写）：
   - 交易面：最新价、近52周区间、成交额/换手率（如可得）
   - 估值：PE(TTM/静态如可得)、PB
   - 质量：ROE、毛利率/净利率（如可得）
   - 健康：资产负债率、经营现金流（如可得）
   - 分红：股息率/近几年分红（如可得）
4. 生成统一 Markdown 卡片并写入 outputPath。
5. 返回：status/summary/data/nextAction。

## Output template（Markdown 卡片）
- 基本信息：代码/名称/行业（如可得）
- 快速结论（仅数据层面的“看到什么”，不做买卖建议）
- 指标表（或清单）+ 数据口径与更新时间
- 需要进一步核实的问题（2–5条）

## Safety / Boundaries
- 不输出“买/卖/目标价”。只做数据与学习提示。
- 明确数据来源与可能滞后。

## Failure
- 缺 symbol：报错并给示例。
- 取数失败：给出替代数据源建议，并提示检查网络/依赖安装。
