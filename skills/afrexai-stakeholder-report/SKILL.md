# Stakeholder Report Generator

Generate executive-ready stakeholder reports from raw project data. Covers status updates, risk flags, milestone tracking, budget variance, and next-period outlook.

## When to Use
- Weekly/monthly stakeholder updates
- Board meeting prep
- Investor updates
- Client project status reports
- Internal leadership briefings

## How It Works

The agent structures your raw inputs into a polished report with these sections:

### 1. Executive Summary (3-5 sentences)
- What happened this period
- Key wins and blockers
- Overall health: 🟢 On Track | 🟡 At Risk | 🔴 Off Track

### 2. Milestone Tracker
| Milestone | Target Date | Status | Notes |
|-----------|------------|--------|-------|
| (filled from your input) | | | |

### 3. Budget & Resource Snapshot
- Spend vs. budget (% variance)
- Burn rate trend
- Resource utilization highlights

### 4. Risk Register
| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| (identified from your input) | H/M/L | H/M/L | Action plan |

### 5. Key Decisions Needed
- Decisions that require stakeholder input this period
- Deadlines for each decision

### 6. Next Period Outlook
- Planned deliverables
- Upcoming milestones
- Known dependencies

## Usage

Tell the agent:
```
Generate a stakeholder report for [project name].
Period: [date range]
Key updates: [paste raw notes, metrics, or bullet points]
Audience: [board / investors / client / internal leadership]
```

The agent adapts tone and detail level based on audience:
- **Board/Investors**: High-level, financial focus, strategic framing
- **Client**: Deliverable-focused, professional, no internal details
- **Internal leadership**: Candid, operational detail, resource asks

## Tips
- Feed it messy notes — the agent structures them for you
- Include numbers whenever possible (hours, dollars, percentages)
- Mention blockers explicitly — the agent will flag them in the risk register
- Run it weekly to build a paper trail of project health over time

## Output Format
Markdown by default. Ask for "slide-ready" to get condensed bullet points suitable for presentation decks.

---

Built by [AfrexAI](https://afrexai-cto.github.io/context-packs/) — AI Context Packs for business teams that ship.
