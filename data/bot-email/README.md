# BotEmail.ai Skill for OpenClaw

Professional email infrastructure for autonomous agents. This OpenClaw skill provides access to [BotEmail.ai](https://botemail.ai) - a bot-friendly email service.

## What is this?

An OpenClaw skill that enables your AI agent to:
- Create permanent bot email addresses (random or custom)
- Receive and read emails programmatically
- Extract verification codes automatically
- Monitor inboxes for specific messages
- Automate email-based workflows

## Features

✅ **Permanent inboxes** - Email addresses never expire  
⚠️ **RECEIVE ONLY** - Currently receive-only (sending emails coming soon)  
✅ **Random or custom** - `9423924_bot@botemail.ai` or `mybot_bot@botemail.ai`  
✅ **JSON-first API** - Bot-friendly responses  
✅ **Free tier** - 1 address, 1000 requests/day  
✅ **Private** - Isolated inboxes per bot  
✅ **Web dashboard** - Human-accessible viewer  
✅ **Webhook support** - Push notifications  
✅ **MCP server** - Claude Desktop integration  

## Installation

### For OpenClaw Users

```bash
# Clone to your OpenClaw skills directory
cd ~/.openclaw/skills  # or your custom skills path
git clone https://github.com/claw-silhouette/bot-email-skill.git bot-email
```

Restart OpenClaw and the skill will be available.

### For ClawHub Users

Find and install via [ClawHub.com](https://clawhub.com) (coming soon).

## Quick Start

### Create a Bot Email

**Random username (instant):**
```bash
curl -X POST https://api.botemail.ai/api/create-account \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Custom username:**
```bash
curl -X POST https://api.botemail.ai/api/create-account \
  -H "Content-Type: application/json" \
  -d '{"username": "mybot"}'
```

### Check Inbox

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://api.botemail.ai/api/emails/mybot_bot@botemail.ai
```

## Example Workflows

### 1. Bot Registration Flow

```javascript
// 1. Create bot email
const account = await createAccount();
// { email: "9423924_bot@botemail.ai", apiKey: "..." }

// 2. Register bot with external service
await registerBot(account.email);

// 3. Wait for verification email
const verificationEmail = await pollInbox(account);

// 4. Extract verification code
const code = extractCode(verificationEmail.bodyText);

// 5. Complete registration
await verifyBot(code);
```

### 2. Extract Verification Code

```javascript
function extractCode(emailBody) {
  const patterns = [
    /code[:\s]+([A-Z0-9]{6,8})/i,
    /verification code[:\s]+([A-Z0-9]{6,8})/i,
    /\b([A-Z0-9]{6})\b/,
  ];
  
  for (const pattern of patterns) {
    const match = emailBody.match(pattern);
    if (match) return match[1];
  }
  return null;
}
```

### 3. Monitor for Specific Sender

```javascript
async function waitForSender(email, apiKey, senderDomain, timeout = 300000) {
  const startTime = Date.now();
  
  while (Date.now() - startTime < timeout) {
    const response = await fetch(
      `https://api.botemail.ai/api/emails/${email}`,
      { headers: { 'Authorization': `Bearer ${apiKey}` } }
    );
    
    const data = await response.json();
    const matchingEmail = data.emails?.find(e => 
      e.from.includes(senderDomain)
    );
    
    if (matchingEmail) return matchingEmail;
    
    await new Promise(resolve => setTimeout(resolve, 10000));
  }
  
  throw new Error('Timeout waiting for email');
}
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/create-account` | Create bot email account |
| GET | `/api/emails/{email}` | Get all emails in inbox |
| GET | `/api/emails/{email}/{id}` | Get specific email |
| DELETE | `/api/emails/{email}/{id}` | Delete specific email |
| DELETE | `/api/emails/{email}` | Clear entire inbox |

## Use Cases

- 🤖 **Bot registration** - Automated signup flows
- 📧 **Email verification** - Extract verification codes
- 🔐 **2FA monitoring** - Retrieve authentication codes
- 🔔 **Alert monitoring** - Watch for specific emails
- 📊 **Testing** - End-to-end email testing
- 🤝 **Multi-bot** - Separate inbox per bot

## Documentation

- **Full API Docs**: https://botemail.ai/docs
- **Main Site**: https://botemail.ai
- **Dashboard**: https://botemail.ai/dashboard
- **Skill Documentation**: [SKILL.md](SKILL.md)

## MCP Server

For Claude Desktop integration:

```bash
git clone https://github.com/claw-silhouette/botemail-mcp-server.git
cd botemail-mcp-server
npm install
```

Configure in `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "botemail": {
      "command": "node",
      "args": ["/path/to/botemail-mcp-server/index.js"]
    }
  }
}
```

## Rate Limits

**Free Tier (Only):**
- 1 bot email address
- 1,000 requests per day
- 6-month email retention

Contact support@botemail.ai for higher limits or enterprise plans.

## Error Codes

| Status | Error | Description |
|--------|-------|-------------|
| 400 | Bad Request | Invalid username or format |
| 401 | Unauthorized | Invalid or missing API key |
| 404 | Not Found | Account or email doesn't exist |
| 409 | Conflict | Username already taken |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Server Error | Internal server error |

## Support

- **Email**: support@botemail.ai
- **Issues**: https://github.com/claw-silhouette/bot-email-skill/issues

## Related Projects

- **BotEmail.ai Main Site**: https://botemail.ai
- **MCP Server**: https://github.com/claw-silhouette/botemail-mcp-server
- **OpenClaw**: https://openclaw.ai

## License

MIT License - Free to use

## Contributing

Contributions welcome! Please open an issue or PR.

---

Built with ❤️ for autonomous agents
