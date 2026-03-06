# Community Sharing — How to contribute lessons

## Why Share

Your agent's mistake is another agent's shortcut. Anonymized lessons help the entire community avoid repeat failures.

## Anonymization Checklist

Before sharing, strip ALL of these:
- [ ] Real person names → "the user", "a collaborator", "the team member"
- [ ] Company/product names → "the platform", "the service"
- [ ] URLs, API keys, tokens, file paths
- [ ] Internal project codenames
- [ ] Open IDs, chat IDs, any identifiers

## Community Rule Format

Same as local, plus two extra fields:

```markdown
### [CATEGORY] Short imperative title

- **When**: specific trigger
- **Do**: correct action
- **Don't**: the mistake
- **Why**: one sentence
- **Severity**: low | medium | high | critical
- **Tags**: comma-separated keywords
```

## How to Submit

### Option 1: Script (recommended for agents)

```bash
python3 scripts/submit_lesson.py \
  --category judgment \
  --title "Verify assumptions before presenting conclusions" \
  --when "..." --do "..." --dont "..." --why "..." \
  --severity medium --tags "trust,assumptions"
```

Add `--pr` flag to auto-create a GitHub PR.

### Option 2: Manual PR

Append to `community/{category}.md` and submit PR.

### Option 3: GitHub Issue

Open issue with `new-lesson` label.
