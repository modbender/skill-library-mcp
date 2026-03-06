---
name: linkedin-outreach
version: 1.0.3
description: 🚀 LinkedIn automation with Free (10/month) & Pro ($29/mo unlimited) tiers. Automate connections, follow-ups & lead gen.
author: CEO Claw
tags: [linkedin, outreach, automation, leads, sales]
---

# LinkedIn Outreach Automation

Automated LinkedIn lead generation tool supporting connection requests, follow-up messages, and report generation.

## Features

- 🔐 **Login to LinkedIn** - Secure authentication with session reuse support
- 🔍 **Search Target Users** - Search by keywords, company, title
- ➕ **Send Connection Requests** - Batch sending with personalized messages
- 💬 **Send Follow-up Messages** - Auto-follow up on sent requests
- 📊 **Generate Reports** - Lead reports in CSV/JSON format

## Usage

```bash
# Login to LinkedIn
linkedin login

# Search users (keywords + filters)
linkedin search --keywords "software engineer" --location "San Francisco" --limit 50

# Send connection requests
linkedin connect --urns "urn1,urn2" --message "Hi, I'd love to connect!"

# Send follow-up messages
linkedin followup --days 3 --message "Hi, just following up..."

# Generate report
linkedin report --format csv --output leads.csv
```

## Options

### login
No parameters. Opens browser for login on first use.

### search
| Parameter | Description | Default |
|-----------|-------------|---------|
| --keywords | Search keywords | required |
| --location | Geographic location | - |
| --company | Company name | - |
| --title | Job title | - |
| --limit | Result limit | 10 |

### connect
| Parameter | Description | Default |
|-----------|-------------|---------|
| --urns | User URN list (comma-separated) | required |
| --message | Personalized message | - |
| --file | Message template file | - |

### followup
| Parameter | Description | Default |
|-----------|-------------|---------|
| --days | Wait days | 3 |
| --message | Follow-up message | required |
| --dry-run | Preview only, no send | false |

### report
| Parameter | Description | Default |
|-----------|-------------|---------|
| --format | Format: csv, json | csv |
| --output | Output file path | stdout |
| --status | Filter status: all, pending, connected | all |

## Environment Variables

```bash
# LinkedIn credentials (optional, for auto-login)
LINKEDIN_EMAIL=your@email.com
LINKEDIN_PASSWORD=yourpassword

# Config file path
LINKEDIN_CONFIG=~/.config/linkedin-outreach.json
```

## Message Template Examples

```json
{
  "connect": "Hi {first_name}, I came across your profile and I'm impressed by your work at {company}. I'd love to connect and learn more about what you're working on.",
  "followup": "Hi {first_name}, I noticed we haven't connected yet. I'd love to network with you and share some insights about {industry} that might be valuable."
}
```

## Notes

1. **Follow LinkedIn Terms of Service** - Over-automation may lead to account restrictions
2. **Limit Request Frequency** - Recommend 50-100 connection requests per day max
3. **Use Personalized Messages** - Improves acceptance rate
4. **Session Reuse** - Avoid frequent logins

## Pricing

$29/month or $49 one-time

## Free vs Pro

- **Free**: 10 connection requests/month
- **Pro** ($29/month): Unlimited + Auto-followup + Analytics

**Upgrade**: https://buy.stripe.com/8x24gz1t800q7osf9057W00 or contact @ceo_claw

## Dependencies

- Node.js 18+
- Playwright
- Config stored in ~/.config/linkedin-outreach/
