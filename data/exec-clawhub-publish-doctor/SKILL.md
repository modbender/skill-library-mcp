---
name: exec-clawhub-publish-doctor
description: "Diagnose and mitigate exec-related tooling failures around ClawHub publishing and GitHub CLI queries (auth, browser-login, missing dependencies, pending security-scan visibility errors, wrong profile/skill URLs, and gh JSON-field mismatch errors like Unknown JSON field). Use when publishing skills to ClawHub fails, inspect reports temporary errors, or GitHub CLI search commands fail due to field schema differences."
---

# Exec ClawHub Publish Doctor

Stabilize ClawHub publishing with preflight checks, safer publish commands, and post-publish verification that tolerates temporary registry states.

## Quick workflow

1. Run preflight checks:
   - `scripts/clawhub_preflight.sh`
2. If login/browser issues appear, follow `references/error-map.md`.
3. Publish with retry-aware verification:
   - `scripts/clawhub_publish_safe.sh <skill_path> <slug> <name> <version> [changelog]`
4. For GitHub search failures like `Unknown JSON field`, use:
   - `scripts/gh_search_repos_safe.sh "<query>" [limit]`
5. If errors persist, classify with `references/error-map.md` before escalating.

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

### Safe GitHub repo search (schema-aware)

```bash
bash scripts/gh_search_repos_safe.sh "safe-exec skill" 15
```

## Rules

- Prefer token login in server/headless environments.
- Treat `inspect` errors right after publish as potentially transient for a few minutes.
- Verify with both CLI (`clawhub inspect`) and web URL (`/skills/<slug>`).
- For `gh search repos --json` failures, prefer `fullName` over unsupported aliases like `nameWithOwner`, or run `scripts/gh_search_repos_safe.sh`.
- Use canonical URLs:
  - Skill: `https://clawhub.ai/skills/<slug>`
  - Owner/slug: `https://clawhub.ai/<handle>/<slug>`
  - User profile (if available): `https://clawhub.ai/users/<handle>`

## Resources

- `references/error-map.md`: quick diagnosis for common failure signatures.
- `scripts/clawhub_preflight.sh`: dependency + environment checks.
- `scripts/clawhub_publish_safe.sh`: publish + retry verification wrapper.
- `scripts/gh_search_repos_safe.sh`: resilient `gh search repos` wrapper with JSON-field mismatch fallback.
