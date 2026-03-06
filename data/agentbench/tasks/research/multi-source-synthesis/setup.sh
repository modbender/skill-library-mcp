#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="$1"
cd "$WORKSPACE"

git init

# --- Document 1: Product Specification ---
cat > product-spec.md << 'SPEC'
# TaskFlow — Product Specification

## Overview

TaskFlow is a project management SaaS platform designed for mid-size companies (50–500 employees). It aims to replace fragmented tool stacks with a single, integrated workspace for planning, executing, and reporting on work across departments.

## Core Features

### Task Boards
- Kanban and list views with drag-and-drop
- Custom columns, labels, and swimlanes
- Subtask hierarchies up to 3 levels deep
- Bulk operations for triaging and sprint planning

### Team Collaboration
- Real-time commenting on tasks with @mentions
- Shared team dashboards with customizable widgets
- Activity feeds scoped per project, team, or individual
- File attachments up to 50 MB per task

### Time Tracking
- Built-in timer with manual entry fallback
- Weekly timesheets with approval workflow
- Billable vs. non-billable hour categorization
- Integration with payroll export formats

### Reporting
- Pre-built reports: velocity, burndown, workload distribution
- Custom report builder with saved filters
- Scheduled email digests (daily/weekly)
- CSV and PDF export

## Target Market

Mid-size companies with 50–500 employees that have outgrown basic tools like Trello or spreadsheets but find enterprise platforms like Jira overly complex and expensive.

## Required Integrations

- **Slack**: Bidirectional — create tasks from Slack messages, receive task update notifications in channels
- **Email**: Forward emails to create tasks, send task assignments and due-date reminders via email
- **Calendar**: Sync task due dates to Google Calendar and Outlook; show availability in workload view

## Roadmap

### MVP (Phase 1)
Task boards, basic collaboration, Slack integration, core reporting

### Phase 2
Time tracking, advanced reporting, email integration

### Phase 3
Calendar sync, resource planning, API marketplace for third-party integrations
SPEC

# --- Document 2: CTO Feedback ---
cat > cto-feedback.md << 'FEEDBACK_CTO'
From: Alex Chen <alex.chen@taskflow.io>
To: Product Team <product@taskflow.io>
Subject: Re: TaskFlow Architecture — My Recommendations
Date: Mon, 14 Oct 2024 09:17:00 -0700

Team,

I've reviewed the product spec and want to share my architectural recommendations before we start building.

**Architecture**: We should go with microservices from day one. I know it's tempting to start with a monolith and refactor later, but I've seen that story play out at three companies now — you never actually refactor, and eighteen months in you're stuck with a tangled mess nobody wants to touch. Let's do it right from the start: separate services for auth, task management, notifications, reporting, and integrations.

**API Layer**: I strongly recommend GraphQL over REST. Our frontend will need flexible queries — think about a dashboard that pulls tasks, team activity, and time entries in a single request. With REST you'd need three round trips. GraphQL gives us exactly the data shape the UI needs with zero over-fetching.

**Infrastructure**: Kubernetes is the right choice for deployment. It gives us auto-scaling, rolling deployments, and service mesh capabilities out of the box. We can run on EKS to keep ops overhead manageable.

**Frontend**: React with TypeScript is the most productive stack for our use case. Strong typing catches bugs early, and the React ecosystem has everything we need for drag-and-drop boards, real-time updates, and complex form handling.

Even if it takes longer to set up this foundation, architecture matters. The decisions we make now will determine how fast we can move in year two and year three. I'd rather spend an extra month on the foundation than accumulate tech debt from day one. We need to build for scale from the start.

Happy to walk through my service decomposition proposal in Thursday's meeting.

— Alex
FEEDBACK_CTO

# --- Document 3: VP Sales Feedback ---
cat > sales-feedback.md << 'FEEDBACK_SALES'
From: Jamie Park <jamie.park@taskflow.io>
To: Product Team <product@taskflow.io>
Subject: Re: TaskFlow MVP — Sales Perspective
Date: Tue, 15 Oct 2024 14:32:00 -0700

Hi everyone,

Wanted to share what I'm hearing from the field and what we need from a go-to-market standpoint.

**Timeline is everything.** The ProjectWorld conference is in 3 months and we absolutely need a working demo by then. I've already committed to three prospects that they'd see a live product. If we miss that window, we lose first-mover advantage and those deals go to Asana or Monday.com.

