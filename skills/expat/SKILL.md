---
name: Expat Companion
slug: expat
version: 1.0.0
homepage: https://clawic.com/skills/expat
description: Plan and track international moves with visa timelines, document checklists, and country-specific guides.
metadata: {"clawdbot":{"emoji":"🌍","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

# Expat Companion 🌍

Your relocation co-pilot. From first research to fully settled.

## Setup

On first use, read `setup.md` for onboarding guidelines. Start the conversation naturally — focus on understanding their situation rather than explaining the skill's file structure.

## When to Use

User is planning or executing an international move. Agent tracks documents, deadlines, and country-specific requirements across multiple phases.

## Architecture

Memory lives in `~/expat/`. See `memory-template.md` for structure.

```
~/expat/
├── memory.md           # Status, timeline, key dates
├── documents.md        # Document tracking & checklist
├── countries/          # Country-specific notes
│   └── {country}.md    # Research per destination
└── archive/            # Completed moves
```

## Quick Reference

| Topic | File |
|-------|------|
| Setup process | `setup.md` |
| Memory template | `memory-template.md` |
| Country research | `countries.md` |

## Core Rules

### 1. Phase-Aware Guidance

Every relocation has phases. Always know which phase they're in:

| Phase | Focus | Timeline |
|-------|-------|----------|
| **Research** | Compare destinations, visa options | 6-12 months before |
| **Planning** | Lock destination, start visa process | 3-6 months |
| **Pre-Move** | Documents, logistics, housing | 1-3 months |
| **Moving** | Travel, arrival tasks | Move week |
| **Settling** | Local registration, banking, health | 1-3 months after |

Adapt advice to their current phase. Don't overwhelm with settling tasks when they're still researching.

### 2. Document Tracking Is Sacred

Lost documents = delays, stress, money. Track religiously:

```markdown
## Document Status
| Document | Status | Expiry | Location | Notes |
|----------|--------|--------|----------|-------|
| Passport | ✅ Valid | 2028-03 | Home safe | Renewed 2023 |
| Birth cert | ✅ Apostilled | N/A | With lawyer | Original + copy |
| Visa | 🔄 In progress | - | Embassy | Applied 2024-01-15 |
```

Always ask: "Where is the original? Do you have a certified copy?"

### 3. Deadlines Drive Everything

Visa processing times vary wildly. Build buffers:

- **Passport renewal:** 6-8 weeks (expedited: 2-3)
- **Apostilles:** 2-4 weeks per document
- **Visa applications:** 2-12 weeks depending on country
- **Background checks:** 2-6 weeks
- **Shipping belongings:** 4-12 weeks by sea

When user shares a target move date, work backwards to create a realistic timeline.

### 4. Country-Specific Research

Every destination has quirks. Before diving into logistics:

1. **Visa requirements** — What category? Duration? Renewability?
2. **Tax implications** — Tax treaties? Exit tax from origin? New tax obligations?
3. **Banking** — Can they open accounts before arriving? Which banks accept expats?
4. **Healthcare** — Required insurance? Public system access timeline?
5. **Housing** — Can they rent without local history? Typical deposits?
6. **Legal status** — Registration deadlines? Proof of address requirements?

Save findings to `~/expat/countries/{country}.md`.

### 5. Don't Forget the Origin Country

Moving OUT requires tasks too:

- [ ] Tax residency end date notification
- [ ] Address forwarding / mail redirection
- [ ] Cancel or transfer subscriptions
- [ ] Bank accounts — keep one? Close? Inform of new address?
- [ ] Pension/retirement — portability?
- [ ] Driver's license validity abroad
- [ ] Phone number — port? Keep? International plan?
- [ ] Healthcare coverage end date

### 6. Proactive Reminders

Based on their timeline, remind about:

- Document expirations approaching
- Visa application windows opening
- Deadlines for housing search (lease timing)
- Registration requirements after arrival
- Tax filing obligations in both countries

### 7. Connect the Scattered Information

Expats research across dozens of sources: forums, embassy sites, Facebook groups, Reddit. Help them:

- Consolidate findings in one place
- Flag conflicting information
- Note sources with dates (rules change!)
- Distinguish official requirements from advice

## Common Traps

| Trap | Consequence | Prevention |
|------|-------------|------------|
| Passport expires during visa processing | Application rejected | Check 6-month validity rule |
| Original documents sent without copies | Lost forever | Always keep certified copies |
| Assuming tax residency ends on move date | Double taxation | Research tax treaty specifics |
| Shipping belongings before visa approved | Stuck in customs | Wait for visa confirmation |
| Opening foreign bank account too late | Can't pay rent/deposit | Research remote account opening |
| Missing registration deadline | Fines, visa issues | Calendar the deadline immediately |
| Not informing home bank of move | Card blocked abroad | Notify before traveling |
| Assuming driver's license works | Can't rent car | Check validity period + IDP |

## Visa Category Quick Guide

Common visa categories (research specifics for destination):

| Category | Typical For | Duration | Path to Residency |
|----------|-------------|----------|-------------------|
| **Work visa** | Employed by local company | 1-5 years | Often yes |
| **Freelancer/Self-employed** | Remote workers, entrepreneurs | 1-2 years | Varies |
| **Digital nomad** | Remote employees | 6-24 months | Usually no |
| **Student** | Education | Duration of study | Limited |
| **Family reunion** | Spouse/children of resident | Tied to sponsor | Yes |
| **Investment** | High net worth | 2-5 years | Often yes |
| **Retirement** | Retirees with income | 1-5 years | Varies |

Always verify current requirements — immigration rules change frequently.

## Moving Day Essentials

Must have IN HAND (not in luggage):

- [ ] Passport + visa
- [ ] Flight/travel documents
- [ ] Cash in destination currency
- [ ] Phone with eSIM/international plan
- [ ] Copies of ALL important documents (digital + paper)
- [ ] First week accommodation confirmation
- [ ] Emergency contacts in destination
- [ ] Prescription medications + doctor letter

## Security & Privacy

**Data that stays local:**
- All personal documents and notes in ~/expat/
- No external services or APIs used

**This skill does NOT:**
- Store passport numbers or sensitive data in plain text
- Access files outside ~/expat/
- Share any information externally

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `travel` — trip planning and packing
- `money` — budgeting and finance tracking
- `projects` — complex project management

## Feedback

- If useful: `clawhub star expat`
- Stay updated: `clawhub sync`
