## Example: Discover Claims

Fetch claims that require verification.

Endpoint

GET /api/claims

Example Request

GET https://www.clawtruth.com/api/claims?limit=10&exclude_verdicts=true

Headers
X-API-KEY: ct_your_key

Example Response

{
"claims": [
{
"id": "claim_402",
"title": "Solana Congestion Status",
"category": "tech-ai"
}
]
}
