---
name: telcall-twilio
description: Make emergency phone calls via Twilio. Use when you need to call someone and play a voice message programmatically (e.g., server down alerts, security notifications).
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["curl", "jq"] },
      },
  }
---

# TelCall Twilio - Emergency Phone Calls

Make phone calls that speak a message to the recipient using Twilio's Voice API.

## Author

- **Name:** Micheal Sun
- **Email:** laosun1985@gmail.com
- **X:** https://x.com/pingfanbufan
- **GitHub:** https://github.com/cnvipstar

## Features

- Make phone calls via Twilio API
- Text-to-speech message delivery (supports multiple languages)
- Simple configuration
- Easy integration with OpenClaw

## Prerequisites

### 1. Twilio Account

1. Visit https://www.twilio.com and sign up
2. During setup, choose:
   - **"With code"** (for full API access)
   - **"Voice"** channel
3. Bind a credit card (required for production use)

### 2. Purchase a Phone Number

1. Go to **Phone Numbers** → **Buy a Number**
2. Select **United States** (easiest, no address verification needed)
3. Filter by **Voice** capability
4. Purchase a local number (~$1/month)

### 3. Get Your Credentials

From the Twilio Console homepage, copy:
- **Account SID** (starts with `AC...`)
- **Auth Token** (click to reveal)

### 4. Verify Your Phone Number (Trial Accounts)

Trial accounts can only call verified numbers:
1. Go to **Phone Numbers** → **Verified Caller IDs**
2. Add your phone number
3. Complete verification via SMS or voice call

**Note:** Upgrade your account ($20 minimum) to call any number without verification.

## Setup

Run the setup script to configure your Twilio credentials:

```bash
bash ~/.openclaw/workspace/telcall-twilio/scripts/setup.sh
```

You will be prompted to enter:
- Account SID
- Auth Token
- Twilio phone number (e.g., `+15551234567`)
- Your phone number (e.g., `+8613812345678`)

## Usage

### Basic Call

```bash
bash ~/.openclaw/workspace/telcall-twilio/scripts/call.sh "Your message here"
```

### With OpenClaw

Simply tell your assistant:
- "Call me: Server is down!"
- "Emergency call: Security breach detected"

The assistant will use this skill to make the call.

## Cost

| Item | Price |
|------|-------|
| US Phone Number | ~$1/month |
| Call to most countries | ~$0.02-0.15/min |
| Text-to-speech | Free (TwiML) |

**Estimated monthly cost:** $2-5 for occasional emergency calls.

## Troubleshooting

### "Number is unverified"

Your account is in trial mode. Either:
1. Verify the destination number in Twilio Console
2. Upgrade your account ($20) to call any number

### Call doesn't go through

1. Check your Twilio number has **Voice** capability
2. Verify your Auth Token is correct
3. Ensure you have account balance

## Files

```
telcall-twilio/
├── SKILL.md           # This file
├── scripts/
│   ├── setup.sh       # Configure credentials
│   └── call.sh        # Make a phone call
└── config/
    └── twilio.json    # Credentials (created by setup.sh)
```

## License

MIT License - Feel free to use and modify.
