# LifeLog - Automated Life Logging System

[English](./README_EN.md) | [中文](./README.md)

> ⚠️ **Notice**: This skill and its documentation are AI-generated. For reference only.

Automatically record daily life to Notion, with intelligent date recognition and automatic summary analysis.

## Features

- 🤖 **Smart Date Recognition** - Automatically recognize "yesterday", "day before yesterday", etc., and log to the corresponding date
- 🔁 **Backfill Marker** - Non-same-day entries are marked as "🔁补录" (backfilled)
- 📝 **Real-time Logging** - Record life moments anytime, automatically saved to Notion
- 🌙 **Auto Summary** - Daily automatic LLM analysis to generate emotional state, main events, locations, and people
- 🔍 **Smart Filter** - Automatically filter pure work commands, test messages, etc.

## Preview

![LifeLog Preview](./assets/preview.png)

## Quick Start

### 1. Install

Via ClawHub:
```bash
clawhub install lifelog
```

Or manually:
```bash
git clone https://github.com/421zuoduan/lifelog.git
```

### 2. Configure Notion

1. **Create Integration**
   - Visit https://www.notion.so/my-integrations
   - Click **New integration**
   - Fill in name (e.g., "LifeLog")
   - Copy the **Internal Integration Token**

2. **Create Database**
   - Create a new Database with fields (all rich_text type):
     | Field | Type | Description |
     |-------|------|-------------|
     | Date | title | Date, e.g., 2026-02-22 |
     | Original Text | rich_text | Raw log content |
     | Emotional State | rich_text | LLM-analyzed emotion |
     | Main Events | rich_text | LLM-analyzed events |
     | Location | rich_text | Places |
     | People | rich_text | People involved |
   - Click **...** in the top right → **Connect to** → Select your Integration

3. **Get Database ID**
   - Extract from URL: `notion.so/{workspace}/{database_id}?v=...`
   - database_id is a 32-character string (with `-`)

4. **Update Script Configuration**
   - Edit scripts in `scripts/`, replace:
     ```bash
     # ===== Configuration =====
     NOTION_KEY="your_notion_api_key"
     DATABASE_ID="your_database_id"
     # ====================
     ```

### 3. Usage

```bash
# Log today's events
bash scripts/lifelog-append.sh "Had fried dough sticks for breakfast"

# Log yesterday's events (auto-recognized)
bash scripts/lifelog-append.sh "Went to the supermarket yesterday"

# Log day-before-yesterday's events
bash scripts/lifelog-append.sh "Had dinner with friends the day before yesterday"

# Log specific date
bash scripts/lifelog-append.sh "Went hiking with family on February 22"
```

### 4. Set Up Scheduled Summary (Optional)

```bash
openclaw cron add \
  --name "LifeLog-DailySummary" \
  --cron "0 5 * * *" \
  --tz "Asia/Shanghai" \
  --session isolated \
  --message "Run LifeLog daily summary"
```

## Supported Date Expressions

- 今天/今日/今儿 (today) → current day
- 昨天/昨日/昨儿 (yesterday) → previous day
- 前天 (day before yesterday) → 2 days ago
- 明天/明儿 (tomorrow) → next day
- 后天 (day after tomorrow) → 2 days later
- Specific date: 2026-02-22, 2月22日

## Scripts

| Script | Function | Usage |
|--------|----------|-------|
| `lifelog-append.sh` | Real-time message logging | `bash lifelog-append.sh "message content"` |
| `lifelog-daily-summary-v5.sh` | Pull original text for a date | `bash lifelog-daily-summary-v5.sh 2026-02-22` |
| `lifelog-update.sh` | Write back analysis results | `bash lifelog-update.sh "<page_id>" "<emotion>" "<events>" "<location>" "<people>"` |

## Auto Summary Workflow

1. User sends life log → call `lifelog-append.sh` → write to Notion
2. Scheduled task triggers (5 AM daily) → call `lifelog-daily-summary-v5.sh` → pull previous day's text
3. LLM analyzes → call `lifelog-update.sh` → fill emotion, events, location, people fields

## Filtering Rules

The system automatically filters the following content and will **NOT** log:

| Type | Example |
|------|---------|
| Pure work commands | "帮我写代码", "部署服务", "git push" |
| Test messages | "测试一下", "试一下" |
| System messages | "设置记录", "配置Notion" |
| Very short acknowledgments | Single characters (e.g., "好", "嗯") |

**Note**: Content with emotional expressions will be logged even if work-related, e.g., "写代码累死了" will be logged.

## Troubleshooting

### API Request Failed
- Check if Notion API Key is correct
- Ensure Integration is connected to Database

### Date Recognition Not Accurate
- Make sure using supported date expression formats
- Check if system timezone is correct

### Scheduled Task Not Running
- Check cron task status: `openclaw cron list`
- View task logs: `openclaw cron runs --id <job_id>`

## FAQ

**Q: How to view today's logs?**
A: Search today's date in Notion.

**Q: Can I log multiple messages?**
A: Yes, multiple calls will automatically append to the same day's record.

**Q: What's the difference between backfilled and same-day logs?**
A: Backfilled content is marked with "🔁补录" after the timestamp for easy identification.

## ClawHub

This skill is published on ClawHub: https://clawhub.com/s/lifelog

## License

MIT
