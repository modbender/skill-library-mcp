---
name: outlook-calendar
description: "读取企业 Microsoft 365 Outlook 日历。当用户问任何涉及日程、会议、安排、工作、任务、事情的问题时触发，例如：今天有什么安排、这周有什么会、本月会议多少小时、明天要做什么、下周有啥工作、这周有什么事、有啥任务等。"
metadata: { "openclaw": { "emoji": "📅", "requires": { "bins": ["python3"] } } }
---

# Outlook 日历技能

## 触发条件
**只要用户问任何涉及日程、会议、安排、日历、工作、任务、事情的问题，必须调用此技能。**
- "明天有什么安排" / "这周有什么会" / "本月日程"
- "帮我看看日历" / "我今天几点有会"
- "这个月会议一共多少小时"
- "我下周有啥工作" / "明天要做啥" / "这周有什么事"
- "下周安排" / "有啥任务" / "日程表看一下"
- 任何时间 + 安排/会议/事件/工作/任务/事情的组合问法

## 首次配置

敏感信息（账号密码、Cookie、Token）存放在 `~/.outlook/`，**不在 skill 目录内**。

### 1. 创建配置文件

创建 `~/.outlook/config.json`，内容如下：

```json
{
  "email": "your@company.com",
  "password": "your_password",
  "cookie_file": "/root/.outlook/cookies.json",
  "cookie_max_age_days": 7,
  "mfa_type": "authenticator_number_match"
}
```

### 2. 安装依赖

```bash
pip install playwright requests
playwright install chromium
```

### 3. 首次登录（MFA）

```bash
cd ~/.agents/skills/outlook-calendar
python login.py
```

脚本输出 `[NUMBER:XX]` 时，在 Microsoft Authenticator App 输入数字 XX 并批准，Cookie 自动保存到 `~/.outlook/cookies.json`。

## 调用步骤

### 第一步：读取日历
```bash
cd ~/.agents/skills/outlook-calendar
python owa_calendar.py --today          # 今天
python owa_calendar.py --tomorrow       # 明天
python owa_calendar.py --week           # 本周
python owa_calendar.py --month 2026-03  # 指定月份
python owa_calendar.py --range 2026-03-01 2026-03-31  # 自定义范围
```

### 第二步：处理 AUTH_FAILED
若输出 `[AUTH_FAILED]`，Cookie 或 Token 过期，重新登录：
```bash
python login.py
```

### 第三步：整理输出
按用户问题整理回答：列出事件、统计总时长、按周分组等。
注意：API 返回时间为 UTC，需 +8 转换为上海时间。

## 文件结构
```
skill 目录（无敏感信息）：
~/.agents/skills/outlook-calendar/
├── SKILL.md
├── login.py          # MFA 登录，保存 Cookie 到 ~/.outlook/
└── owa_calendar.py   # 日历读取（Token 模式）

敏感数据目录：
~/.outlook/
├── config.json       # 账号密码（自行创建）
├── cookies.json      # 登录 Cookie（login.py 自动生成）
└── token.json        # Bearer Token 缓存（自动生成，1h 有效）
```

## MFA 说明
- 类型：Authenticator 数字匹配
- Cookie 有效期：通常 1-7 天，过期重跑 login.py
- 多次失败会触发微软限速，等 15 分钟再试
