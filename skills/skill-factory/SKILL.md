---
name: skill-factory
description: "Create, evaluate, improve, benchmark, and publish OpenClaw skills. Use when building a new skill from scratch, iterating on an existing skill, running evals to measure quality, comparing skill versions, or analyzing patterns across installed skills to synthesize new ones. Triggers on: 'create a skill', 'build a skill', 'make a skill', 'eval this skill', 'improve this skill', 'benchmark skill versions', 'analyze skill patterns', 'synthesize skill from patterns', 'package skill', 'publish skill'."
---

# Skill Creator

Build, refine, and publish OpenClaw skills. Supports six modes.

## Modes at a Glance

| Mode | When to Use | Output |
|------|-------------|--------|
| **Create** | New skill from scratch | `<name>/SKILL.md` + resources |
| **Eval** | Measure skill quality | Run report + pass/fail |
| **Improve** | Iterate an existing skill | New version with changelog |
| **Benchmark** | Compare two skill versions | Winner + delta analysis |
| **Analyze** | Extract reusable patterns | `patterns.md` report |
| **Synthesize** | Build skill from patterns | Scaffolded `SKILL.md` |

---

## Mode 1: Create

Build a skill from scratch in 6 steps.

### Step 1 — Understand
Clarify before writing a single line:
- What does this skill do that no existing skill does?
- Who triggers it and when? (the `description` field drives triggering)
- What CLI tools, APIs, or files does it need?
- What's the output format?

Run `scripts/analyze_patterns.py --query "<skill concept>"` to see if relevant patterns already exist.

### Step 2 — Plan
Write a one-paragraph spec covering: trigger conditions, happy path, error cases, output format. Confirm with user if uncertain.

### Step 3 — Init

Scripts are bundled in `scripts/` — no external path needed:

```bash
# From your workspace skills directory:
python3 $(openclaw skills info skill-creator --json 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin).get('path',''))")/scripts/init_skill.py \
  <skill-name> \
  --path ~/.openclaw/workspace/skills/ \
  --resources scripts,references \
  --examples
```

Or locate the skill dir and use relative path:
```bash
SKILL_DIR=$(dirname $(find ~/.openclaw/workspace/skills ~/.nvm -name "init_skill.py" 2>/dev/null | head -1))
python3 "$SKILL_DIR/init_skill.py" <skill-name> --path ~/.openclaw/workspace/skills/ --resources scripts,references
```

This creates:
```
<skill-name>/
  SKILL.md          # Edit this
  scripts/          # Helper scripts
  references/       # Reference docs, cheat sheets
  _meta.json        # Auto-populated on publish
```

### Step 4 — Write SKILL.md

**Frontmatter rules:**
```yaml
---
name: my-skill-name          # lowercase-hyphen, max 64 chars
description: "One sentence: what it does AND when to use it. Include trigger phrases."
---
```

**Body structure:**
```markdown
# Skill Title

Brief one-liner.

## Quick Start
[Most common usage — 3-5 lines max]

## Commands / Recipes
[Concrete examples with real output]

## Reference
[Full option tables, edge cases, advanced usage]
```

**Progressive disclosure rules:**
- Frontmatter: always loaded (~100 words) — make it count
- Body: loaded on trigger (<500 lines) — stay under limit
- Bundled resources: loaded on demand — put verbosity here

### Step 5 — Package
```bash
# package_skill.py is bundled in this skill's scripts/ directory:
SKILL_SCRIPTS="$(dirname "$(find ~/.openclaw/workspace/skills/skill-creator ~/.nvm -name "package_skill.py" 2>/dev/null | head -1)")"
python3 "$SKILL_SCRIPTS/package_skill.py" ~/.openclaw/workspace/skills/<skill-name>
```
Validates structure, outputs `<skill-name>.skill` zip.

### Step 6 — Iterate
Run evals (Mode 2) → identify failures → update SKILL.md → re-package → repeat.

---

## Mode 2: Eval

Measure skill quality against defined expectations.

### Setup
Create `evals/evals.json`:
```json
[
  {
    "id": "basic-create",
    "prompt": "Create a skill that sends a Slack message",
    "expected_output": "SKILL.md with slack-notifier name and working command",
    "assertions": [
      "contains SKILL.md frontmatter with name and description",
      "contains at least one bash command example",
      "description includes trigger phrases"
    ]
  }
]
```

### Eval Run
For each eval case:
1. Execute the prompt using current skill
2. Grade against `assertions` (pass/fail per assertion)
3. Log result to `evals/runs/<timestamp>.json`

