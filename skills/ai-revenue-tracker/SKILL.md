---
name: SKILL.md
description: 每日收入汇总和追踪系统。
---

# SKILL.md

# Revenue Tracker

每日收入汇总和追踪系统。

## 能力

- 记录每笔收入
- 生成每日汇总报告
- 按来源/技能统计
- 追踪累计收入

## 使用方式

```bash
# 记录收入
./main.sh log 10 "market-intelligence" "单次报告"
./main.sh log 100 "data-scraper" "月度订阅"

# 生成报告
./main.sh report

# 查看今日收入
./main.sh today

# 查看总收入
./main.sh total
```

## 收费模式

| 服务 | 价格 | 说明 |
|------|------|------|
| **单次报告** | $10-50 | 各类服务按次收费 |
| **月度订阅** | $50-200 | 批量服务订阅制 |
| **企业定制** | 按需 | API 集成、定制开发 |

## 数据存储

- 收入日志: `logs/revenue.log`
- 每日报告: `reports/daily_summary.md`

## 输出示例

```markdown
# 每日收入汇总

**日期:** 2026-02-20
**总收入:** $150
**总交易数:** 3
**累计总收入:** $150

---

## 今日交易

• 150 | market-intelligence | 单次报告
• 50  | data-scraper        | 月度订阅

---

## 技能收入明细

• market-intelligence: 1
• data-scraper: 1
```

## 开发者

OpenClaw AI Agent
License: MIT
Version: 1.0.0
