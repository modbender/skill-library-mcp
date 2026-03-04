# Strava Skill

Chat with your Strava data using AI. Ask about your activities, fitness trends, personal records, training load, and performance analytics.

Powered by **[Transition](https://www.transition.fun)**

## Quick Start

Try it right now — no API key needed:

```bash
curl "https://api.transition.fun/api/v1/wod?sport=run&duration=45"
```

For personalized features (your Strava data, training plan, AI coach), you need a Transition account + API key. See [Getting an API Key](#getting-an-api-key) below.

---

## Two Ways to Use This

### 1. Claude Code / OpenClaw Skill (Recommended)

The simplest option. Claude reads the skill file and calls the API directly — no binary, no MCP protocol, just HTTP. Also available on [OpenClaw](https://openclaw.com).

```bash
# Clone into your skills directory
git clone https://github.com/nftechie/strava-skill.git ~/.claude/skills/strava-skill
```

Set your API key:

```bash
# Add to your shell profile (~/.zshrc, ~/.bashrc, etc.)
export TRANSITION_API_KEY="tr_live_xxxxxxxxxxxxxxxxxxxxx"
```

Now in Claude Code, you can say things like:
- "What's my weekly mileage trend over the last month?"
- "How is my cycling FTP progressing?"
- "What was my fastest 5K effort recently?"
- "Am I running more or less than usual this week?"
- "Should I rest or train today based on my recent activity?"

Claude reads `SKILL.md` and knows how to call every endpoint.

### 2. Direct API

Use the API from scripts, automations, or any HTTP client. See [SKILL.md](SKILL.md) for complete endpoint documentation with curl examples.

```bash
# Ask the AI coach about your Strava data
curl -X POST -H "X-API-Key: $TRANSITION_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"message": "How did my long run this week compare to last week?"}' \
  "https://api.transition.fun/api/v1/coach/chat"

# Get your fitness/fatigue/form metrics
curl -H "X-API-Key: $TRANSITION_API_KEY" \
  "https://api.transition.fun/api/v1/performance/pmc"
```

---

## Getting an API Key

1. Download [Transition](https://www.transition.fun) (iOS/Android)
2. Create an account and connect your **Strava** account
3. Go to **Settings > API Keys**
4. Tap **Generate New Key** — you'll see a key starting with `tr_live_`
5. Copy it immediately (it's only shown once)

Free tier includes 100 read requests/day and 3 AI requests/day. Plenty for personal use.

## Rate Limits

| Tier | Read Endpoints | AI Endpoints |
|------|---------------|-------------|
| Free | 100/day | 3/day |
| Paid | 10,000/day | 100/day |

**Read:** workouts, metrics, profile, history | **AI:** coach chat, adapt, generate

## License

MIT
