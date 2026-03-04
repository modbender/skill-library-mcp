# Example: Find SaaS Decision-Makers

## User Request
"Find me 200 VP-level and above decision-makers at mid-market SaaS companies in the US. I need their emails for an outbound campaign."

## What the Agent Does

1. **Parses ICP**: SaaS industry, US-based, 51-500 employees (mid-market), VP+ seniority
2. **Autocompletes**: `linkedin_category` → "Software Development"
3. **Market sizes**: Shows total available prospects (free)
4. **Fetches sample**: 10 preview results
5. **Confirms**: Shows sample, asks user to confirm before full fetch
6. **Full fetch**: 200 prospects
7. **Enriches**: Adds verified emails via `contacts_information`
8. **Exports**: CSV to ~/Downloads/

## Filters Used
```json
{
  "linkedin_category": {"values": ["Software Development"]},
  "company_country_code": {"values": ["US"]},
  "company_size": {"values": ["51-200", "201-500"]},
  "job_level": {"values": ["vice president", "c-suite", "director"]},
  "has_email": true
}
```

## Expected Output
CSV with columns: name, title, company, email, company_size, industry, location
