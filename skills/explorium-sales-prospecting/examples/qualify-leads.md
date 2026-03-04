# Example: Qualify Leads with Growth Signals

## User Request
"Find Series A/B fintech companies that are actively hiring engineers. I want to reach out to their CTOs."

## What the Agent Does

1. **Parses multi-signal query**: Fintech + recent funding + hiring + CTO title
2. **Autocompletes**: `linkedin_category` → "Financial Services", `job_title` → "Chief Technology Officer"
3. **Applies event filter**: `new_funding_round` + `hiring_in_engineering_department` in last 60 days
4. **Fetches companies first**: Gets companies matching all signals
5. **Chains to prospects**: Finds CTOs at those companies
6. **Enriches**: Contact info + profiles
7. **Exports**: Qualified lead list with company context

## Filters Used (Companies)
```json
{
  "linkedin_category": {"values": ["Financial Services"]},
  "events": {
    "values": ["new_funding_round", "hiring_in_engineering_department"],
    "last_occurrence": 60
  }
}
```

## Filters Used (Prospects)
```json
{
  "business_id": {"values": ["<matched business IDs>"]},
  "job_title": {"values": ["Chief Technology Officer"]}
}
```

## Expected Output
CSV with: cto_name, cto_email, cto_phone, company_name, funding_stage, employees, recent_events
