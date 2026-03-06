# Index

| API | Line |
|-----|------|
| Notion | 2 |
| Airtable | 130 |
| Google Sheets | 226 |
| Google Drive | 320 |
| Google Calendar | 403 |
| Dropbox | 487 |
| Linear | 555 |
| Jira | 657 |
| Asana | 765 |
| Trello | 837 |
| Monday.com | 910 |
| ClickUp | 967 |
| Figma | 1028 |
| Calendly | 1089 |
| Cal.com | 1168 |
| Loom | 1249 |
| Typeform | 1336 |

---

# Notion

## Base URL
```
https://api.notion.com/v1
```

## Authentication
```bash
curl https://api.notion.com/v1/users/me \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2022-06-28"
```

Note: `Notion-Version` header is required.

## Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /pages | POST | Create page |
| /pages/:id | GET | Get page |
| /pages/:id | PATCH | Update page |
| /databases/:id/query | POST | Query database |
| /databases | POST | Create database |
| /blocks/:id/children | GET | Get blocks |
| /blocks/:id/children | PATCH | Append blocks |
| /search | POST | Search pages/databases |

## Quick Examples

### Query Database
```bash
curl -X POST "https://api.notion.com/v1/databases/DB_ID/query" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  -d '{
    "filter": {
      "property": "Status",
      "select": {"equals": "Done"}
    }
  }'
```

### Create Page
```bash
curl -X POST https://api.notion.com/v1/pages \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"database_id": "DB_ID"},
    "properties": {
      "Name": {"title": [{"text": {"content": "New Page"}}]},
      "Status": {"select": {"name": "In Progress"}}
    }
  }'
```

### Update Page Properties
```bash
curl -X PATCH "https://api.notion.com/v1/pages/PAGE_ID" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "Status": {"select": {"name": "Done"}}
    }
  }'
```

### Append Block Content
```bash
curl -X PATCH "https://api.notion.com/v1/blocks/PAGE_ID/children" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  -d '{
    "children": [
      {
        "paragraph": {
          "rich_text": [{"text": {"content": "Hello World"}}]
        }
      }
    ]
  }'
```

### Search
```bash
curl -X POST https://api.notion.com/v1/search \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  -d '{"query": "meeting notes"}'
```

## Property Types

| Type | Example Value |
|------|---------------|
| title | `{"title": [{"text": {"content": "..."}}]}` |
| rich_text | `{"rich_text": [{"text": {"content": "..."}}]}` |
| number | `{"number": 42}` |
| select | `{"select": {"name": "Option"}}` |
| multi_select | `{"multi_select": [{"name": "Tag1"}]}` |
| date | `{"date": {"start": "2024-01-01"}}` |
| checkbox | `{"checkbox": true}` |
| url | `{"url": "https://..."}` |
| email | `{"email": "user@example.com"}` |

## Common Traps

- Always include `Notion-Version` header
- Page IDs can have dashes or not (both work)
- Database queries return max 100 items (paginate with `start_cursor`)
- Integration must be shared with pages/databases to access them
- Rich text is always an array, even for single text

## Rate Limits

- 3 requests/second per integration
- Pagination: 100 items max per request

## Official Docs
https://developers.notion.com/reference
# Airtable

## Base URL
```
https://api.airtable.com/v0
```

## Authentication
```bash
curl https://api.airtable.com/v0/$BASE_ID/$TABLE_NAME \
  -H "Authorization: Bearer $AIRTABLE_API_KEY"
```

## Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /:baseId/:tableName | GET | List records |
| /:baseId/:tableName | POST | Create records |
| /:baseId/:tableName/:recordId | GET | Get record |
| /:baseId/:tableName/:recordId | PATCH | Update record |
| /:baseId/:tableName/:recordId | DELETE | Delete record |

## Quick Examples

### List Records
```bash
curl "https://api.airtable.com/v0/$BASE_ID/$TABLE_NAME?maxRecords=10" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY"
```

### List with Filter
```bash
curl "https://api.airtable.com/v0/$BASE_ID/$TABLE_NAME" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" \
  --data-urlencode "filterByFormula={Status}='Done'"
```

### Create Record
```bash
curl -X POST "https://api.airtable.com/v0/$BASE_ID/$TABLE_NAME" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "records": [{
      "fields": {
        "Name": "John Doe",
        "Email": "john@example.com",
        "Status": "Active"
      }
    }]
  }'
```

