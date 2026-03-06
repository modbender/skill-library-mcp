---
name: clawhub-skill-publisher
version: 1.0.1
description: "Research, structure, and publish skills to ClawHub. Analyzes top listings for content patterns, generates gap reports against your draft, patches README/SKILL files to match marketplace standards, and runs clawhub publish."
metadata:
  {"openclaw":{"emoji":"🏗️","requires":{"bins":["clawhub"]},"os":["darwin","linux","win32"]}}
---

# ClawHub Skill Publisher v1

> Turn a rough skill idea into a polished, publish-ready ClawHub listing — informed by what's actually working in the marketplace.

Use this skill when you want to:
- Publish a new skill to ClawHub
- Audit an existing skill draft against marketplace standards
- Research what top-performing skills look like before writing yours

---

## Workflow

### Step 1 — Research Top Listings

Install the most relevant published skills in a temp directory and read their SKILL.md + README.md:

```bash
mkdir -p /tmp/ch-research

# Search for skills in your category
clawhub search "your-category-keyword"

# Install top 3-5 results for analysis
clawhub install <slug1> --dir /tmp/ch-research --force
clawhub install <slug2> --dir /tmp/ch-research --force
# (rate limit: add 3s sleep between installs)
```

**What to capture per skill:**
- Description line: length, tone, value-first or feature-first?
- First sentence of SKILL.md: does it state the use case immediately?
- Structure: does it use tables, code blocks, headers?
- Word count (target: 400–700 words for SKILL.md)
- Sections present: commands, when-to-use, safety, version history
- Trust signals: safety section, version history, explicit opt-outs

### Step 2 — Gap Analysis

Compare your draft against findings. Score each dimension:

| Dimension | Best Practice | Your Draft | Action |
|-----------|---------------|------------|--------|
| Description line | ≤160 chars, value-first, no buzzwords | ? | Patch or OK |
| "When to use" | Explicit trigger + do/don't | ? | Patch or OK |
| Commands/interface | Slash commands or trigger phrases | ? | Patch or OK |
| Word count (SKILL.md) | 400–700 words | ? | Trim or expand |
| Tables vs. prose | Tables preferred for comparisons | ? | Patch or OK |
| Version history | Present, at bottom | ? | Add or OK |
| Safety section | Explicit "never does X" list | ? | Add or OK |
| Examples | Concrete ✅/❌ pairs | ? | Add or OK |
| Attribution | Link back to openclaw.ai / clawhub.ai | ? | Add or OK |

### Step 3 — Patch the Draft

Apply gap findings. Priority order:
1. Description line (most visible — fix first)
2. "When to use" section (drives installs)
3. Trim word count if over 700 (cut prose, keep tables)
4. Add missing sections (safety, version history)
5. Convert prose comparisons to tables
6. Add examples file if none exists

### Step 4 — Publish

```bash
# Verify auth
clawhub whoami

# Publish (run from workspace root or skill parent dir)
clawhub publish ./skills/<your-skill> \
  --slug <your-slug> \
  --name "Your Skill Name" \
  --version 1.0.0 \
  --changelog "Initial release"
```

Published URL: `https://clawhub.ai/skills/<your-slug>`

---

## ClawHub Listing Anatomy

### Description Field (≤160 chars)
The most important text. Shows in search results and install prompts.

**Formula:** `[What it does] + [how] + [key outcome].`

✅ Good: `"Reduce AI costs by batching related asks into fewer responses. ~30–50% fewer API calls, no quality loss."`
❌ Bad: `"ClawSaver — Combines Linked Asks into Well-structured Sets for Affordable, Verified, Efficient Responses"`

### SKILL.md Structure (what the agent reads)

```markdown
---
name: skill-name
version: X.Y.Z
description: "Same as listing description"
metadata: {"openclaw":{"emoji":"🔧"}}
---

# Skill Name vX

> One-line positioning statement.

[One paragraph: what it does and why.]

## When to Use
[Use / Do not use — explicit conditions]

## Core Behavior / Commands
[Tables preferred. Trigger phrases, commands, decision rules.]

## Safety
[What it never does. Explicit opt-outs.]

## Installation
[clawhub install command]

## Version History
[- X.Y.Z — what changed]
```

### README.md Structure (humans + listing body)

```markdown
# Skill Name
> Tagline

## Why [Skill Name]?
[Problem → solution in 2-3 sentences]

## What It Does
[Numbered or bulleted feature list]

## [Key Decision Table or Usage Example]

## Safety Model

## Installation

## Version
```

---

## Marketplace Patterns (Observed Feb 2026)

### What top skills have in common
- Value-first description (outcome before feature list)
- "When to use" is explicit — most top skills have do/don't lists
- Tables over prose for anything comparative
- Safety section is a trust signal — include it even if short
- Version history at the bottom — shows maintenance
- Word count 400–700 for SKILL.md; README can be longer

### What separates good from great
- Great: examples file with concrete ✅/❌ pairs
- Great: trigger phrase detection (tells agent *when* to activate)
- Great: explicit opt-outs ("say X to disable")
- Good but not great: long prose descriptions, missing opt-outs
- Avoid: backronyms or clever names in the description line (save for README)

### Category density (as of Feb 2026)
- Cost/token tracking: **saturated** — need a differentiated angle
- Batch/workflow: **sparse** — opportunity
- Provider-specific tools: **mixed** — Kimi-heavy, OpenAI moderate
- Productivity/meta-skills: **sparse** — opportunity

---

## File Checklist Before Publishing

- [ ] `SKILL.md` — frontmatter has name, version, description
- [ ] `SKILL.md` — word count 400–700
- [ ] `SKILL.md` — has "When to Use" section
- [ ] `SKILL.md` — has Safety section
- [ ] `SKILL.md` — has Version History
- [ ] `README.md` — value-first, ≤600 words
- [ ] `README.md` — installation command correct
- [ ] `examples/` — at least one example file (optional but recommended)
- [ ] Description line — ≤160 chars, value-first
- [ ] `clawhub whoami` — auth confirmed before publish

### Skill Type: Behavior-Change vs. Active Tool

Most ClawHub skills are **behavior-change skills** — they work by shaping agent judgment through instructions, not by running code or intercepting requests at the system level. This is the same mechanism as `execution-loop-breaker`, `token-saver`, and most top listings.

**When writing a behavior-change skill:**
- Be explicit in the description that it works through agent behavior, not automated interception
- Use language like "trains your agent to..." or "gives your agent the judgment to..." — not "automatically detects" or "intercepts"
- Don't overstate automation. "Teaches your agent to consolidate related asks" is honest. "Automatically batches requests" implies system-level routing that the skill doesn't do.
- The benefit is still real — behavior change produces real cost and efficiency improvements

**When a skill needs to be an active tool:**
- Requires pre-response hooks or middleware (OpenClaw doesn't currently expose these)
- Requires script files (analyzer.js, optimizer.js) that actually run
- Example: a real token optimizer that reads context size and trims it before sending

**Bottom line:** Instruction-based skills are legitimate and valuable. Just be honest about the scope. Users trust skills that set accurate expectations.

---

## Version History

- **1.0.1** — Added "Skill Type: Behavior-Change vs. Active Tool" lesson from ClawSaver development
- **1.0.0** — Initial release. Research workflow, gap analysis framework, listing anatomy, marketplace patterns from Feb 2026 analysis.
