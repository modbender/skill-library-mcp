# RentAHuman Telegram Bot

(Telegram-Bot-Easy skills & set up can be found here. (Drag and drop the .claude folder contents into your OpenClaw skills folder): https://github.com/shane9coy/Telegram-Bot-Easy)

# Give your openclaw the following prompt:

Integrate our Rent-A-Human-Agent into our Telegram bot with the following specifications - 
A Telegram bot that brings [RentAHuman.ai](https://rentahuman.ai) to your Telegram chat. Browse available humans, view open bounties, post jobs, and get AI-powered opportunity recommendations — all from your phone.

## Features

- 🔗 **MCP Integration** - Direct connection to official RentAHuman.ai MCP
- 🔍 **Scan Bounties** - Find and score job opportunities based on your location and skills
- 🧑‍💼 **Browse Humans** - View available humans for hire with skills and rates
- 💼 **View Bounties** - See open jobs and opportunities
- 📝 **Post Jobs** - Create new bounties directly from Telegram
- 🎯 **Smart Scanning** - AI-scored opportunity recommendations
- 🔒 **Private** - Bot only responds to your user ID



```bash
python telegram_bot.py
```

## Commands

| Command | Description |
|---------|-------------|
| `/rent` | Browse available humans |
| `/rent status` | Check API connection |
| `/rent bounties` | View open jobs |
| `/rent skills` | Browse available skills |
| `/rent scan` | Get AI-scored opportunities |
| `/rent post <desc>` | Post a new bounty |
| `help` | Show all commands |

## Examples

```
/rent                          # List available humans
/rent bounties                 # Show open jobs
/rent scan                     # Get top opportunities
/rent post Logo design. Budget $150  # Create a bounty
```