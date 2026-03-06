---
name: clawhub-web-only-publish
description: Publish skills to ClawHub via web dashboard only. No CLI login, no device flow. Reuse existing browser session.
---

# ClawHub Web-Only Publish

Publish to ClawHub via web dashboard. No CLI login.

## Problem

CLI login causes:
- Auth loop failures
- Token expiration issues
- Device flow complexity
- Session management overhead

## Workflow

### 1. Prerequisites

- Browser already logged in to https://clawhub.ai
- Skill folder contains SKILL.md
- No secrets in skill files

### 2. Web Publish Steps

1. Navigate to https://clawhub.ai/upload
2. Verify logged in (username visible)
3. Fill form:
   - Slug: `skill-name`
   - Display name: `Skill Name`
   - Version: `1.0.0`
4. Click "Choose folder" -> Select skill directory
5. Wait for validation (SKILL.md recognized)
6. (Optional) Add changelog
7. Click "Publish skill"
8. Capture result URL

### 3. Fallback (No CLI Login)

If browser upload fails:
- Use existing CLI token (if already authenticated)
- Run: `clawhub publish <path> --version 1.0.0`
- Do NOT run `clawhub login`

## Executable Completion Criteria

| Criteria | Verification |
|----------|-------------|
| Skill URL accessible | Navigate to URL, 200 OK |
| Name matches SKILL.md | Frontmatter name = listing name |
| Version correct | URL shows v1.0.0 |
| No CLI login used | No `clawhub login` in history |

## Privacy/Safety

- No credentials in skill files
- Scan for apiKey/token/secret before publish
- Use relative paths only

## Self-Use Trigger

Use when:
- Publishing any skill to ClawHub
- CLI login fails or unavailable
- Browser session already active

---

**Web first. No login loops.**