### Update Record
```bash
curl -X PATCH "https://api.airtable.com/v0/$BASE_ID/$TABLE_NAME/$RECORD_ID" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "fields": {
      "Status": "Done"
    }
  }'
```

### Delete Record
```bash
curl -X DELETE "https://api.airtable.com/v0/$BASE_ID/$TABLE_NAME/$RECORD_ID" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY"
```

## Filter Formula Examples

| Filter | Formula |
|--------|---------|
| Equals | `{Field}='value'` |
| Contains | `FIND('text', {Field})` |
| Greater than | `{Number}>10` |
| Multiple conditions | `AND({A}='x', {B}='y')` |
| Is empty | `{Field}=BLANK()` |

## Common Traps

- Table names with spaces need URL encoding
- Base ID starts with "app", table name is human-readable
- Pagination returns max 100 records, use `offset` for more
- Field names are case-sensitive
- filterByFormula must be URL encoded

## Rate Limits

- 5 requests/second per base

## Official Docs
https://airtable.com/developers/web/api/introduction
# Google Sheets

## Base URL
```
https://sheets.googleapis.com/v4
```

## Authentication
```bash
curl https://sheets.googleapis.com/v4/spreadsheets/$SPREADSHEET_ID \
  -H "Authorization: Bearer $GOOGLE_ACCESS_TOKEN"
```

## Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /spreadsheets/:id | GET | Get spreadsheet |
| /spreadsheets/:id/values/:range | GET | Get values |
| /spreadsheets/:id/values/:range | PUT | Update values |
| /spreadsheets/:id/values/:range:append | POST | Append rows |
| /spreadsheets/:id:batchUpdate | POST | Batch operations |

## Quick Examples

### Get Values
```bash
curl "https://sheets.googleapis.com/v4/spreadsheets/$SPREADSHEET_ID/values/Sheet1!A1:D10" \
  -H "Authorization: Bearer $GOOGLE_ACCESS_TOKEN"
```

### Update Values
```bash
curl -X PUT "https://sheets.googleapis.com/v4/spreadsheets/$SPREADSHEET_ID/values/Sheet1!A1:B2?valueInputOption=RAW" \
  -H "Authorization: Bearer $GOOGLE_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "values": [
      ["Name", "Email"],
      ["John", "john@example.com"]
    ]
  }'
```

### Append Rows
```bash
curl -X POST "https://sheets.googleapis.com/v4/spreadsheets/$SPREADSHEET_ID/values/Sheet1!A:D:append?valueInputOption=RAW&insertDataOption=INSERT_ROWS" \
  -H "Authorization: Bearer $GOOGLE_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "values": [
      ["New", "Row", "Data", "Here"]
    ]
  }'
```

### Clear Range
```bash
curl -X POST "https://sheets.googleapis.com/v4/spreadsheets/$SPREADSHEET_ID/values/Sheet1!A1:D10:clear" \
  -H "Authorization: Bearer $GOOGLE_ACCESS_TOKEN"
```

## Value Input Options

| Option | Behavior |
|--------|----------|
| RAW | Values stored as-is |
| USER_ENTERED | Parsed like user typed (formulas work) |

## A1 Notation

| Example | Meaning |
|---------|---------|
| Sheet1!A1 | Cell A1 |
| Sheet1!A1:B2 | Range A1 to B2 |
| Sheet1!A:A | Entire column A |
| Sheet1!1:1 | Entire row 1 |
| A1:B2 | First sheet, A1 to B2 |

## Common Traps

- Spreadsheet ID is in URL: `/spreadsheets/d/{ID}/edit`
- Sheet names with spaces need quotes: `'My Sheet'!A1`
- valueInputOption required for write operations
- Empty cells return nothing, not null
- Formulas start with = like in the UI

## Rate Limits

- 300 read requests/minute/project
- 300 write requests/minute/project

## Official Docs
https://developers.google.com/sheets/api/reference/rest
# Google Drive

## Base URL
```
https://www.googleapis.com/drive/v3
```

## Authentication
```bash
curl "https://www.googleapis.com/drive/v3/files" \
  -H "Authorization: Bearer $GOOGLE_ACCESS_TOKEN"
```

## Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /files | GET | List files |
| /files | POST | Create/upload file |
| /files/:id | GET | Get file metadata |
| /files/:id | PATCH | Update file |
| /files/:id | DELETE | Delete file |

## Quick Examples

### List Files
```bash
curl "https://www.googleapis.com/drive/v3/files?pageSize=10&fields=files(id,name,mimeType)" \
  -H "Authorization: Bearer $GOOGLE_ACCESS_TOKEN"
```

