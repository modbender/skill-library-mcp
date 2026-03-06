# Publishing SEO Prospector to ClawHub

## Pre-Flight Checklist

Before publishing, verify:
1. `clawhub.json` has correct pricing ($149 one-time)
2. No personal LWG info in scripts (DEFAULT_CONFIG should show placeholder values)
3. Examples folder has sample reports (these use Louisville as a demo city — that's fine)
4. All scripts run without errors

## Prompt for Ash

Copy-paste this to your OpenClaw instance:

---

Publish the seo-prospector skill to ClawHub. The skill is at ~/.openclaw/skills/seo-prospector/ and has a clawhub.json manifest ready.

Before publishing, do these checks:
1. Read clawhub.json and confirm the metadata looks correct
2. Run a quick syntax check on all Python scripts in scripts/ (python3 -m py_compile each one)
3. Verify no personal info (Louisville Web Guy, Hunter, 502-305-4043) appears in any .py files — only in the examples/ folder and clawhub.json author field (which is fine)
4. Verify the SKILL.md has proper YAML frontmatter with name and description

Then publish:
clawhub publish ~/.openclaw/skills/seo-prospector/

If clawhub CLI is not installed, install it first:
npm install -g @openclaw/clawhub

After publishing, report back: the skill URL, review status, and any warnings.

---

## If Publishing Fails

Common issues:
- **"clawhub not found"** → Run `npm install -g @openclaw/clawhub`
- **"Not authenticated"** → Run `clawhub login` (uses GitHub OAuth)
- **"Duplicate name"** → Change the name in clawhub.json to something unique
- **"Missing required field"** → Check clawhub.json has all required fields

## After Publishing

1. Check the listing at clawhub.ai/skills/seo-prospector
2. Add screenshots (prospect report example, HTML email preview, Discord summary)
3. Consider adding a demo video showing the pipeline in action
4. Share on LinkedIn / X to drive initial traffic
