# CLAUDE.md -- AdaptiveTest Skill

> **Purpose:** Public repo for the AdaptiveTest OpenClaw skill. Contains the skill file, API reference docs, and ClawHub metadata.
> **Owner:** James Williams - Woodstock Software LLC
> **GitHub Org:** https://github.com/woodstocksoftware

---

## What This Repo Contains

1. **SKILL.md** -- The OpenClaw skill file published to ClawHub
2. **references/** -- Detailed API docs and guides injected as skill context
3. **clawhub.json** -- ClawHub manifest (metadata, tags, pricing URL)

Implementation specs live in the private `adaptivetest-specs` repo.

## What This Repo Does NOT Contain

No application code, no tests, no CI, no server-side specs or credentials.

---

## Cross-Repo Dependencies

| Repo | Role |
|------|------|
| `adaptivetest-specs` (private) | Implementation specs for platform and marketing repos |
| `adaptivetest-platform` | API key management module (`src/apikeys/`) |
| `adaptivetest-marketing` | `/developers` landing page |

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
