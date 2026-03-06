---
name: meeting-prep
description: Never walk into a meeting unprepared again. Your agent researches all attendees before calendar events—pulling LinkedIn profiles, recent company news, mutual connections, and conversation starters. Generates a briefing doc with talking points, icebreakers, and context so you show up informed and confident. Triggered automatically before meetings or on-demand. Configure research depth, advance timing, and output format. Walking into meetings blind is amateur hour—missed connections, generic small talk, zero leverage. Use when setting up meeting intelligence, researching specific attendees, generating pre-meeting briefs, or automating your prep workflow.
metadata:
  clawdbot:
    emoji: "🎯"
    requires:
      skills:
        - gog
      env:
        - GOOGLE_CALENDAR_ENABLED
---

# Meeting Prep — Never Walk In Blind

**Walking into meetings unprepared is amateur hour.**

You're juggling back-to-back calls, no time to research who's in the room. You default to generic small talk. You miss the fact that the VP you're pitching used to work at your dream client. You didn't see the news that their company just raised $50M. You fumble the connection.

**Meeting Prep fixes this.** Your agent researches every attendee before you join—LinkedIn profiles, company intel, recent news, mutual connections, conversation hooks. It generates a briefing doc with talking points, icebreakers, and context. You walk in informed, confident, and ready to connect.

## What It Does

- **Auto-triggers** before calendar events (configurable advance time)
- **Researches attendees:** LinkedIn profiles, role, background, recent activity
- **Company intelligence:** Recent news, funding, product launches, leadership changes
- **Connection mapping:** Mutual contacts, shared interests, conversation hooks
- **Generates brief:** Clean, scannable doc with talking points and icebreakers
- **On-demand mode:** Research specific people or meetings instantly

**The difference:** Most meeting tools focus on *agendas*. Meeting Prep focuses on *people*. Know who you're talking to before you open your mouth.

## Setup

1. Run `scripts/setup.sh` to initialize config and brief storage
2. Edit `~/.config/meeting-prep/config.json` with calendar settings and research preferences
3. Ensure `gog` skill is installed (for Google Calendar integration)
4. Test with: `scripts/prep.sh "meeting-id-or-attendee-email" --dry-run`

## Config

Config lives at `~/.config/meeting-prep/config.json`. See `config.example.json` for full schema.

Key sections:
- **calendar** — Which calendars to monitor, event filters, advance notice
- **research** — Depth level (quick/standard/deep), data sources, focus areas
- **output** — Format (markdown/text/telegram), delivery channel, storage location
- **auto_prep** — Enable/disable automatic prep, time thresholds, event criteria
- **icebreakers** — Tone preferences (professional/casual/witty), topic priorities

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/setup.sh` | Initialize config and brief directories |
| `scripts/prep.sh` | Research attendees for a specific meeting (on-demand) |
| `scripts/auto-prep.sh` | Check upcoming calendar events and prep meetings that qualify |
| `scripts/brief.sh` | Output formatted briefing doc for a meeting |

All scripts support `--dry-run` for testing without actually generating briefs.

## Auto-Prep Workflow

Run `scripts/auto-prep.sh` on schedule (cron every 2-4h recommended). The workflow:
1. Fetches upcoming calendar events (next 24-48h based on config)
2. Filters for events matching criteria (external attendees, duration >15min, etc.)
3. Checks if already prepped (dedup against brief history)
4. Researches each attendee: web search for LinkedIn, company site, recent news
5. Generates briefing doc with sections: Attendees, Company Context, Talking Points, Icebreakers
6. Stores brief and optionally delivers to configured channel

## On-Demand Prep

```bash
# Research a specific meeting by calendar event ID
scripts/prep.sh "meeting-id-from-calendar"

# Research specific people by email
scripts/prep.sh "john@acme.com,sarah@bigcorp.io"

# Quick brief for imminent meeting
scripts/prep.sh "john@acme.com" --format telegram --send
```

## Brief Structure

Generated briefs include:

**📋 Meeting Overview**
- Title, time, duration, location/link
- Objective (auto-detected or manual)

**👥 Attendees (per person)**
- Name, title, company
- Background highlights (education, previous roles, tenure)
- Recent activity (posts, articles, company news)
- Mutual connections (if detectable)
- Conversation hooks (shared interests, recent wins)

**🏢 Company Context**
- Recent news (funding, launches, leadership changes)
- Industry position, competitors, challenges
- Relevant talking points

**💬 Icebreakers & Talking Points**
- Personalized conversation starters per attendee
- Strategic questions to ask
- Topics to avoid (if detected)

**🎯 Your Prep Checklist**
- Key things to mention
- Questions to have ready
- Follow-up actions

## Data Files

```
~/.config/meeting-prep/
├── config.json              # User configuration
├── briefs/                  # Generated briefing docs
│   ├── 2026-02-11-acme-intro.md
│   └── 2026-02-15-bigcorp-pitch.md
├── brief-history.json       # Dedup index (event → brief mapping)
└── prep-log.json            # Prep run history
```

## Research Sources

Meeting Prep uses:
- **Web search:** LinkedIn profiles, company pages, news articles
- **Web fetch:** Company blogs, press releases, LinkedIn activity
- **Calendar metadata:** Event titles, descriptions, attendee lists (via gog)
- **Future:** CRM integration, internal notes, past meeting context

## Cron Setup Example

```bash
# Auto-prep upcoming meetings every 3 hours
0 */3 * * * /Users/you/clawd/skills/meeting-prep/scripts/auto-prep.sh

