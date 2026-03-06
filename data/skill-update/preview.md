# Preview Changes

How to analyze updates before applying.

## Fetching New Version

```bash
# Download without installing
npx clawhub fetch <slug>@<version> --dir /tmp/preview-<slug>
```

Compare against current:
```bash
diff -r ~/.clawhub/skills/<slug> /tmp/preview-<slug>
```

## Change Categories

### Additions (usually safe)
- New auxiliary files
- New features in SKILL.md
- New templates or examples

**User impact:** Minimal. New capabilities, existing workflows intact.

### Modifications (review carefully)
- Changed instructions
- Updated references
- Different approaches

**User impact:** Behavior may change. Check if user relies on old behavior.

### Deletions (⚠️ breaking)
- Removed files
- Removed sections
- Removed features

**User impact:** High. Workflows depending on removed content will break.

### Structural changes (⚠️ breaking)
- Renamed files
- Moved content between files
- Changed folder organization

**User impact:** High. References, muscle memory, and automations break.

## Generating Impact Report

For each change, answer:
1. What exactly changed?
2. Does user currently use this?
3. Will their workflow break?
4. Is migration needed?

## Presenting to User

**Format:**
```
## Update Preview: skill-name v1.2.3 → v2.0.0

### ⚠️ Breaking Changes
- `config.md` renamed to `settings.md`
- Section "Quick Deploy" removed

### Modifications
- New approach for authentication
- Updated examples

### Additions
- `templates/` folder with 5 templates
- Troubleshooting section

### Migration Required
- Your preferences in old config.md need to move to settings.md
```

## When to Recommend Update

✅ **Recommend:** Bug fixes, security patches, minor improvements
⚠️ **Cautious:** New major version, structural changes
❌ **Defer:** If user has active work depending on current behavior
