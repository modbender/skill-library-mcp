# Email Send Protocol

## Draft-Review-Send Workflow

**NEVER auto-send.** Always follow this flow:

1. **Compose**: Generate full email content
2. **Review**: Show user the complete message (To, Subject, Body)
3. **Confirm**: Wait for explicit "send" or "OK"
4. **Send**: Execute `himalaya message send`

## Reply Threading

Include these headers or thread breaks:

```
In-Reply-To: <original-message-id@domain.com>
References: <original-message-id@domain.com>
```

**Trap**: "Re:" subject prefix is unreliable for threading. Some clients add it, some don't.

## RFC 2822 Format

himalaya expects stdin in this format:

```
From: sender@example.com
To: recipient@example.com
Subject: Your Subject
In-Reply-To: <message-id> (if reply)
Content-Type: text/plain; charset=utf-8

Email body here.
```

## SMTP Rejection Cases

- **From mismatch**: Some servers reject if From header ≠ authenticated user
- **Missing headers**: Always include Date, Message-ID
- **Rate limits**: Gmail: 500/day personal, 2000/day Workspace

## Attachments

```bash
# himalaya attachment flow
himalaya message send < composed_email.eml
# Attachments via MIME multipart - complex, use library if needed
```

## Trap: Silent Failures

- himalaya may exit 0 even if SMTP rejected
- Check server response in verbose mode: `himalaya -v message send`
- Verify sent folder after important sends
