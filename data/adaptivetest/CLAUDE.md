# CLAUDE.md -- AdaptiveTest Skill

> **Purpose:** Spec-only repo for the AdaptiveTest OpenClaw skill. Contains the skill file, API reference docs, and specs for backend/marketing work in other repos.
> **Owner:** James Williams - Woodstock Software LLC
> **GitHub Org:** https://github.com/woodstocksoftware

---

## What This Repo Contains

1. **SKILL.md** -- The OpenClaw skill file published to ClawHub
2. **references/** -- Detailed API docs and guides injected as skill context
3. **specs/** -- Specs for work in other repos:
   - `CONTENT.md` -- Product copy for ClawHub listing and landing page
   - `REQUIREMENTS.md` -- Usage tiers, purchase flow, API key management
   - `DATA-MODEL.md` -- New `src/apikeys/` module for `adaptivetest-platform`
   - `DESIGN-SYSTEM.md` -- Design tokens for `/developers` landing page
   - `PAGES.md` -- `/developers` page structure for `adaptivetest-marketing`
   - `SITE-ARCHITECTURE.md` -- Route and config changes for marketing site

## What This Repo Does NOT Contain

No application code. No tests. No CI. This is a spec and skill distribution repo.

---

## Cross-Repo Dependencies

| Repo | What It Builds From These Specs |
|------|------|
| `adaptivetest-platform` | `specs/DATA-MODEL.md` -- new `src/apikeys/` module, Stripe webhooks, dual auth middleware |
| `adaptivetest-marketing` | `specs/DESIGN-SYSTEM.md`, `specs/PAGES.md`, `specs/SITE-ARCHITECTURE.md` -- new `/developers` landing page |

---

## Branching Policy

Non-production repo. Direct to main.

---

## Content Rules

- Say "FERPA-aligned" not "FERPA compliant"
- No SOC 2 claims
- "AdaptiveTest" one word, capital A and T
- Developer-facing tone: technical, direct, no marketing fluff in API docs
- Marketing-facing tone: professional, capability-focused on landing page
