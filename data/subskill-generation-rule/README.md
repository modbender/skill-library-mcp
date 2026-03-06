# subskill-generate-rule

Defines file placement rules for skill evolution, so the main skill root stays clean and maintainable.

## Rules

1. Store newly generated recommendation/analysis artifacts in `data/`.
2. Put newly generated feature scripts in `subskills/<feature>/`.
3. Use one folder per feature under `subskills/`.
4. Add a local `SKILL.md` inside each feature folder when usage instructions are needed.
5. Do not place one-off scripts or generated artifacts in the skill root.

## Recommended Layout

```text
<skill>/
  SKILL.md
  config.json
  data/
  subskills/
    <feature-a>/
      SKILL.md
      *.py
    <feature-b>/
      SKILL.md
      *.py
```

## Examples

- Config optimization script: `subskills/config-optimization/optimize_from_aggressive.py`
- Daily recommendation script: `subskills/daily-recommendation/generate_daily_recommendation.py`
- Recommendation artifact: `data/today_recommendation_2026-02-14.json`

## When to Use

- The skill is iterated frequently and root-level temporary files accumulate.
- The workflow usually follows: optimize config first, then generate recommendations.
- New features should be independently maintainable by module.