### Search Files
```bash
curl "https://www.googleapis.com/drive/v3/files?q=name%20contains%20'report'" \
  -H "Authorization: Bearer $GOOGLE_ACCESS_TOKEN"
```

### Download File
```bash
curl "https://www.googleapis.com/drive/v3/files/$FILE_ID?alt=media" \
  -H "Authorization: Bearer $GOOGLE_ACCESS_TOKEN" \
  -o downloaded_file.pdf
```

### Upload File
```bash
curl -X POST "https://www.googleapis.com/upload/drive/v3/files?uploadType=media" \
  -H "Authorization: Bearer $GOOGLE_ACCESS_TOKEN" \
  -H "Content-Type: application/pdf" \
  --data-binary @file.pdf
```

### Create Folder
```bash
curl -X POST "https://www.googleapis.com/drive/v3/files" \
  -H "Authorization: Bearer $GOOGLE_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Folder",
    "mimeType": "application/vnd.google-apps.folder"
  }'
```

## Query Syntax

| Query | Meaning |
|-------|---------|
| `name = 'file.pdf'` | Exact name |
| `name contains 'report'` | Contains text |
| `mimeType = 'application/pdf'` | By type |
| `'FOLDER_ID' in parents` | In folder |
| `trashed = false` | Not in trash |

## Common Traps

- Use `fields` parameter to get specific metadata
- Download needs `alt=media` parameter
- Folders have special mimeType
- Query must be URL encoded
- Export Google Docs with `/export?mimeType=`

## Official Docs
https://developers.google.com/drive/api/reference/rest/v3
# Google Calendar

## Base URL
```
https://www.googleapis.com/calendar/v3
```

## Authentication
```bash
curl https://www.googleapis.com/calendar/v3/calendars/primary \
  -H "Authorization: Bearer $GOOGLE_ACCESS_TOKEN"
```

## Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /calendars/:id | GET | Get calendar |
| /calendars/:id/events | GET | List events |
| /calendars/:id/events | POST | Create event |
| /calendars/:id/events/:eventId | PUT | Update event |
| /calendars/:id/events/:eventId | DELETE | Delete event |
| /freeBusy | POST | Check availability |

## Quick Examples

### List Events
```bash
curl "https://www.googleapis.com/calendar/v3/calendars/primary/events?maxResults=10&orderBy=startTime&singleEvents=true&timeMin=$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  -H "Authorization: Bearer $GOOGLE_ACCESS_TOKEN"
```

### Create Event
```bash
curl -X POST https://www.googleapis.com/calendar/v3/calendars/primary/events \
  -H "Authorization: Bearer $GOOGLE_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "summary": "Meeting",
    "start": {"dateTime": "2024-01-15T10:00:00-07:00"},
    "end": {"dateTime": "2024-01-15T11:00:00-07:00"},
    "attendees": [{"email": "user@example.com"}]
  }'
```

### Create All-Day Event
```bash
curl -X POST https://www.googleapis.com/calendar/v3/calendars/primary/events \
  -H "Authorization: Bearer $GOOGLE_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "summary": "Holiday",
    "start": {"date": "2024-01-15"},
    "end": {"date": "2024-01-16"}
  }'
```

### Check Free/Busy
```bash
curl -X POST https://www.googleapis.com/calendar/v3/freeBusy \
  -H "Authorization: Bearer $GOOGLE_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "timeMin": "2024-01-15T00:00:00Z",
    "timeMax": "2024-01-16T00:00:00Z",
    "items": [{"id": "primary"}]
  }'
```

## Common Traps

- `primary` = user's primary calendar
- All-day events use `date`, timed events use `dateTime`
- `singleEvents=true` expands recurring events
- Times must include timezone or be UTC (Z suffix)
- OAuth scopes: `calendar.events` or `calendar.readonly`

## Rate Limits

- 1,000,000 queries/day per project
- 500 queries/100 seconds per user

## Official Docs
https://developers.google.com/calendar/api/v3/reference
# Dropbox

## Base URLs
```
# Metadata operations
https://api.dropboxapi.com/2

# File content operations
https://content.dropboxapi.com/2
```

## Authentication
```bash
curl https://api.dropboxapi.com/2/users/get_current_account \
  -H "Authorization: Bearer $DROPBOX_TOKEN"
```

## List Files
```bash
curl -X POST https://api.dropboxapi.com/2/files/list_folder \
  -H "Authorization: Bearer $DROPBOX_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"path": ""}'
```

