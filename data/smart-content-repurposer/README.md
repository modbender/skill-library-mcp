# client-manager

**The only CRM a freelancer needs — runs entirely from chat.**

Track clients, leads, projects, time, invoices, proposals, and earnings. All from your OpenClaw agent. No spreadsheets. No $50/month CRM subscriptions. Just chat.

## Why This Exists

Freelancers juggle 5-7 disconnected tools: email, spreadsheets, invoicing software, project management, time trackers. Each handles one function, none share data. You become the manual integration layer.

client-manager replaces all of them with one skill that lives in your OpenClaw chat.

**Replaces:** Notion CRM + FreshBooks + Toggl + Pipedrive + Google Sheets
**Cost of those tools:** $50-150/month
**Cost of client-manager:** Free. Forever.

## 19 Features

| # | Feature | Command | What It Does |
|---|---------|---------|-------------|
| 1 | Add Client | "new client" | Store client details, rate, source, service type |
| 2 | View Clients | "show clients" | Table of all active clients |
| 3 | New Project | "new project" | Create project with deadline + priority |
| 4 | Generate Invoice | "invoice John" | Professional invoice with auto-numbering |
| 5 | Mark Payment | "John paid" | Track payments, partial or full |
| 6 | Follow-Up Reminders | "follow up Sarah" | Never forget to chase payments |
| 7 | Earnings Report | "earnings" | Income by client, service, time period |
| 8 | Dashboard | "dashboard" | Full overview with alerts |
| 9 | Lead Pipeline | "new lead" | Track potential clients (Hot/Warm/Cold) |
| 10 | Time Tracking | "start timer" | Track hours per project, auto-bill |
| 11 | Quick Notes | "log John sent draft" | One-line client activity log |
| 12 | Proposals | "quote Sarah" | Generate quotes with milestones |
| 13 | Retainers | "set retainer" | Monthly recurring client management |
| 14 | Archive | "archive Mike" | Past clients with re-engagement prompts |
| 15 | Milestones | "milestones [project]" | Track project progress with payments |
| 16 | Referral Tracking | "referral report" | See which source brings most revenue |
| 17 | Morning Briefing | "good morning" | Daily overview of priorities + alerts |
| 18 | Show Projects | "show projects" | Active projects with deadline warnings |
| 19 | Export Data | "export" | Export all data to CSV files |

## What Makes This Different

**vs Notion/Spreadsheets:**
- No setup. No templates. Just start talking.
- Agent auto-suggests follow-ups and catches overdue invoices.

**vs Pipedrive/HubSpot ($14-800/month):**
- Free. Local. Private. No vendor lock-in.
- Lead pipeline with Hot/Warm/Cold scoring built in.

**vs Bonsai/HoneyBook ($19-49/month):**
- Time tracking + invoicing + proposals in one tool.
- Milestone-based billing with auto-invoice generation.

**OpenClaw Exclusive Features (no CRM has this):**
- Morning briefing delivered to WhatsApp/Telegram
- Natural language: "John paid me 500 bucks" just works
- Proactive alerts: agent reminds YOU about overdue payments
- Works from your phone via messaging apps

## Example Conversation

```
You: "good morning"
Agent: ☀️ GOOD MORNING — Feb 19, 2026
       💰 This month: $1,200 earned | $700 pending
       🔥 TODAY: Send John revised mockup (deadline tomorrow!)
       ⏳ OVERDUE: Mike Chen owes $200 (5 days)

You: "new lead"
Agent: Lead name? → "Lisa Park"
       Source? → "Twitter DM"
       Need? → "Landing page"
       Budget? → "$800"
       Temperature? → "Hot"
       ✅ Lead added! Lisa Park — Hot — $800

You: "start timer Portfolio Website"
Agent: ⏱️ Timer started for Portfolio Website (John Smith)

You: "stop timer"
Agent: ⏱️ 2h 15m logged. Total this week: 6h 30m

You: "log John — sent revised mockup"
Agent: 📝 Logged: John Smith — sent revised mockup

You: "invoice John"
Agent: 📄 Invoice #INV-2026-004 — $500.00
       Send via email? Save as PDF?

You: "John paid"
Agent: ✅ $500 from John Smith — marked as PAID!

You: "earnings"
Agent: 💰 This month: $1,700 | Best client: Sarah ($2,000 all-time)
       📊 Top source: Twitter/X (42% of revenue)

You: "export"
Agent: 📁 5 CSV files exported to exports folder.
```

## Install

```bash
clawhub install client-manager
```

## Privacy & Security

- All data stored locally in `~/.openclaw/client-manager/`
- 12 JSON files — human-readable, portable, no database needed
- Zero external API calls
- No data collection, no tracking
- Your client data never leaves your machine
- Weekly auto-backups to `backups/` directory
- Export everything to CSV anytime

## Author

**Manish Pareek** (@Mkpareek19_)

I build AI agents and OpenClaw skills for freelancers. Follow me on X for more tools.

## Tags

freelance, clients, invoicing, projects, earnings, business, crm, money, tracking, productivity, leads, pipeline, time-tracking, proposals, retainers
