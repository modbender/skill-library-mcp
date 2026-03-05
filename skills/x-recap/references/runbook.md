# X Recap runbook (actionbook-rs + profile=x)

## One-time / whenever X breaks: login

```bash
cd /Users/daboluo/.openclaw/workspace
./bin/actionbook --profile x browser open https://x.com/home
```

If screenshots are blank / spinner-only / no timeline:
- assume login expired → re-run login above.

## Fetch scripts (single source of truth)

- Breaking (full-page): `skills/x-recap/scripts/fetch_official_breaking.sh`
  - Output: `output/x-claude-breaking/`
- Daily (viewport): `skills/x-recap/scripts/fetch_official_daily.sh`
  - Output: `output/x-claude/`

## Common failure / easy-to-forget pain points

### 1) Blank / spinner-only timeline screenshots
Symptoms:
- Screenshot is empty, only a loading spinner, or no timeline content.

Cause:
- X login/session expired for actionbook `--profile x`.

Fix:
```bash
cd /Users/daboluo/.openclaw/workspace
./bin/actionbook --profile x browser open https://x.com/home
```

### 2) Gateway timeout when triggering cron runs
Symptoms:
- cron run errors like: gateway timeout / ws://127.0.0.1:18789 not responding.

Fix:
```bash
openclaw gateway restart
```

### 3) Rate limits / bot detection / consent walls (intermittent)
Symptoms:
- Timeline loads partially, then stops; or content differs run-to-run.

Mitigation:
- Prefer official profile pages (no search).
- Reduce fetch frequency if it becomes flaky.
- Re-login (often clears the state).

### 4) Consistency drift (scripts vs cron text)
Rule:
- Fetch logic MUST live in `skills/x-recap/scripts/*.sh` only.
- Cron payloads should only call those scripts + recap from screenshots.
