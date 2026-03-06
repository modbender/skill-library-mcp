# LobsterMail

An OpenClaw skill that gives Claude real `@lobstermail.ai` email inboxes — create them instantly, receive email in real-time, send email. No API keys, no human signup, no configuration.

## What Claude can do with this skill

- **Create an email address on the fly** — picks a meaningful name based on context (e.g. `sarah-shield@lobstermail.ai`) with automatic collision handling
- **Receive emails** — poll an inbox, wait for a specific message, or filter by sender/subject
- **Send emails** — compose and send from any provisioned inbox (requires Tier 1+)
- **Read content safely** — every email is scanned for prompt injection, spam, and phishing before being passed to the model

## Quick test

After installing the skill, try asking Claude:

> Create yourself an email inbox and tell me the address.

or

> Sign up for [some service] using a LobsterMail inbox and read the verification email.

Claude will create a `@lobstermail.ai` inbox, auto-provision an account (no API key needed), and start receiving real email.

## How it works

The skill uses the `lobstermail-mcp` MCP server, which runs as a local process and exposes email tools directly to Claude.

| Step | What happens |
|------|-------------|
| **1. Account** | Auto-signup on first use — no API key or human action required |
| **2. Inbox creation** | `create_inbox` tries identity-based names, then numbered fallbacks, then random |
| **3. Receive** | `wait_for_email` long-polls the server and returns the moment a matching email arrives |
| **4. Safe read** | `get_email` returns content wrapped in boundary markers with injection risk metadata |

## Security

Every inbound email is scanned for:

- **Prompt injection** — boundary manipulation, system prompt overrides, role hijacking, data exfiltration attempts, obfuscated payloads
- **Spam & phishing** — keyword patterns, suspicious URLs, urgency language
- **SPF / DKIM / DMARC** — sender authentication results from SES

Claude checks `isInjectionRisk` before acting on any email content.

## Links

- **MCP server on npm**: [`lobstermail-mcp`](https://www.npmjs.com/package/lobstermail-mcp)
- **SDK on npm**: [`lobstermail`](https://www.npmjs.com/package/lobstermail)
- **Website**: [lobstermail.ai](https://lobstermail.ai)
- **API docs**: [api.lobstermail.ai/v1/docs/openapi](https://api.lobstermail.ai/v1/docs/openapi)
