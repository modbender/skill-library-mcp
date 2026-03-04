Endpoint: POST https://pr-risk-analyzer.onrender.com/analyze-pr

Request body:
repo: string (owner/repo)
pr_number: number
github_token: optional string

Response:
riskScore: number (0-100)
riskLevel: Low | Medium | High
issues: array
summary: string
