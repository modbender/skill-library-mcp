# Skill Doctor | OpenClaw Skill

Scans the skills folder for **missing** and **unused** dependencies, can **fix** `requirements.txt`, and **test** a skill in or out of **sandbox**.

## Quick start

```bash
# Scan all skills
python3 workspace/skills/skill-doctor/scripts/skill_doctor.py

# Scan one skill
python3 workspace/skills/skill-doctor/scripts/skill_doctor.py --skill my-skill --scan

# Fix missing deps
python3 workspace/skills/skill-doctor/scripts/skill_doctor.py --skill my-skill --fix

# Fix and remove unused
python3 workspace/skills/skill-doctor/scripts/skill_doctor.py --skill my-skill --fix --fix-unused

# Test (sandbox)
python3 workspace/skills/skill-doctor/scripts/skill_doctor.py --skill my-skill --test

# Test (no sandbox)
python3 workspace/skills/skill-doctor/scripts/skill_doctor.py --skill my-skill --test --no-sandbox
```

## Options

- `--skill SLUG` — Run for one skill only.
- `--scan` — Report missing/unused deps (default if no `--fix`/`--test`).
- `--fix` — Add missing packages to `requirements.txt`.
- `--fix-unused` — Also remove unused packages when fixing.
- `--dry-run` — With `--fix`: only show what would be done.
- `--test` — Run skill-tester for the skill.
- `--no-sandbox` — Run tests with full environment.
- `--json` — JSON output.
- `--skills-dir PATH` — Override skills root.

## Dependencies

- Python 3.7+ (stdlib only for scan/fix).
- [skill-tester](workspace/skills/skill-tester) for `--test`.