## Download File
```bash
curl -X POST https://content.dropboxapi.com/2/files/download \
  -H "Authorization: Bearer $DROPBOX_TOKEN" \
  -H 'Dropbox-API-Arg: {"path": "/folder/file.pdf"}' \
  -o file.pdf
```

## Upload File
```bash
curl -X POST https://content.dropboxapi.com/2/files/upload \
  -H "Authorization: Bearer $DROPBOX_TOKEN" \
  -H "Content-Type: application/octet-stream" \
  -H 'Dropbox-API-Arg: {"path": "/folder/file.pdf", "mode": "add"}' \
  --data-binary @file.pdf
```

## Create Folder
```bash
curl -X POST https://api.dropboxapi.com/2/files/create_folder_v2 \
  -H "Authorization: Bearer $DROPBOX_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"path": "/new_folder"}'
```

## Search
```bash
curl -X POST https://api.dropboxapi.com/2/files/search_v2 \
  -H "Authorization: Bearer $DROPBOX_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "report", "options": {"max_results": 10}}'
```

## Common Traps

- Paths start with `/` (root of app folder or full Dropbox)
- File content uses different base URL
- `Dropbox-API-Arg` header for file operations (JSON)
- Empty string `""` for root folder listing
- Rate limit: varies, auto-retry on 429

## Official Docs
https://www.dropbox.com/developers/documentation/http/documentation
# Linear

## Base URL
```
https://api.linear.app/graphql
```

## Authentication
```bash
curl https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ viewer { id name } }"}'
```

## GraphQL Queries

### Get Current User
```bash
curl https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{ viewer { id name email } }"
  }'
```

### List Issues
```bash
curl https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{ issues(first: 10) { nodes { id title state { name } } } }"
  }'
```

### Create Issue
```bash
curl https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation { issueCreate(input: { title: \"Bug fix\", teamId: \"TEAM_ID\" }) { success issue { id identifier title } } }"
  }'
```

### Update Issue
```bash
curl https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation { issueUpdate(id: \"ISSUE_ID\", input: { stateId: \"STATE_ID\" }) { success } }"
  }'
```

### Search Issues
```bash
curl https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{ issueSearch(query: \"bug\", first: 10) { nodes { id title identifier } } }"
  }'
```

### List Teams
```bash
curl https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{ teams { nodes { id name key } } }"
  }'
```

## Common Queries

| Resource | Query |
|----------|-------|
| Issues | `issues(first: N) { nodes { ... } }` |
| Projects | `projects(first: N) { nodes { ... } }` |
| Teams | `teams { nodes { ... } }` |
| Cycles | `cycles(first: N) { nodes { ... } }` |
| Users | `users { nodes { ... } }` |

## Common Traps

- GraphQL only, no REST endpoints
- API key goes in Authorization header without Bearer prefix
- Team ID required for creating issues
- Use identifier (ABC-123) for human-readable issue IDs
- Mutations return success boolean and object

## Rate Limits

- 1500 requests/hour for Personal API keys
- Higher limits for OAuth apps

## Official Docs
https://developers.linear.app/docs/graphql/working-with-the-graphql-api
# Jira

## Base URL
```
https://{site}.atlassian.net/rest/api/3
```

## Authentication
```bash
curl "https://{site}.atlassian.net/rest/api/3/myself" \
  -u "email@example.com:$JIRA_API_TOKEN" \
  -H "Accept: application/json"
```

## Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /issue | POST | Create issue |
| /issue/:key | GET | Get issue |
| /issue/:key | PUT | Update issue |
| /search | POST | JQL search |
| /project | GET | List projects |

## Quick Examples

### Get Issue
```bash
curl "https://{site}.atlassian.net/rest/api/3/issue/PROJ-123" \
  -u "email@example.com:$JIRA_API_TOKEN"
```

### Create Issue
```bash
curl -X POST "https://{site}.atlassian.net/rest/api/3/issue" \
  -u "email@example.com:$JIRA_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "fields": {
      "project": {"key": "PROJ"},
      "summary": "Bug report",
      "description": {
        "type": "doc",
        "version": 1,
        "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Description"}]}]
      },
      "issuetype": {"name": "Bug"}
    }
  }'
```

### Update Issue
```bash
curl -X PUT "https://{site}.atlassian.net/rest/api/3/issue/PROJ-123" \
  -u "email@example.com:$JIRA_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "fields": {
      "summary": "Updated summary"
    }
  }'
```

