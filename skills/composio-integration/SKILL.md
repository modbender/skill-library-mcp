---
name: Composio Integration Skill
description: "Access 600+ apps and services through Composio's unified API.
  Currently connected: Gmail and Google Tasks."
---

# Composio Integration Skill

Access 600+ apps and services through Composio's unified API. Currently connected: Gmail and Google Tasks.

## 🔑 API Key Location

**Saved securely in:** `/home/sidharth/clawd/memory/composio-credentials.md`  
**Also in:** `~/.bashrc` (line 135) - auto-loads on terminal start

**API Key:** `ak_AXxQjyexBuSiJXTYOTPB`

## 📦 Connected Accounts

### Gmail (ca_0cxayHx2BME1)
- **Email:** sonukumar5fr@gmail.com
- **Status:** ACTIVE ✅
- **Capabilities:** Read/send emails, manage labels, drafts, contacts

### Google Tasks (ca_kSNnWG4OHngG)
- **Email:** sonukumar5fr@gmail.com  
- **Status:** ACTIVE ✅
- **Capabilities:** Create/update/delete tasks and task lists

## 🛠️ Available Tools

### Gmail Tools (20+)
- `GMAIL_FETCH_EMAILS` - Fetch emails
- `GMAIL_SEND_EMAIL` - Send emails
- `GMAIL_CREATE_EMAIL_DRAFT` - Create draft
- `GMAIL_REPLY_TO_THREAD` - Reply to email
- `GMAIL_SEARCH_EMAILS` - Search inbox
- `GMAIL_ADD_LABEL_TO_EMAIL` - Manage labels
- `GMAIL_DELETE_MESSAGE` - Delete emails
- And 13+ more...

### Google Tasks Tools (17)
- `GOOGLETASKS_INSERT_TASK` - Create task
- `GOOGLETASKS_LIST_TASKS` - List tasks
- `GOOGLETASKS_LIST_ALL_TASKS` - List all tasks across all lists
- `GOOGLETASKS_UPDATE_TASK` - Update task
- `GOOGLETASKS_DELETE_TASK` - Delete task
- `GOOGLETASKS_CREATE_TASK_LIST` - Create task list
- `GOOGLETASKS_BULK_INSERT_TASKS` - Bulk create tasks
- And 10+ more...

## 📝 Usage Examples

### List Available Tools
```bash
export COMPOSIO_API_KEY="ak_AXxQjyexBuSiJXTYOTPB"
node scripts/list-tools.mjs gmail        # Gmail tools only
node scripts/list-tools.mjs googletasks  # Google Tasks tools
node scripts/list-tools.mjs              # All tools (paginated)
```

### Execute a Tool

**Fetch Gmail Emails:**
```bash
node scripts/execute-tool.mjs GMAIL_FETCH_EMAILS ca_0cxayHx2BME1 '{"maxResults":5}'
```

**Create Google Task:**
```bash
node scripts/execute-tool.mjs GOOGLETASKS_INSERT_TASK ca_kSNnWG4OHngG '{"title":"My Task","notes":"Task details"}'
```

**Send Email:**
```bash
node scripts/execute-tool.mjs GMAIL_SEND_EMAIL ca_0cxayHx2BME1 '{"to":"recipient@example.com","subject":"Hello","body":"Hi there!"}'
```

## 🔧 Implementation Details

### Base URL (v3 API)
```
https://backend.composio.dev/api/v3/
```

### Authentication
All requests use header:
```
x-api-key: ak_AXxQjyexBuSiJXTYOTPB
```

### User ID
All tool executions use:
```
user_id: pg-test-228260f1-217f-40f6-a08a-41fdd0b8d8e6
```

### Scripts Location
```
/home/sidharth/clawd/skills/composio-integration/scripts/
├── list-tools.mjs       # List available tools
├── execute-tool.mjs     # Execute any tool
└── (future scripts)
```

## 🎯 Common Use Cases

### Morning Email Summary
```bash
node scripts/execute-tool.mjs GMAIL_FETCH_EMAILS ca_0cxayHx2BME1 '{"maxResults":10,"labelIds":["INBOX"]}'
```

### Add Task from Email
1. Fetch email
2. Extract key info
3. Create task:
```bash
node scripts/execute-tool.mjs GOOGLETASKS_INSERT_TASK ca_kSNnWG4OHngG '{"title":"Follow up: Email subject","notes":"From: sender@example.com"}'
```

### Send Follow-up Email
```bash
node scripts/execute-tool.mjs GMAIL_SEND_EMAIL ca_0cxayHx2BME1 '{
  "to":"client@example.com",
  "subject":"Re: Your inquiry",
  "body":"Thank you for reaching out..."
}'
```

## 🔄 Adding New Apps

To connect more apps (Calendar, Notion, Slack, etc.):

1. Visit: https://app.composio.dev/apps
2. Click "Connect" on desired app
3. Complete OAuth flow
4. Note the `connected_account_id`
5. Use with `execute-tool.mjs`

## 📚 API Reference

**Full v3 API Docs:** https://docs.composio.dev/rest-api/

**Key Endpoints Used:**
- `GET /api/v3/tools` - List tools
- `GET /api/v3/tools/:slug` - Get tool schema
- `POST /api/v3/tools/execute/:slug` - Execute tool
- `GET /api/v3/connected_accounts` - List connections

## ✅ Tested & Working

- ✅ API key authentication
- ✅ Gmail email fetching
- ✅ Tool discovery (600+ apps)
- ✅ Connected account management
- ✅ v3 API compliance (no deprecated endpoints)

## 🚀 Next Steps

- [ ] Create wrapper functions for common tasks
- [ ] Add Google Calendar integration
- [ ] Build email-to-task automation
- [ ] Create morning digest generator
- [ ] Add error handling & retry logic

---

**Last Updated:** 2026-01-20  
**Status:** ✅ Fully Operational  
**Integration Time:** ~30 minutes
