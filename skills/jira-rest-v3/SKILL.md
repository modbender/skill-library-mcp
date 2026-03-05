# File: skills/jira-rest-v3/SKILL.md

# openClaw Skill — Jira Daily Work via ATREST (Jira Cloud REST API v3 + Jira Software Agile API)

## What this skill is for
Use this skill to perform everyday Jira work from openClaw:
- find/triage issues (JQL search)
- read/update issues (fields, assignee, status transition)
- create issues
- manage comments (list/add/update/delete)
- log time (worklogs)
- work with boards/backlogs/sprints (Jira Software Agile API)

This skill assumes Jira Cloud.

---

## Required environment variables (openclaw.json -> "env")
All variables MUST use the `ATREST_` prefix.

### Jira site + authentication
- `ATREST_JIRA_BASE_URL`
  - Example: `https://your-domain.atlassian.net`
  - Do NOT include a trailing slash.
- `ATREST_JIRA_AUTH_MODE`
  - `basic` (recommended for scripts) or `bearer`
- `ATREST_JIRA_EMAIL`
  - Required when `ATREST_JIRA_AUTH_MODE=basic`
- `ATREST_JIRA_API_TOKEN`
  - Required when `ATREST_JIRA_AUTH_MODE=basic`
- `ATREST_JIRA_BEARER_TOKEN`
  - Required when `ATREST_JIRA_AUTH_MODE=bearer`
- `ATREST_JIRA_USER_AGENT`
  - Example: `openClaw-jira-atrest/1.0`

### Defaults (optional but practical)
- `ATREST_JIRA_DEFAULT_PROJECT_KEY`
- `ATREST_JIRA_DEFAULT_ISSUE_TYPE`
  - Example: `Task`, `Bug`, `Story`
- `ATREST_JIRA_DEFAULT_BOARD_ID`
- `ATREST_JIRA_DEFAULT_MAX_RESULTS`
  - Example: `50`
- `ATREST_JIRA_DEFAULT_FIELDS`
  - Comma-separated list for search/read, e.g. `summary,status,assignee,priority,updated`

### Resilience (optional)
- `ATREST_HTTP_TIMEOUT_MS` (e.g. `30000`)
- `ATREST_HTTP_RETRY_MAX` (e.g. `3`)
- `ATREST_HTTP_RETRY_BACKOFF_MS` (e.g. `1000`)

See also: `refs/openclaw_env_example.json`.

---

## API base paths (two families)
1) Jira Cloud *Platform* REST API v3 (issues, comments, projects, users, worklogs, …)
- Base: `${ATREST_JIRA_BASE_URL}/rest/api/3`

2) Jira Software *Agile* REST API (boards, sprints, backlog, ranking, …)
- Base: `${ATREST_JIRA_BASE_URL}/rest/agile/1.0`

---

## Authentication rules (must follow)
### If AUTH_MODE = basic
- Use HTTP Basic Auth with **email + API token**.
- Either:
  - Set `Authorization: Basic base64(email:apiToken)`, or
  - Use the HTTP client’s built-in basic auth feature (username=email, password=api token).

### If AUTH_MODE = bearer
- Set `Authorization: Bearer ${ATREST_JIRA_BEARER_TOKEN}`

Never print secrets, never echo tokens into logs, never store tokens in repo.

---

## Rich-text fields (ADF)
Jira Cloud v3 uses Atlassian Document Format (ADF) for:
- issue `description`, `environment`, and textarea custom fields
- comment `body`
- worklog `comment`

When the user provides plain text, wrap it into minimal ADF.
See `refs/jira-json-quickref.md#adf-minimal`.

---

## ATREST request contract (openClaw)
When executing a command, perform an HTTP request with:
- method: GET|POST|PUT|DELETE
- url: `${ATREST_JIRA_BASE_URL} + path`
- headers:
  - `Accept: application/json`
  - `Content-Type: application/json` (for JSON bodies)
  - `User-Agent: ${ATREST_JIRA_USER_AGENT}` (if set)
  - `Authorization: ...` (per auth mode)
