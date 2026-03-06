---
name: Jira PAT Skill
description: Manage Jira issues on self-hosted/enterprise Jira instances using
  Personal Access Tokens (PAT). This skill is designed for environments where
  Basic Auth doesn't work due to SSO/SAML authentication.
---

# Jira PAT Skill

Manage Jira issues on self-hosted/enterprise Jira instances using Personal Access Tokens (PAT). This skill is designed for environments where Basic Auth doesn't work due to SSO/SAML authentication.

## When to Use This Skill

Use this skill when working with:
- Self-hosted Jira instances (e.g., Red Hat, enterprise deployments)
- Jira instances with SSO/SAML authentication
- Environments where `jira-cli` or Basic Auth fails

**Note:** For Atlassian Cloud with email + API token auth, use the `clawdbot-jira-skill` instead.

## Prerequisites

1. **Personal Access Token (PAT)**: Create one in Jira:
   - Go to your Jira profile → Personal Access Tokens
   - Create a new token with appropriate permissions
   - Store it in environment variable `JIRA_PAT`

2. **Jira Base URL**: Your Jira instance URL in `JIRA_URL`

## Environment Variables

```bash
export JIRA_PAT="your-personal-access-token"
export JIRA_URL="https://issues.example.com"
```

## Tools

This skill uses `curl` and `jq` for all operations.

## Instructions

### Get Issue Details

Fetch full details of a Jira issue:

```bash
curl -s -H "Authorization: Bearer $JIRA_PAT" \
  "$JIRA_URL/rest/api/2/issue/PROJECT-123" | jq
```

Get specific fields only:

```bash
curl -s -H "Authorization: Bearer $JIRA_PAT" \
  "$JIRA_URL/rest/api/2/issue/PROJECT-123?fields=summary,status,description" | jq
```

### Search Issues (JQL)

```bash
# Find child issues of an epic
curl -s -H "Authorization: Bearer $JIRA_PAT" \
  "$JIRA_URL/rest/api/2/search?jql=parent=EPIC-123" | jq

# Complex queries (URL-encoded)
curl -s -H "Authorization: Bearer $JIRA_PAT" \
  "$JIRA_URL/rest/api/2/search?jql=project%3DPROJ%20AND%20status%3DOpen" | jq
```

Common JQL patterns:
- `parent=EPIC-123` - Child issues of an epic
- `project=PROJ AND status=Open` - Open issues in project
- `assignee=currentUser()` - Your assigned issues
- `labels=security` - Issues with specific label
- `updated >= -7d` - Recently updated

### Get Available Transitions

Before changing status, query available transitions:

```bash
curl -s -H "Authorization: Bearer $JIRA_PAT" \
  "$JIRA_URL/rest/api/2/issue/PROJECT-123/transitions" | jq '.transitions[] | {id, name}'
```

### Transition (Change Status)

Close an issue with a comment:

```bash
curl -s -X POST \
  -H "Authorization: Bearer $JIRA_PAT" \
  -H "Content-Type: application/json" \
  -d '{
    "transition": {"id": "61"},
    "update": {
      "comment": [{"add": {"body": "Closed via API"}}]
    }
  }' \
  "$JIRA_URL/rest/api/2/issue/PROJECT-123/transitions"
```

### Add a Comment

```bash
curl -s -X POST \
  -H "Authorization: Bearer $JIRA_PAT" \
  -H "Content-Type: application/json" \
  -d '{"body": "Comment added via API."}' \
  "$JIRA_URL/rest/api/2/issue/PROJECT-123/comment"
```

### Update Issue Fields

```bash
curl -s -X PUT \
  -H "Authorization: Bearer $JIRA_PAT" \
  -H "Content-Type: application/json" \
  -d '{
    "fields": {
      "summary": "Updated summary",
      "labels": ["api", "automated"]
    }
  }' \
  "$JIRA_URL/rest/api/2/issue/PROJECT-123"
```

### Create an Issue

```bash
curl -s -X POST \
  -H "Authorization: Bearer $JIRA_PAT" \
  -H "Content-Type: application/json" \
  -d '{
    "fields": {
      "project": {"key": "PROJ"},
      "summary": "New issue via API",
      "description": "Issue description",
      "issuetype": {"name": "Task"},
      "parent": {"key": "EPIC-123"}
    }
  }' \
  "$JIRA_URL/rest/api/2/issue"
```

## Useful jq Filters

```bash
# Summary and status
jq '{key: .key, summary: .fields.summary, status: .fields.status.name}'

# List search results
jq '.issues[] | {key: .key, summary: .fields.summary, status: .fields.status.name}'

# Issue links
jq '.fields.issuelinks[] | {type: .type.name, key: (.inwardIssue // .outwardIssue).key}'
```

## Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| 401 Unauthorized | Invalid/expired PAT | Regenerate token, check `Bearer` format |
| 404 Not Found | Issue doesn't exist or no access | Verify issue key and permissions |
| 400 Bad Request on transition | Invalid transition ID | Query available transitions first |

## Comparison with Basic Auth Skills

This skill uses **Bearer token authentication** (`Authorization: Bearer <PAT>`), which works with self-hosted Jira instances using SSO/SAML. For Atlassian Cloud with email + API token, use skills that implement Basic Auth instead.
