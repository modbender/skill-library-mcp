# Bloom Discovery Skill

Zero questions asked — reads your conversation memory and reveals your builder personality, blind spots, and matched tools.

## Purpose

Allows OpenClaw bot to analyze conversations **directly from context**, without needing to read session files or external APIs.

## Architecture

```
User: /bloom-identity
       ↓
OpenClaw Bot (has conversation in context)
       ↓
execute.sh (this wrapper)
       ↓
Collects conversation context
       ↓
Pipes to scripts/run-from-context.ts
       ↓
Bloom analyzer (direct text analysis)
       ↓
Returns identity card + recommendations
```

## Installation

### 1. Install Bloom Identity Skill

```bash
cd ~/.openclaw/workspace
git clone https://gitlab.com/bloom-protocol/bloom-discovery-skill.git
cd bloom-identity-skill
npm install
```

### 2. Copy Wrapper to OpenClaw Skills

```bash
cp -r openclaw-wrapper ~/.openclaw/skills/bloom-identity-openclaw
```

### 3. Test

In OpenClaw:
```
/bloom-identity
```

Or from command line:
```bash
echo "User: I love AI tools
Assistant: Great! What kind of AI tools?
User: Mostly coding assistants and LLMs" | bash ~/.openclaw/skills/bloom-identity-openclaw/execute.sh telegram:123
```

## Files

- `SKILL.md` - OpenClaw skill definition
- `execute.sh` - Wrapper script that pipes conversation to analyzer
- `README.md` - This file

## How It Works

1. OpenClaw bot invokes this skill via `/bloom-identity`
2. Bot collects current conversation context (automatically)
3. Context is piped to `execute.sh`
4. `execute.sh` calls `../scripts/run-from-context.ts`
5. TypeScript script analyzes conversation directly
6. Returns formatted identity card

## Key Differences vs. Original Skill

| Feature | Original | OpenClaw Wrapper |
|---------|----------|------------------|
| Data Source | Session files | Conversation context |
| User ID | Required | Provided by bot |
| Wallet | Creates new | Creates new |
| Min Messages | 3 | 3 |
| Execution | External process | Bot context |

## Troubleshooting

**Error: "Bloom Identity Skill not found"**
```bash
# Install the main skill first
cd ~/.openclaw/workspace
git clone https://gitlab.com/bloom-protocol/bloom-discovery-skill.git
cd bloom-identity-skill
npm install
```

**Error: "Insufficient conversation data"**
- Need at least 3 messages in conversation
- Continue chatting with the bot

**Error: "npx command not found"**
- Install Node.js 18+
- Ensure npx is in PATH

## Development

To modify the wrapper:

1. Edit `execute.sh` for shell logic
2. Edit `../scripts/run-from-context.ts` for analysis logic
3. Edit `SKILL.md` for skill documentation

To test locally:
```bash
echo "test conversation" | bash execute.sh test-user-123
```

## Environment Variables

- `OPENCLAW_USER_ID` - Auto-provided by OpenClaw bot
- `JWT_SECRET` - For dashboard token generation
- `DASHBOARD_URL` - Dashboard URL (default: https://bloomprotocol.ai)
- `NETWORK` - Blockchain network (default: base-mainnet)

## License

MIT - See main repository LICENSE file
