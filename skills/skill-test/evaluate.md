# Multi-Agent Evaluation

Spawn specialized reviewers for thorough skill evaluation.

## Reviewer Types

### Structure Reviewer
Questions:
- Is SKILL.md under 80 lines?
- Are details in auxiliary files?
- Clear progressive disclosure?
- No README/CHANGELOG clutter?

### Safety Reviewer
Questions:
- Any personal data? (names, emails, paths)
- Any credentials or secrets?
- Model-specific references? (Claude, GPT)
- Dangerous patterns or commands?

### Usefulness Reviewer
Questions:
- Clear what it does?
- Clear WHEN to use it?
- Instructions actionable?
- Would this actually help?

### Domain Reviewer (if applicable)
Questions:
- Technically correct for the domain?
- Best practices followed?
- Missing important aspects?
- Outdated information?

## Spawning Reviewers

For each reviewer, spawn sub-agent with:
- The skill content to review
- Specific questions to answer
- Request: concise findings + recommendation (approve/concerns/reject)

## Synthesizing Results

Collect all reviewer outputs:

| Reviewer | Verdict | Key Finding |
|----------|---------|-------------|
| Structure | ✅/⚠️/❌ | [summary] |
| Safety | ✅/⚠️/❌ | [summary] |
| Usefulness | ✅/⚠️/❌ | [summary] |
| Domain | ✅/⚠️/❌ | [summary] |

## Final Recommendation

- **All ✅** → Recommend
- **Any ❌** → Don't recommend (explain why)
- **Mixed ⚠️** → Present concerns, let user decide

## Handling Conflicts

If reviewers disagree:
- Present both perspectives
- Explain the tradeoff
- Let user make informed choice
