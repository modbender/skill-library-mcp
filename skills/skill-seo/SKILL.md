---
name: skill-seo
description: "Optimize your ClawHub skill for maximum discoverability. Analyzes and rewrites SKILL.md description for vector search ranking, suggests keyword coverage, checks competitor positioning, and plans update cadence. Use when you want to 'improve skill SEO', 'get more downloads', 'optimize skill description', 'skill not showing in search', 'increase skill visibility', 'clawhub ranking', 'skill marketing', 'skill discovery', 'why no one finds my skill', 'skill description optimization', 'publish strategy', 'skill metadata', 'get featured on clawhub'. Works with any skill folder — just point it at your SKILL.md."
---

# Skill SEO Optimizer 🔍

Get your ClawHub skill found. This skill analyzes your SKILL.md and optimizes it for ClawHub's vector search, explore rankings, and agent auto-discovery.

## Quick Start

```
Optimize my skill for ClawHub: [path/to/skill/SKILL.md]
```

The agent will audit your skill and output an optimized version.

## How ClawHub Discovery Works

Skills are found through three channels. Each needs different optimization:

### Channel 1: `clawhub search` (Vector Search) — 70% of discovery

ClawHub uses **semantic vector search** on the `description` field in YAML frontmatter. This is NOT keyword matching — it's meaning matching.

**What gets indexed:** Only the `description` field.
**What does NOT get indexed:** The markdown body, scripts, references, filenames.

**Optimization rules:**

1. **Cover synonyms and variations**
   ```yaml
   # ❌ Bad: narrow description
   description: Generate weekly reports from Reddit data.
   
   # ✅ Good: covers how users actually search
   description: "Generate weekly trend reports from Reddit, Twitter/X, and 
     YouTube. Social media monitoring, content research, competitive analysis, 
     trend tracking. Use when asked to 'monitor trends', 'weekly report', 
     'what's trending', 'social listening', 'content ideas from social media',
     'track competitors', 'find viral topics'."
   ```

2. **Include trigger phrases** — Write the exact phrases users say:
   - "how do I..."
   - "is there a skill that..."  
   - "I want to..."
   - "can my agent..."

3. **Name the problem, not just the solution**
   ```yaml
   # ❌ Solution only
   description: Agent journaling and mood tracking.
   
   # ✅ Problem + solution
   description: "Reduce repetitive AI output and pattern rigidity. Agent 
     journaling, mood tracking, creative refresh. Fix agent burnout, boring 
     responses, lack of personality."
   ```

4. **Optimal description length:** 150-300 words. Too short = misses search terms. Too long = dilutes relevance.

### Channel 2: `clawhub explore` (Rankings) — 20% of discovery

Users browse by: `newest`, `trending`, `downloads`, `rating`.

**Optimization rules:**

1. **Update frequently** — Each version bump puts you in `newest`
   - Ship v0.1.0, then v0.1.1 next week, v0.1.2 the week after
   - Even small improvements (typo fix, example added) justify a patch
   
2. **Version strategically** — Big features = minor bump (0.2.0), polish = patch (0.1.1)

3. **Seed initial downloads** — Install your own skill across your agents to get off zero

### Channel 3: Agent Auto-Discovery (find-skills) — 10% of discovery

Some agents have `find-skills` installed, which searches ClawHub when users ask for capabilities.

**Optimization rules:**
- Description must match natural language questions
- Include the phrase patterns from Channel 1

## Audit Checklist

Run this against any SKILL.md:

```markdown
## Description Audit
- [ ] Length: 150-300 words?
- [ ] Contains 10+ synonym/variation phrases?
- [ ] Contains 5+ "trigger phrases" (user natural language)?
- [ ] Names the PROBLEM, not just the solution?
- [ ] Mentions target audience/use case?
- [ ] Includes negative triggers ("not showing", "can't find", "no results")?

## Competitive Audit  
- [ ] Searched ClawHub for your top 5 keywords — where do you rank?
- [ ] Identified top 3 competing skills?
- [ ] Description differentiates from competitors?

## Freshness Audit
- [ ] Updated in the last 2 weeks?
- [ ] Changelog or version history maintained?
- [ ] Plan for next 3 patch releases?
```

## Workflow: Optimize an Existing Skill

### Step 1: Extract current state
```bash
# Read the current description
head -20 path/to/SKILL.md

# Check current search ranking
clawhub search "your main keyword" --limit 10
clawhub search "alternate keyword" --limit 10
```

### Step 2: Competitor analysis
```bash
# Find competing skills
clawhub search "your niche" --limit 10
# Inspect top results
clawhub inspect competitor-skill-name
```

### Step 3: Generate optimized description

**Formula:**
```
[Core capability in 1 sentence]
[3-4 specific features/modules]
[5+ trigger phrases in natural language]
[Target audience]
[Differentiator from competitors]
[Token/resource cost if relevant]
```

### Step 4: Publish and verify
```bash
clawhub publish ./your-skill --version X.Y.Z

# Wait 2-3 minutes for indexing, then verify
clawhub search "your keyword 1" --limit 5
clawhub search "your keyword 2" --limit 5
clawhub search "natural language question" --limit 5
```

### Step 5: Track and iterate
- Check ranking weekly for your top 5 keywords
- If dropping, update description and bump version
- Monitor competitors for new entrants

## Anti-Patterns

- ❌ **Keyword stuffing with irrelevant terms** — Vector search penalizes semantic mismatch
- ❌ **Description longer than 400 words** — Dilutes relevance signal
- ❌ **Generic descriptions** — "A useful skill for various tasks" matches nothing
- ❌ **Never updating** — Falls off newest, loses freshness signal
- ❌ **Ignoring competitors** — If 3 skills match the same query, differentiation matters
