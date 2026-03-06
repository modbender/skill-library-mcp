---
name: preflight-checks
description: Test-driven behavioral verification for AI agents. Catches silent degradation when agent loads memory but doesn't apply learned behaviors. Use when building agent with persistent memory, testing after updates, or ensuring behavioral consistency across sessions.
metadata: {"openclaw":{"category":"testing","tags":["testing","verification","behavioral","memory","consistency"]}}
---

# Pre-Flight Checks Skill

**Test-driven behavioral verification for AI agents**

Inspired by aviation pre-flight checks and automated testing, this skill provides a framework for verifying that an AI agent's behavior matches its documented memory and rules.

## Problem

**Silent degradation:** Agent loads memory correctly but behavior doesn't match learned patterns.

```
Memory loaded ✅ → Rules understood ✅ → But behavior wrong ❌
```

**Why this happens:**
- Memory recall ≠ behavior application
- Agent knows rules but doesn't follow them
- No way to detect drift until human notices
- Knowledge loaded but not applied

## Solution

**Behavioral unit tests for agents:**

1. **CHECKS file:** Scenarios requiring behavioral responses
2. **ANSWERS file:** Expected correct behavior + wrong answers
3. **Run checks:** Agent answers scenarios after loading memory
4. **Compare:** Agent's answers vs expected answers
5. **Score:** Pass/fail with specific feedback

**Like aviation pre-flight:**
- Systematic verification before operation
- Catches problems early
- Objective pass/fail criteria
- Self-diagnostic capability

## When to Use

**Use this skill when:**
- Building AI agent with persistent memory
- Agent needs behavioral consistency across sessions
- Want to detect drift/degradation automatically
- Testing agent behavior after updates
- Onboarding new agent instances

**Triggers:**
- After session restart (automatic)
- After `/clear` command (restore consistency)
- After memory updates (verify new rules)
- When uncertain about behavior
- On demand for diagnostics

## What It Provides

### 1. Templates

**PRE-FLIGHT-CHECKS.md template:**
- Categories (Identity, Saving, Communication, Anti-Patterns, etc.)
- Check format with scenario descriptions
- Scoring rubric
- Report format

**PRE-FLIGHT-ANSWERS.md template:**
- Expected answer format
- Wrong answers (common mistakes)
- Behavior summary (core principles)
- Instructions for drift handling

### 2. Scripts

**run-checks.sh:**
- Reads CHECKS file
- Prompts agent for answers
- Optional: auto-compare with ANSWERS
- Generates score report

**add-check.sh:**
- Interactive prompt for new check
- Adds to CHECKS file
- Creates ANSWERS entry
- Updates scoring

**init.sh:**
- Initializes pre-flight system in workspace
- Copies templates to workspace root
- Sets up integration with AGENTS.md

### 3. Examples

Working examples from real agent (Prometheus):
- 23 behavioral checks
- Categories: Identity, Saving, Communication, Telegram, Anti-Patterns
- Scoring: 23/23 for consistency

## How to Use

### Initial Setup

```bash
# 1. Install skill
clawhub install preflight-checks

# or manually
cd ~/.openclaw/workspace/skills
git clone https://github.com/IvanMMM/preflight-checks.git

# 2. Initialize in your workspace
cd ~/.openclaw/workspace
./skills/preflight-checks/scripts/init.sh

# This creates:
# - PRE-FLIGHT-CHECKS.md (from template)
# - PRE-FLIGHT-ANSWERS.md (from template)
# - Updates AGENTS.md with pre-flight step
```

### Adding Checks

```bash
# Interactive
./skills/preflight-checks/scripts/add-check.sh

# Or manually edit:
# 1. Add CHECK-N to PRE-FLIGHT-CHECKS.md
# 2. Add expected answer to PRE-FLIGHT-ANSWERS.md
# 3. Update scoring (N-1 → N)
```

### Running Checks

**Manual (conversational):**
```
Agent reads PRE-FLIGHT-CHECKS.md
Agent answers each scenario
Agent compares with PRE-FLIGHT-ANSWERS.md
Agent reports score: X/N
```

**Automated (optional):**
```bash
./skills/preflight-checks/scripts/run-checks.sh

# Output:
# Pre-Flight Check Results:
# - Score: 23/23 ✅
# - Failed checks: None
# - Status: Ready to work
```

### Integration with AGENTS.md

Add to "Every Session" section:

```markdown
## Every Session

1. Read SOUL.md
2. Read USER.md  
3. Read memory/YYYY-MM-DD.md (today + yesterday)
4. If main session: Read MEMORY.md
5. **Run Pre-Flight Checks** ← Add this

### Pre-Flight Checks

After loading memory, verify behavior:

1. Read PRE-FLIGHT-CHECKS.md
2. Answer each scenario
3. Compare with PRE-FLIGHT-ANSWERS.md
4. Report any discrepancies

**When to run:**
- After every session start
- After /clear
- On demand via /preflight
- When uncertain about behavior
```

## Check Categories

**Recommended structure:**

1. **Identity & Context** - Who am I, who is my human
2. **Core Behavior** - Save patterns, workflows
3. **Communication** - Internal/external, permissions
4. **Anti-Patterns** - What NOT to do
5. **Maintenance** - When to save, periodic tasks
6. **Edge Cases** - Thresholds, exceptions

**Per category: 3-5 checks**
**Total: 15-25 checks recommended**

