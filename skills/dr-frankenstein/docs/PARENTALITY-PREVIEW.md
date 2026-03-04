# 👶 Parentality Preview (Draft)

Status: **draft (not deployed)**

This preview separates responsibilities:

## A) OpenClaw Core (independent)
- parent/child linkage + lineage
- child stage (`newborn|toddler|child|adolescent|adult`)
- child need scores (`hunger`, `fear`, `anger`, `learning`, `protection`, `bonding`)
- `hunger` can be derived from token usage (example: starts with 100k tokens, rises as remaining budget drops)
- threshold engine and event/cron triggers
- escalation policy + audit

## B) Dr. Frankenstein Layer (optional)
- hormonal interpretation of child scores
- complementary parent actions
- parenting instinct prompts (Nurture / Teach / Protect / Co-regulate)

## Threshold Bands
- `0-39` monitor
- `40-69` soft intervention
- `70-84` active intervention
- `85-100` urgent intervention

## Complementary Parent Roles
- **Parent A (Nurturer):** calming, emotional safety, bonding
- **Parent B (Builder/Teacher):** structure, lessons, action plans

Both react to high `protection`, with different actions.

## Rollout Plan (Preview)
1. validate schema + prompt templates
2. generate example cron payloads
3. dry-run in isolated session
4. manual approval before production deploy

No deployment is performed in this draft phase.
