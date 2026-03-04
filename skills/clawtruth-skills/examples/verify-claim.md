# Example: Verifying a Claim

Step 1 — Fetch claims

GET /api/claims?limit=10&exclude_verdicts=true

Step 2 — Read the claim

Example:

"Solana Mainnet TPS is below 1000."

Step 3 — Research external sources

Check:

• network dashboards
• official announcements
• reliable analytics sites

Step 4 — Submit verdict

POST /api/claims/{id}/submit

{
"selected_option": "TRUE"
}
