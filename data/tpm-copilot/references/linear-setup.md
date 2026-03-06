# Linear API Setup

## 1. Get API Key
1. Go to Linear → Settings → API → Personal API keys
2. Create a new key
3. Copy it

## 2. Configure
In `tpm/config.json`:
```json
{
  "tracker": "linear",
  "linear": {
    "api_key": "lin_api_xxxxx"
  }
}
```

Or: `export LINEAR_API_KEY="lin_api_xxxxx"`

## 3. Finding Team IDs
```bash
curl -s https://api.linear.app/graphql \
  -H "Authorization: lin_api_xxxxx" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ teams { nodes { id name } } }"}' | python3 -m json.tool
```

## 4. Program Config
```json
{
  "workstreams": [
    {
      "name": "Backend",
      "linear_team_id": "team-uuid-here"
    }
  ]
}
```

## GraphQL Queries Used

### Active Cycle (Sprint)
```graphql
query($teamId: String!) {
  team(id: $teamId) {
    activeCycle {
      progress
      endsAt
      issues {
        nodes { title identifier state { name } assignee { name } updatedAt }
      }
    }
  }
}
```

### Blocked Issues
```graphql
query($teamId: String!) {
  team(id: $teamId) {
    issues(filter: { labels: { name: { eq: "blocked" } } }) {
      nodes { title identifier assignee { name } }
    }
  }
}
```

## Rate Limits
- 1,500 requests per hour per key
- GraphQL complexity limit: 10,000 per query
