# Starter Workflows (Built-in)

Use these immediately after onboarding.

## 1) Top 25 Accounts to Work Today
Goal: prioritize accounts with strong intent, recent engagement signal, no current open pipeline.

Suggested logic:
- High 6sense intent score
- Buying stage in Consideration/Decision/Purchase
- Not churned
- No open opportunities
- No recent outreach in last 21-30 days

## 2) Pipeline Rescue Board
Goal: find open opportunities at risk due to inactivity.

Suggested logic:
- Opportunity IsClosed = false
- Last activity older than N days (e.g., 14)
- Low recent engagement or no recent meetings
- Optional: deprioritize if account is churn-risk suppressed for net-new work

## 3) Campaign Follow-up Opportunities
Goal: capture demand-gen responses that never got sales follow-up.

Suggested logic:
- CampaignMember HasResponded = true
- Include both Contact- and Lead-based campaign members
- Join to recent Tasks/Events
- Keep rows with no qualifying follow-up within N days

## Output format recommendation
Each workflow returns:
- `summary`: one-line what this list means
- `count`: number of returned rows
- `next_best_action.follow_up_query`: contextual next query suggestion
- `next_best_action.automation_idea`: pragmatic automation nudge
- `rows`: actionable records

For each row include:
- account_name
- account_domain
- reason_to_act (plain language)
- priority_score
- owner
- suggested_next_step
