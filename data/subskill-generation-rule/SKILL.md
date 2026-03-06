---
name: subskill-generation-rule
description: Define and enforce project orgnization rules for generating subskills. put generated recommendation outputs under data/, place new feature scripts under subskills/<feature>/, and optionally add SKILL.md inside each feature folder to keep main skill root clean.
---

# Subskill Generate Rule

Apply these rules for future updates:

1. Store newly generated recommendation/result artifacts in `data/`.
2. Place newly generated code scripts in `subskills/<feature>/`.
3. Use one folder per feature under `subskills/`.
4. Add `SKILL.md` inside the feature folder when behavior/usage needs instructions.
5. Avoid adding one-off scripts and generated files in the main skill root.

Recommended layout:

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

## When to Use

- Creating new subskills
- Organizing existing features
- Enforcing file placement conventions
- Keeping skill root clean