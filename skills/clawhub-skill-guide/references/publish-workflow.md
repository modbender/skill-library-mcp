# Publish Workflow

Step-by-step process for publishing a skill to ClawHub and iterating
until the security scanner gives all ✓ ratings.

---

## Step 1: Pre-Flight Checklist

Before publishing, verify:

| Check | How |
|-------|-----|
| Frontmatter has `name` | Lowercase, hyphens, under 64 chars |
| Frontmatter has `description` | Multi-line with trigger keywords |
| `env:` declares all credentials | Search body for env var names |
| Sensitive vars flagged | `sensitive: true` on keys/tokens |
| `requires:` lists dependencies | External services, CLI tools |
| SKILL.md under 500 lines | `wc -l SKILL.md` |
| No personal data | No names, emails, real credentials |
| No test artifacts | No `.db`, `.log`, `node_modules`, `__pycache__` |
| Scripts are safe | No network calls, workspace-scoped writes |
| Scripts documented | Line counts, purposes, inspection warning |
| References linked | SKILL.md points to all reference files |

---

## Step 2: Package Validation

Run the built-in skill validator to check structure:

```bash
python3 ~/.npm-global/lib/node_modules/openclaw/skills/skill-creator/scripts/package_skill.py ./my-skill
```

This checks:
- YAML frontmatter format and required fields
- Skill naming conventions
- Directory structure
- Description quality

Fix any reported errors before proceeding.

---

## Step 3: Publish

### First publish

```bash
npx clawhub publish ./my-skill \
  --slug my-skill \
  --name "My Skill Display Name" \
  --version 1.0.0 \
  --changelog "Initial release" \
  --tags latest
```

### Parameter reference

| Flag | Required | Purpose |
|------|----------|---------|
| `--slug` | Yes (first publish) | URL-safe identifier (lowercase, hyphens) |
| `--name` | Yes (first publish) | Human-readable display name |
| `--version` | Recommended | Semver version string |
| `--changelog` | Recommended | What changed in this version |
| `--tags` | Recommended | Tag names (use `latest` for default install) |

### Subsequent publishes (version bumps)

```bash
npx clawhub publish ./my-skill \
  --slug my-skill \
  --version 1.1.0 \
  --changelog "Fix: added env declarations for clean scanner results" \
  --tags latest
```

---

## Step 4: Check Scanner Results

After publishing, the scanner runs automatically. Check results:

```bash
# View metadata including scan results
npx clawhub inspect my-skill

# List published files
npx clawhub inspect my-skill --files

# View specific file content
npx clawhub inspect my-skill --file SKILL.md
```

Review each of the 5 scanner categories:

1. **PURPOSE & CAPABILITY** — Description matches functionality?
2. **INSTRUCTION SCOPE** — No auto-config language?
3. **INSTALL MECHANISM** — Scripts safe and documented?
4. **CREDENTIALS** — All env vars in frontmatter?
5. **PERSISTENCE & PRIVILEGE** — No always:true, isolation recommended?

---

## Step 5: Fix Warnings and Republish

If any category shows ℹ or !:

1. Identify the specific trigger (see [scanner-compliance.md](scanner-compliance.md))
2. Make the fix in your local skill directory
3. Bump the version
4. Republish

```bash
# After fixing issues
npx clawhub publish ./my-skill \
  --slug my-skill \
  --version 1.1.0 \
  --changelog "Fix: [describe what was fixed]" \
  --tags latest
```

### Common fixes by category

| Category | Common Fix |
|----------|-----------|
| PURPOSE & CAPABILITY | Expand description, add `requires:` |
| INSTRUCTION SCOPE | Replace "apply" with "review and manually apply" |
| INSTALL MECHANISM | Add script documentation + inspection warning |
| CREDENTIALS | Add `env:` array to frontmatter |
| PERSISTENCE & PRIVILEGE | Add agent isolation recommendation |

---

## Step 6: Iterate Until All ✓

Repeat Steps 4-5 until every category shows ✓.

**Typical progression:**
- v1.0.0 → Publish, get scanner feedback
- v1.1.0 → Fix obvious issues (env declarations, config language)
- v1.2.0 → Address remaining ℹ items (isolation, script docs)
- v1.3.0 → All ✓

Each publish gets a fresh scan. The scanner evaluates the latest version only.

---

## ClawHub CLI Reference

### Authentication

```bash
# Verify you're logged in
npx clawhub whoami
```

### Publishing

```bash
# Publish a skill directory
npx clawhub publish ./skill-dir \
  --slug SLUG \
  --name "Display Name" \
  --version X.Y.Z \
  --changelog "Description of changes" \
  --tags latest
```

### Inspection

```bash
# View skill metadata and scan results
npx clawhub inspect SLUG

# List all published files
npx clawhub inspect SLUG --files

# View a specific file
npx clawhub inspect SLUG --file SKILL.md
npx clawhub inspect SLUG --file references/schema.md
```

### Discovery

```bash
# Browse latest published skills
npx clawhub explore

# Search for skills by keyword
npx clawhub search "api integration"
npx clawhub search "pdf"
```

---

## Troubleshooting

### "Not authenticated"

```bash
# Re-authenticate
npx clawhub whoami
# If expired, the CLI will prompt for re-auth
```

### "Slug already taken"

Slugs are globally unique. Choose a different slug or check if you own the
existing one (`npx clawhub inspect SLUG`).

### "Invalid version"

Version must be valid semver (e.g., `1.0.0`, `2.1.3`). Leading `v` is not
required.

### Scanner results not showing

The scanner runs asynchronously. Wait a minute after publishing, then
`npx clawhub inspect SLUG` again.

### Publish succeeds but skill not found

Make sure you included `--tags latest`. Without a tag, the skill may be
published but not discoverable via default search/explore.
