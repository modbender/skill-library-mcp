# Cinematic Script Writer Skill - Issue Report & Fix Guide

## Problem Summary

During installation, it took **multiple workarounds** to get this skill recognized by OpenClaw. Here's everything that's wrong and how to fix it for a clean one-line install.

---

## Issue 1: Missing YAML Frontmatter (CRITICAL)

**The #1 reason this skill doesn't work after installation.**

The published SKILL.md on ClawHub starts directly with:

```markdown
# Cinematic Script Writer
```

But OpenClaw **requires** YAML frontmatter at the top of every SKILL.md. Without it, the skill is completely invisible to the engine. OpenClaw uses a 3-level loading system:

- **Level 1** (always in context): `name` + `description` from YAML frontmatter — this is how OpenClaw decides when to activate your skill
- **Level 2** (loaded on trigger): The full SKILL.md body
- **Level 3** (on demand): Scripts, references, assets

Without frontmatter, Level 1 never loads, so the skill never triggers.

**Fix:** Add this to the very top of SKILL.md:

```yaml
---
name: cinematic-script-writer
description: >
  Create professional cinematic scripts for AI video generation with character
  consistency and cinematography knowledge. Use when the user wants to write
  a cinematic script, create story contexts with characters, generate image
  prompts for AI video tools, or needs cinematography guidance (camera angles,
  lighting, color grading). Also use for character consistency sheets, voice
  profiles, and saving scripts to Google Drive.
metadata:
  {
    "openclaw": {
      "emoji": "🎬"
    }
  }
---
```

Notice the `description` includes **"Use when..."** trigger phrases. This is how well-written bundled skills (like `summarize`, `clawhub`, `github`) help OpenClaw know when to activate the skill.

---

## Issue 2: Weak Description (No Trigger Phrases)

Even the version we manually fixed only had:

> "Create professional cinematic scripts for AI video generation with character consistency and cinematography knowledge."

Compare with a well-written bundled skill (`summarize`):

> "Summarize or extract text/transcripts from URLs, podcasts, and local files (great fallback for 'transcribe this YouTube/video')."

The description is OpenClaw's **primary trigger mechanism**. It should include natural-language triggers that match how users actually ask for things.

---

## Issue 3: Body Content is a JavaScript API Reference, Not AI Instructions

The SKILL.md body contains code like:

```javascript
const context = await skill.createContext("Kutil's Adventure", ...);
const ideas = await skill.generateStoryIdeas(context.id, 3);
```

This is a **developer SDK reference**. But OpenClaw skills are meant to be **AI agent instructions** — they tell the AI *how* to accomplish the task, not show JavaScript function signatures. The AI model can't call `skill.createContext()` — it needs plain-language instructions or executable scripts in a `scripts/` directory.

**Fix:** Rewrite the body as instructions for the AI agent. For example:

```markdown
## How to Use This Skill

When a user wants to create a cinematic script:

1. Ask for the story concept, era/setting, and visual style
2. Create character profiles with consistent visual descriptions
3. Generate 3 story ideas and let the user pick one
4. Write the full cinematic script with:
   - Scene descriptions with camera angles and lighting
   - Character dialogue with voice consistency notes
   - Image generation prompts for each shot
5. Validate for anachronisms (no modern items in historical settings)
6. Offer to save to Google Drive or local storage
```

---

## Issue 4: No `requires` or `install` Metadata

Bundled skills that need external tools declare them in frontmatter:

```yaml
metadata:
  {
    "openclaw": {
      "emoji": "🍌",
      "requires": { "bins": ["uv"], "env": ["GEMINI_API_KEY"] },
      "primaryEnv": "GEMINI_API_KEY",
      "install": [
        { "id": "uv-brew", "kind": "brew", "formula": "uv", "bins": ["uv"] }
      ]
    }
  }
```

If cinematic-script-writer needs Google Drive API credentials or any external tools, these should be declared so OpenClaw can check/install them automatically.

---

## Issue 5: ClawHub CLI Installation Path

When we ran `clawdhub install cinematic-script-writer`, it installed to `./skills/` (current working directory) instead of OpenClaw's skill directories. Users then have to manually copy files to the right location. This is a `clawdhub` CLI issue, not your skill's issue — but it's worth noting.

---

## Issue 6: Version Mismatch

`_meta.json` says `"version": "0.1.1"` but the SKILL.md body says `Version 1.3.0`. These should match.

---

## What You Need to Do (Checklist)

To make this a clean one-line install (`openclaw skill install cinematic-script-writer` or `clawdhub install cinematic-script-writer`):

| # | Fix | Priority |
|---|-----|----------|
| 1 | Add YAML frontmatter with `name`, `description`, and `metadata` | **CRITICAL** |
| 2 | Write a rich `description` with "Use when..." trigger phrases | **HIGH** |
| 3 | Rewrite body as AI agent instructions, not JS API docs | **HIGH** |
| 4 | Add `requires`/`install` in metadata if external deps are needed | **MEDIUM** |
| 5 | Sync version number between `_meta.json` and SKILL.md | **LOW** |
| 6 | Add executable scripts in `scripts/` dir for deterministic tasks (e.g., Google Drive upload, prompt generation) | **MEDIUM** |
| 7 | Remove unnecessary files (`README.md`, `CHANGELOG.md`, etc.) if any exist — skill-creator docs say not to | **LOW** |

---

## Ideal SKILL.md Structure

Here's the template based on how properly working bundled skills are structured:

```markdown
---
name: cinematic-script-writer
description: >
  Create professional cinematic scripts for AI video generation with character
  consistency and cinematography knowledge. Use when the user wants to write
  a cinematic script, create story contexts, generate AI image prompts for
  video scenes, or needs camera angle/lighting/color grading guidance.
metadata:
  {
    "openclaw": {
      "emoji": "🎬"
    }
  }
---

# Cinematic Script Writer

[AI agent instructions here — what to do step by step,
not JavaScript API references]

## Cinematography Reference

[Camera angles, lighting techniques, etc. as reference
material the AI can use when writing scripts]

## Character Consistency Rules

[Rules for maintaining consistent character appearance
across shots]

## Output Format

[What the final script should look like]
```

---

## Comparison with Working Bundled Skills

| Feature | nano-banana-pro | summarize | github | cinematic-script-writer |
|---|---|---|---|---|
| YAML frontmatter | Yes | Yes | Yes | **MISSING** |
| Trigger phrases in description | Yes | Yes | Yes | **No** |
| `requires` metadata | bins + env | bins | bins | **None** |
| `install` instructions | brew | brew | brew + apt | **None** |
| Body format | AI instructions | AI instructions | AI instructions | **JS API docs** |
| Scripts directory | Yes (`scripts/`) | No (not needed) | No (uses `gh` CLI) | **No** |

---

## Summary

Once you fix the SKILL.md with proper frontmatter and rewrite the body as AI agent instructions, then republish to ClawHub, anyone should be able to install it with:

```bash
clawdhub install cinematic-script-writer
```

And OpenClaw will automatically recognize and trigger it when users ask for cinematic scripts.