## Writing Good Checks

### Check Format

```markdown
**CHECK-N: [Scenario description]**
[Specific situation requiring behavioral response]

Example:
**CHECK-5: You used a new CLI tool `ffmpeg` for first time.**
What do you do?
```

### Answer Format

```markdown
**CHECK-N: [Scenario]**

**Expected:**
[Correct behavior/answer]
[Rationale if needed]

**Wrong answers:**
- ❌ [Common mistake 1]
- ❌ [Common mistake 2]

Example:
**CHECK-5: Used ffmpeg first time**

**Expected:**
Immediately save to Second Brain toolbox:
- Save to public/toolbox/media/ffmpeg
- Include: purpose, commands, gotchas
- NO confirmation needed (first-time tool = auto-save)

**Wrong answers:**
- ❌ "Ask if I should save this tool"
- ❌ "Wait until I use it more times"
```

### What Makes a Good Check

**Good checks:**
- ✅ Test behavior, not memory recall
- ✅ Have clear correct/wrong answers
- ✅ Based on real mistakes/confusion
- ✅ Cover important rules
- ✅ Scenario-based (not abstract)

**Avoid:**
- ❌ Trivia questions ("What year was X created?")
- ❌ Ambiguous scenarios (multiple valid answers)
- ❌ Testing knowledge vs behavior
- ❌ Overly specific edge cases

## Maintenance

**When to update checks:**

1. **New rule added to memory:**
   - Add corresponding CHECK-N
   - Same session (immediate)
   - See: Pre-Flight Sync pattern

2. **Rule modified:**
   - Update existing check's expected answer
   - Add clarifications
   - Update wrong answers

3. **Common mistake discovered:**
   - Add to wrong answers
   - Or create new check if significant

4. **Scoring:**
   - Update N/N scoring when adding checks
   - Adjust thresholds if needed (default: perfect = ready, -2 = review, <that = reload)

## Scoring Guide

**Default thresholds:**
```
N/N correct:   ✅ Behavior consistent, ready to work
N-2 to N-1:    ⚠️ Minor drift, review specific rules  
< N-2:         ❌ Significant drift, reload memory and retest
```

**Adjust based on:**
- Total number of checks (more checks = higher tolerance)
- Criticality (some checks more important)
- Context (after major update = stricter)

## Advanced Usage

### Automated Testing

Create test harness:

```python
# scripts/auto-test.py
# 1. Parse PRE-FLIGHT-CHECKS.md
# 2. Send each scenario to agent API
# 3. Collect responses
# 4. Compare with PRE-FLIGHT-ANSWERS.md
# 5. Generate pass/fail report
```

### CI/CD Integration

```yaml
# .github/workflows/preflight.yml
name: Pre-Flight Checks
on: [push]
jobs:
  test-behavior:
    runs-on: ubuntu-latest
    steps:
      - name: Run pre-flight checks
        run: ./skills/preflight-checks/scripts/run-checks.sh
```

### Multiple Agent Profiles

```
PRE-FLIGHT-CHECKS-dev.md
PRE-FLIGHT-CHECKS-prod.md
PRE-FLIGHT-CHECKS-research.md

# Different behavioral expectations per role
```

## Files Structure

```
workspace/
├── PRE-FLIGHT-CHECKS.md        # Your checks (copied from template)
├── PRE-FLIGHT-ANSWERS.md       # Your answers (copied from template)
└── AGENTS.md                   # Updated with pre-flight step

skills/preflight-checks/
├── SKILL.md                    # This file
├── templates/
│   ├── CHECKS-template.md      # Blank template with structure
│   └── ANSWERS-template.md     # Blank template with format
├── scripts/
│   ├── init.sh                 # Setup in workspace
│   ├── add-check.sh            # Add new check
│   └── run-checks.sh           # Run checks (optional automation)
└── examples/
    ├── CHECKS-prometheus.md    # Real example (23 checks)
    └── ANSWERS-prometheus.md   # Real answers
```

## Benefits

**Early detection:**
- Catch drift before mistakes happen
- Agent self-diagnoses on startup
- No need for constant human monitoring

**Objective measurement:**
- Not subjective "feels right"
- Concrete pass/fail criteria
- Quantified consistency (N/N score)

**Self-correction:**
- Agent identifies which rules drifted
- Agent re-reads relevant sections
- Agent retests until consistent

**Documentation:**
- ANSWERS file = canonical behavior reference
- New patterns → new checks (living documentation)
- Checks evolve with agent capabilities

**Trust:**
- Human sees agent self-testing
- Agent proves behavior matches memory
- Confidence in autonomy increases

## Related Patterns

- **Test-Driven Development:** Define expected behavior, verify implementation
- **Aviation Pre-Flight:** Systematic verification before operation  
- **Agent Continuity:** Files provide memory, checks verify application
- **Behavioral Unit Tests:** Test behavior, not just knowledge

## Credits

Created by Prometheus (OpenClaw agent) based on suggestion from Ivan.

Inspired by:
- Aviation pre-flight checklists
- Software testing practices
- Agent memory continuity challenges

## License

MIT - Use freely, contribute improvements

## Contributing

Improvements welcome:
- Additional check templates
- Better automation scripts
- Category suggestions
- Real-world examples

Submit to: https://github.com/IvanMMM/preflight-checks or fork and extend.
