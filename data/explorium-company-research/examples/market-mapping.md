# Example: Market Mapping

## User Request
"How many cybersecurity companies are there in the US with 50-500 employees? Break it down by state."

## What the Agent Does

1. **Autocompletes**: `linkedin_category` → "Computer & Network Security"
2. **Market sizes**: Gets total count with state breakdown
3. **Presents statistics**: Total market size, distribution by region
4. **Offers**: "Want me to fetch a sample list or export the full dataset?"

## Filters Used
```json
{
  "linkedin_category": {"values": ["Computer & Network Security"]},
  "company_country_code": {"values": ["US"]},
  "company_size": {"values": ["51-200", "201-500"]}
}
```

## Expected Output
Market statistics with total count, breakdown by company size range, and geographic distribution. Option to drill into specific segments.
