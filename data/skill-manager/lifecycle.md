# Skill Lifecycle Management

Reference — installation, updates, and cleanup.

## Installation

When user consents to install:

```bash
npx clawhub install <slug>
```

Then add to inventory:
```markdown
## Installed
- slug@1.0.0 — "purpose" — 2026-02-16
```

## Checking Updates

To check if skill has updates:

```bash
npx clawhub info <slug>
```

Compare version with inventory. If newer available:
> "skill-name has an update (v1.0.0 → v1.1.0). Update?"

## Updating

When user consents:

```bash
npx clawhub update <slug>
```

Update version in inventory.

## Removal

When user asks to remove:

```bash
npx clawhub uninstall <slug>
```

Remove from inventory.

## Periodic Audit

When user asks "what skills do I have?" or "cleanup skills":

1. List installed from inventory
2. For each: "Still using [slug] for [purpose]?"
3. User says no → offer to remove
4. User says yes → keep

## Inventory Format

```markdown
# Skill Manager Inventory

## Installed
- github@1.2.0 — "PR workflows" — 2026-01-15
- stripe@1.0.0 — "payment integration" — 2026-02-01

## Declined
- jira — "don't use Jira"
```

## Rules

- Always get consent before install/update/remove
- Track purpose so audit makes sense
- Keep inventory current
- Don't auto-remove anything
