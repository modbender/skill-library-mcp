---
name: lifelog
description: |
  生活记录自动化系统。自动识别消息中的日期（今天/昨天/前天/具体日期），记录到 Notion 对应日期，支持补录标记。
  适用于：(1) 用户分享日常生活点滴时自动记录；(2) 定时自动汇总分析并填充情绪、事件、位置、人员字段
---

# LifeLog 生活记录系统

自动将用户的日常生活记录到 Notion，支持智能日期识别和自动汇总分析。

## 核心功能

1. **实时记录** - 用户分享生活点滴时自动记录到 Notion
2. **智能日期识别** - 自动识别"昨天"、"前天"等日期，记录到对应日期
3. **补录标记** - 非当天记录的内容会标记为"🔁补录"
4. **自动汇总** - 每天凌晨自动运行 LLM 分析，生成情绪状态、主要事件、位置、人员

## Notion 数据库要求

创建 Notion Database，需包含以下字段（全部为 rich_text 类型）：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| 日期 | title | 日期，如 2026-02-22 |
| 原文 | rich_text | 原始记录内容 |
| 情绪状态 | rich_text | LLM 分析后的情绪描述 |
| 主要事件 | rich_text | LLM 分析后的事件描述 |
| 位置 | rich_text | 地点列表 |
| 人员 | rich_text | 涉及的人员 |

## 脚本说明

### 1. lifelog-append.sh

实时记录脚本，接收用户消息内容：

```bash
# 基本用法
bash lifelog-append.sh "今天早上吃了油条"

# 识别昨天
bash lifelog-append.sh "昨天去超市买菜了"

# 识别前天
bash lifelog-append.sh "前天和朋友吃饭了"
```

**支持的日期表达**：
- 今天/今日/今儿 → 当天
- 昨天/昨日/昨儿 → 前一天
- 前天 → 前两天
- 明天/明儿 → 后一天
- 后天 → 后两天
- 具体日期：2026-02-22、2月22日

### 2. lifelog-daily-summary-v5.sh

拉取指定日期的原文，用于 LLM 分析：

```bash
# 拉取昨天
bash lifelog-daily-summary-v5.sh

# 拉取指定日期
bash lifelog-daily-summary-v5.sh 2026-02-22
```

输出格式：
```
PAGE_ID=xxx
---原文开始---
原文内容
---原文结束---
```

### 3. lifelog-update.sh

将 LLM 分析结果写回 Notion：

```bash
bash lifelog-update.sh "<page_id>" "<情绪状态>" "<主要事件>" "<位置>" "<人员>"
```

## 配置步骤

1. 创建 Notion Integration 并获取 API Key
2. 创建 Database 并共享给 Integration
3. 获取 Database ID（URL 中提取）
4. 修改脚本中的 `NOTION_KEY` 和 `DATABASE_ID`

## 定时任务（可选）

每天凌晨 5 点自动汇总昨天数据：

```bash
openclaw cron add \
  --name "LifeLog-每日汇总" \
  --cron "0 5 * * *" \
  --tz "Asia/Shanghai" \
  --session isolated \
  --message "运行 LifeLog 每日汇总" \
  --delivery-mode announce \
  --channel qqbot \
  --to "<用户ID>"
```

## 工作流

1. 用户发送生活记录 → 调用 `lifelog-append.sh` → 写入 Notion
2. 定时任务触发 → 调用 `lifelog-daily-summary-v5.sh` → 拉取原文
3. LLM 分析原文 → 调用 `lifelog-update.sh` → 填充分析字段
