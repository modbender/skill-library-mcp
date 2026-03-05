# BillionVerify Skill

An Agent Skill for verifying email addresses using the [BillionVerify API](https://billionverify.com/).

## Overview

This skill enables AI agents to verify email addresses — single verification, batch verification, bulk file processing, credit management, and webhook configuration — through the BillionVerify API.

## Installation

Install this skill using the `skills` CLI:

```bash
npx skills add BillionVerify/billionverify-skill
```

Or install to specific agents:

```bash
npx skills add BillionVerify/billionverify-skill -a cursor -a claude-code
```

## Setup

Before using this skill, you need to:

1. Get your BillionVerify API key from [https://billionverify.com/auth/sign-in?next=/home/api-keys](https://billionverify.com/auth/sign-in?next=/home/api-keys)
2. Set it as an environment variable:

```bash
export BILLIONVERIFY_API_KEY=your_api_key_here
```

## Usage Examples

Once installed, your AI agent can use this skill to:

### Verify a single email

```
Verify the email address user@example.com
```

### Batch verify multiple emails

```
Verify these emails: alice@gmail.com, bob@company.com, test@tempmail.org
```

### Upload a file for bulk verification

```
Upload emails.csv and verify all the email addresses in it
```

### Check credit balance

```
How many verification credits do I have left?
```

### Download filtered results

```
Download only the valid and risky emails from job task_abc123
```

### Manage webhooks

```
Create a webhook to notify https://myapp.com/hook when file verification completes
```

```
List all my webhooks
```

## Features

- Verify single email addresses in real-time
- Batch verify up to 50 emails per request
- Upload CSV/Excel/TXT files for bulk verification (up to 100,000 emails)
- Track async file verification job status with long-polling
- Download filtered results by verification status
- Check credit balance and usage
- Create, list, and delete webhooks for file completion events
- Health check endpoint

## Verification Statuses

| Status | Description | Credits |
|--------|-------------|---------|
| `valid` | Email is valid and deliverable | 1 |
| `invalid` | Email is invalid or does not exist | 0 |
| `unknown` | Verification result is uncertain | 0 |
| `risky` | Email may be risky to send to | 1 |
| `disposable` | From a disposable email service | 1 |
| `catchall` | Domain accepts all emails | 1 |
| `role` | Role-based address (info@, support@) | 1 |

## API Documentation

For detailed API documentation, visit [https://billionverify.com/docs](https://billionverify.com/docs)

## Requirements

- BillionVerify API key (get one at [https://billionverify.com/auth/sign-in?next=/home/api-keys](https://billionverify.com/auth/sign-in?next=/home/api-keys))
- Environment variable `BILLIONVERIFY_API_KEY` must be set

## License

MIT

## Related Links

- [BillionVerify Website](https://billionverify.com/)
- [BillionVerify API Documentation](https://billionverify.com/docs)
- [BillionVerify Node SDK](https://www.npmjs.com/package/billionverify-sdk)
- [BillionVerify MCP Server](https://www.npmjs.com/package/billionverify-mcp)
- [Skills.sh Directory](https://skills.sh/)
