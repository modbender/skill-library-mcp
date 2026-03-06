# Shared File Templates

Templates for workspace shared files. Variables: `{{TEAM_NAME}}`, `{{CEO_TITLE}}`, `{{TZ}}`.

## AGENTS.md

```markdown
# AGENTS.md - {{TEAM_NAME}}

## First Instruction

You are a member of {{TEAM_NAME}}. Your identity.name is set in OpenClaw config.

Execute immediately:
1. Confirm your role (identity name shown in system prompt)
2. Read agents/[your-id]/SOUL.md
3. Read shared/decisions/active.md
4. Read shared/inbox/to-[your-id].md
5. Read agents/[your-id]/MEMORY.md

### Role Lookup
| identity.name | ID | Position |
|---------------|-----|----------|
(generated from role config)

## Inbox Protocol

### Write format
## [YYYY-MM-DD HH:MM] from:[your-id] priority:[high/normal/low]
To: [target-id]
Subject: ...
Expected output: ...
Deadline: ...

### Rules
- Read inbox at session start
- Move processed items to "Processed" section at bottom
- Urgent items also notify chief-of-staff

## Output rules
- Personal memory: agents/[id]/MEMORY.md
- Daily log: agents/[id]/memory/YYYY-MM-DD.md
- To other agents: shared/inbox/to-[id].md
- Products: shared/products/[name]/
- Knowledge: shared/knowledge/
- Tasks: shared/kanban/

## Prohibited
- Do not read/write other agents' private dirs
- Do not modify shared/decisions/ (CEO only)
- Do not delete shared/ files
- Do not publish externally without CEO approval
- Do not fabricate data
```

## shared/decisions/active.md

```markdown
# Active Decisions

> All agents must read this file every session. CEO directives and priorities.

## Strategy
- Team: {{TEAM_NAME}}
- Stage: Cold start
- Focus: GEO (AI search optimization)

## Growth Channel Priority
1. GEO - highest priority
2. SEO - long-term foundation
3. Community - precision acquisition
4. Content - brand building
5. Paid ads - not yet

## Team Rules
- All output goes to shared/ directories
- Agent communication via inbox files
- Daily briefs by Chief of Staff
- Major decisions require CEO approval

## CEO Decision Queue
(None yet)

---
*Fill in: main product, goals, resource allocation*
```

## shared/products/_index.md

```markdown
# Product Matrix

> All agents reference this file for product overview.

## Product Template
- Name:
- URL:
- Code directory: (any path)
- One-line description:
- Target users:
- Core features:
- Tech stack:
- Status: (dev / live / maintenance)
- Keywords (for GEO/SEO):
- Competitors:
- Differentiator:

---
*CEO: fill in your products*
```

## shared/knowledge/tech-standards.md

```markdown
# Tech Standards

> All code-related agents must follow. Product Lead reviews, Fullstack Dev executes.

## Core Principles
1. First-principles design, KISS + SOLID + DRY implementation
2. Research first: search code, find reuse opportunities, trace call chains before modifying
3. Three questions before changing: Real problem? Existing code to reuse? What breaks?

## Red Lines
- No copy-paste duplication
- No breaking existing functionality
- No blind execution without thinking
- Critical paths must have error handling

## Code Quality
- Methods under 200 lines, files over 500 lines need refactoring
- Follow existing architecture and code style
- New tech requires CEO approval
- Auto-cleanup: unused imports, debug logs, temp files

## Security
- No hardcoded secrets
- DB changes via SQL scripts, not direct execution
- User input must be validated at system boundaries

## Change Control
- Minimal change scope
- Update all call sites when changing function signatures
- Clear commit messages

---

## Tech Stack Preferences (New Projects)
New project tech stack must be confirmed with CEO before starting.
- Backend: PHP (Laravel/ThinkPHP preferred), Python as fallback
- Frontend: Vue.js or React
- Mobile: Flutter or UniApp-X
- CSS: Tailwind CSS
- DB: MySQL or PostgreSQL
- Existing projects: keep current stack
- Always propose first, get approval, then code
*CEO: customize with your tech stack specifics*
```

## Knowledge Base Files

### geo-playbook.md
```
# GEO Playbook
AI search engine optimization strategies and best practices.
(Growth Lead maintains)
```

### seo-playbook.md
```
# SEO Playbook
Traditional search engine optimization strategies.
(Growth Lead maintains)
```

### competitor-map.md
```
# Competitor Map
Competitor list and analysis.
(Intel Analyst maintains, updated Mon/Wed/Fri)
*CEO: fill in initial competitor info*
```

### content-guidelines.md
```
# Content Guidelines
Brand voice, writing standards, format requirements.
(Content Chief maintains)
```

### user-personas.md
```
# User Personas
Target user characteristics and needs.
(Data Analyst maintains)
```
