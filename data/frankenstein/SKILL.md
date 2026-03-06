---
name: frankenstein
version: 1.2.0
description: "Combine the best parts of multiple skills into one. Searches ClawHub, GitHub, skills.sh, skillsmp.com and other AI skill repos. Analyzes each safely, compares features, and builds a combined 'Frankenstein' skill with the best of each. Uses skill-auditor for security scanning and sandwrap for safe analysis. Use when: (1) Multiple skills exist for same purpose, (2) Want best-of-breed combination, (3) Building a comprehensive skill from fragments."
---

# Frankenstein

## Model Requirements

**Default: Opus (or best available thinking model)**

Frankenstein requires deep reasoning to:
- Compare multiple skill approaches
- Identify subtle methodology differences
- Synthesize the best parts creatively
- Catch security/quality issues others miss

Only use a smaller model if user explicitly requests it for cost reasons. The synthesis quality depends heavily on reasoning depth.

Create monster skills by combining the best parts of existing ones.

## Quick Start

```
Frankenstein me an SEO audit skill
```

## How It Works

### Step 1: Search All Sources

Search EVERY AI skills repository for matching skills:

**1. ClawHub (primary)**
```bash
clawhub search "[topic]" --registry "https://clawhub.ai"
```

**2. GitHub**
```
Search: "[topic] AI skill" OR "[topic] claude skill" OR "[topic] agent skill"
Look for: SKILL.md, CLAUDE.md, or similar agent instruction files
```

**3. skills.sh**
```
https://skills.sh/search?q=[topic]
```

**4. skillsmp.com (Skills Marketplace)**
```
https://skillsmp.com/search/[topic]
```

**5. Other sources to check:**
- Anthropic's skill examples
- OpenAI GPT configurations (convert to skill format)
- LangChain agent templates
- AutoGPT/AgentGPT skill repos

**Gather all candidates before filtering.** More sources = better Frankenstein.

### Step 2: Security Scan
Run each skill through skill-auditor. Skip any with HIGH risk scores.

For each skill found:
- Install to temp directory
- Run skill-auditor scan
- Score >= 7 = SAFE (proceed)
- Score < 7 = RISKY (skip with warning)

### Step 3: Safe Analysis
Analyze safe skills in sandwrap read-only mode.

For each safe skill, extract:
- Core features (what it does)
- Methodology (how it approaches the problem)
- Scripts/tools (reusable code)
- Unique strengths (what makes it special)
- Weaknesses (what's missing)

### Step 4: Compare
Build comparison matrix:

| Feature | skill-A | skill-B | skill-C | WINNER |
|---------|---------|---------|---------|--------|
| Feature 1 | Yes | No | Yes | A, C |
| Feature 2 | Basic | Advanced | None | B |
| Feature 3 | No | No | Yes | C |

### Step 5: Synthesize
Take the winning approach for each feature:
- Feature 1 methodology from skill-A
- Feature 2 implementation from skill-B
- Feature 3 approach from skill-C

### Step 6: Build Initial Draft
Use skill-creator to assemble the Frankenstein skill:
- Combine winning features
- Resolve conflicts (if two approaches clash)
- Write unified SKILL.md
- Include scripts from winners
- Document sources

### Step 7: Vetting Loop (CRITICAL)

**Run plan → test → improve loop until 3 stable passes:**

```
Pass 1:
  1. Read draft
  2. Try to break it (find holes, contradictions, gaps)
  3. Document issues
  4. Fix them
  
Pass 2:
  1. Read improved version
  2. Actively try to find MORE issues
  3. Fix any found
  
Pass 3+:
  Continue until you genuinely try to improve
  but can't find significant issues
```

**What to look for each pass:**
- Missing features that sources had
- Contradictions between combined approaches
- Vague instructions that aren't actionable
- Token waste (verbose where concise works)
- Security gaps
- Broken references to files/scripts

**Document in VETTING-LOG.md:**
- Each pass number
- Issues found
- Fixes applied
- Why considered stable

**Only proceed when:**
- 3 consecutive passes with no major issues
- Minor issues documented as known limitations

### Step 8: Human Review
Present the vetted skill for approval:
- Show what came from where
- Highlight conflicts resolved
- Show vetting summary
- Ask for final OK before saving

## Output

Creates a new skill with:
- Best features from all analyzed skills
- Clear attribution (credits source skills)
- Security-scanned components only
- Unified documentation

## Example Session

User: "Frankenstein me an SEO audit skill"

Frankenstein:
```
Searching ClawHub for "SEO audit"...
Found 5 skills:
  1. seo-audit (coreyhaines31)
  2. audit-website (squirrelscan)
  3. seo-optimizer (local)
  4. technical-seo (unknown)
  5. seo-checker (unknown)

Security scanning...
  ✓ seo-audit: SAFE (8/10)
  ✓ audit-website: SAFE (7/10)
  ✓ seo-optimizer: SAFE (9/10)
  ✗ technical-seo: RISKY (4/10) - skipping
  ✗ seo-checker: RISKY (3/10) - skipping

Analyzing 3 safe skills...

Comparison:
| Feature              | seo-audit | audit-website | seo-optimizer |
|----------------------|-----------|---------------|---------------|
| Methodology depth    | ★★★★★     | ★★★           | ★★★★          |
| Automated rules      | None      | 230+          | 50+           |
| Auto-fix capability  | No        | No            | Yes           |
| CLI tool             | No        | squirrel      | No            |
| E-E-A-T coverage     | Yes       | Yes           | Partial       |

Recommended combination:
- Methodology: seo-audit (best framework)
- Rules engine: audit-website (230+ rules via squirrel CLI)
- Auto-fix: seo-optimizer (automated fixes)
- E-E-A-T: seo-audit (comprehensive)

Build this Frankenstein? [Yes/No]
```

## Dependencies

This skill uses:
- clawhub CLI (search/install)
- skill-auditor (security scanning)
- sandwrap (safe analysis)
- skill-creator (building)

## Spawning Sub-Agents

When spawning analysis sub-agents, always use Opus (or best thinking model) unless user explicitly requests otherwise:

```
sessions_spawn(
  task: "FRANKENSTEIN ANALYSIS: [topic]...",
  model: "opus"
)
```

Cheaper models miss nuances between skills and produce shallow combinations.

## Limitations

- Only combines publicly available skills
- Skips skills that fail security scan
- Cannot resolve deep architectural conflicts
- Human judgment needed for final synthesis
- Quality depends on available skills

## Credits

When a Frankenstein skill is built, it includes attribution:
```
## Sources
Built from best parts of:
- seo-audit by coreyhaines31 (methodology)
- audit-website by squirrelscan (rules engine)
- seo-optimizer (auto-fix)
```
