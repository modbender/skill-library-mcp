---
name: tpm-copilot
description: "AI-powered operating system for Technical Program Managers and Project Managers. Pulls data from Jira, Linear, GitHub, and calendars to auto-generate status reports, track risks and blockers, manage meeting workflows, map dependencies, and deliver stakeholder dashboards. Use when: (1) generating status reports or program updates, (2) tracking risks, blockers, or stale tickets, (3) preparing meeting agendas or extracting action items, (4) mapping cross-team dependencies, (5) creating stakeholder dashboards, (6) monitoring sprint health or velocity, (7) writing executive summaries, or (8) automating any TPM/PM workflow."
---

# TPM Copilot

Your AI program management operator. Pulls from Jira, Linear, GitHub, and calendars — synthesizes everything into status reports, risk alerts, meeting prep, and stakeholder dashboards.

## Setup

### Dependencies

```bash
pip3 install requests
```

For GitHub: install `gh` CLI and authenticate (`gh auth login`).

### API Connections (configure in `config.json`)

- **Jira** — `JIRA_BASE_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN` (Atlassian API token)
- **Linear** — `LINEAR_API_KEY`
- **GitHub** — uses `gh` CLI (already authenticated) or `GITHUB_TOKEN`
- **Slack** — `SLACK_WEBHOOK_URL` (for report delivery)
- **Calendar** — iCal URL or Google Calendar API

Not all required — skill adapts to what's configured.

### Workspace

```
tpm/
├── config.json           # API keys, project settings, team config
├── programs/             # Per-program data
│   └── program-name/
│       ├── config.json   # Program-specific settings (board IDs, repos, teams)
│       ├── reports/      # Generated status reports
│       ├── risks/        # Risk register snapshots
│       └── dependencies/ # Dependency maps
├── templates/            # Report templates
├── meetings/             # Meeting notes and action items
└── state.json            # Persistent state (last check timestamps, etc.)
```

Run `scripts/init-workspace.sh` to create this structure.

## Core Workflows

### 1. Status Report Generator

The flagship workflow. Pulls from all connected tools, generates audience-specific reports.

```bash
scripts/status-report.sh --program "my-program" --audience exec
scripts/status-report.sh --program "my-program" --audience eng
scripts/status-report.sh --program "my-program" --audience full
scripts/status-report.sh --program "my-program" --audience exec --deliver slack
```

**Data pulled:**
- Jira/Linear: sprint progress, tickets by status, velocity, blockers, recent completions
- GitHub: PRs merged/open/stale, CI status, release tags
- Calendar: upcoming milestones, meetings this week

**Audience formats:**
- **exec** — 3-5 bullet executive summary, RAG status per workstream, top risks, key decisions needed. Under 200 words.
- **eng** — sprint metrics, PR review queue, blockers, velocity trends, upcoming deadlines
- **full** — comprehensive program update with all sections, dependencies, action items

**Delivery options:**
- stdout (default) — prints to terminal
- slack — posts to configured webhook
- email — sends via Resend/SMTP
- confluence — creates/updates a Confluence page
- file — saves to `programs/<name>/reports/`

### 2. Risk & Blocker Radar

Proactive scanning for problems before they become crises.

```bash
scripts/risk-radar.sh --program "my-program"
scripts/risk-radar.sh --program "my-program" --alert     # Send alerts for new risks
scripts/risk-radar.sh --program "my-program" --history    # Show risk trends
```

**Auto-detected risks:**
- **Stale tickets** — no updates in N days (configurable, default 5)
- **Blocked tickets** — status = blocked, or flagged
- **PR review bottlenecks** — PRs open >48h without review
- **Sprint scope creep** — tickets added mid-sprint
- **Missed commitments** — tickets rolled over from previous sprint
- **CI failures** — broken builds on main branch
- **Dependency delays** — upstream team's deliverables slipping

**Risk register** maintained as JSON in `programs/<name>/risks/`:
```json
{
  "id": "RISK-001",
  "severity": "high",
  "category": "delivery",
  "title": "Auth service migration blocked on Team B API",
  "detected_at": "2026-02-24",
  "source": "jira_blocked_ticket",
  "ticket": "PROJ-1234",
  "status": "open",
  "mitigation": "",
  "owner": ""
}
```

