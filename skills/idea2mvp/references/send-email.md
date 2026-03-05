# 邮件通知 — 使用指南

## 概述

通过 `scripts/send_email.py` 将任意文本内容（搜索报告、验证结论、MVP 进度等）发送到用户邮箱。仅使用 Python 标准库（smtplib），无额外依赖。

## 前置条件

脚本运行时会自动检查 `.env.idea2mvp` 中的邮件配置项（`EMAIL_SMTP_HOST`、`EMAIL_SENDER`、`EMAIL_PASSWORD`、`EMAIL_RECEIVER`）。如果缺失或未配置，脚本会报错退出并提示缺少哪些参数。此时应引导用户在 `.env.idea2mvp` 中补充配置，可参考下方「常用邮箱 SMTP 配置」表格。

## 使用方式

### 发送文本内容

```bash
python3 scripts/send_email.py --subject "工具探索报告" --body "报告正文..."
```

### 从文件读取内容发送（支持多个文件合并为一封邮件）

```bash
python3 scripts/send_email.py --subject "工具探索报告" --file tmp/ph_results.txt
python3 scripts/send_email.py --subject "全平台报告" --file tmp/ph_results.txt tmp/github_results.txt tmp/v2ex_results.txt
```

> **Markdown 自动渲染**：当 `--file` 中包含 `.md` 文件时，脚本会自动将内容转换为 HTML 格式发送，邮件中会以渲染后的富文本形式展示（标题、列表、表格、代码块等）。非 `.md` 文件仍以纯文本发送。

### 从 stdin 读取内容

```bash
cat tmp/ph_results.txt | python3 scripts/send_email.py --subject "Product Hunt 报告"
```

### 指定收件人（覆盖 `.env` 中的默认收件人）

```bash
python3 scripts/send_email.py --subject "报告" --body "内容" --to someone@example.com
```

## 触发时机

邮件发送仅在**用户主动要求**时执行。当用户要求将某些信息（报告、搜索结果、文档等）发送到邮箱时，直接运行脚本即可。如果脚本报错提示缺少配置，引导用户补充 `.env.idea2mvp` 中的邮件参数。

## 常用邮箱 SMTP 配置

| 邮箱 | SMTP 地址 | 端口 | 授权码获取 |
|------|----------|------|-----------|
| QQ 邮箱 | smtp.qq.com | 465 | 设置 → 账户 → POP3/SMTP → 生成授权码 |
| Gmail | smtp.gmail.com | 465 | Google 账户 → 安全 → 应用专用密码 |
| 163 邮箱 | smtp.163.com | 465 | 设置 → POP3/SMTP → 开启并获取授权码 |
| Outlook | smtp.office365.com | 587 | 直接使用登录密码 |
