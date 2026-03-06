---
name: Clients
description: Build a personal client system for tracking relationships, projects, documents, and history.
metadata: {"clawdbot":{"emoji":"💼","os":["linux","darwin","win32"]}}
---

## Core Behavior
- User mentions client → offer to create/update profile
- User needs context → surface relevant history
- User shares document → help associate to client
- Create `~/clients/` as workspace

## File Structure
```
~/clients/
├── active/
│   └── acme-corp/
│       ├── profile.md
│       ├── projects/
│       ├── documents/
│       ├── communications/
│       └── notes.md
├── past/
├── leads/
└── templates/
```

## Client Folder Structure
```
acme-corp/
├── profile.md          # Main info, contacts
├── projects/
│   ├── 2024-rebrand/
│   └── 2023-website/
├── documents/
│   ├── contracts/
│   ├── invoices/
│   ├── proposals/
│   └── assets/
├── communications/
│   └── meeting-notes/
└── notes.md            # Quick notes, observations
```

## Client Profile
```markdown
# profile.md
## Company
Acme Corp
Industry: E-commerce
Website: acme.com
Since: 2022

## Contacts
### Primary
Sarah Chen — VP Product
sarah@acme.com | +1 555-0123
Best channel: Slack

### Others
- Mike Torres — Engineering
- Lisa Park — Finance/Invoicing

## Preferences
- Communication: Slack, quick responses
- Meetings: Tuesdays, mornings
- Decisions: Needs CEO approval over $5k

## Key Info
- Payment terms: Net 30
- Timezone: PST
- Fiscal year ends: December
```

## Projects
```markdown
# projects/2024-rebrand/project.md
## Overview
Scope: Full brand refresh
Budget: $25,000
Timeline: Feb - April 2024
Status: In progress

## Milestones
- [x] Discovery
- [x] Brand strategy
- [ ] Visual identity — due Feb 20
- [ ] Guidelines

## Team
- Lead: Sarah
- Stakeholders: CEO, Marketing

## Deliverables
/documents/deliverables/

## Notes
Scope expanded to include motion graphics (+$5k approved)
```

## Documents Organization
```
documents/
├── contracts/
│   └── 2024-service-agreement.pdf
├── invoices/
│   ├── INV-2024-001.pdf
│   └── INV-2024-002.pdf
├── proposals/
│   └── rebrand-proposal-v2.pdf
├── assets/
│   └── brand-files/
└── received/
    └── their-materials/
```

## Communications Log
```markdown
# communications/log.md
## 2024-02-10 — Call with Sarah
- Reviewed wireframes, approved with minor changes
- Budget discussion: approved motion graphics add-on
- Next: send revised timeline by Friday

## 2024-02-03 — Email thread
- Sent proposal v2
- Questions about timeline, addressed
```

## Quick Notes
```markdown
# notes.md
## Observations
- Prefers visual presentations over documents
- CEO is hands-off until final review
- Always pays on time
- Referred two other clients

## To Remember
- Sarah's assistant handles scheduling
- Use project code "ACM24" on invoices
- They close office last week of December
```

## Leads
```markdown
# leads/pipeline.md
## Hot
- TechStartup — proposal sent, decision Friday

## Warm
- AgencyXYZ — interested, following up next week

## Cold
- BigCorp — revisit Q3
```

## What To Surface
- "Last contact with Acme was 2 weeks ago"
- "Sarah prefers Slack"
- "Contract renewal due next month"
- "Open invoice: $5,000, sent 15 days ago"

## Before Meetings
Pull context:
- Current project status
- Last communication
- Open items
- Their preferences

## What To Track
- All contacts with roles
- Communication preferences
- Project history with outcomes
- Payment patterns
- Important dates (renewals, reviews)

## Progressive Enhancement
- Start: create folder for active clients
- Add key contacts and preferences
- Move documents into structure
- Log communications after meetings

## What NOT To Do
- Keep documents scattered outside client folder
- Forget to log important calls
- Lose track of open invoices
- Miss contract renewal dates
