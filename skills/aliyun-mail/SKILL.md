---
name: aliyun-mail
description: A skill to send emails via Aliyun enterprise email service with support for markdown, HTML text, attachments, and syntax highlighting for code blocks.
---

# Aliyun Mail Skill

This skill enables sending emails through Aliyun enterprise email service with advanced features including Markdown conversion, HTML styling, file attachments, and syntax highlighting for code blocks.

## Features
- **Aliyun Enterprise Email Support**: Optimized for Aliyun's SMTP service (smtp.mxhichina.com)
- **Multiple Content Types**: Send plain text, Markdown, or HTML emails
- **Markdown with Syntax Highlighting**: Automatic syntax highlighting for code blocks in Markdown
- **File Attachments**: Include one or more files as attachments
- **Configuration-based**: Uses a secure configuration file for SMTP credentials
- **Error Handling**: Includes retry logic and detailed error reporting

## Prerequisites
- **SMTP Configuration File**: Create `aliyun-mail-config.json` in your OpenClaw config directory (`/root/.openclaw/`)

Example configuration file:
```json
{
  "server": "smtp.mxhichina.com",
  "port": 465,
  "username": "your-email@yourdomain.com",
  "password": "your-app-password",
  "emailFrom": "your-email@yourdomain.com",
  "useTLS": true
}
```

Ensure the configuration file has secure permissions:
```bash
chmod 600 /root/.openclaw/aliyun-mail-config.json
```

## Usage

### Basic Text Email
```bash
aliyun-mail send --to "recipient@example.com" --subject "Hello" --body "This is a plain text email"
```

### Markdown Email with Syntax Highlighting
```bash
aliyun-mail send \
  --to "recipient@example.com" \
  --subject "Code Report" \
  --body "**Check out this Python code:**\n\n```python\nprint('Hello World')\n```" \
  --markdown
```

### HTML Email with Attachment
```bash
aliyun-mail send \
  --to "recipient@example.com" \
  --subject "Weekly Report" \
  --body "<h1>Weekly Report</h1><p>See attached file.</p>" \
  --html \
  --attachments "/path/to/report.pdf"
```

### Using Body from File
```bash
aliyun-mail send \
  --to "recipient@example.com" \
  --subject "Report from File" \
  --body-file "/path/to/report.md" \
  --markdown \
  --attachments "/path/to/data.csv"
```

## Command Line Options
- `--to`: Recipient email address (required)
- `--subject`: Email subject (required)
- `--body`: Email body content (required if --body-file not provided)
- `--body-file`: Path to file containing email body
- `--html`: Send as HTML email (default: plain text)
- `--markdown`: Send as Markdown email with syntax highlighting
- `--attachments`: Space-separated list of file paths to attach

## Error Handling
The tool includes robust error handling with up to 3 retry attempts on failure. Network issues, authentication errors, and invalid email addresses are reported with detailed error messages.

## Security Notes
- Always use app-specific passwords rather than your main email password
- Keep the configuration file secure with proper file permissions
- Never commit configuration files to version control

## Future Enhancements
- Support for CC/BCC recipients
- Email templates system
- Scheduled email sending
- Rich text editor integration