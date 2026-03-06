# Jira API Setup

## 1. Get API Token
1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Name it "TPM Copilot"
4. Copy the token

## 2. Find Your Base URL
Your Jira Cloud URL: `https://yourcompany.atlassian.net`

## 3. Configure
In `tpm/config.json`:
```json
{
  "jira": {
    "base_url": "https://yourcompany.atlassian.net",
    "email": "you@company.com",
    "api_token": "your-api-token"
  }
}
```

Or environment variables:
```bash
export JIRA_BASE_URL="https://yourcompany.atlassian.net"
export JIRA_EMAIL="you@company.com"
export JIRA_API_TOKEN="your-api-token"
```

## 4. Program Config
In `tpm/programs/<name>/config.json`, set per-workstream:
```json
{
  "workstreams": [
    {
      "name": "Backend",
      "jira_project": "BACK",
      "jira_board_id": "123"
    }
  ]
}
```

## Finding Board IDs
```bash
curl -s "https://yourcompany.atlassian.net/rest/agile/1.0/board" \
  -u "email:token" | python3 -m json.tool
```

## JQL Queries Used
- Sprint progress: `project = X AND sprint in openSprints()`
- Blockers: `project = X AND (status = Blocked OR labels = blocked)`
- Stale: `project = X AND updated < "-5d" AND status NOT IN (Done, Closed)`
- Recent: `project = X AND status changed to Done AFTER -7d`
- Scope creep: `project = X AND sprint in openSprints() AND created > -3d`

## Rate Limits
- Basic auth: 100 requests/minute
- Recommended: cache responses, batch where possible
