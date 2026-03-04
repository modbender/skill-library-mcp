---
name: skill-maker
description: Create new agent skills from scratch. Use when: (1) Building a new skill for specific capabilities, (2) Converting workflows into reusable skills, (3) Designing skill structure and triggers, (4) Setting up skill resources (scripts, references, assets).
version: 1.1.0
changelog: "v1.1.0: Fresh approach with reasoning framework"
metadata: {"clawdbot":{"emoji":"🔨","category":"creation"}}
---

# Skill Maker 🔨

Create powerful, reusable skills with structured reasoning.

---

## The Skill Maker Framework

```
┌─────────────────────────────────────────────────────────────┐
│  SKILL FORGING PROCESS                                      │
├─────────────────────────────────────────────────────────────┤
│  1. INTERPRET  → What capability does this skill need?     │
│  2. DESIGN    → Structure, resources, trigger conditions   │
│  3. FORGE     → Write SKILL.md, create resources          │
│  4. TEST      → Verify triggers, check quality            │
│  5. POLISH    → Refine based on testing                   │
└─────────────────────────────────────────────────────────────┘
```

---

## Decision Tree: What Are We Building?

```
INTENT
    │
    ├── Brand new skill ──→ Start from Step 1
    │
    ├── Replace existing ──→ 
    │       └── Read old first, then improve
    │
    └── Clone & modify ──→ 
            └── Copy, rename, customize
```

---

## Step 1: Interpret

### The Core Questions

| Question | Your Answer |
|----------|-------------|
| **What does this skill DO?** | [Capability] |
| **Who asks for it?** | [User triggers] |
| **What's the DOMAIN?** | [Topic area] |
| **How COMPLEX is it?** | Simple/Medium/Complex |

### Self-Check: Interpretation

- [ ] Can I describe the skill in one sentence?
- [ ] Do I know what phrases would trigger it?
- [ ] Is this truly a new capability?

---

## Step 2: Design

### Complexity Decision

```
COMPLEXITY LEVEL
    │
    ├── Simple ──→ SKILL.md only
    │       └── One capability, clear steps
    │
    ├── Medium ──→ SKILL.md + references/
    │       └── Needs docs to reference
    │
    └── Complex ──→ SKILL.md + scripts/ + references/
            └── Needs executable code
```

### Directory Structure

```
skill-name/
├── SKILL.md              # Required: name, description, body
├── scripts/              # Optional: executable code
├── references/          # Optional: detailed docs
└── assets/              # Optional: templates, files
```

### Writing Triggers

Users typically say:
- "I need to [action]"
- "How do I [task]?"
- "Help me with [domain]"
- "Can you [capability]?"

**Formula for description:**
> "[What it does]. Use when: (1) [situation 1], (2) [situation 2], (3) [situation 3]."

**Example:**
> "Fetch weather data from wttr.in. Use when: (1) User asks about weather, (2) User wants forecast, (3) User asks temperature in [city]."

### Self-Check: Design

- [ ] Name follows convention (lowercase, hyphens)?
- [ ] Description has clear triggers?
- [ ] I know which resources to include?

---

## Step 3: Forge

### SKILL.md Template

Copy this template for your skill:

```yaml
---
name: my-skill
description: "[What it does]. Use when: (1) [trigger 1], (2) [trigger 2], (3) [trigger 3]."
---

# My Skill

## When This Skill Activates
This skill triggers when user wants to [capability].

## The [Domain] Framework

| Step | Action |
|------|--------|
| 1 | [What to do] |
| 2 | [What to do] |
| 3 | [What to do] |

## Workflow

### Step 1: [Name]
[What to do and why]

### Step 2: [Name]
[What to do and why]

### Decision Point
- If [condition]: do [A]
- If [condition]: do [B]

## Common Scenarios

### Scenario 1: [Case]
[What to do]

### Scenario 2: [Case]
[What to do]

## Troubleshooting

### Problem: [Error]
- Cause: [why]
- Fix: [how]

## Quick Reference

| Task | Action |
|------|--------|
| [Task 1] | [Command/Step] |
| [Task 2] | [Command/Step] |
```

### Content Patterns

| Pattern | Use For |
|---------|---------|
| Numbered steps | Sequential workflows |
| Decision tree | Branching logic |
| Tables | Quick reference |
| Code blocks | Examples |
| Error sections | Troubleshooting |

### Progressive Disclosure

```
IN SKILL.MD (< 500 lines):
├── Core workflow (must-know)
├── Key examples (most common)
└── Quick reference

IN REFERENCES/:
├── Detailed documentation
├── API specs
├── Edge cases
└── Extended examples
```

### Self-Check: Forge

- [ ] Frontmatter complete (name + description)?
- [ ] Body has reasoning framework?
- [ ] Self-check prompts included?
- [ ] Resources properly structured?

---

## Step 4: Test

### Trigger Testing

Read your description and ask:

```
Description: "[your description]"

Would this match user saying:
- "[trigger phrase 1]"? → YES/NO
- "[trigger phrase 2]"? → YES/NO
- "[trigger phrase 3]"? → YES/NO
```

### Self-Check: Test

- [ ] Does description match likely user phrases?
- [ ] Is the skill findable via search?
- [ ] Are there clear steps to follow?
- [ ] Does it include error handling?

---

## Step 5: Polish

### Refinement Loop

```
Use the skill → Notice issues → Fix → Use again
    ↑                                    │
    └────────────────────────────────────┘
```

### Common Fixes

| Problem | Solution |
|---------|----------|
| Won't trigger | Add more "Use when:" triggers |
| Too long | Move details to references/ |
| Confusing | Add example scenarios |
| Missing cases | Add troubleshooting section |

