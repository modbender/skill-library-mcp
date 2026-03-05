# Workspace Maintenance Checklist

Run weekly during a heartbeat cycle.

## 1. Consolidate Daily Logs (10 min)

Read the last 7 days of `memory/YYYY-MM-DD.md`:

- [ ] Extract infrastructure facts → update `projects/*/references/`
- [ ] Extract debugging lessons → append to `runbooks/lessons-learned.md`
- [ ] Extract decisions → update `memory/entities/decisions.md`
- [ ] Extract new people/contacts → update `memory/entities/people.md`
- [ ] Update MEMORY.md if current state changed

## 2. Prune MEMORY.md (5 min)

- [ ] Remove resolved urgent items
- [ ] Remove decisions that are now "how things work" (they live in references)
- [ ] Remove fixed issues
- [ ] Check line count: `wc -l MEMORY.md` — must be ≤100

## 3. Check Front-Matter (5 min)

Scan `projects/` and `runbooks/` for:

- [ ] Files without `---` YAML header → add front-matter
- [ ] `status: active` with `updated:` >2 weeks ago → verify or mark `stale`
- [ ] `status: stale` files → archive or update

## 4. Verify References (5 min)

- [ ] Project references match deployed reality
- [ ] Skills catalogue matches actual `skills/` directory
- [ ] `projects/_index.md` lists all active projects

## 5. Budget Check

| File | Budget | Check |
|------|--------|-------|
| MEMORY.md | ≤100 lines | `wc -l MEMORY.md` |
| Each reference doc | ≤200 lines | Spot-check largest files |

If over budget: split into multiple files or move detail to sub-files.

## 6. Commit

```bash
git add -A
git commit -m "Weekly workspace maintenance: consolidate, prune, update"
git push
```
