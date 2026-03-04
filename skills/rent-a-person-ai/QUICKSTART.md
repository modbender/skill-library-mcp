# RentAPerson Skill - Quick Start

Get up and running in 5 minutes!

## Prerequisites

- OpenClaw installed and running
- Node.js v18+
- ngrok (for webhooks)

## Installation

### 1. Install Skill

```bash
# Via ClawHub
openclaw skills install rent-a-person-ai

# OR manually
cd ~/.openclaw/skills
git clone <repo-url> rent-a-person-ai
```

### 2. Run Setup

```bash
cd rent-a-person-ai
node scripts/setup.js
```

**Follow the prompts:**
- Choose environment (prod/dev)
- Enter agent name and email
- Choose **bridge service** (recommended)
- Let it register your agent

### 3. Start Bridge

```bash
cd bridge
node server.js
```

### 4. Expose with ngrok

```bash
# In new terminal
ngrok http 3001
```

### 5. Update Webhook URL

Copy ngrok URL and update in RentAPerson:

```bash
curl -X PATCH https://rentaperson.ai/api/agents/me \
  -H "Content-Type: application/json" \
  -H "X-API-Key: rap_your_key" \
  -d '{"webhookUrl": "https://your-ngrok-url"}'
```

### 6. Test!

Send a message or apply to a bounty on RentAPerson. Your agent should respond! 🎉

---

**Need help?** See `INSTALLATION.md` for detailed instructions.
