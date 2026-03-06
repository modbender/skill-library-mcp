# Rent-A-Human-Agent // Your lobster Bounty Hunter 🦞

🤖💰 OpenClaw-compatible SKILL that scans Rentahuman.ai in real time via MCP + API.** </br>
🧠 **Custom [Grok](https://x.ai)-powered job hunting Bounty Hunter that filters spam, ranks by your location + skills + how easy the cash is, and beams the winners straight to your Telegram, or MCP messenger of your choice.** </br>
🎮 **Bringing the power of robot bounty hunting to the everyday player.** </br>
💻 Claude code / CLI version: git remote add origin https://github.com/shane9coy/Rent-A-Human-Agent

<img width="1053" height="1138" alt="rentahumanagent" src="https://github.com/user-attachments/assets/590943eb-6649-4296-bdd8-5e5a08add654" />

## Install

```bash
clawhub install rent-a-human-agent
```

Or manually drag & drop the `rent/` folder into your OpenClaw skills directory.

## Setup

Add these environment variables to your OpenClaw config or `.env`:

```bash
RENTAHUMAN_API_KEY=your_key        # Required: from rentahuman.ai/dashboard
XAI_API_KEY=your_key               # Required: from x.ai for Grok scoring
TELEGRAM_BOT_TOKEN=your_token      # Optional: for Telegram notifications
TELEGRAM_CHAT_ID=your_chat_id      # Optional: for Telegram notifications
```

## What It Does

- Connects to the RentAHuman.ai MCP server to pull live bounties
- Uses Grok-4-1-fast-reasoning to score each bounty 0-100
- Filters spam and scam signals (crypto transfers, wallet addresses, etc.)
- Ranks by budget, skill match, remote availability, and competition
- Caches results for 12 hours to avoid redundant API calls
- Sends top opportunities to Telegram (optional)

## Skill Structure

```
rent/
├── SKILL.md              # Skill definition and triggers
└── scripts/
    └── bounty_hunter.py  # Main scanner script
```

## Usage

Once installed, your OpenClaw agent can use the skill via natural language:

- "scan for bounties near me"
- "find easy remote gigs on rentahuman"
- "hunt for the best paying bounties and send them to my telegram"

Or run the script directly:

```bash
python3 rent/scripts/bounty_hunter.py           # Normal scan (uses cache)
python3 rent/scripts/bounty_hunter.py --force    # Fresh scoring
python3 rent/scripts/bounty_hunter.py --jobs     # List all open jobs
python3 rent/scripts/bounty_hunter.py --humans   # List available humans
python3 rent/scripts/bounty_hunter.py --no-telegram  # Skip notifications
```

## Also Available As

Full Claude Code project with `/rent` command, MCP server config, and CLAUDE.md system prompt:
[github.com/shane9coy/Rent-A-Human-Agent](https://github.com/shane9coy/Rent-A-Human-Agent)

## Author

Built by [@shaneswrld_](https://x.com/shaneswrld_) | [github.com/shane9coy](https://github.com/shane9coy)

## License

MIT
