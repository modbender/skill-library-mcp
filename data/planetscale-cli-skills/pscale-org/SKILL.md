---
name: pscale-org
description: List, show, and switch PlanetScale organizations. Use when managing multiple organizations, switching between accounts, viewing organization details, or troubleshooting organization access. Triggers on org, organization, switch org, list orgs.
---

# pscale org

List, show, and switch organizations.

## Common Commands

```bash
# List all organizations
pscale org list

# Show current organization
pscale org show

# Switch organization
pscale org switch <org-name>
```

## Workflows

### Switch Between Organizations

```bash
# View current org
pscale org show

# List available orgs
pscale org list

# Switch to different org
pscale org switch my-other-org

# Verify switch
pscale database list --org my-other-org
```

## Troubleshooting

### Cannot see expected databases

**Solution:** Check current organization

```bash
pscale org show
pscale org switch <correct-org>
```

## Related Skills

- **pscale-auth** - Authentication and account management
- **pscale-database** - Organization-scoped database operations

## References

See `references/commands.md` for complete command reference.
