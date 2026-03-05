---
name: epragma-redmine-issue
description: Read Redmine issues from any Redmine server via REST API with configurable URL and credentials. Use when you need to fetch a single issue, list/filter issues, or inspect issue fields for change planning; supports deployment to different Redmine instances via environment variables.
user-invocable: true
---

# ePragma Redmine Issue

Read Redmine issues through REST API.

## Configuration

This skill requires `REDMINE_URL` and `REDMINE_API_KEY` to be configured.

### Setup with OpenClaw CLI

Run these commands to configure the skill:

```bash
# Set your Redmine URL
openclaw skills config epragma-redmine-issue set REDMINE_URL https://your-redmine-server.com

# Set your API key (generate from Redmine My Account page)
openclaw skills config epragma-redmine-issue set REDMINE_API_KEY your-api-key-here
```

### Get your API Key

1. Log in to your Redmine server
2. Go to "My Account" 
3. Click "Show" next to "API access key"
4. Copy the key

## Get one issue

```bash
node {baseDir}/scripts/issues.mjs get --id 123
```

## List issues

```bash
node {baseDir}/scripts/issues.mjs list
node {baseDir}/scripts/issues.mjs list --project-id my-project --status-id open --limit 20 --offset 0
node {baseDir}/scripts/issues.mjs list --assigned-to-id me --sort "updated_on:desc"
node {baseDir}/scripts/issues.mjs list --project my-project
```

## List projects

```bash
node {baseDir}/scripts/issues.mjs projects
```

## List statuses

```bash
node {baseDir}/scripts/issues.mjs statuses
```

## Update one issue

```bash
node {baseDir}/scripts/issues.mjs update --id 123 --status-id 2 --notes "this is ok"
node {baseDir}/scripts/issues.mjs update --id 123 --assigned-to-id 6 --priority-id 3
node {baseDir}/scripts/issues.mjs update --id 123 --done-ratio 50 --notes "done 50%"
```

## Add comment to issue

```bash
node {baseDir}/scripts/issues.mjs comment --id 123 --notes "This is a comment"
```

## Create new issue

```bash
# Required: --project-id (or project name), --subject
# Optional: --description, --tracker-id, --priority-id, --assigned-to-id, --status-id, --start-date, --due-date, --done-ratio, --estimated-hours

node {baseDir}/scripts/issues.mjs create --project-id 1 --subject "New issue title"
node {baseDir}/scripts/issues.mjs create --project-id epragma --subject "Bug report" --description "Details here" --priority-id 4
```

## Time Entries

```bash
# List time entries (filters: --issue-id, --project-id, --user-id, --from, --to, --spent-on)
node {baseDir}/scripts/issues.mjs time-list
node {baseDir}/scripts/issues.mjs time-list --issue-id 232
node {baseDir}/scripts/issues.mjs time-list --project-id 1 --from 2026-01-01 --to 2026-01-31

# Add time entry (required: --issue-id OR --project-id, --hours; optional: --activity-id, --spent-on, --comments)
node {baseDir}/scripts/issues.mjs time-add --issue-id 232 --hours 2 --activity-id 9 --comments "Work done"
node {baseDir}/scripts/issues.mjs time-add --project-id 1 --hours 1.5 --activity-id 8

# List available activities
node {baseDir}/scripts/issues.mjs time-activities
```

## Notes

- URL and auth are variables by design for cross-environment deployment.
- API responses are output as JSON.
- For automation, prefer `REDMINE_API_KEY` over username/password.
