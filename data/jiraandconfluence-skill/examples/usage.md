---
title: "Jira & Confluence Skill Usage"
description: |
  Examples of how to interact with the Jira and Confluence integration skill.
platforms:
  - OpenClaw CLI
---

## Example 1: Read a Jira issue
```bash
export JIRA_API_TOKEN="your_token"
./scripts/jira_reader.sh PROJ-123
```

## Example 2: Read a Confluence page by ID
```bash
export CONFLUENCE_API_TOKEN="your_token"
./scripts/confluence_reader.sh 123456
```

## Notes
- You must have API tokens with the appropriate permissions.
- The domain `your-domain.atlassian.net` must be replaced with your real domain.
- Future improvements will include output parsing and suggestion generation.
