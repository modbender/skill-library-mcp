# Agent Roles — Reference

All available specialist roles for war room sessions. Select the subset that fits your project.

---

## Core Roles

### ARCH — Architect
- **Domain:** System architecture, technology choices, component design
- **When to include:** Any project with technical architecture decisions
- **Produces:** Architecture spec, dependency map, API contracts, technology rationale
- **Key decisions:** Stack, patterns, component boundaries, data flow

### PM — Product Manager
- **Domain:** Scope, requirements, user stories, roadmap, competitive analysis
- **When to include:** Any project that ships to users
- **Produces:** MVP scope doc, user journey, competitive analysis, roadmap, via negativa (explicit exclusions)
- **Key decisions:** What's in/out of scope, user stories, milestones, success metrics

### DEV (or SWIFT, WEB, etc.) — Developer
- **Domain:** Implementation, code architecture, feasibility assessment
- **When to include:** Any project involving code
- **Produces:** Implementation plan, code scaffolding, feasibility notes, technical constraints
- **Key decisions:** Implementation approach, library choices, code structure
- **Note:** Rename to match the stack (SWIFT, WEB, BACKEND, MOBILE, etc.)

### SEC — Security
- **Domain:** Threat modeling, legal compliance, privacy, licensing
- **When to include:** Anything that handles user data, has network access, or ships publicly
- **Produces:** Threat model, compliance checklist, legal assessment, licensing audit
- **Key decisions:** Auth approach, data handling, encryption, regulatory compliance

### UX — User Experience
- **Domain:** Interface design, interaction flows, design system
- **When to include:** Anything with a user interface
- **Produces:** Wireframes, interaction spec, design tokens, accessibility notes
- **Key decisions:** Layout, navigation, visual language, interaction patterns

### QA — Quality Assurance
- **Domain:** Testing strategy, edge cases, acceptance criteria
- **When to include:** Any project that ships
- **Produces:** Test plan, edge case catalog, smoke test checklist, acceptance criteria
- **Key decisions:** Test coverage strategy, ship-blocker criteria, pre-release gates

### CHAOS — Devil's Advocate ⚡
- **Domain:** Stress-testing every decision, finding failure modes, proposing alternatives
- **When to include:** **ALWAYS.** Non-negotiable.
- **Produces:** Challenge report (SURVIVE/WOUNDED/KILLED per decision), failure scenarios, counter-proposals
- **Key behavior:** Shadows every wave. Asks the question nobody wants to ask.
- **The hardest question:** "If [core assumption] is wrong, does this project still exist?"

---

## Extended Roles

### OPS — Operations / DevOps
- **Domain:** Build pipeline, deployment, infrastructure, monitoring
- **When to include:** Projects that need CI/CD, cloud infra, or complex build processes
- **Produces:** Build pipeline spec, infrastructure plan, deployment checklist, monitoring strategy

### MKT — Marketing
- **Domain:** Positioning, messaging, launch strategy, distribution channels
- **When to include:** Products that will be marketed/sold
- **Produces:** Positioning doc, launch plan, messaging framework, channel strategy

### RESEARCH — Researcher
- **Domain:** Market research, technical research, prior art, competitive landscape
- **When to include:** Projects entering unfamiliar markets or using unfamiliar technology
- **Produces:** Research report, prior art analysis, benchmark data, literature review

### AI-ENG — AI/ML Engineer
- **Domain:** Model selection, ML pipeline, inference optimization, prompt engineering
- **When to include:** Projects involving AI/ML components
- **Produces:** Model feasibility report, inference spec, prompt engineering guide, benchmark results

### AUDIO — Audio Engineer
- **Domain:** Audio pipeline, signal processing, codec selection, playback
- **When to include:** Projects with audio/music components
- **Produces:** Audio pipeline spec, format decisions, DSP requirements, quality benchmarks

### DATA — Data Engineer
- **Domain:** Data modeling, storage, ETL, analytics pipeline
- **When to include:** Projects with significant data processing or storage needs
- **Produces:** Data model, schema design, ETL pipeline spec, storage strategy

### LEGAL — Legal Advisor
- **Domain:** Contracts, IP, regulatory compliance, terms of service
- **When to include:** Projects with licensing, regulatory, or IP concerns
- **Produces:** Legal risk assessment, licensing analysis, compliance requirements, ToS review

### FINANCE — Financial Analyst
- **Domain:** Cost modeling, pricing strategy, unit economics, fundraising
- **When to include:** Projects that need financial viability analysis
- **Produces:** Cost model, pricing analysis, unit economics, financial projections

---

## Custom Roles

Create domain-specific roles as needed. Follow this template:

```
### ROLE-NAME — Human-readable title
- **Domain:** What this agent owns
- **When to include:** Trigger conditions
- **Produces:** List of deliverables
- **Key decisions:** What this agent decides
```

Examples of custom roles: CONTENT (content strategy), INFRA (infrastructure), DESIGN (graphic design), GAME (game design), EDU (educational design), API (API design).

---

## Agent Briefing Template

When spawning an agent subagent, include this in its prompt:

```
You are {ROLE} in a War Room session for project "{PROJECT_NAME}".

## Your DNA
{contents of DNA.md}

## Project Brief
{contents of BRIEF.md}

## Your Mission
{role description from above}

## Instructions
1. Read DECISIONS.md for prior decisions
2. Read agents/*/ folders for prior wave outputs (if any)
3. Do your analysis for YOUR domain
4. Write your outputs to agents/{role}/
5. Log your decisions in DECISIONS.md: [D###] {ROLE} — what — why
6. Update STATUS.md with your completion status
7. If you see problems in other agents' work, file a CHALLENGE in comms/

## Constraints
- Max 200 words per document section
- Data > opinion. Evidence > intuition
- If unsure, say UNKNOWN. Never fabricate.
- You own YOUR domain. Defer to others in theirs.
```
