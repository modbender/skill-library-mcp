---
name: owa-outlook
description: "读取企业 Microsoft 365 Outlook 日历和邮件。当用户问任何涉及日程、会议、安排、工作、任务、事情、邮件、收件箱、未读邮件的问题时触发。"
metadata: { "openclaw": { "emoji": "📬", "requires": { "bins": ["python3"] } } }
---

# OWA Outlook 技能（日历 + 邮件）

## 触发条件
- 日历：今天/明天/本周有什么安排、会议、日程、任务、工作
- 邮件：有没有新邮件、未读邮件、查收件箱、搜索邮件

## 首次配置

敏感信息存放在 `~/.outlook/`，不在 skill 目录内。

### 1. 创建配置文件

```json
// ~/.outlook/config.json
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
cd ~/.agents/skills/owa-outlook
python login.py
```

脚本输出 `[NUMBER:XX]` 时，在 Microsoft Authenticator App 输入数字 XX 并批准。

## 日历用法

```bash
cd ~/.agents/skills/owa-outlook
python owa_calendar.py --today
python owa_calendar.py --tomorrow
python owa_calendar.py --week
python owa_calendar.py --month 2026-03
python owa_calendar.py --range 2026-03-01 2026-03-31
```

注意：API 返回时间为 UTC，需 +8 转换为上海时间。

## 邮件用法

```bash
cd ~/.agents/skills/owa-outlook
python owa_mail.py --unread              # 未读邮件（默认最近20封）
python owa_mail.py --today               # 今天收到的邮件
python owa_mail.py --limit 50            # 最近50封
python owa_mail.py --search "关键词"     # 搜索主题/发件人
python owa_mail.py --folder Inbox        # 指定文件夹
python owa_mail.py --json                # JSON 格式输出
```

## 认证说明
- Token 过期（1小时）→ 自动续，无感知
- Cookie 过期 → 自动重新登录，输出 `[MFA] 请在 Authenticator 选择数字：【XX】`，你在手机上批准即可，脚本自动继续

## 文件结构
```
~/.agents/skills/owa-outlook/
├── SKILL.md
├── login.py          # MFA 登录
├── owa_calendar.py   # 日历读取
└── owa_mail.py       # 邮件读取

~/.outlook/
├── config.json       # 账号密码
├── cookies.json      # 登录 Cookie
└── token.json        # Bearer Token 缓存
```
