---
name: daily-review-assistant
description: Generate A-share daily review report (stock-analysis/daily_review.py). Supports --email.
metadata:
  {
    "openclaw": {
      "emoji": "📈",
      "requires": { "bins": ["python3"] }
    }
  }
---

# 每日复盘小助手

## 功能
生成 A 股每日复盘 Markdown 报告（基于 AkShare），并可选通过 SMTP 发送邮件。

包含：
- 全市场概览（指数、涨跌家数、成交额等）
- 连板统计与明细（含成交额/换手/封板时间）
- 板块涨幅榜（行业板块；失败时回退概念板块）
- 龙虎榜（标题带总数；列出全部净买入个股，含涨幅；并附“其他上榜”简表）
- 舆情监控（涨停股新闻标题关键词打分）
- 次日策略

## 使用方式

### 命令触发（推荐）
- 生成报告：`/daily-review 2026-02-27`
- 发送邮件：`/daily-review 2026-02-27 --email`
- 不传日期：默认今日

由助手在工作区执行：`python3 stock-analysis/daily_review.py <date> [--email]`。

### 手动生成
在工作区运行：

```bash
python3 stock-analysis/daily_review.py 20260227
```

日期支持：
- `YYYYMMDD`
- `YYYY-MM-DD`
- 不传日期：默认今日

### 发送邮件（可选）

```bash
python3 stock-analysis/daily_review.py 20260227 --email
```

邮件配置文件：
- 默认：`stock-analysis/email_config.json`
- 可用环境变量覆盖：`DAILY_REVIEW_EMAIL_CONFIG=/path/to/email_config.json`

SMTP 密码（授权码）从环境变量读取：
- 默认：`SMTP_PASSWORD`

配置示例：
- `stock-analysis/email_config.example.json`

## 输出
- 报告保存路径：`stock-analysis/reports/YYYYMMDD.md`

## 依赖
- Python 3
- `akshare`

## 注意
- AkShare 数据源偶发断连，脚本已对板块接口做退避重试与回退。
- 邮件发送使用 SMTP，建议使用服务商的“授权码”而不是登录密码。