- query: object (encoded as querystring)
- body: object (JSON)

Always:
- handle pagination (see each command)
- handle 429 rate limits (respect `Retry-After` if present, then retry with backoff)
- handle 401/403 by reporting missing permissions/auth setup
- for destructive actions (delete), ask for explicit confirmation unless the user already asked to delete.

---

# Command Catalog

## 1) Projects & Users (Platform v3)

### jira.projects.search
- GET `/rest/api/3/project/search`
- Query: `startAt`, `maxResults`, (optional filters per Jira)
- Use for: selecting a project id/key, listing available projects.
- Output: id, key, name, projectTypeKey/style if available.

### jira.users.search
- GET `/rest/api/3/user/search`
- Query: `query` (string), optional pagination params supported by Jira
- Use for: resolving a person name/email fragment into `accountId`.

---

## 2) Issue search & read (Platform v3)

### jira.issues.searchJql (Enhanced search)
- GET `/rest/api/3/search/jql`  (or POST for very long JQL)
- Query: `jql`, `nextPageToken`, `maxResults`, `fields[]`, `expand`, `properties[]`, `fieldsByKeys`, `failFast`, `reconcileIssues[]`
- Pagination: use `nextPageToken` until `isLast=true`.
- Default: use `ATREST_JIRA_DEFAULT_MAX_RESULTS` and `ATREST_JIRA_DEFAULT_FIELDS` if provided.
- Output: list of issues with key fields.

### jira.issues.get
- GET `/rest/api/3/issue/{issueIdOrKey}`
- Query: `fields` (comma-separated or array, depending on client), `expand`
- Output: key, summary, status, assignee, description (ADF), priority, labels, updated.

### jira.issues.changelog
- GET `/rest/api/3/issue/{issueIdOrKey}/changelog`
- Query: `startAt`, `maxResults`
- Output: recent changes (field, from, to, author, created).

---

## 3) Create & update issues (Platform v3)

### jira.issues.create
- POST `/rest/api/3/issue`
- Body: see `refs/jira-json-quickref.md#issue-create`
- Required fields: `project`, `issuetype`, `summary`
- Common optional: `description` (ADF), `priority`, `labels`, `assignee` (accountId)
- Output: created issue key + self link.

### jira.issues.edit
- PUT `/rest/api/3/issue/{issueIdOrKey}`
- Query: `notifyUsers`, `returnIssue`, `overrideScreenSecurity`, `overrideEditableFlag`, `expand`
- Body: `fields` and/or `update` (operations)
- Rule: transitions are NOT done here (use transitions endpoint).
- Body reference: `refs/jira-json-quickref.md#issue-edit`
- Output: 204 (no content) unless `returnIssue=true` (then return updated issue).

### jira.issues.assign
- PUT `/rest/api/3/issue/{issueIdOrKey}/assignee`
- Body: `{ "accountId": "..." }` (or `null` for unassigned where allowed)
- Use for: assigning to a user by accountId.
- Output: 204.

### jira.issues.transitions.list
- GET `/rest/api/3/issue/{issueIdOrKey}/transitions`
- Query: `expand`, optional filters supported by Jira
- Use for: retrieving available workflow transitions (and ids).
- Output: list transitions: id, name, to.status.

### jira.issues.transitions.apply
- POST `/rest/api/3/issue/{issueIdOrKey}/transitions`
- Body: `{ "transition": { "id": "X" }, ... }` optionally plus `update.comment.add` etc.
- Body reference: `refs/jira-json-quickref.md#issue-transition`
- Output: 204.

### jira.issues.delete  (destructive)
- DELETE `/rest/api/3/issue/{issueIdOrKey}`
- Query: `deleteSubtasks` (optional)
- Require explicit user intent before calling.
- Output: 204.

---

## 4) Comments (Platform v3)

### jira.comments.list
- GET `/rest/api/3/issue/{issueIdOrKey}/comment`
- Query: `startAt`, `maxResults`, `orderBy`, `expand`
- Output: comment id, author, created/updated, body (ADF), visibility.

