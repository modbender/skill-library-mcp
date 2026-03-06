# Remediation Actions

## Security Issues

### Secrets in plaintext
**Detection:** `grep -r "password\|api_key\|token" --include="*.env" --include="*.md"`
**Remediation:**
1. Rotate the exposed credential immediately
2. Move to Keychain: `security add-generic-password -a clawdbot -s NAME -w "VALUE"`
3. Update references to use `security find-generic-password`
4. Check git history: `git log -p -- <file>` — if committed, consider force push or repo recreation
**Auto-fixable:** No (requires credential rotation)

### SSH key permissions too open
**Detection:** `stat -f "%Lp" ~/.ssh/*`
**Remediation:** `chmod 600 ~/.ssh/id_*`
**Auto-fixable:** Yes

### Secrets committed to git
**Detection:** `git log -p | grep -i "password\|token\|api_key"`
**Remediation:** 
1. Rotate credential
2. Use `git filter-branch` or BFG Repo-Cleaner
3. Force push
**Auto-fixable:** No (requires careful manual intervention)

---

## Operational Issues

### Gateway not running
**Detection:** `pgrep -f openclaw` or `openclaw gateway status`
**Remediation:** `openclaw gateway start`
**Auto-fixable:** Yes

### Zombie subagent sessions
**Detection:** Check `sessions_list` for spawn sessions >24h old without completion
**Remediation:** Note the pattern, potentially kill stale sessions
**Auto-fixable:** Partially (can list, killing needs judgment)

### Cron job failures
**Detection:** Check cron run history via `cron action=runs`
**Remediation:** Fix the failing job's payload or schedule
**Auto-fixable:** No (depends on failure type)

### Memory bloat
**Detection:** `du -sh memory/` or count lines in daily files
**Remediation:** 
1. Consolidate old daily files into MEMORY.md
2. Archive or delete files >30 days old
3. Remove duplicate entries
**Auto-fixable:** Partially (can identify, consolidation needs review)

---

## Hygiene Issues

### BOARD.md bloat
**Detection:** `wc -l BOARD.md` > 100 with many ✅ items
**Remediation:** Archive completed items, keep only active
**Auto-fixable:** Yes (move ✅ older than 7 days to archive)

### Orphaned memory files
**Detection:** Compare `ls memory/*.md` vs entries in `memory/INDEX.md`
**Remediation:** Either add to INDEX.md or delete if obsolete
**Auto-fixable:** Partially (can identify, decision needs judgment)

### Redundant skill triggers
**Detection:** Extract triggers from all SKILL.md files, find overlaps
**Remediation:** Refine triggers to be more specific, or merge skills
**Auto-fixable:** No (architectural decision)

### Stale BACKLOG entries
**Detection:** 📋 or 🔄 items >7 days old
**Remediation:** Review and either complete, delegate, or mark ⏸️
**Auto-fixable:** No (requires task evaluation)

---

## Auto-Fix Script Templates

### Fix SSH permissions
```bash
find ~/.ssh -type f -name "id_*" ! -name "*.pub" -exec chmod 600 {} \;
find ~/.ssh -type f -name "*.pub" -exec chmod 644 {} \;
chmod 700 ~/.ssh
```

### Clean old memory files
```bash
# Archive files older than 30 days
mkdir -p memory/archive
find memory/ -maxdepth 1 -name "202*.md" -mtime +30 -exec mv {} memory/archive/ \;
```

### Restart gateway
```bash
openclaw gateway restart
```

### Kill browser zombie sessions
```bash
# List and close idle browser sessions
browser action=tabs profile=openclaw
# Then close each stale tab
browser action=close targetId=<id>
```
