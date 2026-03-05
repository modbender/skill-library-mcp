# skill-governance

Use this skill to control multi-skill side effects with a balanced governance model.

## When to use

- After installing a new skill (must pass acceptance before becoming `ready`)
- Daily/heartbeat governance refresh
- Core pool tuning and automatic promotion/demotion
- Routing decisions: core first, then all ready skills, then explore fallback

## Policy

- Status model: `candidate` -> `ready` -> `core` -> `quarantine` -> `retired`
- Third-party skills default to `candidate`
- Only `ready` or `core` skills are eligible for automatic selection
- Quarantine after 2 consecutive failures
- Demote `core` skill to `ready` after 3 days without usage
- Dynamic core cap range: 8 to 14

## Source of truth

- `skill-registry.json`

## Scripts

1. Reconcile runtime + filesystem into registry:
   - `scripts/reconcile-ready.ps1 -Root <workspace>`
2. Audit one skill with 4-step acceptance:
   - `scripts/audit-skill.ps1 -Root <workspace> -SkillName <name>`
3. Record skill usage outcome:
   - `scripts/record-skill-usage.ps1 -Root <workspace> -SkillName <name> -Outcome success|failure|blocked`
4. Evaluate core pool promotion/demotion and dynamic cap:
   - `scripts/update-core-pool.ps1 -Root <workspace>`
5. Route execution chain (core -> ready -> explore):
   - `scripts/route-skill.ps1 -Root <workspace> -TaskText "<text>" -Candidates "a,b,c"`
6. Weekly cleanup (retire stale or missing skills):
   - `scripts/weekly-cleanup.ps1 -Root <workspace>`

## Required install flow

After installing a new skill:

1. Run `reconcile-ready.ps1`
2. Run `audit-skill.ps1` for that skill
3. Confirm status in `skill-registry.json` is `ready` before use in automatic routing
