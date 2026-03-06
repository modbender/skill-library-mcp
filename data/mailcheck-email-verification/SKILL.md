---
name: mailcheck-email-verification
description: Email verification skill for MailCheck API - verify emails, bulk processing, authenticity analysis
---

# MailCheck Email Verification

Verify email addresses with the MailCheck API - comprehensive email validation with syntax, disposable, DNS, and SMTP checks.

## Features

- **Single Email Verification** - Verify one email at a time
- **Bulk Verification** - Verify up to 100 emails in one request
- **Authenticity Analysis** - Detect phishing, spoofing, and email fraud
- **Risk Scoring** - 0-100 score with risk level (low/medium/high)

## Commands

### `email-verify` - Verify single email

Verifies a single email address.

**Parameters:**
- `email` (required): Email address to verify
- `api_key` (optional): MailCheck API key (falls back to `MAILCHECK_API_KEY` env var)

**Example:**
```bash
email-verify email="user@example.com" api_key="sk_live_..."
```

### `email-bulk-verify` - Bulk verification

Verifies up to 100 email addresses in one request.

**Parameters:**
- `emails` (required): Array of email addresses
- `api_key` (optional): MailCheck API key

**Example:**
```bash
email-bulk-verify emails="[user1@example.com, user2@gmail.com]" api_key="sk_live_..."
```

### `email-auth-verify` - Email authenticity analysis

Analyzes email headers for spoofing, phishing, and CEO fraud.

**Parameters:**
- `headers` (required): Email headers to analyze
- `trusted_domains` (optional): Domains for lookalike detection
- `api_key` (optional): MailCheck API key

**Example:**
```bash
email-auth-verify headers="From: sender@example.com\nReceived: ..." trusted_domains="[company.com]"
```

## Environment Variables

Set `MAILCHECK_API_KEY` with your MailCheck API key to avoid passing it on every command.

## Installation

This skill is available on [ClawHub](https://clawhub.com).

```bash
clawhub install mailcheck-email-verification
```

## API Reference

See full API documentation: https://api.mailcheck.dev/docs

## Repository

Source code: https://github.com/bnuyts/mailcheck-skill

## License

MIT
