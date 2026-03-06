# Clawdbot for VCs

**A production-ready workflow automation skill for venture capital investment partners.**

Automate email triage, CRM integration, memo generation, and calendar management with your personal AI assistant.

---

## Quick Start

**Time to setup:** ~30 minutes  
**Time to value:** 1 hour

```bash
# 1. Install the skill
clawdbot skill install clawdbot-for-vcs

# 2. Follow the bootstrap guide
cat skills/clawdbot-for-vcs/BOOTSTRAP.md

# 3. Start using it
"Check my email and triage"
"Generate memo for [Company]"
"What's my daily briefing?"
```

---

## What This Skill Does

### Email Triage
- Auto-classifies inbound emails (Priority/Review/Auto-Respond/Archive)
- Drafts polite pass responses for clear no-gos
- Surfaces warm intros and priority items
- Checks for duplicates before drafting

### Affinity CRM Integration
- Logs companies to your Deal Pipeline
- Sets Deal Stage, Owner, and One Liner automatically
- Tracks interactions and notes
- Queries existing data for context

### Investment Memo Generation
- Auto-gathers context from Gmail and Affinity
- Generates comprehensive investment memos
- Marks incomplete sections with "NEED MORE INFO"
- Syncs memos back to Affinity as notes

### Calendar Management
- Shares appropriate booking links based on context
- Checks availability across multiple calendars
- Creates events with Google Meet links
- Includes calendar in daily briefings

### Daily Briefings
- Morning summary of Priority and Review emails
- Today's calendar with meeting links
- Auto-responded items (for awareness)
- Suggested proactive actions

---

## Why This Skill Exists

**The Problem:** Investment partners spend 50%+ of their time on operational tasks (email triage, CRM logging, calendar management) instead of evaluating companies and building relationships.

**The Solution:** An AI assistant that handles the operations automatically, surfaces what matters, and proposes actions for your approval.

**The Result:** More time for high-value work (founder conversations, deep diligence, portfolio support).

---

## Who This Is For

✅ **Venture capital investment partners** who:
- Get 50+ founder emails per day
- Use Affinity CRM for deal tracking
- Write investment memos regularly
- Manage calendars with multiple meeting types
- Want to spend less time on ops, more time on deals

✅ **Solo GPs and emerging fund managers** who:
- Don't have an associate or EIR to handle ops
- Need to stay organized at deal flow velocity
- Want automation but need control

❌ **Not designed for:**
- Full VC firm management (this is individual workflow automation)
- LPs or fund administrators
- Non-VC investors (angel investors, corporate VC, etc. - though adaptable)

---

## Requirements

