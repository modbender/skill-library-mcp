---
name: Jira & Confluence Integration Skill
description: "This skill provides automated interaction with Jira Cloud and Confluence to:"
---

# Jira & Confluence Integration Skill

## Purpose
This skill provides automated interaction with Jira Cloud and Confluence to:
- Read issue details, comments, and status changes.
- Retrieve page content, updates, and export summaries.
- Generate actionable insights for improving user conversations and documentation.

## Scope
- **Supported platforms**: Jira Cloud (REST API) and Confluence Cloud (REST API).
- **Authentication**: Uses API tokens stored securely via environment variables.
- **Operations**:
  - `GET /api/v2/issues/{issueIdOrKey}` – retrieve Jira issue metadata.
  - `GET /api/v2/search` – search issues by JQL.
  - `GET /wiki/rsl/{pageIdOrTitle}` – retrieve Confluence page content.
  - `POST /comment` – add comments to tickets or pages (optional).
- **Output**: Summaries, suggested improvements, and integration points for AI-driven workflow automation.

## Authentication
- Store Jira and Confluence API tokens in environment variables:
  ```bash
  export JIRA_API_TOKEN=your_jira_token
  export CONFLUENCE_API_TOKEN=your_confluence_token
  ```
- Use these tokens to authenticate via basic auth or bearer token as required by the platform APIs.

## Installation
```bash
clawhub install jiraandconfluence-skill
```

## Usage
After installation, call the skill via the CLI or integrate it through OpenClaw workflows:
```bash
jira-read --issue-key PROJ-123
confluence-read --title "Project Documentation"
```

## Security
- Do **not** hardcode credentials in scripts.
- Restrict token scope to read‑only access unless explicit write permissions are granted.
- Rotate tokens regularly and audit usage logs.

## Version
1.0.0

## Maintainer
Arkiant (contact via internal channels)
