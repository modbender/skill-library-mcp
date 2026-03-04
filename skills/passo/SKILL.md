# Passo - Remote Browser Access

Give your user remote access to a browser on your server. Perfect for logins, 2FA, captchas, or any manual browser action.

## Installation

Run this on the server where you want the browser:

```bash
curl -fsSL https://raw.githubusercontent.com/felipegoulu/passo-client/main/install.sh | bash
```

The script will:
1. Prompt the user to sign up at getpasso.app (if no account)
2. Install dependencies (Chromium, VNC, etc.)
3. Create the `passo` command

## Your Browser URL

{{ACCESS_URL}}

Protected by: {{EMAIL}}

## Commands

```bash
passo start   # Start the browser tunnel
passo stop    # Stop everything  
passo status  # Check if running
```

## How to use

1. Send the URL above when you need human help
2. User opens it on their phone/laptop
3. User signs in with Google (only their email can access)
4. User does the action (login, 2FA, captcha, etc.)
5. User says "done"
6. You continue

## Pricing

$5/month after 30-day free trial. Managed via getpasso.app/dashboard.

## Links

- Website: https://getpasso.app
- Docs: https://getpasso.app/docs
