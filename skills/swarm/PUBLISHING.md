# Publishing Swarm to ClawHub

## What Gets Published

ClawHub skills are **documentation**, not code. Users get the SKILL.md and reference docs that tell the agent how to use the daemon. The actual runtime (lib/, bin/) is installed separately via git clone.

### Published files (staged to /tmp/swarm-publish/):
```
SKILL.md                    ← Main skill doc (OpenClaw reads this)
references/
  api.md                    ← Full API endpoint reference
  config.md                 ← YAML config + env vars
  install.md                ← Installation guide
  readme.md                 ← Overview
```

### NOT published:
- lib/, bin/ (runtime code — installed via git)
- node_modules/
- test/, docker/, examples/
- benchmark scripts, tap-analysis, bench.js
- .git, .gitignore

## Step-by-Step Process

### 1. Make your code changes
Edit files in `~/clawd/skills/node-scaling/`

### 2. Update SKILL.md
Update the root `SKILL.md` with any new features, endpoints, or config changes. This is what the agent reads.

### 3. Bump version
```bash
# In package.json
"version": "X.Y.Z"
```

### 4. Commit and push to GitHub
```bash
cd ~/clawd/skills/node-scaling
git add -A
git commit -m "vX.Y.Z: description"
git push origin main
```

### 5. Stage the publish directory
```bash
# Clean slate
rm -rf /tmp/swarm-publish
mkdir -p /tmp/swarm-publish/references

# Copy docs only
cp ~/clawd/skills/node-scaling/SKILL.md /tmp/swarm-publish/
cp ~/clawd/skills/node-scaling/INSTALL.md /tmp/swarm-publish/references/install.md
cp ~/clawd/skills/node-scaling/README.md /tmp/swarm-publish/references/readme.md
```

Then update the reference docs if API/config changed:
- `/tmp/swarm-publish/references/api.md` — endpoint reference
- `/tmp/swarm-publish/references/config.md` — config reference

### 6. Publish to ClawHub (ONE attempt only)
```bash
clawhub publish /tmp/swarm-publish \
  --slug swarm \
  --name "Swarm" \
  --version X.Y.Z \
  --changelog "vX.Y.Z: what changed"
```

**Rules:**
- ONE publish attempt per update. Do not retry on failure.
- If rate limited or timed out, report the result and move on.
- Jacy can retry manually later if needed.

## Quick Reference

| What | Where |
|------|-------|
| Source code | `~/clawd/skills/node-scaling/` |
| GitHub | https://github.com/Chair4ce/node-scaling |
| ClawHub slug | `swarm` |
| Publish staging | `/tmp/swarm-publish/` |
| Config | `~/.config/clawdbot/node-scaling.yaml` |
| Daemon | `http://localhost:9999` |

## Version History

| Version | Date | Key Changes |
|---------|------|-------------|
| 1.3.2 | 2026-02-18 | Chain pipelines, prompt cache, stage retry, cost tracking |
| 1.3.0 | 2026-02-18 | Chain, auto-chain, benchmark, capabilities discovery |
| 1.1.0 | 2026-02-11 | Web search grounding |
| 1.0.0 | 2026-02-11 | Initial: parallel, research, daemon |
