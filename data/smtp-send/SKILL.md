---
name: smtp-send
description: Send emails via SMTP or Resend API with support for plain text, HTML, and attachments. Use when the user asks to send an email, email someone, or compose and send a message. Supports single recipients and can include file attachments. Works with Gmail, Outlook, Yahoo, QQ Mail, 163 Mail, Resend, and any SMTP server.
---

# Email Send

发送邮件，支持 SMTP 和 Resend API 两种方式。

## 🚀 快速使用

```bash
# 发送简单邮件
python3 scripts/send_email.py \
  --to recipient@example.com \
  --subject "Meeting Tomorrow" \
  --body "Hi, let's meet at 2pm tomorrow."

# 发送 HTML 邮件
python3 scripts/send_email.py \
  --to recipient@example.com \
  --subject "Weekly Report" \
  --body "<h1>Report</h1><p>Here are the updates...</p>" \
  --html

# 发送带附件的邮件
python3 scripts/send_email.py \
  --to recipient@example.com \
  --subject "Documents" \
  --body "Please find the attached files." \
  --attachments report.pdf,data.csv

# 指定使用 Resend
python3 scripts/send_email.py \
  --to recipient@example.com \
  --subject "Test" \
  --body "Hello" \
  --provider resend
```

## ⚙️ 配置

在 `~/.smtp_config` 中配置（二选一或两个都配）：

### 方式 1: Resend API（推荐，更简单）

```json
{
    "resend_api_key": "re_xxxxx",
    "resend_from": "you@your-domain.com"
}
```

获取 API key: https://resend.com

**注意**：免费账户只能发给注册邮箱，要发给其他人需要验证域名。

### 方式 2: SMTP（163/QQ/Gmail 等）

```json
{
    "host": "smtp.163.com",
    "port": 465,
    "user": "your-email@163.com",
    "password": "your-auth-code",
    "from": "your-email@163.com",
    "use_ssl": true
}
```

### 两个都配（自动 fallback）

```json
{
    "resend_api_key": "re_xxxxx",
    "resend_from": "you@your-domain.com",
    "host": "smtp.163.com",
    "port": 465,
    "user": "your-email@163.com",
    "password": "your-auth-code",
    "from": "your-email@163.com",
    "use_ssl": true
}
```

配置完后设置权限：
```bash
chmod 600 ~/.smtp_config
```

## 📋 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `--to` | ✅ | 收件人邮箱 |
| `--subject` | ✅ | 邮件标题 |
| `--body` | ✅ | 邮件内容 |
| `--html` | ❌ | 以 HTML 格式发送 |
| `--attachments` | ❌ | 附件路径，多个用逗号分隔 |
| `--provider` | ❌ | `auto`/`smtp`/`resend`（默认 auto） |

## 🔄 Provider 选择逻辑

- `auto`（默认）：优先 Resend，失败则 fallback 到 SMTP
- `smtp`：强制使用 SMTP
- `resend`：强制使用 Resend API

## 📧 常见 SMTP 配置

| 邮箱 | Host | Port | SSL |
|------|------|------|-----|
| 163 | smtp.163.com | 465 | true |
| QQ | smtp.qq.com | 465 | true |
| Gmail | smtp.gmail.com | 587 | false |
| Outlook | smtp.office365.com | 587 | false |

**注意**：163/QQ/Gmail 都需要使用授权码而非登录密码。

## 🔐 安全

- 凭据存储在 `~/.smtp_config`，权限应设为 600
- API key 和密码不会出现在命令行参数中
- 配置文件不应提交到版本控制

## 🐛 常见问题

**认证失败**：检查授权码是否正确，是否开启了 SMTP 服务

**Resend 403**：免费账户只能发给注册邮箱，需要验证域名才能发给其他人

**连接超时**：检查网络，或者端口是否被防火墙拦截
