---
name: tomorrow-weather
description: 获取北京明日天气预报和黄历，每天下午6点推送。包含气温对比提醒（波动超5℃警告）、雨天带伞提醒、以及第二天的黄历信息。
metadata: { "openclaw": { "emoji": "🌤️", "requires": { "bins": ["curl"] } } }
---

# Tomorrow Weather Skill — 明日天气推送

## 功能概述

每天下午 6:00（北京时间）自动执行，推送以下内容给用户：

1. **明日天气** — 北京明日天气状况 + 最高/最低气温
2. **气温变化提醒** — 今日 vs 明日最高气温，波动超过 5℃ 时发出警告
3. **雨天提醒** — 明日有雨（小雨/中雨/大雨/暴雨/雷雨/雨夹雪等）时提醒带伞
4. **明日黄历** — 宜/忌事项

---

## 执行步骤

### Step 1：获取今日和明日天气

使用 wttr.in 获取北京两天的天气数据（JSON格式）：

```bash
curl -s "https://wttr.in/Beijing?format=j1"
```

返回的 JSON 中：
- `weather[0]` = 今日天气，`maxtempC` 为今日最高气温
- `weather[1]` = 明日天气，包含：
  - `maxtempC` — 明日最高气温
  - `mintempC` — 明日最低气温
  - `hourly[4].weatherDesc[0].value` — 天气描述（英文）
  - `hourly[4].chanceofrain` — 降雨概率

中文天气描述映射（根据英文描述判断）：
- Sunny / Clear → 晴
- Partly Cloudy → 多云
- Cloudy / Overcast → 阴
- Rain / Drizzle / Light rain → 小雨
- Moderate rain → 中雨
- Heavy rain → 大雨
- Thunderstorm → 雷阵雨
- Snow / Blizzard → 雪
- Sleet → 雨夹雪
- Mist / Fog → 雾/霾

### Step 2：获取明日黄历

使用以下 API 获取黄历（根据明日实际日期构造 URL）：

```bash
# 先计算明天日期
TOMORROW=$(date -d "+1 day" +%Y%m%d)
curl -s "https://www.mxnzp.com/api/holiday/single/${TOMORROW}?ignoreHoliday=false&app_id=your_app_id&app_secret=your_secret"
```

**备用方案（无需 API Key）**：
直接搜索获取黄历信息：

使用 `batch_web_search` 搜索：`北京 {明日日期} 黄历 宜忌`

从搜索结果中提取：
- 宜：适合做的事（2-4项）
- 忌：不适合做的事（2-4项）

### Step 3：构建推送内容

按以下逻辑组装消息：

```
**🌤 明日天气预报（北京）**

明天天气是{天气描述}，最高气温{maxtempC}℃，最低气温{mintempC}℃。

{气温变化提醒（条件触发）}
{雨天提醒（条件触发）}

**📅 明日黄历（{具体日期，如2月29日}）**
✅ 宜：{宜1}、{宜2}、{宜3}
❌ 忌：{忌1}、{忌2}、{忌3}

---
🤖 Jay · 天气助手
```

**条件触发规则：**

- 气温波动提醒（满足任一触发）：
  - 明日最高气温 - 今日最高气温 > 5℃ → 追加：`⚠️ 明日气温较今日上升超过5℃（今日{今日气温}℃→明日{明日气温}℃），注意增减衣物！`
  - 今日最高气温 - 明日最高气温 > 5℃ → 追加：`⚠️ 明日气温较今日下降超过5℃（今日{今日气温}℃→明日{明日气温}℃），注意保暖！`

- 雨天提醒（满足任一触发）：
  - 天气描述包含"雨"字 → 追加：`☂️ 明日有雨，记得带伞！`
  - chanceofrain > 50 → 追加：`☂️ 明日降雨概率较高（{概率}%），建议带伞出门。`

### Step 4：通过飞书发送给用户

使用 `message` tool，发送给用户 `你的飞书openid`，channel 为 feishu。

---

## 注意事项

- 天气数据来源：wttr.in（免费，无需 API Key）
- 黄历优先通过搜索获取，确保日期准确（取明日实际日期）
- 气温单位统一使用摄氏度（℃）
- 推送时间：每天 18:00（Asia/Shanghai）
- 若 wttr.in 请求失败，重试一次；仍失败则推送"天气数据获取失败，请稍后查看"

---

## 触发方式

- **定时任务（主要）**：每天 18:00 由 cron 自动触发
- **手动触发**：用户说"发送明日天气"、"明天天气怎么样"、"天气推送"时激活
