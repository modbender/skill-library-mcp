---
name: helpscout
description: Fetch and reply to Helpscout conversations
metadata:
  {
    "openclaw":
      {
        "requires": { "env": ["API_KEY", "APP_SECRET", "INBOX_IDS"] },
      },
  }
---

# Helpscout Skill

## Description

This skill interacts with Helpscout to fetch conversations from specific inboxes and send replies. It is designed to streamline customer support operations directly from OpenClaw.

## Features
- Fetch conversations from multiple Helpscout inboxes
- Send replies to conversations (customer-visible or internal notes)
- Filter by status, folder, assignee, customer, tags, and more
- Sort conversations by various fields
- Embed thread data directly in the response
- Securely authenticate using an API key and App Secret
- Handle potential errors like invalid credentials or network issues gracefully

## Setup Instructions

To use this skill, you need to configure Helpscout credentials and specify the IDs of the inboxes you want to fetch conversations from.

### 1. Retrieve Helpscout API Key & App Secret
1. Go to your Helpscout account.
2. Navigate to **Manage > Apps**.
3. Create or open your app to retrieve the following details:
   - **API Key**
   - **App Secret**

### 2. Collect Inbox IDs
1. Retrieve the IDs of the inboxes you want to fetch conversations from using Helpscout's [API documentation](https://developer.helpscout.com/).

### 3. Save Credentials in OpenClaw
Use the following command to save your Helpscout credentials:

```bash
cat ~/.openclaw/openclaw.json | jq '.skills.entries.helpscout = {
  enabled: true,
  env: {
    API_KEY: "your-api-key",
    APP_SECRET: "your-app-secret",
    INBOX_IDS: ["inbox-id-1", "inbox-id-2"]
  }
}' | openclaw gateway config.apply
```

### 4. Verify Configuration
To ensure the credentials are properly set, check your configuration:

```bash
openclaw gateway config.get
```
Make sure the `helpscout` object looks correct (avoid sharing the `API_KEY` or `APP_SECRET`).

## Usage

### Basic Usage
Fetch all active conversations from configured inboxes:

```javascript
const { fetchAllInboxes } = require('./index.js');

// Fetch all active conversations (default)
const results = await fetchAllInboxes();
```

### Advanced Filtering

```javascript
const { fetchConversations } = require('./index.js');

// Fetch closed conversations from a specific inbox
const conversations = await fetchConversations(321755, {
  status: 'closed',
  sortField: 'modifiedAt',
  sortOrder: 'desc',
  page: 1
});

// Fetch conversations assigned to a specific user
const assigned = await fetchConversations(321755, {
  assignedTo: 782728,
  status: 'active'
});

// Fetch conversations with a specific tag
const tagged = await fetchConversations(321755, {
  tag: 'urgent',
  status: 'active'
});

// Fetch conversations with embedded threads
const withThreads = await fetchConversations(321755, {
  embed: 'threads',
  status: 'active'
});

// Advanced search query
const searched = await fetchConversations(321755, {
  query: '(customerEmail:user@example.com)',
  status: 'all'
});
```

### Sending Replies

```javascript
const { sendReply } = require('./index.js');

// Send a customer-visible reply (will send email)
await sendReply(3227506031, {
  text: 'Hi there,\n\nThanks for your message!\n\nBest regards,',
  inboxId: 321755  // Required to auto-fetch customer ID
});

// Send a reply without emailing the customer (imported)
await sendReply(3227506031, {
  text: 'Draft reply - not sent to customer yet',
  customerId: 856475517,  // Or provide inboxId to auto-fetch
  imported: true
});

// Send a reply and close the conversation
await sendReply(3227506031, {
  text: 'All done! Let me know if you need anything else.',
  inboxId: 321755,
  status: 'closed'
});

// Create an internal note
const { createNote } = require('./index.js');
await createNote(3227506031, 'Internal note: Customer called, issue resolved.');
```

### sendReply Options

| Parameter | Type | Description |
|-----------|------|-------------|
| `text` | string | **Required.** The reply text (HTML supported) |
| `inboxId` | number | Inbox ID - required if `customerId` not provided (auto-fetches customer) |
| `customerId` | number | Customer ID - if not provided, will be auto-fetched using `inboxId` |
| `imported` | boolean | Mark as imported (won't email customer). Default: `false` |
| `status` | string | Conversation status after reply: `active`, `pending`, `closed`. Optional. |
| `userId` | number | User ID sending the reply. Optional (defaults to authenticated user). |

### createNote

| Parameter | Type | Description |
|-----------|------|-------------|
| `text` | string | **Required.** The note text (HTML supported) |

### Available Options (fetchConversations)

| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | string | Filter by status: `active`, `pending`, `closed`, `spam`, or `all` (default: `active`) |
| `folderId` | number | Filter by folder ID |
| `assignedTo` | number | Filter by user ID |
| `customerId` | number | Filter by customer ID |
| `number` | number | Filter by conversation number |
| `modifiedSince` | string | ISO8601 date to filter conversations modified after this date |
| `sortField` | string | Sort field: `createdAt`, `mailboxId`, `modifiedAt`, `number`, `score`, `status`, `subject` (default: `createdAt`) |
| `sortOrder` | string | Sort order: `asc` or `desc` (default: `desc`) |
| `tag` | string | Filter by tag name |
| `query` | string | Advanced search query in `fieldId:value` format |
| `embed` | string | Comma-separated list of resources to embed: `threads` |
| `page` | number | Page number for pagination (default: 1) |



### Security Best Practices
- Never hardcode credentials into your codebase.
- Use OpenClaw's `config.apply` system for securely managing sensitive details.
- Avoid sharing sensitive parts of your configuration output (`API_KEY` and `APP_SECRET`) with others.

## Contribution Guidelines
- Ensure compliance with Helpscout's API usage policies.
- Add documentation for any new features added.