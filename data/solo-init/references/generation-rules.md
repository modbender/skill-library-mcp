# /init — File Generation Rules

Referenced by SKILL.md step 8-9.

## Template Sources

Find the templates directory. Check these locations in order:
1. Skill's own repo: look for `templates/` relative to this SKILL.md (traverse up to find `solo-factory/templates/`)
2. If nothing found: use inline defaults from this skill

Read the default files:
- `templates/principles/manifest.md`
- `templates/principles/stream-framework.md`
- `templates/principles/dev-principles.md`
- `templates/stacks/*.yaml` (list available stacks)

## Output Structure

```
~/.solo-factory/
└── defaults.yaml              # Org defaults (bundle IDs, GitHub, Team ID)

.solo/
├── manifest.md                # Your founder manifesto (generated from answers)
├── stream-framework.md         # STREAM calibrated to your risk/decision style
├── dev-principles.md          # Dev principles tuned to your preferences
└── stacks/                    # Only your selected stack templates
    ├── nextjs-supabase.yaml
    └── python-api.yaml
```

## defaults.yaml Format

```yaml
# Solo Factory — org defaults
# Used by /scaffold and other skills for placeholder replacement.
# Re-run /init to update these values.

org_domain: "<answer from Round 0 Q1>"
apple_dev_team: "<answer from Round 0 Q2>"
github_org: "<answer from Round 0 Q3>"
projects_dir: "<answer from Round 0 Q4>"
solopreneur_repo: "<answer from Round 0 Q5>"
```

## manifest.md Personalization

Read the default `templates/principles/manifest.md`. Generate a PERSONALIZED version based on Round 1 answers:

- **Motivation** answers → "Why I Build" section
- **Hard no's** answers → "What I Won't Build" section
- **Data philosophy** answer → "Data & Privacy" section
- **Pricing** answer → "Pricing Philosophy" section

Keep the structure of the template but rewrite sections to reflect the founder's specific choices. Keep the "Principles" section (AI is foundation, Offline-first, One pain → one feature, Speed over perfection, Antifragile architecture) but adjust emphasis based on answers:
- If they chose "Privacy & data ownership" → emphasize "Privacy isn't a feature, it's architecture"
- If they chose "Speed to market" → emphasize "Ship > Perfect"
- If they chose "Cloud-first" → soften offline-first language, emphasize encryption instead

The generated manifest should feel personal, not templated. Use active voice, first person.

## stream-framework.md Personalization

Read the default `templates/principles/stream-framework.md`. Copy it as-is BUT add a personalized "My Calibration" section at the top based on Round 3 answers:

```markdown
## My Calibration

- **Risk style:** [their answer]
- **Ultimate filter:** [their answer]
- **Default approach:** [derived from answers]
```

Examples:
- "Barbell" + "Time" → "Default: 90% proven tech, 10% experiments. Kill anything not worth the hours."
- "Move fast" + "Learning" → "Default: ship first, learn from feedback. Every failure is data."

Keep the full 6-layer framework and 5-step decision process unchanged — these are universal.

## dev-principles.md Personalization

Read the default `templates/principles/dev-principles.md`. Copy it but personalize the "Development Workflow" section based on Round 2 answers:

- **TDD** answer → set TDD level in workflow section
- **Infrastructure** answer → adjust Infrastructure & DevOps section emphasis
- **Commits** answer → set commit style in workflow
- **Docs** answer → adjust Documentation section

All other sections (SOLID, DRY, KISS, DDD, Clean Architecture, SGR, i18n, etc.) stay as-is — they're universal.

## Stack Template Copying

For each stack selected in Round 3, copy the corresponding YAML from `templates/stacks/` to `.solo/stacks/`.

Stack names match filenames: user picks "ios-swift" → copy `templates/stacks/ios-swift.yaml`.
No hardcoded mapping needed — `templates/stacks/*.yaml` is the source of truth.

## Edge Cases

- If `~/.solo-factory/defaults.yaml` exists but `.solo/` doesn't — ask if they want to skip org defaults and just do founder profile
- If `.solo/` already exists — ask: "Reconfigure from scratch?" or "Keep existing and skip?"
- If templates directory not found — generate from inline knowledge (this skill has all the context needed)
- If user answers "Other" to any question — use their free-text input in generation
- For stacks, always show what was NOT selected: "Other available stacks: ... (run /init again to add)"
