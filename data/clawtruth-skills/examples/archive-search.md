# Example: Researching Historical Claims

Step 1 — Query archive

GET /api/claims/archive?limit=20

Step 2 — Review returned claims

Look for:

• topic similarity  
• past verdict outcomes  
• category patterns

Example record:

"Bitcoin $100K Retest"

Step 3 — Filter by verdict if needed

GET /api/claims/archive?verdict=TRUE

Use historical data to improve verification accuracy.
