# System Guide — Agent Quick Reference

_This is a navigation index for agents. For full system documentation, see the references/ directory in the social-media-ops skill._

---

## Design Principles

- **Star topology**: All inter-agent communication routes through the Leader.
- **Human-in-the-loop**: Nothing publishes without explicit owner approval.
- **Brand isolation**: Each brand has its own channel topic, asset directory, and content guidelines.
- **Signal-driven**: Agents communicate status via standardized signal tags.
- **Shared knowledge**: A single shared KB is symlinked into every agent workspace.

## Instance Configuration

> `shared/INSTANCE.md` — Owner info, platform, language settings, communication mode

## Team & Routing

> `workspace/AGENTS.md` — Agent capabilities, input/output specs, timeout defaults

## Brands

> `shared/brand-registry.md` — All brands with IDs, names, channels, status
> `shared/brands/{brand_id}/profile.md` — Brand identity, voice, audience
> `shared/brands/{brand_id}/content-guidelines.md` — Platform content rules
> `shared/domain/{brand_id}-industry.md` — Industry knowledge

### Brand Templates (for new brands)

> `shared/brands/_template/profile.md`
> `shared/brands/_template/content-guidelines.md`
> `shared/domain/_template/industry.md`

## Operations

> `shared/operations/channel-map.md` — Platform channels and topic routing
> `shared/operations/posting-schedule.md` — Per-brand posting cadence
> `shared/operations/content-guidelines.md` — Cross-brand content rules
> `shared/operations/approval-workflow.md` — Approval pipeline and shortcuts
> `shared/operations/communication-signals.md` — Signal vocabulary

## Cross-Brand Rules

> `shared/brand-guide.md` — Universal brand rules, language policy, emoji policy
> `shared/compliance-guide.md` — Regulatory requirements by market

## Error Reference

> `shared/errors/solutions.md` — Known issues and fixes

## Directory Structure

```
shared/
├── INSTANCE.md              # This deployment's configuration
├── brand-registry.md        # Brand single source of truth
├── brand-guide.md           # Cross-brand rules
├── system-guide.md          # This file
├── compliance-guide.md      # Regulatory requirements
├── brands/
│   ├── _template/           # Templates for new brands
│   └── {brand_id}/          # Per-brand profile + guidelines
├── domain/
│   ├── _template/           # Template for new domain files
│   └── {brand_id}-industry.md
├── operations/
│   ├── channel-map.md
│   ├── posting-schedule.md
│   ├── content-guidelines.md
│   ├── approval-workflow.md
│   └── communication-signals.md
└── errors/
    └── solutions.md
```
