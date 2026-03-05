# Aliyun Mail Skill

A通用的邮件发送技能，专为阿里云企业邮箱优化，支持多种邮件格式和高级功能。

## 功能特性

- **多格式支持**: 纯文本、Markdown、HTML 邮件
- **语法高亮**: Markdown 中的代码块自动添加语法高亮
- **附件支持**: 支持多个文件附件
- **配置管理**: 通过 JSON 配置文件管理 SMTP 设置
- **错误处理**: 包含重试机制和详细错误日志
- **阿里云优化**: 针对阿里云企业邮箱 (smtp.mxhichina.com) 进行优化

## 安装和配置

### 1. 创建配置文件

将示例配置文件复制到 OpenClaw 配置目录：

```bash
cp example-smtp-config.json /root/.openclaw/smtp-config.json
```

### 2. 编辑配置文件

编辑 `/root/.openclaw/smtp-config.json` 文件，填入您的阿里云企业邮箱信息：

```json
{
  "server": "smtp.mxhichina.com",
  "port": 465,
  "username": "your-email@yourdomain.com",
  "password": "your-password",
  "emailFrom": "your-email@yourdomain.com",
  "useTLS": true
}
```

**安全提示**: 确保配置文件权限设置为 600:
```bash
chmod 600 /root/.openclaw/smtp-config.json
```

## 使用方法

### 基本用法

```bash
# 发送纯文本邮件
python3 email_sender.py --to "recipient@example.com" --subject "Hello" --body "你好"

# 发送Markdown邮件
python3 email_sender.py --to "recipient@example.com" --subject "Report" --body "**Important updates**" --markdown

# 发送HTML邮件
python3 email_sender.py --to "recipient@example.com" --subject "Newsletter" --body "<h1>Hello</h1>" --html

# 发送带附件的邮件
python3 email_sender.py --to "recipient@example.com" --subject "Documents" --body "See attached files" --attachments file1.pdf file2.docx
```

### 高级用法

```bash
# 从文件读取邮件内容
python3 email_sender.py --to "recipient@example.com" --subject "Long Report" --body-file report.md --markdown

# 组合多种选项
python3 email_sender.py \
  --to "recipient@example.com" \
  --subject "Weekly Update" \
  --body-file weekly-update.md \
  --markdown \
  --attachments report.pdf slides.pptx
```

## 依赖项

- Python 3.6+
- `markdown` 库 (用于Markdown转换)
- `pygments` 库 (用于语法高亮)

安装依赖：
```bash
pip install markdown pygments
```

## 错误处理

- 自动重试机制（最多3次）
- 详细的错误日志记录
- 网络连接和认证错误的明确提示

## 未来扩展

- CC/BCC 支持
- 邮件模板系统
- 定时邮件发送
- 批量邮件发送

## 兼容性

虽然专为阿里云企业邮箱优化，但此技能也兼容其他SMTP服务（如Gmail、Outlook等），只需在配置文件中修改相应的服务器设置即可。