### jira.comments.add
- POST `/rest/api/3/issue/{issueIdOrKey}/comment`
- Body: `{ "body": <ADF>, "visibility": <optional>, "properties": <optional> }`
- Body reference: `refs/jira-json-quickref.md#comment-add`
- Output: created comment (id, timestamps, body).

### jira.comments.update
- PUT `/rest/api/3/issue/{issueIdOrKey}/comment/{id}`
- Body: same shape as add (body/visibility/properties)
- Output: updated comment.

### jira.comments.delete  (destructive)
- DELETE `/rest/api/3/issue/{issueIdOrKey}/comment/{id}`
- Require explicit user intent before calling.
- Output: 204.

---

## 5) Worklogs (Platform v3)

### jira.worklogs.list
- GET `/rest/api/3/issue/{issueIdOrKey}/worklog`
- Output: worklog entries (id, author, started, timeSpentSeconds, comment ADF).

### jira.worklogs.add
- POST `/rest/api/3/issue/{issueIdOrKey}/worklog`
- Body reference: `refs/jira-json-quickref.md#worklog-add`
- Output: created worklog.

---

## 6) Boards & Sprints (Agile API)

### jira.boards.list
- GET `/rest/agile/1.0/board`
- Query: `startAt`, `maxResults`, filters like `type`, `name`, `projectKeyOrId`, etc.
- Output: board id, name, type.

### jira.boards.get
- GET `/rest/agile/1.0/board/{boardId}`
- Output: board details (location, type).

### jira.boards.backlog
- GET `/rest/agile/1.0/board/{boardId}/backlog`
- Query: `startAt`, `maxResults`, `jql`, `fields`, `expand`
- Output: backlog issues.

### jira.boards.issues
- GET `/rest/agile/1.0/board/{boardId}/issue`
- Query: `startAt`, `maxResults`, `jql`, `fields`, `expand`
- Output: issues currently on the board (by board column mapping).

### jira.boards.sprints
- GET `/rest/agile/1.0/board/{boardId}/sprint`
- Query: `startAt`, `maxResults`, `state`
- Output: sprints (id, name, state, dates).

### jira.boards.sprint.issues
- GET `/rest/agile/1.0/board/{boardId}/sprint/{sprintId}/issue`
- Query: `startAt`, `maxResults`, optional filters
- Output: issues in that sprint (board view).

---

## 7) Sprint lifecycle (Agile API)

### jira.sprints.create
- POST `/rest/agile/1.0/sprint`
- Body reference: `refs/jira-json-quickref.md#sprint-create`
- Output: created sprint.

### jira.sprints.get
- GET `/rest/agile/1.0/sprint/{sprintId}`
- Output: sprint details.

### jira.sprints.update
- PUT `/rest/agile/1.0/sprint/{sprintId}`
- Body: full sprint object fields (note: missing fields become null!)
- Use for: rename, goal, start/close by state changes when allowed.

### jira.sprints.issues
- GET `/rest/agile/1.0/sprint/{sprintId}/issue`
- Output: sprint issues.

### jira.sprints.addIssues
- POST `/rest/agile/1.0/sprint/{sprintId}/issue`
- Body: `{ "issues": ["PROJ-1","PROJ-2", ...] }`
- Output: 204 on success.

---

## Output conventions (recommended)
When replying to the user after an API call:
- For issue lists: show `KEY — Summary (Status) [Assignee] updated <date>`
- For single issue: show key fields + the user-requested detail (description/comments/etc.)
- For updates/transitions: confirm what changed + resulting status/assignee

---

## Quickref — embedding app data into Jira issue text
For patterns and ready-to-copy ADF payload snippets (including an example for “ContentCraft: Mermaid Diagrams for Jira”), see:
- `refs/app-embedding-quickref.md`

---

## JSON references
- `refs/jira-json-quickref.md` (payload shapes, short parameter notes, ADF helper)
- `refs/jql-cheatsheet.md` (ready-to-use JQL patterns)
- `refs/openclaw_env_example.json` (env snippet)
- `refs/app-embedding-quickref.md` (how to embed app data into Jira text bodies; includes ContentCraft Mermaid example)
