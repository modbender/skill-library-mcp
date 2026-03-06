# Pre-Flight Checks Skill

**Test-driven behavioral verification for AI agents**

Catches "silent degradation" - when agent loads memory but doesn't apply learned behaviors.

## Quick Start

```bash
# Install
cd ~/.openclaw/workspace/skills
git clone https://github.com/IvanMMM/preflight-checks.git

# Initialize in workspace
cd ~/.openclaw/workspace
./skills/preflight-checks/scripts/init.sh

# Edit your checks and answers
vim PRE-FLIGHT-CHECKS.md
vim PRE-FLIGHT-ANSWERS.md

# Update AGENTS.md to run checks after loading memory
```

## What It Does

**Problem:** Agent knows rules but doesn't follow them.

```
Memory loaded ✅ → Rules understood ✅ → Behavior wrong ❌
```

**Solution:** Behavioral unit tests.

```
1. Agent loads memory
2. Agent reads PRE-FLIGHT-CHECKS.md
3. Agent answers scenarios
4. Agent compares with PRE-FLIGHT-ANSWERS.md
5. Agent reports score: N/N ✅ or failures ❌
```

## Files

```
skills/preflight-checks/
├── SKILL.md              # Full documentation
├── README.md             # This file
├── templates/
│   ├── CHECKS-template.md    # Blank template
│   └── ANSWERS-template.md   # Blank template
├── scripts/
│   ├── init.sh               # Setup in workspace
│   └── add-check.sh          # Add new check
└── examples/
    ├── CHECKS-prometheus.md  # Real example (23 checks)
    └── ANSWERS-prometheus.md # Real answers
```

## Usage

### Add Check

```bash
./skills/preflight-checks/scripts/add-check.sh
# Interactive prompts guide you through
```

### Run Checks

**Manual (recommended for agents):**
```
1. Read PRE-FLIGHT-CHECKS.md
2. Answer each CHECK-N
3. Compare with PRE-FLIGHT-ANSWERS.md
4. Report score
```

**Automated (optional, TBD):**
```bash
./skills/preflight-checks/scripts/run-checks.sh
```

## Examples

See `examples/` directory for real working pre-flight system:
- 23 behavioral checks
- Categories: Identity, Saving, Communication, Telegram, Anti-Patterns
- Covers common degradation patterns

## When to Use

- ✅ Building agent with persistent memory
- ✅ Want behavioral consistency across sessions
- ✅ Testing agent after updates
- ✅ Catching drift/degradation early

## Integration

Add to `AGENTS.md`:

```markdown
## Every Session

1. Read SOUL.md
2. Read USER.md
3. Read memory/YYYY-MM-DD.md
4. If main session: Read MEMORY.md
5. **Run Pre-Flight Checks**

### Pre-Flight Checks

1. Read PRE-FLIGHT-CHECKS.md
2. Answer each scenario
3. Compare with PRE-FLIGHT-ANSWERS.md
4. Report discrepancies
```

## Learn More

See `SKILL.md` for:
- Detailed problem description
- Check writing guidelines
- Scoring rubrics
- Advanced usage (CI/CD, automation)
- Contributing guide

## Credits

Created by Prometheus (OpenClaw agent)  
Inspired by aviation pre-flight checklists

## License

MIT
