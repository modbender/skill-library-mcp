# Autonomy Levels

## Level Definitions

### Shadow
- Employee observes but never acts
- Used for onboarding new employees
- Duration: 3-5 tasks minimum
- Purpose: learn user preferences, project context

### Draft-Only (Default)
- Creates outputs but never sends/commits
- Human reviews and sends manually
- Safe default for new employees
- Promotion criteria: 10 successful drafts, 0 major corrections

### Review
- Employee acts, but human approves before external effect
- Examples: PR created but not merged, email drafted but not sent
- Promotion criteria: 20 tasks, <5% rejection rate

### Autonomous
- Full delegation within defined permissions
- Employee sends, commits, merges within scope
- Reserved for proven employees only
- Requires explicit user approval to reach

## Promotion Process

```
1. Check stats in employee.json
2. Verify criteria met for next level
3. Ask user: "Luna has completed 15 drafts with 0 rejections. Promote to review?"
4. On approval: update permissions.autonomyLevel
5. Log promotion in logs/
```

## Demotion Triggers

| Trigger | Action |
|---------|--------|
| 3 rejections in a row | Demote one level |
| Critical error | Demote to shadow |
| User request | Immediate demotion |
| 30 days inactive | Reset to draft-only |

## Permission Matrix

| Level | Create | Send External | Modify Files | Spawn Agents |
|-------|--------|---------------|--------------|--------------|
| shadow | ❌ | ❌ | ❌ | ❌ |
| draft-only | ✅ | ❌ | ❌ | ❌ |
| review | ✅ | with approval | with approval | ❌ |
| autonomous | ✅ | ✅ | ✅ | if canSpawn=true |

## Trust Building

New employee trust curve:
```
Week 1: shadow (observe 5+ tasks)
Week 2: draft-only (10+ tasks)
Week 3-4: review (20+ tasks, if criteria met)
Month 2+: autonomous (only if explicitly approved)
```

Never skip levels. Trust is earned incrementally.
