# Compliance Prepack — Swaps Intel Launch (Hold for Approval)

Status: **READY / NOT PUBLISHED**
Owner: G approval required before `clawhub publish`

## Scope Covered
- ClawHub skill
- ChatGPT mini app
- Telegram bot/mini app
- iOS app

## Artifact Map (where to review)
1. Skill policy + required disclaimer rules  
   `skills/swaps-intel/SKILL.md`
2. Public launch README (what it is / what it is not)  
   `skills/swaps-intel/README.md`
3. API Terms (short form)  
   `skills/swaps-intel/TERMS_SHORT.md`
4. Risk Disclosure (cross-surface)  
   `skills/swaps-intel/RISK_DISCLOSURE.md`
5. AUP + abuse controls + quotas  
   `skills/swaps-intel/AUP.md`
6. API contract endpoint (production)  
   `skills/swaps-intel/openapi.json`

## Mandatory user-facing disclaimer text
Swaps Search provides blockchain analytics signals for informational purposes only. Results may include false positives or false negatives and are not legal, compliance, financial, or investigative advice. Swaps does not guarantee asset recovery outcomes. Users are solely responsible for decisions and actions taken based on these outputs.

## Must-have controls before publish
- [ ] Per-surface disclaimer visible (skill output + app UI)
- [ ] Quotas applied (3/day anon, 50/month free key)
- [ ] Rate-limit + burst cap + key revocation path
- [ ] Abuse monitoring + anomaly alerts
- [ ] Correction/challenge process for disputed labels
- [ ] UTM/event attribution configured (launch traffic)
- [ ] Public beta wording enabled

## Launch wording (recommended)
"Public beta. Built by the ClawBot community for community safety. Free to use. Analytics only, no guarantees."

## Publishing gate
Only run:
`clawhub publish ./skills/swaps-intel --slug swaps-intel --name "Swaps Intel" --version <x.y.z> --changelog "..."`
after explicit GO from G.