### JQL Search
```bash
curl -X POST "https://{site}.atlassian.net/rest/api/3/search" \
  -u "email@example.com:$JIRA_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "jql": "project = PROJ AND status = \"In Progress\"",
    "maxResults": 50,
    "fields": ["summary", "status", "assignee"]
  }'
```

### Transition Issue (change status)
```bash
# First get transitions
curl "https://{site}.atlassian.net/rest/api/3/issue/PROJ-123/transitions" \
  -u "email@example.com:$JIRA_API_TOKEN"

# Then apply transition
curl -X POST "https://{site}.atlassian.net/rest/api/3/issue/PROJ-123/transitions" \
  -u "email@example.com:$JIRA_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"transition": {"id": "31"}}'
```

## JQL Examples

| Query | Meaning |
|-------|---------|
| `project = PROJ` | Issues in project |
| `assignee = currentUser()` | My issues |
| `status = "In Progress"` | By status |
| `created >= -7d` | Last 7 days |
| `labels in (bug, urgent)` | By labels |

## Common Traps

- Description uses Atlassian Document Format (ADF), not plain text
- Issue types vary by project (Bug, Task, Story, etc.)
- Transitions have IDs, not names - fetch first
- Basic auth uses email:API_TOKEN, not password
- Rate limits: ~100 requests/minute

## Official Docs
https://developer.atlassian.com/cloud/jira/platform/rest/v3/
# Asana

## Base URL
```
https://app.asana.com/api/1.0
```

## Authentication
```bash
curl https://app.asana.com/api/1.0/users/me \
  -H "Authorization: Bearer $ASANA_TOKEN"
```

## Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /tasks | POST | Create task |
| /tasks/:id | GET | Get task |
| /tasks/:id | PUT | Update task |
| /projects/:id/tasks | GET | List project tasks |
| /workspaces | GET | List workspaces |

## Quick Examples

### List Tasks in Project
```bash
curl "https://app.asana.com/api/1.0/projects/$PROJECT_GID/tasks?opt_fields=name,completed,due_on" \
  -H "Authorization: Bearer $ASANA_TOKEN"
```

### Create Task
```bash
curl -X POST "https://app.asana.com/api/1.0/tasks" \
  -H "Authorization: Bearer $ASANA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "name": "New task",
      "projects": ["PROJECT_GID"],
      "due_on": "2024-01-15",
      "notes": "Task description"
    }
  }'
```

### Update Task
```bash
curl -X PUT "https://app.asana.com/api/1.0/tasks/$TASK_GID" \
  -H "Authorization: Bearer $ASANA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"data": {"completed": true}}'
```

### Add Comment
```bash
curl -X POST "https://app.asana.com/api/1.0/tasks/$TASK_GID/stories" \
  -H "Authorization: Bearer $ASANA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"data": {"text": "Comment text"}}'
```

## Common Traps

- Use `gid` (global ID), not numeric ID
- Wrap data in `data` object for POST/PUT
- Use `opt_fields` to get specific fields (default is minimal)
- Tasks can be in multiple projects
- Rate limit: 150 requests/minute

## Official Docs
https://developers.asana.com/reference/rest-api-reference
# Trello

## Base URL
```
https://api.trello.com/1
```

## Authentication
```bash
curl "https://api.trello.com/1/members/me?key=$TRELLO_KEY&token=$TRELLO_TOKEN"
```

## Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /boards/:id | GET | Get board |
| /boards/:id/lists | GET | Get lists |
| /boards/:id/cards | GET | Get cards |
| /cards | POST | Create card |
| /cards/:id | PUT | Update card |

## Quick Examples

### Get Board
```bash
curl "https://api.trello.com/1/boards/$BOARD_ID?key=$TRELLO_KEY&token=$TRELLO_TOKEN"
```

### Get Lists
```bash
curl "https://api.trello.com/1/boards/$BOARD_ID/lists?key=$TRELLO_KEY&token=$TRELLO_TOKEN"
```

### Get Cards
```bash
curl "https://api.trello.com/1/boards/$BOARD_ID/cards?key=$TRELLO_KEY&token=$TRELLO_TOKEN"
```

### Create Card
```bash
curl -X POST "https://api.trello.com/1/cards?key=$TRELLO_KEY&token=$TRELLO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New card",
    "desc": "Description",
    "idList": "LIST_ID",
    "due": "2024-01-15T12:00:00.000Z"
  }'
```

