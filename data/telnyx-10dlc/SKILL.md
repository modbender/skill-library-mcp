---
name: 10dlc-registration
description: Register for 10DLC as a sole proprietor to enable SMS messaging in the USA. Use when setting up A2P SMS, registering brands/campaigns, or assigning phone numbers for compliant US messaging. Requires Telnyx CLI.
metadata: {"openclaw":{"emoji":"📱","requires":{"bins":["telnyx"],"env":["TELNYX_API_KEY"]},"primaryEnv":"TELNYX_API_KEY"}}
---

# 10DLC Registration

Register for 10DLC (10-Digit Long Code) to enable A2P SMS in the USA.

## Quick Start with Scripts

```bash
# Interactive registration wizard
./scripts/register.sh

# Check status of brands/campaigns
./scripts/status.sh

# Assign a phone number to a campaign
./scripts/assign.sh +15551234567 <campaign-id>
```

## Prerequisites

- Telnyx CLI installed: `npm install -g @telnyx/api-cli`
- API key configured: `telnyx auth setup`
- At least one US phone number

## Quick Start

Interactive wizard (easiest):

```bash
telnyx 10dlc wizard
```

## Manual Registration

### Step 1: Create Sole Proprietor Brand

```bash
telnyx 10dlc brand create --sole-prop \
  --display-name "Your Business Name" \
  --phone +15551234567 \
  --email you@example.com
```

### Step 2: Verify Brand (if required)

```bash
telnyx 10dlc brand get <brand-id>
telnyx 10dlc brand verify <brand-id> --pin 123456
```

### Step 3: Create Campaign

```bash
telnyx 10dlc campaign create \
  --brand-id <brand-id> \
  --usecase CUSTOMER_CARE \
  --description "Customer notifications and support" \
  --sample-message-1 "Your order #12345 has shipped." \
  --sample-message-2 "Reply STOP to opt out."
```

### Step 4: Assign Phone Number

```bash
telnyx 10dlc assign +15551234567 <campaign-id>
```

### Step 5: Wait for Approval

```bash
telnyx 10dlc campaign get <campaign-id>
```

## Use Cases

| Use Case | Description |
|----------|-------------|
| `2FA` | Auth codes |
| `CUSTOMER_CARE` | Support messages |
| `ACCOUNT_NOTIFICATION` | Account alerts |
| `DELIVERY_NOTIFICATION` | Shipping updates |
| `MIXED` | Multiple purposes |

List all: `telnyx 10dlc usecases`

## Status Commands

```bash
telnyx 10dlc brand list
telnyx 10dlc campaign list
telnyx 10dlc assignment status +15551234567
```

## Troubleshooting

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Brand verification required` | Sole proprietor brands need phone verification | Check email/SMS for PIN, run `telnyx 10dlc brand verify <id> --pin <code>` |
| `Campaign rejected: insufficient description` | Description too vague | Be specific about message purpose, include business context |
| `Sample messages must include opt-out` | Missing STOP instructions | Add "Reply STOP to unsubscribe" to sample messages |
| `Phone number already assigned` | Number linked to another campaign | Run `telnyx 10dlc unassign +1...` first |
| `Brand pending` | Still under review (24-72h typical) | Wait and check status with `telnyx 10dlc brand get <id>` |
| `Invalid use case for sole proprietor` | Some use cases restricted | Sole prop limited to: 2FA, CUSTOMER_CARE, DELIVERY_NOTIFICATION, ACCOUNT_NOTIFICATION |
| `Rate limit exceeded` | Too many API calls | Wait 60s and retry |

### Debug Tips

```bash
# Verbose output for debugging
telnyx 10dlc brand get <id> --json

# Check number assignment status
telnyx 10dlc assignment status +15551234567

# List all campaigns with details
telnyx 10dlc campaign list --json | jq '.data[] | {id, status, usecase}'
```

### Timeline Expectations

| Step | Typical Time |
|------|--------------|
| Brand creation | Instant |
| Brand verification | 1-5 minutes (PIN via SMS/email) |
| Brand approval | 24-72 hours |
| Campaign review | 24-48 hours |
| Number assignment | Instant (after campaign approved) |

### Getting Help

- Telnyx docs: https://developers.telnyx.com/docs/messaging/10dlc
- Support portal: https://support.telnyx.com
- API status: https://status.telnyx.com

## Pricing

Brand and campaign registration: **Free**
