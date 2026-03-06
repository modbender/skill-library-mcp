# Jira JSON Quick Reference (short shapes + parameters)

## ADF minimal (plain text -> Jira rich text)
Use this wrapper for comment bodies, descriptions, textarea fields, and worklog comments.

### Shape
```json
{
  "type": "doc",
  "version": 1,
  "content": [
    {
      "type": "paragraph",
      "content": [
        { "type": "text", "text": "Hello world" }
      ]
    }
  ]
}
```

### Notes

- Multiple paragraphs =&gt; multiple `paragraph` items in `content`.
- Newlines inside a paragraph are not guaranteed to render as separate lines; prefer multiple paragraphs.

* * *

* * *

## Issue create — POST /rest/api/3/issue

### Minimal payload
```json
{
  "fields": {
    "project": { "key": "PROJ" },
    "issuetype": { "name": "Task" },
    "summary": "Short summary"
  }
}
```

### Common payload (everyday)
```json
{
  "fields": {
    "project": { "key": "PROJ" },
    "issuetype": { "name": "Task" },
    "summary": "Implement X",
    "description": {
      "type": "doc",
      "version": 1,
      "content": [
        { "type": "paragraph", "content": [{ "type": "text", "text": "Context and requirements..." }] }
      ]
    },
    "priority": { "name": "Medium" },
    "labels": ["automation", "openclaw"],
    "assignee": { "accountId": "ACCOUNT_ID" }
  },
  "update": {}
}
```

### Parameters (short)

- `fields.project`: `{ key }` or `{ id }`
- `fields.issuetype`: `{ name }` or `{ id }`
- `fields.summary`: string
- `fields.description`: ADF doc
- `fields.assignee.accountId`: string (Cloud uses accountId)
- `update`: optional operation-based updates (rare on create)

* * *

## Issue edit — PUT /rest/api/3/issue/{issueIdOrKey}

### Typical “set fields” edit
```json
{
  "fields": {
    "summary": "New summary",
    "labels": ["automation", "triage"]
  }
}
```

### Typical “operations” edit (update block)
```json
{
  "update": {
    "labels": [
      { "add": "needs-review" },
      { "remove": "wip" }
    ]
  }
}
```

### Parameters (short)

- `fields`: direct field replacement (strings, arrays, objects, ADF where required)
- `update`: operations such as `add`, `remove`, `set` depending on field type
- Query (useful):

    - `notifyUsers` (bool)
    - `returnIssue` (bool) to get updated issue back

* * *

## Issue transitions

### List transitions — GET /rest/api/3/issue/{issueIdOrKey}/transitions

No body. Use response to pick a `transition.id`.

### Apply transition — POST /rest/api/3/issue/{issueIdOrKey}/transitions
```json
{
  "transition": { "id": "5" },
  "update": {
    "comment": [
      {
        "add": {
          "body": {
            "type": "doc",
            "version": 1,
            "content": [
              { "type": "paragraph", "content": [{ "type": "text", "text": "Moved to Done." }] }
            ]
          }
        }
      }
    ]
  }
}
```

### Parameters (short)

- `transition.id`: required (string)
- `update.comment[].add.body`: ADF doc (optional)
- `fields`: optional field updates allowed by that transition screen

* * *

## Comments

### List — GET /rest/api/3/issue/{issueIdOrKey}/comment

No body.

### Add — POST /rest/api/3/issue/{issueIdOrKey}/comment
```json
{
  "body": {
    "type": "doc",
    "version": 1,
    "content": [
      { "type": "paragraph", "content": [{ "type": "text", "text": "Status update..." }] }
    ]
  },
  "visibility": {
    "type": "role",
    "value": "Administrators"
  }
}
```

### Update — PUT /rest/api/3/issue/{issueIdOrKey}/comment/{id}

Same shape as Add (body/visibility/properties).

### Parameters (short)

- `body`: ADF doc (required for add/update)
- `visibility`: optional restriction

    - typical: `{ "type": "role", "value": "<RoleName>" }` or group-based restriction
- `properties`: optional entity properties array

* * *

## Worklogs — POST /rest/api/3/issue/{issueIdOrKey}/worklog
```json
{
  "started": "2026-02-24T09:30:00.000+0100",
  "timeSpentSeconds": 3600,
  "comment": {
    "type": "doc",
    "version": 1,
    "content": [
      { "type": "paragraph", "content": [{ "type": "text", "text": "Implemented feature X." }] }
    ]
  }
}
```

### Parameters (short)

- `started`: timestamp string
- `timeSpentSeconds`: int
- `comment`: ADF doc (optional)
- `visibility`: optional

* * *

## JQL enhanced search — GET /rest/api/3/search/jql

### Example query parameters
```json
{
  "jql": "project = PROJ AND statusCategory != Done ORDER BY updated DESC",
  "maxResults": 50,
  "fields": ["summary", "status", "assignee", "priority", "updated"]
}
```

### Pagination

- Use `nextPageToken` from the response until `isLast=true`.

* * *

## Boards — GET /rest/agile/1.0/board

### Example query parameters
```json
{
  "maxResults": 50,
  "type": "scrum",
  "name": "Backend"
}
```

## Sprint create — POST /rest/agile/1.0/sprint
```json
{
  "name": "Sprint 42",
  "originBoardId": 123,
  "goal": "Ship feature X",
  "startDate": "2026-03-02T09:00:00.000+0100",
  "endDate": "2026-03-16T17:00:00.000+0100"
}
```

### Parameters (short)

- `name`: required
- `originBoardId`: required (int)
- `goal`: optional
- `startDate`, `endDate`: optional (but required to start sprint by state change later)

* * *

## Sprint add issues — POST /rest/agile/1.0/sprint/{sprintId}/issue
```json
{
  "issues": ["PROJ-101", "PROJ-102"]
}
```