### Run Report Format
```json
{
  "skill": "skill-creator",
  "version": "1.0.0",
  "timestamp": "2026-02-22T03:00:00Z",
  "pass_rate": 0.85,
  "cases": [
    { "id": "basic-create", "passed": true, "assertions_passed": 3, "assertions_total": 3 }
  ]
}
```

---

## Mode 3: Improve

Iterate on an existing skill using eval feedback.

### Improvement Loop
```
1. Run evals → identify failing assertions
2. Read current SKILL.md
3. Draft changes targeting failures
4. Write new version (increment semver in _meta.json)
5. Re-run evals → confirm pass rate improved
6. Update history.json
```

### history.json
Track all versions at `evals/history.json`:
```json
[
  {
    "version": "1.0.0",
    "parent": null,
    "expectation_pass_rate": 0.70,
    "is_current_best": false,
    "notes": "Initial version"
  },
  {
    "version": "1.1.0",
    "parent": "1.0.0",
    "expectation_pass_rate": 0.85,
    "is_current_best": true,
    "notes": "Improved trigger description, added Synthesize mode"
  }
]
```

---

## Mode 4: Benchmark

Blind A/B comparison of two skill versions.

### Process
1. Run identical eval suite against version A and version B
2. Collect raw outputs without labels
3. Compare blind (no version labels) → pick winner per case
4. Reveal versions, compute delta
5. Recommend: keep A, adopt B, or cherry-pick specific cases

### Benchmark Output
```
Version A: 1.0.0  pass_rate=0.70
Version B: 1.1.0  pass_rate=0.85
Delta: +0.15 (B wins)
Regressions: 0
Recommendation: Adopt B
```

---

## Mode 5: Analyze Patterns

Scan installed skills to extract reusable building blocks.

```bash
python3 ~/.openclaw/workspace/skills/skill-creator/scripts/analyze_patterns.py \
  --scan-dirs ~/.openclaw/workspace/skills/,~/.nvm/versions/node/v22.22.0/lib/node_modules/openclaw/skills/ \
  --output ~/.openclaw/workspace/skills/skill-creator/references/patterns.md
```

What it extracts:
- **Trigger phrases** — common description keywords that activate skills
- **Tool patterns** — CLI tools, APIs, Docker patterns used across skills
- **Output formats** — JSON schemas, markdown templates, log formats
- **Structural patterns** — how skills organize commands/recipes
- **Error handling patterns** — retry logic, circuit breakers, fallbacks

See `references/patterns.md` for the current extracted pattern library.

---

## Mode 6: Synthesize from Patterns

Build a new skill scaffold by combining patterns from the library.

### Usage
When asked to create a skill in a domain that resembles existing skills:

1. Run `Analyze Patterns` first
2. Query `references/patterns.md` for relevant patterns
3. Compose a SKILL.md that combines:
   - Best trigger phrases from similar skills
   - Relevant tool/API patterns
   - Appropriate output format
   - Error handling from most robust similar skill

### Example
"Create a skill for Twitter scraping":
- Pull trigger phrases from `reddit-scraper`
- Pull CDP/browser patterns from `fast-browser-use`
- Pull output format (JSON array) from `crypto-market-data`
- Synthesize into `twitter-scraper/SKILL.md`

---

## Skill Anatomy Quick Reference

```
<skill-name>/
  SKILL.md           # Required: frontmatter + body
  scripts/           # Helper Python/bash scripts
  references/        # Cheat sheets, API docs, schemas
  assets/            # Images, templates
  evals/
    evals.json       # Test cases
    runs/            # Eval run results
    history.json     # Version history
  _meta.json         # Publishing metadata
```

**_meta.json template:**
```json
{
  "ownerId": "",
  "slug": "skill-name",
  "version": "1.0.0",
  "publishedAt": null
}
```

---

## Publishing to OpenClaw Community

Registry: **clawhub.com** — use the `clawhub` CLI (already installed).

```bash
# 1. Login (opens browser once)
clawhub login

# 2. Publish directly from skill folder — no .skill zip needed
clawhub publish ~/.openclaw/workspace/skills/<skill-name> \
  --version 1.0.0 \
  --changelog "Initial release"

# 3. Or sync all workspace skills at once:
clawhub sync --workdir ~/.openclaw/workspace --dir skills
```

1. Ensure `_meta.json` has correct `slug` and `version`
2. Run full eval suite — pass rate must be ≥ 0.80
3. `clawhub login` (one-time browser auth)
4. `clawhub publish <skill-folder>`
5. Verify at clawhub.com/skills/<slug>

**Quality bar for publishing:**
- [ ] Description triggers correctly (test with 3+ natural phrasings)
- [ ] At least 3 concrete command examples with real output
- [ ] Error cases documented
- [ ] Eval pass rate ≥ 0.80
- [ ] `_meta.json` complete
