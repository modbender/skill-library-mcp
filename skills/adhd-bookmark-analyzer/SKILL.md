# ADHD X Bookmark Analysis

Your bookmarks are a graveyard. This brings them back to life.

## What This Skill Does

You bookmark 50 tweets a day. You read maybe 2. That thread about the $200K agency architecture? Buried. The AI tool that would save you hours? Forgotten.

This skill turns your X bookmark chaos into actionable intelligence. Your agent scrapes your bookmarks, categorizes them by topic, extracts the key insights, and delivers a summary to your preferred channel.

**No more bookmark graveyards. No more "I saved something about that..." Just organized, searchable knowledge from everything you thought was worth saving.**

Built for ADHD brains who collect everything and process nothing.

## Capabilities

- ✅ **Automatic X bookmark scraping** (scheduled or on-demand)
- ✅ **Smart categorization** by topic (AI, business, tools, threads)
- ✅ **Key insight extraction** from threads and long-form content
- ✅ **Channel delivery** (Discord, Slack, Telegram, or file-only)
- ✅ **Searchable archive** of everything you saved

## Requirements

### X Authentication (Required)

**Option A: `bird` CLI (Recommended)**
```bash
# Install bird CLI
npm install -g bird-cli

# Authenticate (opens browser for OAuth)
bird login

# Verify access
bird whoami
bird bookmarks --limit 5
```

Credentials are stored securely in `~/.bird/` by the CLI. The skill never handles raw tokens directly.

**Option B: Browser Session (Advanced)**

If you prefer browser cookies:
1. Log into X in Chrome/Safari
2. OpenClaw's browser tool can access your session
3. Less reliable than `bird` CLI — session expires, requires re-login

⚠️ **Security Note:** Never paste raw session cookies into config files. Use `bird` CLI for persistent, secure auth.

### Message Delivery (Optional)

To receive summaries in Discord/Slack/Telegram, configure via **environment variables** (not plaintext files):

```bash
# Discord (using OpenClaw's built-in message tool)
# No extra config needed — just specify channel ID in your prompt

# Or use a webhook (store securely):
export BOOKMARK_DISCORD_WEBHOOK="https://discord.com/api/webhooks/..."

# Slack
export BOOKMARK_SLACK_WEBHOOK="https://hooks.slack.com/services/..."
```

The skill reads these from environment. Never commit webhooks to files.

## Installation

```bash
clawhub install adhd-bookmark-analyzer
```

Or manually copy to your workspace:
```
~/.openclaw/workspace/skills/adhd-bookmark-analyzer/
├── SKILL.md           # This file (instructions for your agent)
├── bookmark-rules.md  # Categorization logic & settings
```

## Usage

### On-Demand Analysis

Just ask your agent:
```
"Analyze my X bookmarks from this week"
"What did I bookmark about AI agents?"
"Summarize my bookmarks and send to Discord"
```

The agent will:
1. Run `bird bookmarks` to fetch your saves
2. Categorize and extract insights per `bookmark-rules.md`
3. Deliver summary to your specified channel (or just reply inline)

### Scheduled Daily Reports

Add to your agent's cron schedule (via OpenClaw cron or HEARTBEAT.md):
```
# Daily at 9 AM: Analyze yesterday's bookmarks
"Check my X bookmarks from the last 24 hours, categorize them, and post summary to Discord channel 123456789"
```

### Search Your Archive

```
"Search my bookmark archive for 'pricing strategy'"
```

The agent searches `bookmark-archive/` and returns matching entries with context.

## Example Output

```
📚 X Bookmark Summary — Feb 15, 2026

You saved 18 bookmarks in the last 24 hours:

🤖 AI & Tech Tools (7)
• New Claude API pricing ($0.25/M output tokens)
• OpenClaw 0.7.0 release notes  
• Thread on RAG vs fine-tuning tradeoffs

💼 Business & Strategy (5)
• How @username built $50K MRR with AI agents
• Pricing psychology thread (15 tactics)
• Case study: AI replacing $200K/year ops role

🔧 Development & Code (4)
• Python async patterns for LLM calls
• GitHub repo: AI code review automation

📖 Threads Worth Reading (2)
• @username's 20-tweet thread on AI safety
• Founder story: 0 to $1M in 8 months
```

## Categorization

Default categories in `bookmark-rules.md`:

| Category | Matches |
|----------|---------|
| AI & Tech Tools | Product launches, tool reviews, API updates |
| Business & Strategy | Growth tactics, pricing, case studies |
| Development & Code | Code snippets, repos, technical threads |
| Threads Worth Reading | Long-form content, storytelling |
| Resources | Books, courses, guides, lists |
| Other | Doesn't fit above |

**Customize** by editing `bookmark-rules.md`:
```yaml
categories:
  - name: "Indie Hacking"
    keywords: ["indie hacker", "SaaS", "MRR", "bootstrap"]
  - name: "Crypto Alpha"
    keywords: ["alpha", "degen", "airdrop", "farming"]
```

## File Structure

After running, the skill creates:
```
~/.openclaw/workspace/skills/adhd-bookmark-analyzer/
├── SKILL.md              # Instructions (this file)
├── bookmark-rules.md     # Categories & settings
└── bookmark-archive/     # Created by agent
    ├── 2026-02-15.json   # Daily snapshots
    └── index.json        # Searchable index
```

## Security Notes

1. **Authentication:** Use `bird login` for X access. Credentials stored in `~/.bird/`, managed by the CLI.

2. **Webhooks:** Store Discord/Slack webhook URLs in environment variables, not config files:
   ```bash
   export BOOKMARK_DISCORD_WEBHOOK="https://..."
   ```

3. **Data Storage:** Bookmark archives are stored locally in your workspace. No data is sent to external services except your configured delivery channel.

4. **Permissions:** The skill only reads your bookmarks and writes to your local archive. It does not post to X, modify bookmarks, or access DMs.

## Troubleshooting

**"No bookmarks found"**
```bash
bird whoami          # Check auth
bird bookmarks --limit 1  # Test access
```

**Categories seem wrong**
- Edit keywords in `bookmark-rules.md`
- Add domain-specific terms for your niche

**Want file-only (no notifications)**
- Just don't configure a webhook
- Ask agent to "save to archive only"

## Tips

1. **Bookmark liberally** — The skill handles organization
2. **Review weekly** — Skim the summaries, dig into what matters
3. **Customize categories** — Match your actual interests
4. **Use search** — Your archive becomes a second brain

---

**The goal:** Make the good stuff findable when you need it. Not inbox zero for bookmarks — just signal over noise.
