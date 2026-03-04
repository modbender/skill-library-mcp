# Project Organizer Quickstart

## 1) Start the skill
In OpenClaw, use this exact skill:

`project-os-organizer`

## 2) Just type normal phrases
Examples:
- "Show my projects"
- "What am I working on today?"
- "Focus list"
- "Add this idea: improve onboarding flow"
- "Next for project-os: run smoke tests"
- "Mark project-os blocked"
- "Start dashboard"
- "Only track project-os, polymarket-trader-v2, poly_market_edge_finder"
- "Show scope"

## 3) Optional shortcuts (power users)
Use the short `project` command:

```bash
project
project focus
project today
project inbox "idea: improve onboarding flow"
project next "project-os" "run smoke tests"
project status "project-os" blocked
project scope set "project-os" "polymarket-trader-v2" "poly_market_edge_finder"
project scope
project weekly
project blockers
project dashboard start
```

## 4) Dashboard
Start:

```bash
project dashboard start
```

Open:

`http://127.0.0.1:8765`

---
Troubleshooting (if needed): run `project setup` once, then retry.

Privacy/Security defaults:
- Chat indexing is OFF by default.
- GitHub sync is OFF by default.
- Remote auto-install is OFF by default.

Optional opt-ins:
- `export PROJECT_OS_INCLUDE_CHAT_ROOTS=1`
- `export PROJECT_OS_ENABLE_GITHUB_SYNC=1`
- `export PROJECT_OS_AUTO_SETUP=1 PROJECT_OS_ALLOW_REMOTE_INSTALL=1`
