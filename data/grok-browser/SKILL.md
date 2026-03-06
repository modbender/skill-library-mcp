---
name: grok-browser
description: Query Grok AI via browser automation. Use when you need to ask Grok questions, get AI responses, or use Grok's DeepSearch/Think features. Copies response text instead of using screenshots.
---

# Grok Browser Skill

Query Grok (grok.com) via Chrome browser automation and copy responses.

## Prerequisites

- Chrome with Browser Relay extension
- Use `profile=chrome` (never `profile=clawd`)

## Quick Start

```bash
# 1. Open Chrome with Grok
open -a "Google Chrome" "https://grok.com"
sleep 3

# 2. Attach browser relay
/Users/eason/clawd/scripts/attach-browser-relay.sh

# 3. Check tabs
browser action=tabs profile=chrome
```

## Input Method (IMPORTANT!)

Grok uses **contenteditable**, not a standard textbox. Use JavaScript evaluate:

```javascript
// Type query via evaluate
browser action=act profile=chrome targetId=<id> request={
  "kind": "evaluate",
  "fn": "(() => { const editor = document.querySelector('[contenteditable=\"true\"]'); if(editor) { editor.focus(); editor.innerText = 'YOUR_QUERY_HERE'; return 'typed'; } return 'not found'; })()"
}
```

Then submit with Enter:
```
browser action=act profile=chrome targetId=<id> request={"kind":"press","key":"Enter"}
```

## Complete Workflow

### 1. Open Grok & Attach Relay

```bash
open -a "Google Chrome" "https://grok.com"
sleep 3
/Users/eason/clawd/scripts/attach-browser-relay.sh
```

### 2. Get Tab ID

```
browser action=tabs profile=chrome
```

Look for Grok tab, note the `targetId`.

### 3. Input Query

```
browser action=act profile=chrome targetId=<id> request={
  "kind": "evaluate",
  "fn": "(() => { const e = document.querySelector('[contenteditable=\"true\"]'); if(e) { e.focus(); e.innerText = 'What is quantum computing?'; return 'ok'; } return 'fail'; })()"
}
```

### 4. Submit

```
browser action=act profile=chrome targetId=<id> request={"kind":"press","key":"Enter"}
```

### 5. Wait for Response

```bash
sleep 10-20  # Grok can take 10-30 seconds
```

### 6. Snapshot & Find Copy Button

```
browser action=snapshot profile=chrome targetId=<id>
```

Look for button with "Copy" in the response area (usually last message).

### 7. Click Copy

```
browser action=act profile=chrome targetId=<id> request={"kind":"click","ref":"<copy_button_ref>"}
```

### 8. Read Clipboard

```bash
pbpaste
```

## Response Detection

After submitting, response is complete when:
- Copy button appears below the response text
- Response time indicator shows (e.g., "952ms")
- Suggested follow-up buttons appear

## New Chat for New Topics

Always start fresh chats for unrelated queries to avoid context overflow:

```
browser action=navigate profile=chrome targetId=<id> targetUrl="https://grok.com"
```

Or use Cmd+J shortcut:
```
browser action=act profile=chrome targetId=<id> request={"kind":"press","key":"Meta+j"}
```

## DeepSearch

To enable DeepSearch, click the button before submitting:
```
# In snapshot, find DeepSearch button
browser action=act profile=chrome targetId=<id> request={"kind":"click","ref":"<deepsearch_ref>"}
# Then type and submit as normal
```

## Troubleshooting

### Tab Not Found
Re-run attach script:
```bash
/Users/eason/clawd/scripts/attach-browser-relay.sh
```

### Relay Not Working
Check status:
```
browser action=status profile=chrome
```
Should show `cdpReady: true`.

### Context Overflow
Navigate to fresh grok.com, don't continue old chats.

### Multiple Windows
Close extra Chrome windows. Keep only one for reliable relay.

### Copy Button Not Found
Response may still be streaming. Wait longer and snapshot again.

## Example Session

```
# Open and attach
exec: open -a "Google Chrome" "https://grok.com"
exec: sleep 3
exec: /Users/eason/clawd/scripts/attach-browser-relay.sh

# Get tab
browser action=tabs profile=chrome
# Returns targetId: ABC123...

# Type query
browser action=act profile=chrome targetId=ABC123 request={
  "kind":"evaluate",
  "fn":"(() => { const e = document.querySelector('[contenteditable=\"true\"]'); e.focus(); e.innerText = 'Explain quantum entanglement briefly'; return 'ok'; })()"
}

# Submit
browser action=act profile=chrome targetId=ABC123 request={"kind":"press","key":"Enter"}

# Wait
exec: sleep 15

# Snapshot to find Copy button
browser action=snapshot profile=chrome targetId=ABC123
# Find Copy button ref, e.g., e326

# Copy
browser action=act profile=chrome targetId=ABC123 request={"kind":"click","ref":"e326"}

# Read result
exec: pbpaste
```