### 3. Meeting Autopilot

Automate meeting prep, notes processing, and follow-up tracking.

```bash
scripts/meeting-prep.sh --program "my-program" --type standup
scripts/meeting-prep.sh --program "my-program" --type sprint-review
scripts/meeting-prep.sh --program "my-program" --type exec-sync
scripts/meeting-prep.sh --program "my-program" --type program-review

scripts/process-notes.sh --file meeting-notes.md         # Extract action items
scripts/action-tracker.sh --program "my-program"          # Show overdue actions
scripts/action-tracker.sh --program "my-program" --create-tickets  # Create Jira tickets for actions
```

**Meeting types and auto-generated agendas:**
- **standup** — yesterday's completions, today's focus, blockers (from Jira)
- **sprint-review** — sprint metrics, completed work, demos, carry-over items
- **exec-sync** — program RAG, top risks, decisions needed, timeline status
- **program-review** — full workstream status, dependencies, resource needs

**Notes processing:**
- Parse markdown notes for action items (lines starting with `AI:`, `TODO:`, `ACTION:`, or `[ ]`)
- Extract owners and due dates
- Optionally create Jira/Linear tickets
- Track completion status across meetings

### 4. Dependency Tracker

Map and monitor cross-team dependencies.

```bash
scripts/dependency-map.sh --program "my-program"           # Generate dependency map
scripts/dependency-map.sh --program "my-program" --check   # Check for slips
scripts/dependency-map.sh --program "my-program" --alert   # Alert on at-risk dependencies
```

**Sources:**
- Jira issue links (blocks/is-blocked-by)
- Jira/Linear labels (e.g., `depends-on:team-b`)
- Manual entries in `programs/<name>/dependencies/deps.json`

**Output:**
- Markdown dependency table with status
- Critical path highlighting
- Alert when upstream dependencies slip

### 5. Program Dashboard

Quick terminal dashboard for program health.

```bash
scripts/dashboard.sh --program "my-program"
```

Shows:
- Overall RAG status
- Sprint progress (% complete, days remaining)
- Open risks by severity
- PR review queue
- Upcoming milestones
- Action items overdue

## Configuration

### Program Config (`programs/<name>/config.json`)

```json
{
  "name": "Project Phoenix",
  "workstreams": [
    {
      "name": "Backend",
      "jira_project": "PHX",
      "jira_board_id": "123",
      "github_repos": ["org/backend-api"],
      "team_lead": "Alice"
    },
    {
      "name": "Frontend",
      "jira_project": "PHX",
      "jira_board_id": "124",
      "github_repos": ["org/web-app"],
      "team_lead": "Bob"
    }
  ],
  "milestones": [
    {"name": "Alpha Release", "date": "2026-03-15", "status": "on-track"},
    {"name": "Beta Release", "date": "2026-04-30", "status": "on-track"}
  ],
  "stakeholders": {
    "exec": ["vp-eng@company.com"],
    "eng": ["#eng-phoenix-slack-channel"],
    "full": ["phoenix-team@company.com"]
  },
  "settings": {
    "stale_ticket_days": 5,
    "pr_review_threshold_hours": 48,
    "sprint_length_weeks": 2,
    "tracker": "jira"
  }
}
```

### Tracker Selection

Set `settings.tracker` to `"jira"` or `"linear"`. Scripts auto-adapt API calls accordingly.

## Cron Integration

- **Daily standup prep** — generate at 8:30 AM before standup
- **Daily risk scan** — run at end of day, alert on new risks
- **Weekly status report** — generate and deliver Monday AM
- **Action item follow-up** — check overdue items daily
- **Sprint boundary** — auto-generate sprint review data on last day of sprint

## References

- `references/jira-setup.md` — Jira API authentication and project configuration
- `references/linear-setup.md` — Linear API setup and GraphQL queries
- `references/report-templates.md` — Customizing report formats and sections
- `references/risk-categories.md` — Risk taxonomy and severity definitions
