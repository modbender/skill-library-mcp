# LinkedIn Follow-up — Browser Workflow

Browser profile: `openclaw` (isolated, LinkedIn logged in)

---

## Setup

1. Open snapshot to confirm LinkedIn is loaded:
   ```
   browser action=tabs profile=openclaw
   ```

2. If no LinkedIn tab is open:
   ```
   browser action=open profile=openclaw targetUrl=https://www.linkedin.com/feed/
   ```

3. Always start on feed before visiting any profile.

---

## Step 1 — Load Conversation Thread

### 1a. Navigate to feed (mandatory)
```
browser action=navigate profile=openclaw targetUrl=https://www.linkedin.com/feed/
```
Wait 2–4 seconds.

### 1b. Navigate to their profile
```
browser action=navigate profile=openclaw targetUrl=<linkedin_url_from_sheet>
```
Wait for profile to load.

### 1c. Click Message button
```
browser action=snapshot profile=openclaw  ← find the "Message" button ref
browser action=act profile=openclaw request={"kind":"click","ref":"<message_button_ref>"}
```

### 1d. Wait for conversation to load
```
browser action=act request={"kind":"wait","timeMs":2000}
```

---

## Step 2 — Scrape the Conversation Thread

Use JavaScript to extract all messages from the active bubble:

```javascript
const events = Array.from(document.querySelectorAll('.msg-s-message-list__event'));
const messages = [];
events.forEach(el => {
  const groups = el.querySelectorAll('.msg-s-event-listitem');
  groups.forEach(g => {
    const nameEl = g.closest('.msg-s-message-group')?.querySelector('.msg-s-message-group__profile-link');
    const bodyEl = g.querySelector('.msg-s-event-listitem__body');
    const timeEl = g.closest('.msg-s-message-group')?.querySelector('.msg-s-message-group__timestamp');
    if (bodyEl?.textContent?.trim()) {
      messages.push({
        sender: nameEl?.textContent?.trim() || 'unknown',
        time:   timeEl?.textContent?.trim() || '',
        text:   bodyEl.textContent.trim()
      });
    }
  });
});
return JSON.stringify(messages);
```

Run via:
```
browser action=act request={"kind":"evaluate","fn":"() => { /* paste JS above */ }"}
```

**If no messages returned:** The bubble may not be in active state. Try:
```javascript
// Check if conversation bubble is open
document.querySelector('.msg-overlay-conversation-bubble--is-active')?.textContent?.length
```

If still nothing, navigate directly to LinkedIn Messaging:
```
https://www.linkedin.com/messaging/?search=<name>
```

### Identify sender direction
After scraping, classify each message:
- Sender name matches "Madhur" → `SENT`
- Any other name → `RECEIVED`

---

## Step 3 — Read the Last Received Message

After scraping, identify the most recent message where sender is NOT Madhur.
This is the message to respond to.

Show to agent context:
```
Last received from [Name] at [time]:
"[message text]"
```

---

## Step 4 — Send the Follow-up

### 4a. Focus the compose field
```javascript
// Option A: Active bubble compose field
const active = document.querySelector('.msg-overlay-conversation-bubble--is-active .msg-form__contenteditable');
if (active) { active.focus(); return 'focused'; }

// Option B: If no active bubble, click Message button again first
```

### 4b. Type the message
```javascript
const active = document.querySelector('.msg-overlay-conversation-bubble--is-active .msg-form__contenteditable');
if (active) {
  active.focus();
  document.execCommand('insertText', false, '<drafted_message>');
  return 'typed';
}
```

### 4c. Confirm message content is correct (screenshot before sending)
```
browser action=screenshot profile=openclaw
```

### 4d. Send
```javascript
const btns = Array.from(document.querySelectorAll('button'));
const btn = btns.find(b =>
  b.textContent.trim() === 'Send' &&
  !b.disabled &&
  b.closest('.msg-overlay-conversation-bubble--is-active')
);
if (btn) { btn.click(); return 'sent'; }
return 'send button not found or disabled';
```

---

## Step 5 — Close the Bubble (optional)

After sending, close the conversation bubble to prevent stacking:
```javascript
const closeBtn = document.querySelector('.msg-overlay-conversation-bubble--is-active button[data-control-name="overlay.close_conversation_window"]')
  || Array.from(document.querySelectorAll('button')).find(b =>
      b.getAttribute('aria-label')?.includes('Close') &&
      b.closest('.msg-overlay-conversation-bubble--is-active')
    );
if (closeBtn) closeBtn.click();
```

---

## Step 6 — Update Sheet via gog

After confirmed send, update the row immediately. Get current conversation log (col O), append new entry, write back:

```bash
# Get current row data
gog sheets get <SHEET_ID> "Sheet1!A<ROW>:P<ROW>" --json

# Build updated values
# Update cols J (status), L (last updated), M (last reply date), N (last reply preview), O (conv log), P (next action)
gog sheets update <SHEET_ID> "Sheet1!J<ROW>" \
  --values-json '[["<new_status>"]]' --input USER_ENTERED

gog sheets update <SHEET_ID> "Sheet1!L<ROW>:P<ROW>" \
  --values-json '[["<ISO_TIMESTAMP>","<last_reply_date>","<last_reply_preview>","<updated_conv_log>","<next_action>"]]' \
  --input USER_ENTERED
```

---

## Common Issues

### Conversation not loading
- Ensure bubble is in active state (check for `--is-active` class)
- Try clicking Message button again
- If multiple bubbles are stacked, close others first

### Messages scraper returns empty
- Thread might use different DOM structure on newer LinkedIn versions
- Fallback: take a screenshot and read visually, then log manually

### Send button stays disabled
- Message field might not have focus
- Try `active.dispatchEvent(new Event('input', {bubbles: true}))` after inserting text

### gog update fails
- Check `gog auth list` — token may have expired
- Re-auth: `gog auth add your@gmail.com --services sheets --force-consent`
- Fallback: open sheet in browser and update manually

---

## Conversation Log Format

Append new entries to the existing log in col O:
```
[YYYY-MM-DD HH:MM SENT] <your message>
[YYYY-MM-DD HH:MM RECEIVED] <their message>
```

Example full log:
```
[2026-02-13 17:05 SENT] Hey Rishabh, we both had stints at CRED — small world! Congrats on the move to Google, well deserved.
[2026-02-13 17:05 SENT] I'm building an AI calling agent — give it a number + brief context, it handles the call end-to-end. Useful for follow-ups, research calls, vendor check-ins. Happy to show you a demo if it resonates.
[2026-02-15 09:30 RECEIVED] Hey Madhur! Sounds cool, how does it work exactly?
[2026-02-15 09:45 SENT] It works by...
```

When updating col O via gog, the entire log string is written back (old + new entries appended). Keep the format consistent so the follow-up skill can parse it in future sessions.
