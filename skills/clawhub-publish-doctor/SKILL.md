---
name: clawhub-publish-doctor
description: Diagnose and mitigate ClawHub/ClawDHUB publish failures (auth, browser-login, missing dependencies, pending security-scan visibility errors, and wrong profile/skill URLs). Use when publishing skills to ClawHub fails, inspect reports temporary errors, or you need a safer publish+verify workflow with retries.
---

# ClawHub Publish Doctor

Stabilize ClawHub publishing with preflight checks, safer publish commands, and post-publish verification that tolerates temporary registry states.

## Quick workflow

1. Run preflight checks:
   - `scripts/clawhub_preflight.sh`
2. If login/browser issues appear, follow `references/error-map.md`.
3. Publish with retry-aware verification:
   - `scripts/clawhub_publish_safe.sh <skill_path> <slug> <name> <version> [changelog]`
4. If inspect still fails, classify the error with `references/error-map.md` before escalating.

## Standard commands

### Preflight

```bash
bash scripts/clawhub_preflight.sh
```

### Login (token-based, headless-safe)

```bash
clawhub login --token <clh_token>
clawhub whoami
```

### Safe publish

```bash
bash scripts/clawhub_publish_safe.sh ./my-skill my-skill "My Skill" 1.0.0 "Initial release"
```

### Manual inspect

```bash
clawhub inspect my-skill --json
```

## Rules

- Prefer token login in server/headless environments.
- Treat `inspect` errors right after publish as potentially transient for a few minutes.
- Verify with both CLI (`clawhub inspect`) and web URL (`/skills/<slug>`).
- Use canonical URLs:
  - Skill: `https://clawhub.ai/skills/<slug>`
  - Owner/slug: `https://clawhub.ai/<handle>/<slug>`
  - User profile (if available): `https://clawhub.ai/users/<handle>`

## Resources

- `references/error-map.md`: quick diagnosis for common failure signatures.
- `scripts/clawhub_preflight.sh`: dependency + environment checks.
- `scripts/clawhub_publish_safe.sh`: publish + retry verification wrapper.
