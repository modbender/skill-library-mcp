---
name: qq-email
description: "Send and receive emails via QQ Mail SMTP/IMAP. Use when: user wants to send/receive emails, check inbox, read messages, or share documents via email. Requires QQ email authorization code configured in TOOLS.md."
homepage: https://mail.qq.com
metadata: { "openclaw": { "emoji": "📧", "requires": { "bins": ["python3"], "files": ["~/.openclaw/workspace/skills/qq-email/qq_email.py", "~/.openclaw/workspace/TOOLS.md"] } } }
---

# QQ Email Skill

Send and receive emails via QQ Mail SMTP/IMAP server.

## When to Use

✅ **USE this skill when:**

- "Send an email to..."
- "Check my emails"
- "Read my unread emails"
- "Email this to [someone]"
- "Notify [person] via email"
- "Share this document via email"
- "What's in my inbox?"

## When NOT to Use

❌ **DON'T use this skill when:**

- Sending SMS/WhatsApp → use messaging tools
- Internal notes → use memory files
- Public posts → use social media tools

## Configuration Required

Before using, configure in `TOOLS.md`:

```markdown
### QQ Email

- Email: your_qq_number@qq.com
- Auth Code: your_16_char_auth_code
- Sender Name: Your Name
```

**Get QQ Auth Code:**
1. Login to mail.qq.com
2. Settings → Account
3. Enable POP3/SMTP service
4. Generate authorization code (16 characters)

## Commands

### Send Email

```bash
python3 ~/.openclaw/workspace/skills/qq-email/qq_email.py send \
  --to "recipient@example.com" \
  --subject "Email Subject" \
  --content "Email content here"
```

### Receive/List Emails

```bash
# List 10 recent emails
python3 ~/.openclaw/workspace/skills/qq-email/qq_email.py receive

# List 20 emails
python3 ~/.openclaw/workspace/skills/qq-email/qq_email.py receive --count 20

# Unread emails only
python3 ~/.openclaw/workspace/skills/qq-email/qq_email.py receive --unread
```

### Read Specific Email

```bash
# Read email by UID
python3 ~/.openclaw/workspace/skills/qq-email/qq_email.py read --uid 123

# Read and save attachments
python3 ~/.openclaw/workspace/skills/qq-email/qq_email.py read --uid 123 --save
```

### Mark Email as Read

```bash
python3 ~/.openclaw/workspace/skills/qq-email/qq_email.py mark-read --uid 123
```

### Send HTML Email

```bash
python3 ~/.openclaw/workspace/skills/qq-email/qq_email.py send \
  --to "recipient@example.com" \
  --subject "HTML Email" \
  --content "<h1>Hello</h1><p>HTML content</p>" \
  --html
```

### Send with Attachment

```bash
python3 ~/.openclaw/workspace/skills/qq-email/qq_email.py send \
  --to "recipient@example.com" \
  --subject "Document Attached" \
  --content "Please find attached." \
  --attachment "/path/to/file.pdf"
```

## Quick Responses

**"Send an email to test@example.com"**

→ Ask for subject and content, then:
```bash
python3 ~/.openclaw/workspace/skills/qq-email/qq_email.py --to "test@example.com" --subject "[subject]" --content "[content]"
```

**"Email this file to someone"**

→ Ask for recipient and add attachment:
```bash
python3 ~/.openclaw/workspace/skills/qq-email/qq_email.py --to "[email]" --subject "[subject]" --content "[content]" --attachment "[file]"
```

## Notes

- Auth code ≠ QQ password (get from mail.qq.com settings)
- SMTP server: smtp.qq.com:465 (SSL)
- Rate limited: ~50 emails/hour for free accounts
- Attachments ≤ 50MB per email
- All sent emails saved in QQ Mail "Sent" folder
