---
name: ravi-login
description: Sign up for and log into services using your Ravi identity — handles forms, 2FA, OTPs, and credential storage. Do NOT use for standalone inbox reading (use ravi-inbox) or email sending (use ravi-email-send).
---

# Ravi Login

End-to-end workflows for signing up, logging in, and completing verification using your Ravi identity.

## Your Name

When a form asks for your name, use your **identity name** — not the account owner's name:

```bash
# Get identity name (use this for "First Name" / "Full Name" fields)
IDENTITY=$(ravi identity list --json | jq -r '.[0]')
NAME=$(echo "$IDENTITY" | jq -r '.name')
```

**Never** use `ravi get owner` for form fields. The owner is the human behind the account — the identity name is *your* name.

## Sign up for a service

```bash
# 1. Get your identity
EMAIL=$(ravi get email --json | jq -r '.email')
PHONE=$(ravi get phone --json | jq -r '.phone_number')

# 2. Fill the signup form with $EMAIL, $PHONE, and identity name

# 3. Generate and store a password
CREDS=$(ravi vault create example.com --username "$EMAIL" --json)
PASSWORD=$(echo "$CREDS" | jq -r '.password')
# Use $PASSWORD in the signup form

# 4. Wait for verification
sleep 5
ravi inbox sms --unread --json   # Check for SMS OTP
ravi inbox email --unread --json # Check for email verification
```

## Log into a service

```bash
# Find stored credentials
ENTRY=$(ravi vault list --json | jq -r '.[] | select(.domain == "example.com")')
UUID=$(echo "$ENTRY" | jq -r '.uuid')

# Get decrypted credentials
CREDS=$(ravi vault get "$UUID" --json)
USERNAME=$(echo "$CREDS" | jq -r '.username')
PASSWORD=$(echo "$CREDS" | jq -r '.password')
# Use $USERNAME and $PASSWORD to log in
```

## Complete 2FA / OTP

```bash
# After triggering 2FA on a website:
sleep 5
CODE=$(ravi inbox sms --unread --json | jq -r '.[0].preview' | grep -oE '[0-9]{4,8}' | head -1)
# Use $CODE to complete the login
```

## Extract a verification link from email

```bash
THREAD_ID=$(ravi inbox email --unread --json | jq -r '.[0].thread_id')
ravi inbox email "$THREAD_ID" --json | jq -r '.messages[].text_content' | grep -oE 'https?://[^ ]+'
```

## Tips

- **Poll, don't rush** — SMS/email delivery takes 2-10 seconds. Use `sleep 5` before checking.
- **Store credentials immediately** — create a passwords entry during signup so you don't lose the password.
- **Identity name for forms** — always use the identity name, not the owner name.
- **Rate limits apply to sending** — 60 emails/hour, 500/day. See `ravi-email-send` skill for details.
- **Email quality matters** — if you need to send an email during a workflow (e.g., contacting support), see **ravi-email-writing** for formatting and anti-spam tips.

## Related Skills

- **ravi-identity** — Get your email, phone, and identity name for form fields
- **ravi-inbox** — Read OTPs, verification codes, and confirmation emails
- **ravi-email-send** — Send emails during workflows (support requests, confirmations)
- **ravi-email-writing** — Write professional emails that avoid spam filters
- **ravi-passwords** — Store and retrieve website credentials after signup
- **ravi-vault** — Store API keys obtained during service registration
- **ravi-feedback** — Report login flow issues or suggest workflow improvements