# Morning brief delivery (7 AM daily)
0 7 * * * /Users/you/clawd/skills/meeting-prep/scripts/auto-prep.sh --morning-brief
```

## Privacy & Ethics

- **Your data only:** Researches public info about people you're *scheduled* to meet
- **No stalking:** Only preps for confirmed calendar events or explicit requests
- **Opt-out friendly:** Skip specific events by adding `#noprep` to event description
- **Transparent:** Briefs cite sources; you see what the agent found

## Pro Tips

- **Set advance time wisely:** 2-4 hours before works well (too early = stale, too late = useless)
- **Customize icebreakers:** Adjust tone in config (corporate vs startup vs casual)
- **Review briefs:** Agent does the research, you add the human touch
- **Feedback loop:** Mark what worked in briefs to improve future prep
- **Combine with agenda tools:** Use Fellow/Hypercontext for *what* to discuss, Meeting Prep for *who* you're discussing with

## Example Brief

```markdown
# 🎯 Meeting Brief: Acme Corp Intro Call
**When:** Today at 2:00 PM (30 min)  
**Where:** Zoom (link in calendar)  
**Objective:** Partnership exploration

## 👥 Attendees

### John Martinez — VP of Product, Acme Corp
- **Background:** 8 years at Acme, prev. led product at DataFlow (acquired 2021)
- **Education:** Stanford CS, MBA from Wharton
- **Recent:** Posted on LinkedIn about AI integration challenges in SaaS (2 days ago)
- **Hook:** Shares your interest in automation; Acme just launched API platform

### Sarah Chen — Head of Partnerships, Acme Corp  
- **Background:** Joined 6mo ago from Google Cloud partnerships
- **Recent:** Spoke at SaaS Conference last week on strategic alliances
- **Mutual:** Connected to Jamie Lee (your former colleague at XYZ)
- **Hook:** Passionate about startups (angel investor, 5 companies)

## 🏢 Company Context

**Acme Corp** — B2B SaaS platform for workflow automation  
- **Recent news:** Series B $50M (Jan 15), TechCrunch coverage
- **Growth:** 200 → 350 employees in past year
- **Challenges:** Scaling integrations (mentioned in John's post)
- **Competitors:** Zapier, Make.com

## 💬 Icebreakers & Talking Points

**For John:**
- "Saw your post on AI integration pain points—we've been tackling similar challenges"
- Ask about the new API platform launch
- Mention DataFlow (his prev. company) if relevant angle emerges

**For Sarah:**
- "Jamie Lee mentioned you were doing great things at Acme!"
- Reference her SaaS Conference talk on alliances
- Her startup/angel background = rapport opportunity

**Strategic questions:**
- What's driving the push for more integrations right now?
- How do you typically evaluate partnership fit?
- What's been your biggest challenge since the Series B?

## 🎯 Your Prep Checklist

- ✅ Review our partnership deck (focus on integration angle)
- ✅ Have 2-3 customer stories ready (SaaS companies, automation wins)
- ✅ Prepare questions about their API roadmap
- ✅ Follow up: Connect with Sarah on LinkedIn post-call

---
*Brief generated by Meeting Prep • Sources: LinkedIn, TechCrunch, Acme blog*
```

## When to Use Meeting Prep

- **Sales calls:** Know your prospect before pitching
- **Investor meetings:** Research partners, understand fund focus
- **New client kickoffs:** Start with context, not cold
- **Networking events:** Pre-game the attendee list
- **Job interviews:** Research interviewers, not just the company
- **Conference meetings:** Brief on everyone you're meeting at the event
- **Board meetings:** Know new board members before they join

## What Makes It Different

- **People-first:** Most tools prep the *agenda*, this preps *the humans*
- **Automated:** Runs in background, delivers briefs without you asking
- **Contextual:** Not just LinkedIn stalking—connects dots, finds hooks
- **Actionable:** Not a data dump—talking points you can actually use
- **Respectful:** Public info only, ethically sourced, transparent

---

**Stop walking into meetings blind.** Let your agent do the homework. You bring the human connection.
