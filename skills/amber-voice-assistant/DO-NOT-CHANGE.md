# DO NOT CHANGE - CRITICAL BRANDING RULES

⚠️ **READ THIS BEFORE EDITING SKILL.MD** ⚠️

## Fixed Branding (DO NOT MODIFY unless explicitly instructed by Abe)

### ClawHub Publish Command --name Flag
```bash
clawhub publish ~/clawd/skills/amber-voice-assistant --version X.Y.Z --name "Amber — Phone-Capable Voice Agent" --changelog "..."
```
**This is what sets the display title on ClawHub!**  
The frontmatter fields do NOT control the ClawHub display name.  
**NOT:** "Amber Voice Assistant"  
**NOT:** "Amber Voice Agent"  
**NOT:** Any other variation

### H1 Heading (in SKILL.md body)
```markdown
# Amber — Phone-Capable Voice Agent
```
For documentation consistency (but doesn't affect ClawHub display).

### Description (frontmatter in SKILL.md)
```
"The most complete phone skill for OpenClaw. Production-ready, low-latency AI calls — inbound & outbound, multilingual, live dashboard, brain-in-the-loop."
```

Must be exactly 155 characters or less.

## Rules
1. **NEVER change the title** unless Abe explicitly instructs you to
2. **NEVER change the description** unless Abe explicitly instructs you to
3. These are finalized branding decisions - respect them
4. If you need to update documentation, update OTHER sections, not these

## Why This File Exists
Because I (Jarvis) keep making mistakes with the title/branding. This file is here to stop that from happening again.

**Mistake history:**
- 2026-02-21 v4.2.2: Reverted title to "Amber Voice Assistant" in H1 heading
- 2026-02-21 v4.2.3: Fixed H1 but ClawHub still showed wrong name
- 2026-02-21 v4.2.4: Added `title` field to frontmatter (but ClawHub doesn't use frontmatter for display name!)
- 2026-02-21 v4.2.5: **FINALLY** discovered the `--name` flag on `clawhub publish` command

**The lesson:** 
- ClawHub display name is set via the `--name` flag during publish, NOT via frontmatter
- Frontmatter fields in SKILL.md do NOT control the ClawHub listing page title
- The publish command must include: `--name "Amber — Phone-Capable Voice Agent"`
