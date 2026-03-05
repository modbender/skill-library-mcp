# Lessons Update Guide

This guide explains how to capture, review, and sync lessons from your workspace into the skill repository.

## Lesson Capture Workflow

### 1. Capture During Work
When you make a mistake or receive a correction:
- Document it immediately in `tasks/lessons.md` in your workspace
- Format: Simple markdown with clear pattern/rule
- Example:
  ```markdown
  ## Always Read API Docs First
  - **Pattern:** Assumed API behavior without checking docs
  - **Lesson:** Read documentation before writing code
  - **Why:** Saves debugging time, prevents wrong approach
  - **Applied to:** Project X authentication issue
  ```

### 2. Review & Refine
Periodically review `tasks/lessons.md`:
- Keep lessons concise and actionable
- Remove outdated or superceded lessons
- Group related lessons under themes

### 3. Sync to Skill Repository
When lessons are stable and reusable across projects:

```bash
# Navigate to skill repo
cd /Volumes/Transcend/GitHub/openclaw-workflow

# Preview changes (dry run)
python3 scripts/sync_lessons.py --workspace ~/.openclaw/workspace --dry-run

# Apply sync
python3 scripts/sync_lessons.py --workspace ~/.openclaw/workspace

# Commit to git
git add references/lessons.md
git commit -m "Update lessons: [description of new lessons]"
git push origin main
```

### 4. Share & Reuse
Once synced and pushed:
- Lessons are version-controlled on GitHub
- Can be shared with other instances of the skill
- Builds a permanent knowledge base of learned patterns

## File Structure

### Workspace (Working Copy)
```
~/.openclaw/workspace/
├── tasks/lessons.md          (raw lessons, frequently updated)
└── memory/YYYY-MM-DD.md      (daily notes that feed into lessons)
```

### Skill Repository (Published)
```
openclaw-workflow/
├── references/lessons.md     (curated, version-controlled)
└── scripts/sync_lessons.py   (automation tool)
```

## Sync Script Details

### What It Does
1. Reads `tasks/lessons.md` from workspace
2. Extracts lessons section (skips philosophy intro)
3. Merges into skill's `references/lessons.md`
4. Preserves philosophy/framing
5. Adds timestamp of last update

### Options
- `--workspace <path>` — Path to workspace (default: ~/.openclaw/workspace)
- `--dry-run` — Preview changes without modifying files

### Example Usage

```bash
# Standard sync
python3 scripts/sync_lessons.py

# Custom workspace
python3 scripts/sync_lessons.py --workspace /path/to/workspace

# Preview before committing
python3 scripts/sync_lessons.py --dry-run
```

## Lesson Format (Best Practices)

Good lessons follow this pattern:

```markdown
## [Rule or Pattern Name]
- **Pattern:** What behavior or situation triggered this lesson
- **Lesson:** What you learned (the actionable insight)
- **Why:** Explanation of why this matters
- **Applied to:** Examples or projects where you used it
```

Example:

```markdown
## Never Skip Testing Edge Cases
- **Pattern:** Wrote API integration without testing rate limiting
- **Lesson:** Always test edge cases: empty inputs, rate limits, errors
- **Why:** 90% of bugs happen at boundaries, not in happy path
- **Applied to:** Binance API integration, paper trading bot
```

## Maintenance Schedule

### Weekly
- Review recent entries in `tasks/lessons.md`
- Clean up duplicates or outdated lessons
- Mark lessons ready for sync

### Monthly
- Run sync script to push curated lessons to skill repo
- Review git history of lessons.md for patterns
- Update references as needed

### Quarterly
- Review all lessons in skill repository
- Consolidate related lessons
- Update SKILL.md if lessons reveal new patterns

## Integration with Workflow

This lesson system integrates with the 6 core disciplines:

1. **Plan Node Default** → Prevents repeating planning mistakes
2. **Subagent Strategy** → Documents subagent coordination patterns
3. **Self-Improvement Loop** → *This is the core mechanism*
4. **Verification Before Done** → Captures verification gaps
5. **Demand Elegance** → Documents refactoring/simplification lessons
6. **Autonomous Bug Fixing** → Records bug patterns and fixes

Each lesson improves future work by preventing repeated mistakes.