### Move Card
```bash
curl -X PUT "https://api.trello.com/1/cards/$CARD_ID?key=$TRELLO_KEY&token=$TRELLO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"idList": "NEW_LIST_ID"}'
```

### Add Label
```bash
curl -X POST "https://api.trello.com/1/cards/$CARD_ID/idLabels?key=$TRELLO_KEY&token=$TRELLO_TOKEN&value=$LABEL_ID"
```

## Common Traps

- Both key AND token required in query params
- Board ID is in URL: trello.com/b/{BOARD_ID}/name
- Lists belong to boards, cards belong to lists
- Dates in ISO 8601 format with timezone
- Rate limit: 100 requests/10 seconds per token

## Official Docs
https://developer.atlassian.com/cloud/trello/rest/api-group-actions/
# Monday.com

## Base URL
```
https://api.monday.com/v2
```

## Authentication
```bash
curl https://api.monday.com/v2 \
  -H "Authorization: $MONDAY_API_KEY" \
  -H "Content-Type: application/json"
```

## GraphQL API

### Get Boards
```bash
curl https://api.monday.com/v2 \
  -H "Authorization: $MONDAY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ boards(limit:10) { id name } }"}'
```

### Get Items from Board
```bash
curl https://api.monday.com/v2 \
  -H "Authorization: $MONDAY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ boards(ids: 123456) { items_page { items { id name column_values { id value } } } } }"}'
```

### Create Item
```bash
curl https://api.monday.com/v2 \
  -H "Authorization: $MONDAY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation { create_item(board_id: 123456, item_name: \"New Task\") { id } }"}'
```

### Update Column Value
```bash
curl https://api.monday.com/v2 \
  -H "Authorization: $MONDAY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation { change_column_value(board_id: 123456, item_id: 789, column_id: \"status\", value: \"{\\"label\\": \\"Done\\"}\") { id } }"}'
```

## Common Traps

- GraphQL only, no REST
- Column values are JSON strings inside JSON
- Rate limit: 10,000 complexity/minute
- Board IDs are numbers

## Official Docs
https://developer.monday.com/api-reference/docs
# ClickUp

## Base URL
```
https://api.clickup.com/api/v2
```

## Authentication
```bash
curl https://api.clickup.com/api/v2/user \
  -H "Authorization: $CLICKUP_API_KEY"
```

## Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /team | GET | Get workspaces |
| /team/:id/space | GET | Get spaces |
| /list/:id/task | GET | Get tasks |
| /list/:id/task | POST | Create task |
| /task/:id | PUT | Update task |

## Get Tasks
```bash
curl "https://api.clickup.com/api/v2/list/$LIST_ID/task" \
  -H "Authorization: $CLICKUP_API_KEY"
```

## Create Task
```bash
curl -X POST "https://api.clickup.com/api/v2/list/$LIST_ID/task" \
  -H "Authorization: $CLICKUP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Task",
    "description": "Task description",
    "status": "to do",
    "priority": 3,
    "due_date": 1704067200000
  }'
```

## Priority Values

| Value | Priority |
|-------|----------|
| 1 | Urgent |
| 2 | High |
| 3 | Normal |
| 4 | Low |

## Common Traps

- Dates are Unix timestamps in milliseconds
- Hierarchy: Workspace > Space > Folder > List > Task
- Status names are case-sensitive
- Rate limit: 100 requests/minute

## Official Docs
https://clickup.com/api
# Figma

## Base URL
```
https://api.figma.com/v1
```

## Authentication
```bash
curl https://api.figma.com/v1/me \
  -H "X-Figma-Token: $FIGMA_TOKEN"
```

## Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /me | GET | Current user |
| /files/:key | GET | Get file |
| /files/:key/nodes | GET | Get specific nodes |
| /images/:key | GET | Export images |
| /files/:key/comments | GET | Get comments |

## Get File
```bash
curl "https://api.figma.com/v1/files/$FILE_KEY" \
  -H "X-Figma-Token: $FIGMA_TOKEN"
```

## Export Images
```bash
curl "https://api.figma.com/v1/images/$FILE_KEY?ids=1:2,1:3&format=png&scale=2" \
  -H "X-Figma-Token: $FIGMA_TOKEN"
```

## Get Comments
```bash
curl "https://api.figma.com/v1/files/$FILE_KEY/comments" \
  -H "X-Figma-Token: $FIGMA_TOKEN"
```

## Post Comment
```bash
curl -X POST "https://api.figma.com/v1/files/$FILE_KEY/comments" \
  -H "X-Figma-Token: $FIGMA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Great work!",
    "client_meta": {"x": 100, "y": 200}
  }'
```

