---
name: reg-limited
description: Vehicle restriction query and reminder tool for Chinese cities. Query daily restrictions and set scheduled reminders.
---

# RegLimited - Vehicle Restriction Query & Reminder

A tool to help you query vehicle restrictions and set reminders for Chinese cities.

## Features

1. **Restriction Query** - Check if your vehicle is restricted today based on city and plate
2. **Scheduled Reminders** - Get notified at specified times about restriction info
3. **Multi-city Support** - Supports major Chinese cities including Beijing, Shanghai, Guangzhou, Shenzhen, Hangzhou, Chengdu, etc.

## Usage

### 1. Query Today's Restrictions

```bash
# Query today's restricted digits for a city
reg-limited query --city beijing

# Check if a plate is restricted
reg-limited check --city beijing --plate 京A12345
```

### 2. Set Restriction Reminders

```bash
# Basic usage
reg-limited add --city beijing --plate 京A12345 --time "07:00"

# Full parameters
reg-limited add --city beijing --plate 京A12345 --time "07:00" --notify-channel feishu
```

### 3. List All Reminders

```bash
reg-limited list
```

### 4. Remove Reminders

```bash
reg-limited remove --id <reminder_id>
```

## Supported Cities

- Beijing (北京)
- Shanghai (上海)
- Guangzhou (广州)
- Shenzhen (深圳)
- Hangzhou (杭州)
- Chengdu (成都)
- Tianjin (天津)
- Wuhan (武汉)
- Xi'an (西安)
- Nanjing (南京)

## Restriction Rules

### Beijing
Queries real-time restriction data from Beijing Traffic Management Bureau:
- Official source: https://jtgl.beijing.gov.cn/jgj/lszt/659722/660341/index.html
- Current period: 2025-12-29 to 2026-03-29
- Restrictions apply Mon-Fri, 7:00-20:00

| Day | Restricted |
|-----|------------|
| Monday | 3, 8 |
| Tuesday | 4, 9 |
| Wednesday | 5, 0 |
| Thursday | 1, 6 |
| Friday | 2, 7 |

### Other Cities
- **Shanghai**: Elevated road restrictions
- **Guangzhou**: "Open Four, Stop Four" policy
- **Shenzhen**: Morning/evening peak hour restrictions
- **Hangzhou/Chengdu/Tianjin/Wuhan/Xi'an/Nanjing**: Day-specific number restrictions

## Output Format

JSON format for program processing:
```json
{
  "success": true,
  "data": {
    "city": "北京",
    "date": "2026-03-03",
    "restricted": ["4", "9"],
    "isRestricted": true,
    "plate": "京A12345",
    "lastDigit": "4"
  }
}
```

## Example Dialogues

> User: What's today's vehicle restriction in Beijing?  
> Bot: Today's restriction digits: 4, 9 (Your plate 4 is restricted!)

> User: Is my car 京A12345 restricted today?  
> Bot: Yes! Today (Tuesday) Beijing restricts digits 4 and 9. Your plate ends with 4, so it's restricted.

> User: Set a reminder for 7am tomorrow about restrictions  
> Bot: Done! You'll receive a restriction reminder at 7am tomorrow.

## Technical Implementation

1. Fetches daily restriction info from official government sources
2. For Beijing: queries https://jtgl.beijing.gov.cn/jgj/lszt/659722/660341/index.html
3. Parses restricted digits from the official table
4. Compares with plate last digit
5. Sends notifications via scheduled tasks

## Dependencies

- Node.js
- Network access (for querying restrictions)
- Message channels (Feishu/Telegram/etc.)

---

*More cities coming soon...*
