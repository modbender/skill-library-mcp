# Chains: core

## 1) Lead intake and qualification

1. `crm.lead.add`
2. `crm.lead.list` (verify/lookup duplicates)
3. `crm.lead.update` (score, owner, comment)

Guardrails:
- use `--confirm-write`
- keep deterministic `filter` for list checks

## 2) Deal change to task assignment

1. `crm.deal.list` with stage filter
2. `tasks.task.add` linked to deal context
3. `crm.deal.update` with task reference

## 3) Event bootstrap for reliable sync

1. `event.bind` for chosen CRM event
2. `event.offline.list`
3. `event.offline.get` with safe processing
4. `event.offline.clear` only after successful persist