## Common Traps

- File key is in URL: figma.com/file/{KEY}/...
- Node IDs use format "1:2" (page:node)
- Export formats: jpg, png, svg, pdf
- Rate limit: varies by endpoint

## Official Docs
https://www.figma.com/developers/api
# Calendly

## Base URL
```
https://api.calendly.com
```

## Authentication
```bash
curl https://api.calendly.com/users/me \
  -H "Authorization: Bearer $CALENDLY_TOKEN"
```

## Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /users/me | GET | Current user |
| /event_types | GET | List event types |
| /scheduled_events | GET | List events |
| /scheduled_events/:uuid/invitees | GET | Get invitees |

## Quick Examples

### Get Current User
```bash
curl https://api.calendly.com/users/me \
  -H "Authorization: Bearer $CALENDLY_TOKEN"
```

### List Event Types
```bash
curl "https://api.calendly.com/event_types?user=$USER_URI" \
  -H "Authorization: Bearer $CALENDLY_TOKEN"
```

### List Scheduled Events
```bash
curl "https://api.calendly.com/scheduled_events?user=$USER_URI&status=active" \
  -H "Authorization: Bearer $CALENDLY_TOKEN"
```

### Get Event Details
```bash
curl "https://api.calendly.com/scheduled_events/$EVENT_UUID" \
  -H "Authorization: Bearer $CALENDLY_TOKEN"
```

### Get Invitees
```bash
curl "https://api.calendly.com/scheduled_events/$EVENT_UUID/invitees" \
  -H "Authorization: Bearer $CALENDLY_TOKEN"
```

### Cancel Event
```bash
curl -X POST "https://api.calendly.com/scheduled_events/$EVENT_UUID/cancellation" \
  -H "Authorization: Bearer $CALENDLY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"reason": "Schedule conflict"}'
```

## Event Status Values

| Status | Meaning |
|--------|---------|
| active | Upcoming |
| canceled | Cancelled |

## Common Traps

- URIs (not IDs) used for user/event references
- User URI from /users/me response
- Pagination via `page_token`
- Webhooks for real-time updates
- Rate limit: 100 requests/minute

## Official Docs
https://developer.calendly.com/api-docs
# Cal.com

Cal.com scheduling API for bookings, availability, and event types.

## Base URL
`https://api.cal.com/v2`

## Authentication
API Key or OAuth 2.0. Pass via Authorization header with Bearer token.

```bash
curl -X GET "https://api.cal.com/v2/me" \
  -H "Authorization: Bearer cal_live_xxxxx"
```

## Core Endpoints

### Get Current User
```bash
curl -X GET "https://api.cal.com/v2/me" \
  -H "Authorization: Bearer {API_KEY}"
```

### List Event Types
```bash
curl -X GET "https://api.cal.com/v2/event-types" \
  -H "Authorization: Bearer {API_KEY}"
```

### Get Availability
```bash
curl -X GET "https://api.cal.com/v2/availability?eventTypeId=123&startTime=2024-01-15T00:00:00Z&endTime=2024-01-16T00:00:00Z" \
  -H "Authorization: Bearer {API_KEY}"
```

### Create Booking
```bash
curl -X POST "https://api.cal.com/v2/bookings" \
  -H "Authorization: Bearer {API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "eventTypeId": 123,
    "start": "2024-01-15T10:00:00Z",
    "responses": {
      "name": "John Doe",
      "email": "john@example.com"
    },
    "timeZone": "America/New_York"
  }'
```

### List Bookings
```bash
curl -X GET "https://api.cal.com/v2/bookings" \
  -H "Authorization: Bearer {API_KEY}"
```

### Cancel Booking
```bash
curl -X DELETE "https://api.cal.com/v2/bookings/{BOOKING_UID}" \
  -H "Authorization: Bearer {API_KEY}"
```

## Rate Limits
- 120 requests/minute (API Key)
- Can be increased upon request to support

## Gotchas
- **API v2 is current**: v1 is deprecated
- Test keys prefix: `cal_`, Live keys prefix: `cal_live_`
- OAuth credentials required for platform/managed users features
- Teams endpoints require Teams plan
- Organizations endpoints require Organizations plan
- Platform features (managed users, OAuth client webhooks) currently limited to existing customers
- Webhook events available for booking lifecycle

