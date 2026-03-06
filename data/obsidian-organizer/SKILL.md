---
name: obsidian-organizer
description: Organize and standardize Obsidian vaults for reliability and long-term maintainability. Use when designing or cleaning vault folder structure, enforcing file naming conventions, migrating messy vaults, reducing duplicate/ambiguous notes, or creating repeatable audit-and-fix workflows for Obsidian notes.
---

# Obsidian Organizer

Use this skill to make a vault predictable, searchable, and low-maintenance.

## Workflow

1. Snapshot current state
   - Count files and top-level folders.
   - Identify naming drift and duplicate patterns.

2. Apply standard structure
   - Read `references/folder-structure.md`.
   - Propose moves before applying.

3. Enforce naming rules
   - Read `references/naming-rules.md`.
   - Run audit script in dry-run mode:
     - `python scripts/obsidian_audit.py <vault-path>`
   - Apply only after confirmation:
     - `python scripts/obsidian_audit.py <vault-path> --apply`

4. Run migration checklist
   - Follow `references/migration-checklist.md` in order.

5. Verify
   - Re-run audit until zero naming issues.
   - Confirm daily notes use `YYYY-MM-DD.md`.
   - Confirm no orphaned notes remain in `inbox/`.

## Guardrails

- Never rename or move files without a dry-run first.
- Never delete notes automatically.
- Prefer deterministic naming over clever naming.
- Keep folder depth shallow (<=3 when possible).
- If link integrity is uncertain, pause and ask before bulk apply.
