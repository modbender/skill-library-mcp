# Update Summary Examples

Reference examples for formatting the update report message.

## Full Update (Everything Changed)
```
🔄 Daily Auto-Update Complete

**OpenClaw**
Updated: v2026.2.1 → v2026.2.2

**Skills Updated (3)**
1. prd: 2.0.3 → 2.0.4
2. browser: 1.2.0 → 1.2.1
3. nano-banana-pro: 3.1.0 → 3.1.2

**Skills Already Current (5)**
prj, gemini, browser, sag, himalaya

✅ All updates completed successfully.
```

## No Updates Available
```
🔄 Daily Auto-Update Check

**OpenClaw**: v2026.2.2 (already latest)
**Skills**: All installed skills are current.
Nothing to update today.
```

## Partial Update (Skills Only)
```
🔄 Daily Auto-Update Complete

**OpenClaw**: v2026.2.2 (no update available)

**Skills Updated (2)**
1. himalaya: 1.0.0 → 1.0.1
2. 1password: 2.1.0 → 2.2.0

**Skills Already Current (6)**
prd, gemini, browser, sag, things-mac, peekaboo

✅ Skill updates completed.
```

## Update With Errors
```
🔄 Daily Auto-Update Complete (with issues)

**OpenClaw**: v2026.2.1 → v2026.2.2

✅ **Skills Updated (1)**
1. prd: 2.0.3 → 2.0.4

❌ **Skills Failed (1)**
1. nano-banana-pro: update failed
   Error: Network timeout while downloading v3.1.2
   Recommendation: Run `clawdhub update nano-banana-pro` manually

**Skills Already Current (6)**
prj, gemini, browser, sag, himalaya, peekaboo

⚠️ Completed with 1 error.
```

## First Run / Setup Confirmation
```
🔄 Auto-Updater Configured
Daily updates will run at 4:00 AM (Europe/Berlin).

**What will be updated:**
- OpenClaw core
- All installed skills via ClawHub

**Current status:**
- OpenClaw: v2026.2.2
- Installed skills: 8

To modify: `openclaw cron edit "Daily Auto-Update"`
To disable: `openclaw cron remove "Daily Auto-Update"`
```

## Formatting Guidelines
1. Use emojis sparingly (🔄 + ✅/❌)
2. Lead with what changed
3. Group updated vs current vs failed
4. Include version numbers (before → after)
5. Keep it short
6. Surface errors prominently