**Architecture**: Honestly, a monolith is fine for v1. We can always refactor later once we have revenue and a bigger team. What matters right now is shipping something that works, not building the perfect system nobody ever sees.

**API**: REST API is the standard. Every customer I've talked to expects a REST API for their integrations. GraphQL is a niche technology — our buyers are IT directors at mid-size companies, not Silicon Valley startups. Let's not make things harder than they need to be.

**What customers actually want**:
1. **Slack integration** — this comes up in literally every sales call. People want to create tasks without leaving Slack. This has to be in the MVP.
2. **Mobile-responsive design** — three of our top prospects specifically asked about mobile access. We don't need a native app yet, but the web app must work well on phones and tablets.

**What we should NOT build yet**: Admin features, advanced permissions, audit logs — none of our prospects have asked for these. Don't waste engineering time on features that don't close deals. Focus on end-user experience: clean UI, fast load times, intuitive workflows.

The product needs to sell itself in a 15-minute demo. That's the bar.

— Jamie
FEEDBACK_SALES

# --- Document 4: Compliance Feedback ---
cat > compliance-feedback.md << 'FEEDBACK_COMPLIANCE'
From: Sam Rivera <sam.rivera@taskflow.io>
To: Product Team <product@taskflow.io>
Subject: Re: TaskFlow — Compliance and Security Requirements
Date: Wed, 16 Oct 2024 11:05:00 -0700

Product Team,

Before development begins, I need to ensure we have alignment on compliance and security requirements. These are non-negotiable for the type of customers we're targeting.

**Audit Trail**: Every data mutation in the system must have a full audit trail — who performed the action, what changed (before and after values), and when it happened. This includes task creation, updates, deletions, permission changes, and user management actions. The audit log must be immutable and retained for a minimum of 7 years. This is not optional; mid-size companies in regulated industries will require this during their procurement reviews.

**Third-Party Data Processors**: We cannot send customer data to any third-party service or data processor without completing a security review first. This applies to analytics tools, error tracking services, email delivery providers, and any SaaS dependency. Each vendor needs a signed Data Processing Agreement on file before integration.

**Encryption**: All data must be encrypted at rest (AES-256 minimum) and in transit (TLS 1.2+). Database backups must also be encrypted. Encryption keys must be managed through a proper KMS — no hardcoded keys, no shared secrets in environment variables.

**SOC 2 Type II**: We need to achieve SOC 2 Type II compliance before launch, not after. Many of our target customers will require a SOC 2 report during their vendor evaluation process. This means we need proper access controls, change management procedures, and incident response plans from day one.

**GDPR Data Residency**: Any EU customer's data must be stored and processed within the EU. We'll need a multi-region deployment strategy to ensure data residency compliance. This affects our infrastructure architecture decisions significantly.

Security is non-negotiable, even if it slows development. A data breach or compliance failure in year one would be an extinction-level event for a startup like ours.

— Sam
FEEDBACK_COMPLIANCE

# --- Document 5: Project Constraints ---
cat > constraints.md << 'CONSTRAINTS'
# TaskFlow — Project Constraints

## Budget
- **Total development budget**: $200,000
- This covers salaries, tools, and infrastructure for the build phase
- No contingency fund — this is a hard ceiling approved by the board

## Timeline
- **Launch deadline**: 4 months from project kickoff
- Milestone 1 (Month 2): Internal alpha with core task board functionality
- Milestone 2 (Month 3): Beta with integrations, limited external testers
- Milestone 3 (Month 4): Production launch

## Team
- **Backend engineers**: 2 (senior and mid-level)
- **Frontend engineer**: 1 (senior)
- **No additional headcount** — hiring freeze in effect until Series A closes
- Product manager and designer available part-time (shared with other projects)

## Infrastructure
- **Monthly infrastructure budget**: $3,000/month maximum
- This must cover hosting, databases, CDN, monitoring, and any managed services
- Cloud provider: AWS (existing account with organizational billing)

## Other Constraints
- Must use existing company GitHub organization and CI/CD pipeline
- On-call rotation starts at launch — the 3-person engineering team will share it
- Legal has already approved open-source license usage (MIT, Apache 2.0, BSD only)
CONSTRAINTS

git add -A
git commit -m "Initial project documents: product spec, stakeholder feedback, and constraints"
