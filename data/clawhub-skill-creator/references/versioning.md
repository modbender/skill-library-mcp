# Versioning Best Practices

## Semantic Versioning

Format: `MAJOR.MINOR.PATCH`

| Version | Change Type | Example |
|---------|-------------|---------|
| 1.0.0 → 1.0.1 | Patch: bug fixes | Fix typo, correct command |
| 1.0.0 → 1.1.0 | Minor: new features | Add reference, new pattern |
| 1.0.0 → 2.0.0 | Major: breaking changes | Rename skill, remove features |

## Critical Rule

**Never downgrade version.**

❌ **Wrong:**
```
1.1.0 → 1.0.2  (downgrade!)
```

✅ **Correct:**
```
1.1.0 → 1.1.1  (patch)
1.1.0 → 1.2.0  (minor)
```

## Before Publishing

Always check current version:

```bash
clawhub inspect skill-name --json | grep version
```

Or check registry:
```bash
clawhub list | grep skill-name
```

## Changelog Guidelines

Good changelog entries:

```
"Add cross-platform command examples"
"Fix: correct CMake integration syntax"
"Update: optimize token usage in SKILL.md"
"Breaking: rename env var ZVUKOGRAM_TOKEN → ZVUK_API_TOKEN"
```

## Common Mistakes

### 1. Version Confusion

Problem: Local `_meta.json` says 1.0.0, registry has 1.1.0.

Solution: Always check registry before publishing.

### 2. Skip Versions

Problem: Jump from 1.0.0 to 1.2.0 without 1.1.0.

Solution: Use sequential versions unless intentional.

### 3. Patch as Minor

Problem: Bug fix published as minor (1.0.0 → 1.1.0).

Solution: Bug fixes = patch, features = minor.

## Version Check Script

```bash
#!/bin/bash
SKILL=$1
CURRENT=$(clawhub inspect $SKILL --json 2>/dev/null | jq -r '.latestVersion.version')
LOCAL=$(jq -r '.version' _meta.json)

echo "Registry: $CURRENT"
echo "Local:    $LOCAL"

if [ "$LOCAL" = "$CURRENT" ]; then
    echo "ERROR: Version not bumped!"
    exit 1
fi

echo "OK: Version updated"
```

## Post-Publish Verification

After publishing:

```bash
# Verify published
clawhub inspect skill-name

# Check version correct
clawhub list | grep skill-name

# Test install (optional)
clawhub install skill-name --dry-run
```