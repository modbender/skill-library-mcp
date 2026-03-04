---
name: redmine-issue
description: Read Redmine issues from any Redmine server via REST API with configurable URL and credentials. Use when you need to fetch a single issue, list/filter issues, or inspect issue fields for change planning; supports deployment to different Redmine instances via environment variables.
---

# Redmine Issue

Read Redmine issues through REST API.

## Required environment variables

- `REDMINE_URL` (example: `https://redmine.sylksoft.com`)
- One auth mode:
  - `REDMINE_API_KEY`, or
  - `REDMINE_USERNAME` + `REDMINE_PASSWORD`

## Get one issue

```bash
node {baseDir}/scripts/issues.mjs get --id 123
```

## List issues

```bash
node {baseDir}/scripts/issues.mjs list
node {baseDir}/scripts/issues.mjs list --project-id my-project --status-id open --limit 20 --offset 0
node {baseDir}/scripts/issues.mjs list --assigned-to-id me --sort "updated_on:desc"
```

## Update one issue

```bash
node {baseDir}/scripts/issues.mjs update --id 123 --status-id 2 --notes "開始處理"
node {baseDir}/scripts/issues.mjs update --id 123 --assigned-to-id 6 --priority-id 3
node {baseDir}/scripts/issues.mjs update --id 123 --done-ratio 50 --notes "完成一半"
```

## Notes

- URL and auth are variables by design for cross-environment deployment.
- API responses are output as JSON.
- For automation, prefer `REDMINE_API_KEY` over username/password.
