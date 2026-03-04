---
name: client-flow
description: >
  Automated client onboarding and project lifecycle management. From a single message, creates Google
  Drive/Dropbox project folder structure, generates project brief, sends templated welcome email,
  schedules kickoff meeting on Google Calendar, sets up task board in Todoist/ClickUp/Linear/Asana/Notion,
  configures follow-up reminders, and maintains a master client registry with status tracking. Use this
  skill for: new client onboarding, project setup, client intake, welcome email, kickoff meeting
  scheduling, project kickoff, client management, project status dashboard, "new client [name]",
  "onboard [company]", "set up a project for [client]", "how are my projects doing", client portfolio
  overview, project lifecycle tracking, client communication templates, progress update emails, project
  closure workflow, freelancer project management, agency client management, or any request involving
  setting up and tracking client projects. One message replaces 30 minutes of manual setup across
  email, calendar, file storage, and task management tools.
metadata:
  openclaw:
    emoji: "🤝"
---

# Client Flow

New client? One message, full setup. From folder structure to welcome email to kickoff meeting — automated in 30 seconds instead of 30 minutes.

## Why This Exists

Client onboarding is one of the most-reported use cases in the OpenClaw community, yet has zero dedicated skills on ClawHub. Freelancers, agencies, and small businesses repeat the same 8-step process for every new client — creating folders, sending emails, scheduling calls, setting up tasks. This skill automates the entire flow.

## The Onboarding Flow

Triggered by something like: "New client: Acme Corp, contact Sarah at sarah@acme.com, project: website redesign, budget: $15k, deadline: March 30"

The skill extracts whatever information is provided, asks for anything critical that's missing, then executes the full onboarding sequence:

### Step 1: Create Project Structure

Create an organized folder hierarchy for the project:

```
[Client Name]/
├── 01-Brief/
│   └── project-brief.md (auto-generated from intake info)
├── 02-Contracts/
├── 03-Design/
├── 04-Development/
├── 05-Content/
├── 06-Deliverables/
└── 07-Communications/
    └── meeting-notes/
```

Where to create:
- **Google Drive**: if `gog` tool is available, create in a "Clients" folder
- **Dropbox**: if Dropbox skill is available
- **Local filesystem**: if running locally, create under a configurable base path (default: `~/Clients/`)
- **Notion**: if Notion skill is available, create a project page instead of folders

### Step 2: Generate Project Brief

Auto-generate a project brief document from the intake information:

```markdown
# Project Brief: [Project Name]
**Client**: [Company Name]
**Contact**: [Name] ([Email])
**Start Date**: [Today or specified]
**Deadline**: [Date]
**Budget**: [Amount]

## Project Description
[Generated from user's input — expand into 2-3 sentences]

## Objectives
- [Extracted or inferred from project type]
- [...]

## Deliverables
- [Inferred from project type — e.g., "website redesign" → wireframes, mockups, final site]
- [...]

## Timeline
- Week 1-2: Discovery & Planning
- Week 3-4: [Phase based on project type]
- [...]

## Notes
[Any additional context from the user's message]
```

Save this to the project folder.

### Step 3: Send Welcome Email

Compose and send (or draft) a welcome email to the client:

```
Subject: Welcome to [Your Name/Company] — [Project Name] Kickoff

Hi [Client First Name],

Thank you for choosing to work with us on [Project Name]. I'm excited to get started!

Here's what happens next:
1. I'll send a kickoff meeting invite for [suggested date/time]
2. Please review and sign the project agreement [if applicable]
3. We'll begin the discovery phase right away

If you have any questions before we kick off, don't hesitate to reach out.

Looking forward to working together!

[User's name/signature from memory]
```

Delivery:
- If email skill is configured: send directly (with user confirmation)
- If not: output the email for the user to copy and send manually

### Step 4: Schedule Kickoff Meeting

Create a calendar event for the kickoff meeting:

- **When**: suggest a time 2-3 business days from now (or use user-specified date)
- **Duration**: 30 minutes (default, customizable)
- **Attendees**: client contact + user
- **Title**: "[Client Name] — Project Kickoff"
- **Description**: include project brief summary and agenda:
  ```
  Agenda:
  1. Introductions & project overview (5 min)
  2. Requirements review (10 min)
  3. Timeline & milestones (10 min)
  4. Next steps & action items (5 min)
  ```