## Links
- [Docs](https://cal.com/docs/api-reference)
- [API v2 Reference](https://cal.com/docs/api-reference/v2/introduction)
- [OAuth](https://cal.com/docs/api-reference/v2/oauth)
- [Webhooks](https://cal.com/docs/api-reference/v2/webhooks)
# Loom

Loom SDK for recording and embedding video messages.

## Base URL
SDK-based integration (Record SDK, Embed SDK). No traditional REST API.

## Authentication
SDK Key from Loom Developer Portal. Passed during SDK initialization.

```javascript
// Record SDK
import { setup } from "@loomhq/record-sdk";

const { configureButton } = await setup({
  publicAppId: "YOUR_PUBLIC_APP_ID"
});
```

## Core Features

### Record SDK - Button Setup
```javascript
import { setup, isSupported } from "@loomhq/record-sdk";

if (isSupported()) {
  const { configureButton } = await setup({
    publicAppId: "YOUR_PUBLIC_APP_ID"
  });

  const button = document.getElementById("record-button");
  
  configureButton({ element: button });
  
  button.addEventListener("loom-record-complete", (e) => {
    const { sharedUrl, embedUrl } = e.detail;
    console.log("Video URL:", sharedUrl);
  });
}
```

### Embed SDK - Embed Video
```javascript
import { oembed } from "@loomhq/loom-embed";

const videoUrl = "https://www.loom.com/share/abc123";
const embedHtml = await oembed(videoUrl);

document.getElementById("video-container").innerHTML = embedHtml.html;
```

### Embed SDK - With Options
```javascript
import { oembed } from "@loomhq/loom-embed";

const embedHtml = await oembed(videoUrl, {
  width: 640,
  height: 360,
  hideOwner: true,
  hideTitle: true
});
```

### oEmbed Endpoint
```bash
curl "https://www.loom.com/v1/oembed?url=https://www.loom.com/share/abc123"
```

## Rate Limits
- SDK usage tracked per Public App ID
- oEmbed: Standard rate limiting applies

## Gotchas
- **No REST API**: Loom uses SDK-only approach for recording
- Record SDK is browser-only (no Node.js support)
- Recording requires user permission (camera/mic)
- Safari has limited support for some features
- Embed URLs differ from share URLs
- Recording callbacks fire when upload completes, not when recording ends
- Enterprise plans required for some SDK features

## Links
- [Developer Portal](https://www.loom.com/developer)
- [Record SDK](https://www.loom.com/sdk/record)
- [Embed SDK](https://www.loom.com/sdk/embed)
- [npm: @loomhq/record-sdk](https://www.npmjs.com/package/@loomhq/record-sdk)
- [npm: @loomhq/loom-embed](https://www.npmjs.com/package/@loomhq/loom-embed)
# Typeform

## Base URL
```
https://api.typeform.com
```

## Authentication
```bash
curl https://api.typeform.com/me \
  -H "Authorization: Bearer $TYPEFORM_TOKEN"
```

## Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /forms | GET | List forms |
| /forms/:id | GET | Get form |
| /forms/:id/responses | GET | Get responses |
| /forms | POST | Create form |

## List Forms
```bash
curl "https://api.typeform.com/forms" \
  -H "Authorization: Bearer $TYPEFORM_TOKEN"
```

## Get Responses
```bash
curl "https://api.typeform.com/forms/$FORM_ID/responses?page_size=25" \
  -H "Authorization: Bearer $TYPEFORM_TOKEN"
```

## Get Responses with Filters
```bash
curl "https://api.typeform.com/forms/$FORM_ID/responses?since=2024-01-01T00:00:00&until=2024-01-31T23:59:59" \
  -H "Authorization: Bearer $TYPEFORM_TOKEN"
```

## Create Form
```bash
curl -X POST "https://api.typeform.com/forms" \
  -H "Authorization: Bearer $TYPEFORM_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Feedback Form",
    "fields": [
      {
        "type": "short_text",
        "title": "What is your name?"
      },
      {
        "type": "rating",
        "title": "How would you rate us?",
        "properties": {"steps": 5}
      }
    ]
  }'
```

## Field Types

| Type | Description |
|------|-------------|
| short_text | Single line text |
| long_text | Multi-line text |
| multiple_choice | Select one |
| rating | Star rating |
| yes_no | Boolean |
| email | Email input |
| number | Numeric input |

## Common Traps

- Response answers keyed by field ref/id
- Pagination via page_size and before/after tokens
- Webhooks for real-time responses
- Rate limit: 2 requests/second

## Official Docs
https://www.typeform.com/developers/create/reference/
