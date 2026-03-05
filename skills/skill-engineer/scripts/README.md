# Validation Scripts for skill-engineer

These scripts provide deterministic validation of skill artifacts. Run them during the review phase to catch errors before manual review.

---

## Scripts

### `check-completeness.sh`
**Purpose:** Verify all required skill files exist.

**Usage:**
```bash
bash scripts/check-completeness.sh /path/to/skill/
```

**Checks:**
- Required: SKILL.md, skill.yml, README.md
- Optional (warns if missing): tests/, scripts/, references/, CHANGELOG.md

**When to run:** After Designer produces artifacts, before Reviewer evaluation.

---

### `count-rubric-checks.sh`
**Purpose:** Count quality rubric checks in SKILL.md and verify the total matches expected (33).

**Usage:**
```bash
bash scripts/count-rubric-checks.sh /path/to/skill/SKILL.md
```

**Checks:**
- Counts SQ-A, SQ-B, SQ-C, SQ-D checks
- Counts SCOPE, OPSEC, REF, ARCH checks
- Verifies total = 33

**When to run:** When designing or refactoring skill-engineer itself, to ensure rubric integrity.

---

### `validate-scorecard.sh`
**Purpose:** Verify that the Quality Scorecard in README.md has correct math (individual scores sum to claimed total).

**Usage:**
```bash
bash scripts/validate-scorecard.sh /path/to/skill/README.md
```

**Checks:**
- Parses scorecard table from README
- Sums individual category scores
- Compares to claimed total
- Exit 0 if match, exit 1 if mismatch

**When to run:** After Orchestrator adds final scorecard to README, before git push.

---

### `quality-score.py`
**Purpose:** Parse a rubric audit markdown file and compute quality scores deterministically.

**Usage:**
```bash
python3 scripts/quality-score.py audits/{skill}-rubric.md
python3 scripts/quality-score.py audits/{skill}-rubric.md --pretty
```

**Output:** JSON to stdout containing:
- `total` — total score (sum of all parsed criteria)
- `max` — maximum possible score
- `percentage` — total/max as a percentage
- `rating` — Deploy (≥80%), Revise (60–79%), Redesign (40–59%), Reject (<40%)
- `sections` — per-section breakdown (SQ-A, SQ-B, SQ-C, SQ-D, AS)
- `criteria` — individual criterion scores with evidence

**Rubric file format expected:**
```markdown
| A1 | criterion description | **N** | evidence text |
```
Where `N` is the integer score (0–3). Section headings must contain `SQ-A`, `SQ-B`, etc.

**Example:**
```bash
python3 scripts/quality-score.py audits/skill-engineer-rubric.md --pretty
# Prints human-readable summary to stderr + JSON to stdout

python3 scripts/quality-score.py audits/skill-engineer-rubric.md | jq '.rating'
# "Deploy"
```

**When to run:** After any rubric audit file is created; as part of the audit pipeline.

---

### `validate-trigger.sh`
**Purpose:** Check skill.yml trigger phrases against tests/test-triggers.json and report coverage.

**Usage:**
```bash
bash scripts/validate-trigger.sh skills/{skill-name}/
bash scripts/validate-trigger.sh /path/to/skill/
```

**Checks:**
- skill.yml exists and has at least 3 trigger phrases (fails if fewer)
- tests/test-triggers.json exists (fails if missing)
- Counts positive (`shouldTrigger`) and negative (`shouldNotTrigger`) test cases
- Verifies minimum coverage: ≥3 positives and ≥3 negatives
- Checks each trigger phrase against positive test cases (warns if uncovered)
- Checks positive:negative ratio balance (warns if >3:1 skew)
- Reports summary with PASS/FAIL verdict

**Exit codes:**
- `0` — all checks passed
- `1` — one or more hard checks failed

**Example:**
```bash
bash scripts/validate-trigger.sh skills/skill-engineer/
# ✓ skill.yml found
# · Trigger phrases found: 15
# ✓ Trigger count is sufficient (15 ≥ 3)
# ✓ tests/test-triggers.json found
# ✓ Positive test coverage sufficient (15 ≥ 3)
# ✓ Negative test coverage sufficient (14 ≥ 3)
# ✓ Test balance is acceptable
# RESULT: ✅ PASS
```

**When to run:** After Designer writes skill.yml and test-triggers.json; before Reviewer evaluation.

---

## Integration with Reviewer Workflow

The Reviewer should run these scripts **BEFORE** manual evaluation:

```bash
# 1. Check file completeness
bash scripts/check-completeness.sh /path/to/skill/

# 2. Validate trigger phrases
bash scripts/validate-trigger.sh /path/to/skill/

# 3. Compute quality score from rubric audit (if audit file exists)
python3 scripts/quality-score.py audits/{skill}-rubric.md --pretty

# 4. Verify rubric check count (for skill-engineer itself)
bash scripts/count-rubric-checks.sh /path/to/skill/SKILL.md

# 5. After Orchestrator adds scorecard, validate math
bash scripts/validate-scorecard.sh /path/to/skill/README.md
```

These deterministic checks catch mechanical errors, allowing the Reviewer to focus on judgment-based evaluation (clarity, design quality, edge cases).

## Script Dependency Requirements

| Script | Runtime | Notes |
|--------|---------|-------|
| `check-completeness.sh` | bash | No external deps |
| `count-rubric-checks.sh` | bash | No external deps |
| `validate-scorecard.sh` | bash | No external deps |
| `quality-score.py` | python3 | stdlib only (json, re, os, sys) |
| `validate-trigger.sh` | bash + python3 | python3 for JSON parsing |

All scripts are tested on macOS (Darwin arm64) and Ubuntu Linux.