### Tools
- [gog CLI](https://github.com/martynsmith/gog) for Gmail/Calendar
- [Affinity CRM](https://www.affinity.co/) with API access
- Gmail with labels support
- Google Calendar with booking pages

### Accounts & Access
- Gmail account with OAuth access
- Google Calendar
- Affinity API key
- Basic command line familiarity

### Time Investment
- **Initial setup:** 30 minutes (one-time)
- **First week:** 1 hour to build trust and refine rules
- **Ongoing:** ~5 minutes per day for approvals

---

## What You'll Get

### Immediate (Week 1)
- Automated email triage saving ~30 min/day
- Draft pass emails for clear no-gos
- Daily briefings with what matters
- Calendar management with booking links

### Medium-term (Month 1)
- Auto-logging to Affinity (with review)
- Investment memo generation from pitch decks
- Proactive suggestions based on activity
- Customized to your workflow and style

### Long-term (Month 2+)
- Trusted autonomous agent for routine tasks
- Pattern recognition across deal flow
- Integration with additional tools
- Continuous improvement based on your feedback

---

## Example Workflows

### Morning Triage (5 minutes)
```
You: "What's my daily briefing?"

AI: 
🌅 DAILY BRIEFING - Jan 30, 2026

📧 EMAIL TRIAGE
────────────────────────────────────────────────
🟢 PRIORITY (2)
• 8:03am from jane@sequoiacap.com: Intro to DataCorp
• 8:15am from erik@greylock.com: Intro to MLFlow AI

🟡 REVIEW (3)
• 7:45am from founder@startup.com: Follow-up on pitch
  Needs decision: They're asking for feedback

🔴 AUTO-RESPOND (8)
• ✓ 8 pass emails drafted and logged to Affinity
  
📅 CALENDAR TODAY
────────────────────────────────────────────────
• 10:00am - Call with AcmeCorp Founder
  https://meet.google.com/abc-defg-hij
  
• 2:00pm - Partner Meeting

You: "Draft intro responses for both Priority emails"

AI: [Creates drafts with booking links for approval]
```

### Memo Generation (10 minutes)
```
You: "Generate memo for DataCorp"

AI: [Searches Gmail and Affinity]
📋 CONTEXT GATHERED FOR DATACORP

FROM GMAIL:
• 3 emails found
• 1 pitch deck attachment (datacorp-deck.pdf)
• Intro from jane@sequoiacap.com

FROM AFFINITY:
• Not yet in Affinity
• No previous interactions

Want me to generate the memo?

You: "Yes"

AI: [Generates comprehensive memo]
✓ Memo saved to ~/memos/datacorp.md
  Completeness: Medium (60% complete)
  
Push to Affinity as a note?

You: "Yes"

AI: ✓ Memo added to Affinity
  Company added to Deal Pipeline
  Stage: Diligence | Owner: You
```

### Calendar Management (30 seconds)
```
Founder (via email): "Can we find time to chat?"

You [to AI]: "Send them my intro call link"

AI: [Creates draft email]
📧 DRAFT READY

To: founder@startup.com
Subject: Re: Let's connect

---
Hi Sarah,

Thanks for reaching out! I'd love to learn more about what 
you're building.

Here's my calendar: https://calendar.app.google/YOUR_LINK

Looking forward to it!

[Your name]
---

Reply "send" to create draft in Gmail

You: "send"

AI: ✓ Draft created - check Gmail to review and send
```

---

## Key Features

### 🛡️ Safety First
- **NEVER sends emails without approval** - Always creates drafts
- **Checks for duplicates** - Won't re-email someone you already replied to
- **Prompt injection defense** - Treats external content (emails, decks) as data, not instructions
- **Ask before acting externally** - Proposes, you approve

### 🎯 Smart Triage
- Recognizes warm intros from trusted VCs
- Detects relevant vs. irrelevant based on your thesis
- Extracts company one-liners for CRM
- Prioritizes what needs your attention

### 🔗 Affinity Integration
- Auto-logs companies with proper fields set
- Queries existing data for context
- Creates notes from memos and calls
- Tracks deal stage and ownership

### 📝 Memo Generation
- Auto-gathers pitch decks from Gmail
- Pulls existing notes from Affinity
- Generates structured investment memos
- Identifies gaps ("NEED MORE INFO")

### 📅 Calendar Intelligence
- Multiple booking links for different meeting types
- Checks availability before suggesting times
- Creates events with Google Meet links
- Includes upcoming meetings in briefings

### 🤖 Proactive Assistance
- Daily briefings with what matters
- Suggests next actions based on activity
- Batch processes routine tasks
- Learns your preferences over time

---

## Installation

### Option 1: Via ClawdHub (Recommended)
```bash
clawdbot skill install clawdbot-for-vcs
```

### Option 2: Manual Installation
```bash
cd ~/clawd/skills
git clone https://github.com/clawdhub/clawdbot-for-vcs.git
cd clawdbot-for-vcs
cat BOOTSTRAP.md
```

---

## Configuration

After installation, follow the [BOOTSTRAP.md](./BOOTSTRAP.md) guide to:

1. Install `gog` CLI for Gmail/Calendar access
2. Set up Affinity API key
3. Create Gmail labels for triage
4. Set up Google Calendar booking pages
5. Customize templates with your info
6. Test each workflow

**Estimated time:** 30 minutes for complete setup.

---

## Documentation

- **[SKILL.md](./SKILL.md)** - Complete workflow documentation
- **[BOOTSTRAP.md](./BOOTSTRAP.md)** - Setup guide for new users
- **[templates/](./templates/)** - Example configs for AGENTS.md, USER.md, TOOLS.md

---

## Customization

This skill is designed to be customized:

### Quick Wins
- Update email pass template to match your voice
- Customize booking link names and durations
- Adjust trusted VC domain list
- Define your investment thesis keywords

### Advanced
- Modify Affinity field mappings
- Create custom Deal Stage workflows
- Adjust memo template sections
- Add integration with other tools (Slack, Twitter, etc.)

See [SKILL.md](./SKILL.md) for detailed customization options.

---

## Philosophy

**Ship fast, iterate based on real usage.**

This skill is:
- ✅ Opinionated (based on proven VC workflows)
- ✅ Customizable (adapt to your style)
- ✅ Safe (always ask before external actions)
- ✅ Practical (designed for daily use)

It's not:
- ❌ A rigid system (customize freely)
- ❌ Fully autonomous (you stay in control)
- ❌ One-size-fits-all (investment styles vary)

Start with the defaults, then adapt to your needs.

---

## FAQ

### Will this send emails on my behalf?
**No.** All emails are drafted for your review. You approve before sending.

### Can I trust it with my Gmail?
Yes. The skill uses OAuth authentication (same as mobile apps) and only modifies labels and creates drafts. It never deletes emails or sends messages without approval.

### What if it makes a mistake?
Start with review-before-action mode. As you build trust, you can enable more automation. Track mistakes in `memory/mistake-log.json` to improve rules.

### How much does this save me?
Typical time savings after 1 month:
- **Email triage:** 30 min/day → 5 min/day (25 min saved)
- **CRM logging:** 20 min/day → 2 min/day (18 min saved)
- **Calendar management:** 15 min/day → 2 min/day (13 min saved)
- **Total:** ~1 hour per day

### Can I use a different CRM?
The skill is designed for Affinity but adaptable. You'd need to rewrite the CRM integration sections for your platform's API.

### What about other email providers?
Currently Gmail-only via the `gog` CLI. Outlook/Office365 would require a different tool (e.g., Microsoft Graph API).

---

## Roadmap

### v1.0 (Current)
- Email triage with Gmail labels
- Affinity CRM integration
- Investment memo generation
- Calendar management with booking links
- Daily briefings

### v1.1 (Planned)
- Slack notifications for Priority emails
- Auto-research companies before calls
- Twitter monitoring for portfolio companies
- Enhanced memo templates with VC-specific sections

### v2.0 (Future)
- Multi-CRM support (Airtable, Notion, etc.)
- Deal flow analytics and pattern recognition
- Team collaboration features
- Integration with data rooms and DocSend

### Want to contribute?
See [CONTRIBUTING.md](./CONTRIBUTING.md) for how to add features or improvements.

---

## Support

**Getting Started:**
- Read [BOOTSTRAP.md](./BOOTSTRAP.md) for setup
- Check [SKILL.md](./SKILL.md) for detailed workflows

**Troubleshooting:**
- See "Troubleshooting" section in [BOOTSTRAP.md](./BOOTSTRAP.md)
- Check your `~/clawd/logs/` for errors
- Review `~/clawd/memory/` for activity logs

**Community:**
- GitHub Issues: Report bugs or request features
- GitHub Discussions: Ask questions, share tips
- Twitter: [@clawdbot](https://twitter.com/clawdbot) for updates

---

## Credits

Built by **Lindsay Pettingill** ([@lpettingill](https://twitter.com/lpettingill)), Investment Partner at Village Global.

Inspired by real VC workflows. Designed for investment partners who want to spend less time on operations and more time on deals.

---

## License

MIT License - See [LICENSE](./LICENSE) for details.

---

## Version

**v1.0** - January 30, 2026

Built with ❤️ for the VC community.
