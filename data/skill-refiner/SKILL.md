---
name: skill-refiner
description: Audit and fix all skills in the workspace for compliance with skill-creator requirements. Use when asked to "refine skills", "audit skills", "check skill quality", or "fix non-compliant skills". Exhaustively searches the entire workspace (not just skills/) to find every SKILL.md, then audits and repairs each one.
---

# Skill Refiner

Finds every skill in the workspace, audits each against skill-creator requirements, and fixes non-compliant ones.

## Workflow

### Step 1 — Discover all skills

```bash
bash scripts/find_skills.sh [workspace_dir]
```

This searches the **entire workspace** for `SKILL.md` files (not just `skills/`). Skills created without following skill-creator conventions may end up anywhere.

### Step 2 — Audit each skill

```bash
python3 scripts/audit_skill.py <skill-dir>
```

Returns JSON with:
- `issues` — blocking problems that must be fixed
- `warnings` — advisory improvements
- `compliant` — true only when issues is empty

Run this on every path returned by Step 1. Batch example:

```bash
bash scripts/find_skills.sh | while read dir; do
  python3 scripts/audit_skill.py "$dir"
done
```

### Step 3 — Report findings

Summarize results in a table:

| Skill | Location | Issues | Warnings | Status |
|-------|----------|--------|----------|--------|
| my-skill | skills/my-skill | 0 | 1 | ⚠️ |
| bad-skill | temp/bad-skill | 2 | 0 | ❌ |

### Step 4 — Fix non-compliant skills

For each skill with issues, fix in this order:

1. **Missing/malformed frontmatter** — Add or correct the `---` block with `name` and `description` only
2. **Extra frontmatter fields** — Remove any fields other than `name` and `description`
3. **Weak description** — Rewrite to include: what the skill does + trigger conditions ("Use when...")
4. **Extraneous files** — Delete README.md, INSTALLATION_GUIDE.md, CHANGELOG.md, etc.
5. **Wrong location** — If a skill is outside `skills/`, move it to `~/.openclaw/workspace/skills/<skill-name>/`
6. **Naming violations** — Rename directory to lowercase-hyphen-case

For warnings (advisory):
- Long SKILL.md (>500 lines): extract detailed content into `references/` files and link from SKILL.md
- Unlinked references: add links in SKILL.md body
- Weak description: improve trigger language

### Step 5 — Validate fixes

Re-run `audit_skill.py` on each fixed skill to confirm `"compliant": true`.

Optionally package with:
```bash
python3 /opt/homebrew/lib/node_modules/openclaw/skills/skill-creator/scripts/package_skill.py <skill-dir>
```

## Compliance Checklist

A compliant skill must have:
- [ ] `SKILL.md` at the root of a named directory
- [ ] YAML frontmatter with exactly `name` and `description` (no other fields)
- [ ] `description` includes what the skill does AND when to trigger it
- [ ] Directory name: lowercase letters, digits, hyphens only; ≤64 chars
- [ ] No extraneous files (README.md, CHANGELOG.md, etc.)
- [ ] Resources only in `scripts/`, `references/`, or `assets/`
- [ ] All `references/` files linked from SKILL.md body
- [ ] SKILL.md body ≤500 lines (split into references/ if longer)
