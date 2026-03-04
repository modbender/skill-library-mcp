# Transition MCP

AI-powered coaching for runners, cyclists, swimmers, and triathletes. Get personalized workouts, training plan adaptation, performance analytics, and AI coaching — all accessible from Claude, MCP clients, or any HTTP client.

Powered by **[Transition](https://www.transition.fun)**

## Quick Start

Try it right now — no API key needed:

```bash
curl "https://api.transition.fun/api/v1/wod?sport=run&duration=45"
```

For personalized features (your training plan, performance data, AI coach), you need a Transition account + API key. See [Getting an API Key](#getting-an-api-key) below.

---

## Three Ways to Use This

### 1. Claude Code / OpenClaw Skill (Recommended)

The simplest option. Claude reads the skill file and calls the API directly — no binary, no MCP protocol, just HTTP. Also available on [OpenClaw](https://openclaw.com).

```bash
# Clone into your skills directory
git clone https://github.com/nftechie/transition-mcp.git ~/.claude/skills/transition-mcp
```

Set your API key:

```bash
# Add to your shell profile (~/.zshrc, ~/.bashrc, etc.)
export TRANSITION_API_KEY="tr_live_xxxxxxxxxxxxxxxxxxxxx"
```

Now in Claude Code, you can say things like:
- "What's my workout today?"
- "Show me my fitness trend for the last month"
- "Ask my coach if I should do intervals or rest today"
- "Generate me a 30-minute swim workout"

Claude reads `SKILL.md` and knows how to call every endpoint.

### 2. MCP Server (Claude Desktop, Cursor, etc.)

For MCP-compatible clients. The server wraps the Transition API as MCP tools and resources.

**Install:**

```bash
cd mcp
go build -o transition-mcp .
```

**Configure Claude Desktop** (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "transition-mcp": {
      "command": "/absolute/path/to/transition-mcp",
      "env": {
        "TRANSITION_API_KEY": "tr_live_xxxxxxxxxxxxxxxxxxxxx"
      }
    }
  }
}
```

Restart Claude Desktop. You'll see 6 tools and 3 resources available:

**Tools:**
| Tool | Description |
|------|-------------|
| `get_todays_workout` | Today's scheduled workout |
| `get_week_plan` | 7-day training plan |
| `adapt_plan` | Trigger plan adaptation |
| `get_fitness_metrics` | CTL/ATL/TSB performance data |
| `chat_with_coach` | AI endurance coach |
| `generate_workout` | Free Workout of the Day (no auth) |

**Resources:**
| Resource | Description |
|----------|-------------|
| `transition://athlete/profile` | Goals, experience, preferences |
| `transition://athlete/recent-activities` | Last 14 days of workouts |
| `transition://athlete/performance` | FTP, thresholds, PMC data |

### 3. Direct API

Use the API from scripts, automations, or any HTTP client. See [SKILL.md](SKILL.md) for complete endpoint documentation with curl examples.

```bash
# Get this week's workouts
curl -H "X-API-Key: $TRANSITION_API_KEY" \
  "https://api.transition.fun/api/v1/workouts?start=2026-02-09&end=2026-02-15"

# Ask the AI coach a question
curl -X POST -H "X-API-Key: $TRANSITION_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"message": "My left knee hurts after long runs. Should I adjust my plan?"}' \
  "https://api.transition.fun/api/v1/coach/chat"
```

---

## Getting an API Key

1. Download [Transition](https://www.transition.fun) (iOS/Android)
2. Create an account and complete onboarding
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

---

## Examples

See the [`examples/`](examples/) directory for scripts:
- `curl-examples.sh` — All endpoints with curl
- More coming soon

## License

MIT
