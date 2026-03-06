# Getting Started with Mailtarget + OpenClaw

Send your first email in under 5 minutes.

## Prerequisites

- [OpenClaw](https://openclaw.ai) installed and running
- A [Mailtarget](https://mailtarget.co) account with API access
- A verified sending domain in Mailtarget

## Step 1: Install the Skill

```bash
clawhub install mailtarget-email
```

## Step 2: Get Your API Key

1. Log in to [app.mailtarget.co](https://app.mailtarget.co)
2. Go to **Settings → API Keys**
3. Click **Create API Key**
4. Copy the key

## Step 3: Configure OpenClaw

Add your API key to the OpenClaw gateway environment:

```bash
openclaw env set MAILTARGET_API_KEY=your_api_key_here
```

Or export it in your shell:

```bash
export MAILTARGET_API_KEY=your_api_key_here
```

## Step 4: Send Your First Email

Just tell your agent:

> "Send a test email to hello@example.com from noreply@mydomain.com with the subject 'Hello from OpenClaw' and a simple welcome message."

The agent handles the rest — writing the HTML, calling the API, confirming delivery.

## Step 5: Try More

Here are things you can ask your agent to do:

- **"Send a campaign to these 50 contacts with personalized greetings"** — uses substitution data
- **"Create an HTML email template for our weekly newsletter"** — stores it via the Template API
- **"List our sending domains and check which ones are verified"** — domain management
- **"Send a transactional receipt email with a PDF attachment"** — attachments + transactional flag

## What's Happening Under the Hood

```
You (vision) → OpenClaw Agent (execution) → Mailtarget API (delivery)
```

- **You** decide what to send and who to send it to
- **OpenClaw** writes the content, builds the HTML, calls the API
- **Mailtarget** handles delivery, authentication (SPF/DKIM/DMARC), tracking, and reliability

## Tracking & Events

Enable open and click tracking by telling your agent:

> "Send the email with open tracking and click tracking enabled."

The agent sets `openTracking: true` and `clickTracking: true` in the API call. Mailtarget fires webhook events for opens, clicks, bounces, and deliveries.

## Troubleshooting

| Problem | Fix |
|---|---|
| `401 Unauthorized` | Check your API key is correct and active |
| `400 Bad Request` | Verify the `from` email uses a verified sending domain |
| Email not arriving | Check spam folder; verify SPF/DKIM records for your domain |
| `MAILTARGET_API_KEY` not found | Ensure the env var is set in the gateway environment |

## Resources

- [Mailtarget API Docs](https://developer.mailtarget.co)
- [Mailtarget Dashboard](https://app.mailtarget.co)
- [OpenClaw Docs](https://docs.openclaw.ai)
- [ClawHub Marketplace](https://clawhub.ai)
