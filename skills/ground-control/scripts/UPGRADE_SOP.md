# OpenClaw Upgrade SOP

## Pre-Upgrade

1. Run `openclaw doctor --fix` — clean orphans, confirm config valid
2. Back up config: `cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.bak.$(date +%Y%m%d)`
3. Confirm `MODEL_GROUND_TRUTH.md` is current (if you changed config/cron recently, update it first)

## Upgrade

```bash
openclaw update        # or: npm install -g openclaw@latest
openclaw gateway restart
```

## Post-Upgrade

Run verification:

```
/verify
```

The agent reads `scripts/post-upgrade-verify.md` and executes the 5-phase check.

## GROUND_TRUTH Maintenance

**⚠️ Any time you modify config or cron, update `MODEL_GROUND_TRUTH.md` to match.**

If using an OpenClaw agent, add the sync rule to AGENTS.md:

```markdown
## 🔒 GROUND_TRUTH Sync Rule

**Every time config changes (model/cron/channel/acp), remind to sync MODEL_GROUND_TRUTH.md.**
- After modification → ask: "Want me to update GROUND_TRUTH too?"
- If yes → update immediately
- If no → log as todo in daily diary
```
