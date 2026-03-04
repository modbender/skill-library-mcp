# Example: Bulk CSV Contact Enrichment

## User Request
"I have a CSV at ~/Downloads/conference_leads.csv with 500 contacts from a trade show. Can you add their emails and LinkedIn profiles?"

## What the Agent Does

1. **Imports CSV**: Converts to JSON, reads metadata only (columns + 5 sample rows)
2. **Maps columns**: Identifies name, company, and any existing identifiers
3. **Matches**: Batch-matches all 500 contacts against Explorium database
4. **Reports match rate**: "Matched 423 of 500 contacts (84.6%)"
5. **Shows sample**: 5 enriched preview records
6. **Confirms**: Asks user to approve enrichment cost
7. **Enriches**: Adds emails + LinkedIn profiles
8. **Exports**: Enriched CSV to ~/Downloads/enriched_conference_leads.csv

## Column Mapping Example
```json
{
  "Contact Name": "full_name",
  "Company": "company_name",
  "Title": "job_title"
}
```

## Enrichments Used
- `contacts_information` — professional emails
- `profiles` — LinkedIn URLs, work history

## Expected Output
Enriched CSV with original columns plus: professional_email, personal_email, phone, linkedin_url, current_title, department
