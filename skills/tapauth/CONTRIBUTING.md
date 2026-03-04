# Contributing to TapAuth Agent Skill

## Source of Truth

The **monorepo** (`tapauth/tapauth` → `packages/skill/`) is the source of truth for provider reference docs. This public repo (`tapauth/tapauth-skill`) is the published distribution.

## Syncing Changes

When provider docs are added or updated in the monorepo:

1. Copy updated files from `packages/skill/references/` to `tapauth-skill/references/`
2. Update the provider list in `SKILL.md` and `README.md` if a new provider was added
3. **Open a PR** — never push directly to main. All changes go through pull requests with review.

```bash
# Example: sync all provider docs
cp ~/tapauth/packages/skill/references/*.md ~/tapauth-skill/references/

# Check for new providers in production
# Compare keys in apps/web/src/lib/providers.ts with references/ directory
```

## Publishing to ClawHub

After pushing changes:

```bash
clawhub publish /path/to/tapauth-skill/ \
  --slug tapauth \
  --name "TapAuth" \
  --version <new-version> \
  --changelog "Description of changes"
```

## Git Identity

Use the bot identity for commits:

```
git config user.name "TapAuth[bot]"
git config user.email "2825152+TapAuth[bot]@users.noreply.github.com"
```

## Checklist for Updates

- [ ] All providers in `apps/web/src/lib/providers.ts` have a reference doc
- [ ] SKILL.md provider list matches `references/` directory
- [ ] README.md provider table matches `references/` directory
- [ ] All URLs use `tapauth.ai` (not `tapauth.com`)
- [ ] Version bumped in `clawhub publish` command
