# Example: Build a Target Account List with Intent Signals

## User Request
"Find companies that are actively looking for project management software. Focus on tech companies with 200-1000 employees."

## What the Agent Does

1. **Identifies intent-based workflow**: Uses `business_intent_topics` filter
2. **Autocompletes**: intent topics for "project management software"
3. **Combines filters**: Intent + tech industry + company size
4. **Market sizes**: Shows total matching companies
5. **Fetches sample**: 10 company previews
6. **Enriches**: Adds firmographics and technographics
7. **Exports**: Company list with intent signals to CSV

## Filters Used
```json
{
  "business_intent_topics": {"values": ["Project Management Software"]},
  "linkedin_category": {"values": ["Software Development", "Information Technology & Services"]},
  "company_size": {"values": ["201-500", "501-1000"]}
}
```

## Expected Output
CSV with columns: company_name, domain, industry, employees, revenue, tech_stack, location, intent_topic
