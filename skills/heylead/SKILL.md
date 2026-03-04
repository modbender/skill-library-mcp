# HeyLead — Autonomous LinkedIn SDR

Your AI sales rep. One command to fill your pipeline.

HeyLead is an MCP-native autonomous LinkedIn SDR that gives your OpenClaw agent the ability to do LinkedIn outreach — find prospects, send personalized messages, follow up, and close deals.

## What This Skill Does

This skill connects HeyLead as an MCP server in your OpenClaw agent, giving it 34 specialized LinkedIn outreach tools:

- **ICP Generation** — RAG-powered buyer personas with pain points, fears, barriers, and LinkedIn search parameters
- **Campaign Management** — Create, pause, resume, archive, and compare outreach campaigns
- **Personalized Outreach** — Voice-matched connection invitations that sound like you, not a bot
- **Multi-Touch Sequences** — Follow-up DMs, engagement warm-ups (comments, likes, endorsements)
- **Reply Handling** — Sentiment classification, auto-responses, meeting scheduling
- **Analytics** — Funnel reports, conversion rates, stale lead detection, engagement ROI
- **Autonomous Scheduling** — 24/7 cloud scheduler for invitations, follow-ups, and reply checks

## Setup

### Prerequisites

- [uv](https://docs.astral.sh/uv/getting-started/installation/) installed (`brew install uv` on Mac, or `curl -LsSf https://astral.sh/uv/install.sh | sh`)

### Configuration

Add to your `openclaw.json`:

```json
{
  "mcp": {
    "servers": [
      {
        "name": "heylead",
        "command": "uvx",
        "args": ["heylead"]
      }
    ]
  }
}
```

### First-Time Account Setup

After adding the MCP server, tell your OpenClaw agent:

> "Set up my HeyLead profile"

You'll get a sign-in link — authenticate with Google, connect LinkedIn, copy your token, and paste it back. Takes ~1 minute, no API keys needed.

## Usage Examples

```
"Find me CTOs at fintech startups in New York"
"Generate an ICP for AI SaaS founders"
"Create a campaign targeting VP of Sales at Series B startups"
"Send outreach to the campaign"
"Check my replies"
"How's my outreach doing?"
"Suggest next action"
"Enable the cloud scheduler"
```

## Typical Workflow

```
1. setup_profile(backend_jwt="...")        → Connect LinkedIn
2. generate_icp(target="CTOs fintech")     → Create buyer personas
3. create_campaign(target="...", icp_id="...") → Find prospects
4. toggle_scheduler(enabled=True)          → Autopilot outreach
5. check_replies() / show_status()         → Monitor pipeline
6. close_outreach(outcome="won")           → Track conversions
```

## Two Modes

- **Autopilot** — AI handles outreach automatically within rate limits and working hours
- **Copilot** — Review every message before it sends

## All 34 Tools

| Tool | What it does |
|------|-------------|
| `setup_profile` | Connect LinkedIn, analyze writing style, create voice signature |
| `generate_icp` | Create Ideal Customer Profiles with buyer personas |
| `create_campaign` | Find prospects and build an outreach campaign |
| `generate_and_send` | Send personalized connection invitations |
| `send_followup` | Follow-up DMs after connection accepted |
| `reply_to_prospect` | Auto-reply based on sentiment analysis |
| `engage_prospect` | Comment, react, follow, or endorse prospects |
| `send_voice_memo` | Send voice notes on LinkedIn |
| `check_replies` | Monitor inbox, classify sentiment, surface hot leads |
| `show_status` | Campaign dashboard with stats and health |
| `campaign_report` | Detailed analytics and funnel report |
| `suggest_next_action` | AI-recommended next step |
| `approve_outreach` | Approve/edit/skip copilot messages |
| `show_conversation` | View full message thread with a prospect |
| `edit_campaign` | Update name, mode, booking link, preferences |
| `pause_campaign` | Pause outreach on a campaign |
| `resume_campaign` | Resume a paused campaign |
| `archive_campaign` | Mark campaign as completed |
| `delete_campaign` | Permanently delete a campaign |
| `skip_prospect` | Remove a bad-fit prospect |
| `retry_failed` | Retry failed outreaches |
| `emergency_stop` | Kill switch — pause all campaigns |
| `export_campaign` | Export results as table/CSV/JSON |
| `compare_campaigns` | Side-by-side campaign comparison |
| `close_outreach` | Record won/lost/opted-out outcome |
| `toggle_scheduler` | Enable/disable autonomous scheduler |
| `scheduler_status` | View scheduler state and pending jobs |
| `create_post` | Generate and publish LinkedIn posts |
| `brand_strategy` | LinkedIn personal brand audit and strategy |
| `import_prospects` | Import prospects from CSV |
| `crm_sync` | Sync won deals to HubSpot CRM |
| `show_strategy` | View strategy engine insights |
| `manage_watchlist` | Manage signal keyword watchlists |
| `show_signals` | View detected buying signals |

## Pricing

| Plan | Price | Limits |
|------|-------|--------|
| **Free** | $0 | 50 invitations/month, 1 campaign, 30 engagements/month |
| **Pro** | $29/mo | Unlimited campaigns, 5 LinkedIn accounts, cloud scheduler |

## Privacy

- Contacts and messages stored in local SQLite database
- AI calls routed through HeyLead backend (Gemini 2.0 Flash) or your own key
- No messages or contacts stored on HeyLead servers

## Links

- [PyPI](https://pypi.org/project/heylead/)
- [GitHub](https://github.com/D4umak/heylead)
- [Issues](https://github.com/D4umak/heylead/issues)

## License

MIT
