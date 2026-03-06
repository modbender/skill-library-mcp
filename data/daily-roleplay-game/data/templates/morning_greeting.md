# 早安消息模板

## 模板（填充变量后整段发送）

```
📅 {{DATE}} {{WEEKDAY}} {{LUNAR_DATE}}{{HOLIDAY_INFO}}

📰 今日简报
{{NEWS_HEADLINES}}

🌤️ 北京 {{WEATHER_INFO}}

📅 本周待办 {{WEEKLY_TODO}}

---
☀️ 早安主人～今天{{CHAR_NAME}}是 {{PROFESSION_NAME}}。
今日穿着（共 {{OUTFIT_COUNT}} 件）：{{OUTFIT_PUBLIC_LIST}}（内衣保密）

{{PROFESSION_GREETING}}
```

---

## 变量与获取方式

| 变量 | 说明 | 获取方式 |
|------|------|----------|
| `{{CHAR_NAME}}` | 角色名称 | `IDENTITY.md` 的 Name 字段 |
| `{{DATE}}` | 日期 | 系统，如 2026年2月23日 |
| `{{WEEKDAY}}` | 星期 | 系统 |
| `{{LUNAR_DATE}}` | 农历 | 见下方命令 |
| `{{HOLIDAY_INFO}}` | 假期 | `data/holidays_china.json`，非假期为空 |
| `{{NEWS_HEADLINES}}` | 头条 5 条 | web_search「今日新闻头条」，`1. xxx\n2. xxx...` |
| `{{WEATHER_INFO}}` | 天气+穿衣 | wttr.in / Open-Meteo 北京，如 `晴 3°C~12°C，建议羽绒服` |
| `{{WEEKLY_TODO}}` | 本周待办 | memory/ + 日历，无则 `暂无` |
| `{{PROFESSION_NAME}}` | 职业 | roleplay-active.md |
| `{{OUTFIT_COUNT}}` | 件数 | roleplay-active.md |
| `{{OUTFIT_PUBLIC_LIST}}` | 穿着清单 | roleplay-active.md |
| `{{PROFESSION_GREETING}}` | 职业问候 | 见下表或按职业生成 |

**农历命令**（需 lunarcalendar）：
```bash
python3 -c "from lunarcalendar import Converter, Solar; import datetime; today=datetime.date.today(); solar=Solar(today.year,today.month,today.day); lunar=Converter.Solar2Lunar(solar); months=['正','二','三','四','五','六','七','八','九','十','冬','腊']; days=['初一','初二','初三','初四','初五','初六','初七','初八','初九','初十','十一','十二','十三','十四','十五','十六','十七','十八','十九','二十','廿一','廿二','廿三','廿四','廿五','廿六','廿七','廿八','廿九','三十']; print(f'农历{months[lunar.month-1]}月{days[lunar.day-1]}')"
```

---

## 职业问候语（示例）

| 职业 | 问候语 |
|------|--------|
| 护士 | 今天也要好好照顾主人的身体呢～ |
| 兔女郎 | 嘛～今天要为主人端酒服务哦～ |
| 巫女 | 神明会守护主人的每一天…… |
| 秘书 | 今天的日程已经为主人准备好了。 |
| 空姐 | 欢迎登机，今天也请多关照～ |
| 女仆 | 今天也会把家里打扫得干干净净～ |
| 老师 | 今天也要好好教导主人呢～ |
| 警察 | 今天也要维护主人的安全！ |
| 医生 | 今天为主人做全身检查～ |
| 律师 | 今天为主人辩护一切～ |
| 高铁乘务员 | 各位旅客，前方到站……今天也请多关照～ |

其他职业按性格生成。必选：与消息同时发送早安自拍（按 TOOLS.md 配置的生图工具，职业场景+今日穿着+职业表情，详见 ENGINE Step 6）。
