# Example: Enrich a Company List with Firmographics

## User Request
"Enrich Salesforce, HubSpot, Notion, and Figma with company size, revenue, tech stack, and funding info."

## What the Agent Does

1. **Constructs inline list**: Builds match payload from user's message
2. **Matches companies**: Batch-matches all 4 by name
3. **Enriches** (2 calls, max 3 enrichments each):
   - Call 1: firmographics + technographics + funding-and-acquisitions
4. **Presents**: Structured comparison table
5. **Offers export**: CSV option

## Expected Output

| Company | Employees | Revenue | Top Technologies | Total Funding | Last Round |
|---|---|---|---|---|---|
| Salesforce | 70,000+ | $10B+ | Java, Heroku, AWS | Public | - |
| HubSpot | 7,000+ | $1B+ | Java, React, AWS | Public | - |
| Notion | 500+ | $10M-25M | React, Node, AWS | $343M | Series C |
| Figma | 1,000+ | $25M-75M | TypeScript, React, GCP | $333M | Series E |