Use Google Calendar via `gog` tool, or Outlook if configured.

### Step 5: Create Task Board

Set up project tasks in the user's preferred task manager:

**For Todoist / ClickUp / Linear / Asana:**
Create a project with these default tasks:
- [ ] Send contract/agreement
- [ ] Kickoff meeting
- [ ] Discovery & requirements gathering
- [ ] First deliverable review
- [ ] Midpoint check-in
- [ ] Final delivery
- [ ] Client feedback
- [ ] Project closure

**For GitHub Issues:** (if the project is technical)
Create a milestone + issues for each phase

**For Notion:** (if used as task manager)
Create a task database within the project page

Each task gets a due date estimated from the project timeline.

### Step 6: Set Up Reminders

Configure follow-up reminders:
- **Day before kickoff**: reminder to prepare
- **Weekly check-in**: recurring reminder to update the client on progress
- **Milestone dates**: reminders for each deliverable deadline
- **1 week before deadline**: "final sprint" reminder

Use OpenClaw cron or the task manager's reminder system.

### Step 7: Update Client Registry

Maintain a master list of all clients and projects:

```markdown
# Client Registry

| Client | Project | Status | Contact | Start | Deadline | Value |
|--------|---------|--------|---------|-------|----------|-------|
| Acme Corp | Website Redesign | 🟢 Active | sarah@acme.com | Feb 15 | Mar 30 | $15k |
| Beta LLC | Brand Identity | 🟡 In Review | john@beta.io | Jan 20 | Feb 28 | $8k |
| Gamma Inc | Mobile App | ✅ Completed | lisa@gamma.co | Nov 1 | Jan 15 | $25k |
```

Store in workspace memory or as a Markdown file in a "Business" folder.

## Post-Onboarding: Project Lifecycle

### Status Check
**User**: "How are my projects doing?" or "Client status"
→ Pull from client registry + task managers and generate:

```
🤝 Active Projects

1. Acme Corp — Website Redesign
   Status: On track ✅
   Next milestone: First mockup review (Feb 22)
   Outstanding tasks: 3 of 8 completed
   Budget used: ~40%
   
2. Beta LLC — Brand Identity
   Status: Needs attention ⚠️
   Next milestone: Final delivery (Feb 28) — 5 days away
   Outstanding tasks: 2 remaining
   Blocker: Waiting for client feedback since Feb 10
```

### Client Communication
**User**: "Draft an update email for Acme Corp"
→ Generate a progress update email using project data:
- What's been completed since last update
- Current status and next steps
- Any blockers or needs from the client
- Timeline update

### Project Closure
**User**: "Close the Beta LLC project"
→ Execute closure workflow:
1. Mark project as completed in registry
2. Send thank-you email to client
3. Archive project folder
4. Create a project retrospective note
5. Set a 30-day follow-up reminder for testimonial request
6. Set a 90-day follow-up for potential repeat business

## Templates

Store customizable templates in workspace memory. Defaults are provided but users can override:

- **Welcome email template**: adjust tone, signature, included links
- **Folder structure**: add/remove folders based on project type
- **Task list**: customize default tasks per project type
- **Project types**: different presets for "website", "branding", "consulting", "development", etc.

**User**: "When I onboard a development client, also add GitHub repo setup and Slack channel creation"
→ Store as a "development" project type template

## Configuration

On first use:

1. **Business info**: company name, user's name, email signature, timezone
2. **Default tools**: which task manager, file storage, calendar, email to use
3. **Project types**: what kinds of projects do they typically do?
4. **Templates**: review and customize default templates
5. **Client folder location**: where to store project folders

Store everything in workspace memory. After first setup, onboarding is one command.

## Edge Cases

- **Minimal info**: if the user only says "new client: Acme", ask for contact email (required) and project name. Everything else can be defaults.
- **Repeat client**: if a client name matches an existing entry, ask if this is a new project for the same client. If yes, add to existing client folder rather than creating a new one.
- **No task manager**: if no external task manager is configured, create tasks as a checklist in the project brief
- **No email configured**: output the welcome email for manual sending. Don't skip the step.
- **International clients**: respect timezone differences in meeting scheduling. If client is in a different timezone, note it.
- **Team projects**: if multiple team members are involved, allow assigning tasks to different people
- **Budget tracking**: this skill doesn't do invoicing (that's a separate concern), but tracks estimated vs. actual budget at a high level
