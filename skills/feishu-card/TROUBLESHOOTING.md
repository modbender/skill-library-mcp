# Troubleshooting

## Issue: MODULE_NOT_FOUND (send.js not found or dependencies missing)

**Symptom:**
Other skills (like `video-gen`) trying to call `feishu-card/send.js` fail with:
```
Error: Cannot find module '.../skills/feishu-card/send.js'
```
Or running the script fails with missing `dotenv`.

**Cause:**
1. The skill directory was empty or missing files after a system restore/cleanup.
2. `node_modules` were missing.

**Solution:**
1. Restore the skill files from backup (e.g., `temp/github-openclaw-workspace/skills/feishu-card`).
2. Run `npm install` inside `skills/feishu-card`.

```bash
cp -r temp/github-openclaw-workspace/skills/feishu-card skills/
cd skills/feishu-card
npm install
```

**Date:** 2026-02-07
