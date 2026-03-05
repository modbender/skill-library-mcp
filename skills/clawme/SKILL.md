---
name: clawme
version: 1.0.0
description: Send instructions to user's real browser via ClawMe Chrome extension. Fill forms, tweet, email, click, extract — user sees and confirms each action in the side panel. Unlike headless browsers, runs in the user's actual Chrome with their login sessions.
tags: ["browser", "automation", "form-fill", "chrome-extension", "twitter", "email"]
metadata: {"openclaw":{"emoji":"🦞","primaryEnv":"CLAWME_CLIENT_TOKEN","requires":{"env":["CLAWME_CLIENT_TOKEN"]}}}
---

# ClawMe — Execute Actions in User's Real Browser

Send instructions to the user's Chrome browser via the ClawMe extension. The user sees each instruction in a side panel and clicks "Execute" to confirm. Unlike headless browsers, ClawMe runs in the user's real browser with their actual login sessions.

**Setup**: User installs ClawMe Chrome extension, configures Backend URL and Token.

## How to Send Instructions

Use the `clawme_send` tool if available. Otherwise, make an HTTP POST:

```
POST ${CLAWME_BASE_URL:-https://api.clawme.net}/v1/instructions
Headers: Content-Type: application/json, X-ClawMe-Token: ${CLAWME_CLIENT_TOKEN}
Body: {"target":"browser","instruction":{"type":"<type>","payload":{...}}}
```

## Instruction Types

### compose_tweet
When user says "tweet about...", "post on X..."
```json
{"type":"compose_tweet","payload":{"text":"tweet content"}}
```

### compose_email
When user says "write email to...", "send email..."
```json
{"type":"compose_email","payload":{"to":"email@example.com","subject":"Subject","body":"Body text","use_gmail":true}}
```

### fill_form
When user says "fill the form...", "enter my info..."
```json
{"type":"fill_form","payload":{"url":"https://example.com/form","fields":{"#name":"John","input[name=email]":"john@example.com","select[name=country]":"US"}}}
```
Supports: inputs, textareas, selects, checkboxes, radio, contenteditable (Xiaohongshu, Medium). Use CSS selectors as field keys. Omit `url` for current page.

### click
When user says "click the button...", "submit the form..."
```json
{"type":"click","payload":{"selector":"button[type=submit]","url":"https://example.com/form"}}
```

### extract
When user says "get the text from...", "scrape..."
```json
{"type":"extract","payload":{"selector":".results","url":"https://example.com/search"}}
```
Result (extracted text) is reported back to the agent.

### open_url
```json
{"type":"open_url","payload":{"url":"https://example.com","in_new_tab":true}}
```

### remind
```json
{"type":"remind","payload":{"title":"Meeting","body":"Team standup in 5 minutes"}}
```

## Multi-Step Workflows

Chain instructions with `meta.workflow_id` and `meta.step`:
```
POST /v1/instructions — {"target":"browser","instruction":{"type":"open_url","payload":{"url":"..."}}, "meta":{"workflow_id":"signup","step":1}}
POST /v1/instructions — {"target":"browser","instruction":{"type":"fill_form","payload":{"fields":{...}}}, "meta":{"workflow_id":"signup","step":2}}
POST /v1/instructions — {"target":"browser","instruction":{"type":"click","payload":{"selector":"button[type=submit]"}}, "meta":{"workflow_id":"signup","step":3}}
```
User sees a workflow card with progress bar and can execute all steps sequentially.

## Environment Variables

- `CLAWME_CLIENT_TOKEN` (required) — matches the token configured in the Chrome extension
- `CLAWME_BASE_URL` (optional) — default `https://api.clawme.net`, or `http://127.0.0.1:31871` for local
