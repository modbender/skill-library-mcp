---
name: email-reader
version: 1.0.0
description: 邮件读取与管理技能 - 让 AI 能够读取、汇总、发送邮件。当用户要求查看邮件、汇总未读、发送邮件通知时触发此技能。
---

# Email Reader - 邮件管理技能

## 概述

赋予 AI 邮件管理能力：
- 读取邮件（IMAP）
- 发送邮件（SMTP）
- 邮件汇总与分类
- 重要邮件提醒

## 触发场景

1. 用户要求"查看邮件"、"读取邮件"
2. 用户要求"汇总未读邮件"
3. 用户要求"发送邮件"
4. 用户要求"检查重要邮件"
5. 定时提醒用户查看邮件

## 支持的邮件服务

| 服务 | 协议 | 说明 |
|------|------|------|
| Gmail | IMAP/SMTP | 需要应用专用密码 |
| Outlook | IMAP/SMTP | 支持 OAuth |
| QQ 邮箱 | IMAP/SMTP | 需要授权码 |
| 网易邮箱 | IMAP/SMTP | 支持 IMAP |

## 使用 himalaya CLI

推荐使用 `himalaya` CLI 进行邮件管理：

### 安装
```bash
# macOS
brew install himalaya

# Linux
cargo install himalaya

# Windows
winget install himalaya
```

### 配置
```bash
himalaya envelope add --name personal \
  --imap-host imap.example.com \
  --imap-port 993 \
  --smtp-host smtp.example.com \
  --smtp-port 587 \
  --username your@email.com \
  --password "your-password"
```

### 常用命令

```bash
# 列出邮件
himalaya list --account personal -w 50

# 阅读邮件
himalaya read <email-id>

# 发送邮件
himalaya send --from your@email.com --to recipient@example.com \
  --subject "Subject" --body "Content"

# 搜索邮件
himalaya search --account personal "keyword"
```

## 工作流

```
1. 检查配置 → 确认 himalaya 已配置
2. 获取邮件 → 使用 list/read 命令
3. 筛选重要 → 标记重要邮件
4. 汇总呈现 → 用中文总结给用户
```

## 安全注意事项

- 不要在日志中暴露密码
- 使用环境变量存储敏感信息
- 建议使用 OAuth 认证（如果支持）

## 输出格式

向用户呈现邮件时：
- 发件人、主题、摘要
- 收到的简要
- 建议操作（回复、删除、标记）
