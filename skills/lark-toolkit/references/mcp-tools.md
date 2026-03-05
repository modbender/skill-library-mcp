# Lark MCP Tools (via mcporter)

38 tools available through `lark-mcp` server. Invoke with:
```bash
mcporter call lark-mcp.<tool_name> key=value
```

All tools accept optional `useUAT=true` to use user access token instead of tenant token.

## Bitable (6 tools)

| Tool | Purpose |
|------|---------|
| `bitable_v1_app_create` | Create a bitable app (optional: name, folder_token, time_zone) |
| `bitable_v1_appTable_create` | Create table in bitable (name, fields with types, default_view_name) |
| `bitable_v1_appTableField_list` | List fields of a table |
| `bitable_v1_appTable_list` | List tables in a bitable app |
| `bitable_v1_appTableRecord_create` | Create record (row) in table |
| `bitable_v1_appTableRecord_search` | Search records with filters |
| `bitable_v1_appTableRecord_update` | Update existing record |

Field types: 1=Text, 2=Number, 3=SingleSelect, 4=MultiSelect, 5=DateTime, 7=Checkbox, 11=User, 13=Phone, 15=URL, 17=Attachment, 18=Link, 20=Formula, 21=DuplexLink, 22=Location, 23=GroupChat

## Calendar (5 tools)

| Tool | Purpose |
|------|---------|
| `calendar_v4_calendarEvent_create` | Create calendar event (summary, start/end time, attendees) |
| `calendar_v4_calendarEvent_get` | Get event details |
| `calendar_v4_calendarEvent_patch` | Update event |
| `calendar_v4_calendar_primary` | Get primary calendar ID |
| `calendar_v4_freebusy_list` | Check free/busy for time range |

## Docs (4 tools)

| Tool | Purpose |
|------|---------|
| `docx_v1_document_rawContent` | Get document raw content |
| `drive_v1_permissionMember_create` | Share document (set permissions) |
| `docx_builtin_search` | Search documents by keyword |
| `docx_builtin_import` | Import document |

## IM / Messaging (5 tools)

| Tool | Purpose |
|------|---------|
| `im_v1_chat_create` | Create a new group chat |
| `im_v1_chat_list` | List all groups bot is in |
| `im_v1_chatMembers_get` | Get group members |
| `im_v1_message_create` | Send a message |
| `im_v1_message_list` | List message history |

## OKR (7 tools)

| Tool | Purpose |
|------|---------|
| `okr_v1_okr_batchGet` | Batch get OKR details |
| `okr_v1_period_list` | List OKR periods |
| `okr_v1_progressRecord_create` | Create progress record |
| `okr_v1_progressRecord_get` | Get progress record |
| `okr_v1_progressRecord_update` | Update progress record |
| `okr_v1_review_query` | Query OKR reviews |
| `okr_v1_userOkr_list` | List user's OKRs |

## Report (3 tools)

| Tool | Purpose |
|------|---------|
| `report_v1_rule_query` | Query report rules (weekly/daily report configs) |
| `report_v1_ruleView_remove` | Remove a rule view |
| `report_v1_task_query` | Query report tasks (who submitted what) |

## Task (4 tools)

| Tool | Purpose |
|------|---------|
| `task_v2_task_create` | Create a task |
| `task_v2_task_patch` | Update a task |
| `task_v2_task_addMembers` | Add members to task |
| `task_v2_task_addReminders` | Add reminders to task |

## Wiki (2 tools)

| Tool | Purpose |
|------|---------|
| `wiki_v1_node_search` | Search wiki nodes |
| `wiki_v2_space_getNode` | Get wiki node details |

## Contacts (1 tool)

| Tool | Purpose |
|------|---------|
| `contact_v3_user_batchGetId` | Batch get user IDs by email or phone |

## Docs-specific (1 tool via lark-docs server)

| Tool | Purpose |
|------|---------|
| `lark-docs.*` | Additional document operations (1 tool available) |

## Example Usage

```bash
# Create a calendar event
mcporter call lark-mcp.calendar_v4_calendarEvent_create \
  path='{"calendar_id":"primary"}' \
  data='{"summary":"Team Standup","start_time":{"timestamp":"1700000000"},"end_time":{"timestamp":"1700003600"}}'

# Search bitable records
mcporter call lark-mcp.bitable_v1_appTableRecord_search \
  path='{"app_token":"xxx","table_id":"tblxxx"}' \
  data='{"filter":{"conditions":[{"field_name":"Status","operator":"is","value":["Done"]}]}}'

# List group members
mcporter call lark-mcp.im_v1_chatMembers_get \
  path='{"chat_id":"oc_xxx"}'
```
