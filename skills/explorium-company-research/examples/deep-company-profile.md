# Example: Deep Company Profile for Account Planning

## User Request
"Research Datadog — I have a meeting with their VP of Engineering next week. Give me everything."

## What the Agent Does

1. **Matches company**: Datadog → datadog.com
2. **Full enrichment chain**:
   - Call 1: firmographics + technographics + funding-and-acquisitions
   - Call 2: workforce-trends + linkedin-posts
3. **Finds executives**: C-suite and VP-level at Datadog
4. **Gets recent events**: Funding, hiring, partnerships in last 90 days
5. **Presents**: Structured research summary

## Enrichments Used
- `firmographics` — company overview
- `technographics` — tech stack (relevant for engineering discussion)
- `funding-and-acquisitions` — investment history
- `workforce-trends` — engineering team growth
- `linkedin-posts` — recent company messaging

## Expected Output
Structured report covering: company overview, tech stack (categorized), funding timeline, workforce composition, recent activity, and key executives with titles.
