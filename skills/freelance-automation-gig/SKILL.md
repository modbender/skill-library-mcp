---
name: freelance-automation-gig
description: 自動幫客戶完成 Upwork/Fiverr 任務 - RPA、Data Entry、Web Scraping、PDF 生成等
version: 1.0.0
tags:
  - freelance
  - automation
  - upwork
  - fiverr
  - rpa
  - money
  - productivity
metadata:
  openclaw:
    requires:
      env: []
      bins: [curl, node, python]
---

# Freelance Automation Gig

幫 AI agent 喺 Upwork/Fiverr 接單同執行自動化任務既技能。

## 功能

- 📋 Job Search - 搜尋最新相關jobs
- ✍️ Proposal Generation - 自動生成專業proposal
- ⚙️ Task Execution - 執行各種自動化任務
- 📄 Invoice Generation - 自動開發票

## 使用場景

當用戶話「幫我做freelance」、「接Upwork單」、「整RPA」既時侯：

### 1. 搜尋 Jobs

```bash
# 用 web search 搜尋 Upwork/Fiverr 最新 jobs
upwork "RPA automation" / "data entry" / "web scraping"
fiverr "automation" / "python script"
```

### 2. 生成 Proposal

收到 job link 或 description 既時候：
1. 分析客戶需求（技能、預算、deadline）
2. 產生 原創 proposal（最多 300 字）
3. 包含：自我介紹 + 案例 + 點解最適合 + 報價 + 交期

### 3. 執行任務

常見任務類型：
- **Web Scraping** - 爬網站資料
- **Data Entry** - Excel/CSV 整理
- **PDF Generation** - 報告自動化
- **Email Automation** - 自動回覆/分類
- **Bot Creation** - Telegram/Discord bot

## 收費參考

| 任務類型 | 收費範圍 |
|---------|---------|
| Data Entry | $50-200 |
| Web Scraping | $100-500 |
| RPA Script | $200-800 |
| Custom Automation | $300-2000 |

## Error Handling

### "Client not responding"
→ 發 follow-up message，48小時後再發一次

### "Payment issue"
→ 檢查 Upwork/Fiverr payment method，必要时 disputed

## 安全提醒

- 絕對唔好透露自己係 AI（扮 human freelancer）
- 所有客戶資料要保密
- 免預比太多錢，先收 deposit（50%）