### Self-Check: Polish

- [ ] Tested on real task?
- [ ] User feedback incorporated?
- [ ] Ready for regular use?

---

## Versioning Guide

### When to Bump Version

| Change Type | Version Bump | Example |
|------------|--------------|---------|
| Bug fix, no new features | 1.0.0 → 1.0.1 | v1.0.1 |
| New feature, backward compatible | 1.0.1 → 1.1.0 | v1.1.0 |
| Breaking changes | 1.1.0 → 2.0.0 | v2.0.0 |

### Changelog Format

```markdown
## Version 1.1.0

### Added
- New feature X

### Changed
- Improved Y

### Fixed
- Bug Z
```

### Self-Check: Versioning

- [ ] Did I increment the version correctly?
- [ ] Is changelog updated?
- [ ] Is this a breaking change?

---

## Metadata Best Practices

### Frontmatter Fields

```yaml
---
name: my-skill
description: "[What it does]. Use when: (1) [trigger 1], (2) [trigger 2]."
version: 1.0.0
changelog: "[Brief summary of changes]"
metadata:
  clawdbot:
    emoji: "🔨"           # Emoji for the skill
    category: "creation"  # Category (research/coding/utility/etc)
    requires:
      bins: ["curl"]      # Required system binaries
      python: ["requests"] # Optional Python packages
---
```

### Emoji Selection

| Category | Emoji | Examples |
|----------|-------|----------|
| Research | 🔬 | deep-research-pro, paper-compare |
| Coding | 💻 | code |
| Creation | 🔨 | skill-forge |
| Utility | ⚡ | surge |
| Weather | 🌤️ | weather |
| Discovery | 🔍 | find-skills |
| Media | 🎞️ | video-frames |
| Files | 📄 | pdf |

### Category Tags

| Category | When to Use |
|----------|-------------|
| research | Research, analysis, comparisons |
| coding | Code-related tasks |
| utility | Tools, downloads, file operations |
| creation | Building new things |
| communication | Messaging, notifications |
| media | Video, audio, images |

### Requirements Metadata

```yaml
metadata:
  clawdbot:
    requires:
      bins: ["ffmpeg", "curl"]       # System binaries
      python: ["requests", "pandas"] # Python packages
      node: ["typescript"]           # Node packages
    os: ["linux", "darwin", "win32"] # Supported OS
```

### Self-Check: Metadata

- [ ] Is frontmatter complete?
- [ ] Is emoji appropriate for category?
- [ ] Are requirements listed?
- [ ] Is version correct?

---

## Quality Score

Evaluate your skill:

| Factor | Score | Notes |
|--------|-------|-------|
| **Trigger Clarity** | | |
| - Clear "Use when:" with 3+ triggers | ⭐⭐⭐ | |
| - "Use when:" with 1-2 triggers | ⭐⭐ | |
| - Vague or missing | ⭐ | |
| **Structure** | | |
| - Has reasoning framework | ⭐⭐⭐ | |
| - Has workflow steps | ⭐⭐ | |
| - No structure | ⭐ | |
| **Decision Trees** | | |
| - Multiple decision points | ⭐⭐⭐ | |
| - One decision point | ⭐⭐ | |
| - None | ⭐ | |
| **Self-Checks** | | |
| - Checklists at each major step | ⭐⭐⭐ | |
| - Some self-checks | ⭐⭐ | |
| - None | ⭐ | |
| **Examples** | | |
| - Working examples included | ⭐⭐⭐ | |
| - Template only | ⭐⭐ | |
| - Nothing | ⭐ | |
| **Metadata** | | |
| - Complete (emoji, category, requires) | ⭐⭐⭐ | |
| - Partial | ⭐⭐ | |
| - Missing | ⭐ | |

### Quality Thresholds

| Score | Rating | Action |
|-------|--------|--------|
| 15-18 | ⭐⭐⭐ Excellent | Ready to publish |
| 10-14 | ⭐⭐ Good | Minor improvements |
| 5-9 | ⭐ Needs Work | Major improvements needed |

### Self-Check: Quality

- [ ] Overall score calculated?
- [ ] Below 10? Improve before publishing

---

## Why This Works

### The Skill Logic Pattern

Based on research (SkillsBench 2026):

1. **Reasoning framework** → Agent knows HOW to think, not just WHAT to do
2. **Decision trees** → Agent can handle different scenarios
3. **Self-checks** → Agent validates its work
4. **Progressive disclosure** → Context-efficient

### The Goldilocks Principle

> "2-3 focused modules beat exhaustive documentation"

Keep it:
- ✅ Complete enough to be useful
- ✅ Concise enough to fit in context
- ✅ Structured enough to guide reasoning

---

## Example: Forging a Weather Skill

### Step 1: Interpret
- **What:** Fetch weather from wttr.in
- **Triggers:** "weather in [city]", "temperature", "forecast"
- **Domain:** Weather data

### Step 2: Design
- **Complexity:** Simple (just API calls)
- **Structure:** SKILL.md only
- **Name:** `weather`

### Step 3: Forge

```yaml
---
name: weather
description: "Get weather data. Use when: (1) User asks weather, (2) User wants forecast, (3) User asks temperature."
---

# Weather

## Reasoning

1. EXTRACT → Location from request
2. FETCH → Call wttr.in API
3. PARSE → Extract temp, conditions
4. PRESENT → Format for user
```

### Step 4-5: Test & Polish
- Add more triggers ("sunny?", "rain?")
- Add error handling (wrong city, no network)
- Add presentation templates

---

## Why This Works

Based on research (SkillsBench 2026), skills with reasoning frameworks perform better because they give agents a thinking structure, not just steps to follow.

*Made with Skill Maker 🔨*
