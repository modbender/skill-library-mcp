# Migration Strategies

How to handle data and state migrations during updates.

## What Needs Migration

Skills may store:
- **Preferences** — User settings in SKILL.md sections
- **State files** — Saved data in skill folder
- **External references** — Paths, URLs, configurations
- **Learned patterns** — Auto-adaptive skills with accumulated knowledge

## Migration Patterns

### Pattern 1: File Rename

Old: `config.md` → New: `settings.md`

```
1. Read content from old file
2. Show user the content: "These preferences will move"
3. Write to new location
4. Verify content matches
5. Remove old file (or keep as backup)
```

### Pattern 2: Structure Change

Old format:
```
## Preferences
- theme: dark
- lang: es
```

New format:
```
## User Settings
theme: dark
language: es
notifications: true  # new field
```

```
1. Parse old format
2. Map to new format
3. Add defaults for new fields
4. Show user: "These settings will migrate, new options added"
5. Apply with confirmation
```

### Pattern 3: Folder Reorganization

Old: `skill/data/` → New: `skill/storage/data/`

```
1. Identify all files in old location
2. Create new folder structure
3. Move files preserving names
4. Update any internal references
5. Remove empty old folders
```

### Pattern 4: Auto-Adaptive Skill

Old learned preferences → New preference format

```
1. Export current preferences (JSON or structured)
2. Map to new schema
3. Import into new version
4. Verify preferences still work
5. Run test to confirm behavior matches
```

## Migration Script Template

```markdown
## Migrating skill-name v1 → v2

**What's moving:**
- Preferences from `old.md` → `new.md`
- Data folder from `/data` → `/storage`

**New defaults added:**
- `feature_x: enabled`
- `timeout: 30s`

**Steps:**
1. Backup current state ✓
2. Copy preferences [waiting approval]
3. Move data files [waiting approval]
4. Update references [waiting approval]
5. Verify [after migration]

**Proceed with migration?**
```

## Handling Failures

If migration fails mid-way:
1. Stop immediately
2. Report what succeeded and what failed
3. Offer to restore from backup
4. Do NOT leave in partial state

## Verification

After migration:
1. Check all files exist in new locations
2. Verify content is readable
3. Run a simple test with the skill
4. Ask user to confirm everything works

Only delete backups after user confirms success.
