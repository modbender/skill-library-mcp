# Changelog

All notable changes to the Clawdbot for VCs skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-01-30

### Added

**Core Documentation:**
- Complete SKILL.md with all VC workflows documented
- BOOTSTRAP.md setup guide (30-minute onboarding)
- README.md with quick-start and examples
- CONTRIBUTING.md for community contributions

**Email Triage:**
- Four-tier classification system (Priority/Review/Auto-Respond/Archive)
- Gmail label-based workflow
- Pass email template with AI indicator
- Intro response template for warm intros
- Duplicate email detection
- Auto-archive for processed emails

**Affinity CRM Integration:**
- Company search and creation
- Deal Pipeline list management
- Field value setting (Deal Stage, Owner, One Liner)
- Note creation for memos and calls
- One-liner extraction from emails
- Complete API integration examples

**Investment Memo Generation:**
- Auto-gathering from Gmail (pitch decks, emails)
- Auto-gathering from Affinity (notes, history)
- Comprehensive memo template
- Completeness scoring (Low/Medium/High)
- "NEED MORE INFO" gap marking
- Sync memos back to Affinity as notes

**Calendar Management:**
- Six booking link types (Intro, Follow-up, Diligence, Portfolio, Network, Priority)
- Availability checking across multiple calendars
- Event creation with Google Meet
- Email templates with booking links
- Daily briefing calendar section

**Daily Briefings:**
- Structured briefing format
- Email triage summary by priority
- Today's calendar with links
- Upcoming 48-hour preview
- Suggested proactive actions
- Auto-generated or on-demand

**Security & Safety:**
- Prompt injection defense
- Duplicate email prevention
- Draft-first approach (never auto-send)
- Message restrictions (only to user)
- External content treated as data

**Template Configs:**
- AGENTS.md.example with VC workflows
- USER.md.example for investment partner context
- TOOLS.md.example with configuration placeholders
- SOUL.md.example for AI personality

**Tools Integration:**
- gog CLI setup for Gmail/Calendar
- Affinity API integration
- Environment variable configuration
- Booking link setup guide

**Documentation:**
- 10 example workflows from real usage
- Troubleshooting guide
- Customization instructions
- FAQ section
- Time savings estimates

### Philosophy

- **Ship fast, iterate based on real usage** - Production-ready v1, improve from feedback
- **Safe by default** - Always ask before external actions
- **Focused on investment partners** - Not broad VC firm management
- **Customizable but opinionated** - Strong defaults, easy to adapt

### Success Criteria Met

✅ Another VC can install and configure in <30 minutes
✅ Clear documentation of required credentials/tools
✅ Works with standard VC tech stack (Gmail, Affinity, Google Calendar)
✅ Ready to publish to ClawdHub
✅ Patterns reused from proven Lindsay Pettingill workflows
✅ Generic enough for any VC, with clear examples

---

## [Unreleased]

### Planned for v1.1

**Integrations:**
- Slack notifications for Priority emails
- Twitter monitoring for portfolio companies
- DocSend analytics integration
- LinkedIn enrichment for founders

**Workflow Enhancements:**
- Auto-research companies before scheduled calls
- Reference call note templates
- Deal flow analytics and pattern recognition
- Portfolio company check-in automation

**Documentation:**
- Video walkthrough of setup process
- More real-world examples from users
- Integration guides for additional tools
- Advanced customization recipes

### Planned for v2.0

**Multi-CRM Support:**
- Airtable integration
- Notion database integration
- Custom CRM adapters

**Team Features:**
- Shared deal notes and context
- Partner handoff workflows
- Team briefing aggregation

**Analytics:**
- Deal flow metrics and trends
- Source quality analysis
- Time saved tracking
- Pipeline velocity metrics

**Advanced Automation:**
- Auto-generate call prep docs
- Auto-schedule reference calls
- Deal room monitoring
- Competitive intelligence tracking

---

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for how to suggest features, report bugs, or contribute improvements.

---

## Version History

- **v1.0.0** (2026-01-30) - Initial production release
  - Complete VC workflow automation
  - Email triage, CRM, memos, calendar, briefings
  - Ready for ClawdHub distribution

---

## Support

- **Issues:** [GitHub Issues](https://github.com/clawdhub/clawdbot-for-vcs/issues)
- **Discussions:** [GitHub Discussions](https://github.com/clawdhub/clawdbot-for-vcs/discussions)
- **Documentation:** See README.md, SKILL.md, BOOTSTRAP.md
