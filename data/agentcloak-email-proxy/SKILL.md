---
name: agentcloak
description: "Secure email proxy for AI agents. Search, read, and draft emails via MCP with server-side credential isolation, PII redaction, prompt injection detection, and content filtering. Unlike raw Gmail/IMAP skills, your agent never sees passwords or unfiltered content. Self-host or use the hosted version."
homepage: https://github.com/ryanfren/AgentCloak
user-invocable: true
metadata:
  clawdbot:
    emoji: "\U0001F6E1\uFE0F"
    requires:
      bins:
        - mcporter
      env:
        - AGENTCLOAK_API_KEY
    primaryEnv: AGENTCLOAK_API_KEY
---

# AgentCloak

Secure email proxy for AI agents. AgentCloak sits between your agent and your email, so the agent gets useful email access without seeing credentials, sensitive financial data, PII, or prompt injection attacks.

Every other email skill on ClawHub gives your agent raw, unfiltered access to your inbox. AgentCloak is the only one with a built-in security pipeline.

## What makes this different

- **Credential isolation** — your email password/OAuth tokens stay server-side; the agent only has an API key
- **4-stage content filter** — blocklist, HTML sanitizer, PII redaction, prompt injection detection
- **Read + draft only** — agents can search, read, list, and draft emails but cannot send, delete, or modify anything
- **Draft safety** — drafts are never sent automatically; you review them first
- **Self-host or hosted** — run your own instance or use the hosted version

## Setup

### Option A: Hosted version (quickest)

1. Sign up at https://agentcloak.up.railway.app
2. Connect your email (IMAP works with any provider, Gmail OAuth available by invite)
3. Create an API key in the dashboard
4. Configure:

```bash
export AGENTCLOAK_API_KEY=ac_your_key_here
mcporter config add agentcloak \
  --baseUrl "https://agentcloak.up.railway.app/mcp" \
  --header "Authorization: Bearer $AGENTCLOAK_API_KEY"
```

### Option B: Self-hosted

1. Clone and run:

```bash
git clone https://github.com/ryanfren/AgentCloak.git
cd agentcloak
pnpm install && pnpm build && pnpm dev
```

2. Open http://localhost:3000, create an account, connect email, create API key
3. Configure:

```bash
export AGENTCLOAK_URL=http://localhost:3000
export AGENTCLOAK_API_KEY=ac_your_key_here
mcporter config add agentcloak \
  --baseUrl "${AGENTCLOAK_URL}/mcp" \
  --header "Authorization: Bearer $AGENTCLOAK_API_KEY"
```

**Requirements for self-hosting:** Node.js 20+, pnpm 10+

## Available tools

| Tool | Description | Key parameters |
|------|-------------|----------------|
| `search_emails` | Search emails with Gmail-style queries | `query`, `max_results` (1-200), `page_token` |
| `read_email` | Read full email content by ID | `message_id` |
| `list_threads` | List conversation threads | `query`, `max_results`, `page_token` |
| `get_thread` | Read all messages in a thread | `thread_id` |
| `create_draft` | Create a draft (not sent) | `to`, `subject`, `body`, `in_reply_to_thread_id` |
| `list_drafts` | List existing drafts | `max_results` |
| `list_labels` | List all labels with unread counts | (none) |
| `get_provider_info` | Get provider type and capabilities | (none) |

## Usage examples

```bash
# Search for unread emails
mcporter call agentcloak.search_emails query:"is:unread" max_results:10

# Read a specific email
mcporter call agentcloak.read_email message_id:"abc123"

# Get a full conversation thread
mcporter call agentcloak.get_thread thread_id:"thread456"

# Draft a reply (not sent until you review it)
mcporter call agentcloak.create_draft subject:"Re: Meeting" body:"Sounds good, see you Thursday." in_reply_to_thread_id:"thread456"

# List labels and unread counts
mcporter call agentcloak.list_labels
```

## Security pipeline

Every email passes through a 4-stage filter before the agent sees it. Each stage is independently configurable from the dashboard.

### Stage 1: Blocklist

Blocks emails from sensitive senders outright. Three toggleable categories:

- **Financial** — 40+ domains (Chase, PayPal, Venmo, Coinbase, etc.)
- **Security senders** — patterns like security@, fraud@, alerts@, .gov addresses
- **Security subjects** — password resets, 2FA codes, verification links, login alerts

Plus custom blocklists: add your own domains, sender patterns, or subject patterns.

### Stage 2: HTML sanitizer

Converts HTML email to plaintext and strips dangerous Unicode (zero-width characters, bidirectional overrides, tag characters, variation selectors) that could be used to hide prompt injection.

### Stage 3: PII redaction

Redacts sensitive patterns with placeholders:

- SSNs, credit card numbers, bank account/routing numbers
- API keys (`sk_`, `pk_`, AWS keys), bearer tokens, PEM private keys
- Optionally: email addresses, large dollar amounts

### Stage 4: Prompt injection detection

Scans for 19 known injection patterns (instruction overrides, role reassignments, system tag injections, data exfiltration attempts). Flags detected content with a `[AGENTCLOAK WARNING]` prefix so the agent knows the email may be adversarial. Does not block — lets the agent make an informed decision.

## Security and privacy

**What data leaves your machine:**

| Scenario | Data flow |
|----------|-----------|
| Self-hosted | Nothing leaves your machine. All processing is local. |
| Hosted version | Your email credentials are stored server-side (encrypted). Email content passes through the hosted server's filter pipeline. No data is shared with third parties. |

- API keys are hashed (SHA-256) before storage — the server cannot recover your key after creation
- Email credentials are stored server-side; the agent never sees them
- All filtering happens server-side before content reaches the agent
- The agent can only read and draft — it cannot send, delete, or modify emails
- Source code is open: https://github.com/ryanfren/AgentCloak

**Trust statement:** By using the hosted version, you trust the AgentCloak server with access to your email account credentials and content. If this is not acceptable, self-host your own instance for full control.

## Email providers

AgentCloak supports three connection methods:

- **IMAP** — works with any email provider (Gmail, Outlook, ProtonMail Bridge, Fastmail, etc.)
- **Gmail OAuth** — direct API access (currently invite-only during beta)
- **Gmail Apps Script** — manual setup via script.google.com, no Google Cloud project needed

## Limitations

- Read and draft only — no send, delete, or modify
- Gmail search syntax only (even for IMAP connections, queries are translated)
- Attachment content is not accessible (metadata can optionally be shown)
- Gmail OAuth is invite-only during beta; IMAP and Apps Script are open to all
- Hosted version is in beta

## Links

- Homepage: https://agentcloak.up.railway.app
- Source: https://github.com/ryanfren/AgentCloak
- License: BSL 1.1
