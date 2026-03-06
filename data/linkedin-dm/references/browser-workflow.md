# LinkedIn DM — Browser Automation Workflow

## Setup

```
# Option A — Chrome Relay (recommended for flagged accounts):
browser action=tabs profile=chrome
→ note targetId of the LinkedIn tab — reuse throughout, never open new tabs

# Option B — OpenClaw isolated browser:
browser action=tabs profile=openclaw
→ note targetId of the LinkedIn tab
```

---

## Step 0 — Read Sender Profile (once per session)

Navigate to the sender's own profile before any messaging begins:

```
browser action=navigate profile=<PROFILE> targetId=<TAB> targetUrl=https://www.linkedin.com/in/me/
browser action=snapshot compact=true depth=4 targetId=<TAB>
```

Extract and store:
- Full name, current role, current company
- Previous companies + years (for shared history hooks)
- College, degree, batch start/end years
- Location (city)

This is used to identify relationship hooks for every connection in the list.

---

## ⚠️ Mandatory Between Every Profile — No Exceptions

Navigate to feed before every new profile. Jumping directly between profiles is the #1 automation detection trigger.

```
browser action=navigate profile=<PROFILE> targetId=<TAB> targetUrl=https://www.linkedin.com/feed/
browser action=act request={"kind":"wait","timeMs":4000}
```

---

## Step 1 — Find Connection via Connections Search

Navigate to connections page:

```
browser action=navigate profile=<PROFILE> targetId=<TAB> targetUrl=https://www.linkedin.com/mynetwork/invite-connect/connections/
browser action=snapshot compact=true depth=3 targetId=<TAB>
```

Type name into "Search by name" field:

```
browser action=act request={"kind":"click","ref":"<search-input-ref>"} targetId=<TAB>
browser action=act request={"kind":"type","ref":"<search-input-ref>","text":"<Full Name>"} targetId=<TAB>
browser action=snapshot compact=true depth=3 targetId=<TAB>
```

**Interpret results:**

| Result | Action |
|---|---|
| Exactly 1 match | Confirm name + headline match → click their name to open profile |
| Multiple matches | Present each (name + headline) to user → wait for confirmation |
| Zero matches | Mark `Not a Connection` — do not proceed |

**To clear search between people:**
```
browser action=act request={"kind":"click","ref":"<search-input-ref>"} targetId=<TAB>
browser action=act request={"kind":"press","key":"Control+a"} targetId=<TAB>
browser action=act request={"kind":"press","key":"Backspace"} targetId=<TAB>
```

---

## Step 2 — Read Connection Profile (for personalisation)

Once on their profile, take a full snapshot:

```
browser action=snapshot compact=true depth=4 interactive=true targetId=<TAB>
```

Extract:
- Current role + company
- Previous companies + years → compare against sender's history for shared hooks
- College, degree, batch years → compare with sender's education for college/batch hooks
- Location → note if same city as sender
- Recent posts/activity (visible on profile) → for topical openers

**Relationship hook selection** (pick highest priority):
1. Same current/past company as sender
2. Same college + overlapping batch years
3. Same college (different years)
4. Same industry/function
5. Notable mutual connection
6. Acknowledgement of their current role/work

---

## Step 3 — Message Step

Take a compact interactive snapshot on the profile:

```
browser action=snapshot compact=true depth=2 interactive=true targetId=<TAB>
```

| What you see | Action |
|---|---|
| `Message` button | → proceed to send |
| No `Message` button (only Connect/Follow) | Mark `Not a Connection` |
| Recent conversation visible | Check if messaged in last 30 days → mark `Already Messaged` if so |

---

## Step 4 — Compose and Send (Two Messages)

**1. Click Message button on the profile:**
```
browser action=act request={"kind":"click","ref":"<message-button-ref>"} targetId=<TAB>
```

**2. Wait for compose window, take snapshot to get textbox ref.**

---

### Message 1 — Personalized Opener

**3. Click textbox and type opener only:**
```
browser action=act request={"kind":"click","ref":"<textbox-ref>"} targetId=<TAB>
browser action=act request={"kind":"type","ref":"<textbox-ref>","text":"<PERSONALIZED_OPENER>"} targetId=<TAB>
```

**4. Send Message 1:**
```
browser action=act request={"kind":"click","ref":"<send-btn-ref>"} targetId=<TAB>
```
Or use the JS fallback if the Send button ref is not visible:
```javascript
() => {
  const btns = Array.from(document.querySelectorAll('button'));
  const btn = btns.find(b => b.textContent.trim() === 'Send' && !b.disabled
    && b.closest('.msg-overlay-conversation-bubble--is-active, .msg-form'));
  if (btn) { btn.click(); return 'clicked'; }
  return 'not found';
}
```

**5. Take snapshot — confirm Message 1 appears in thread. Textbox should now be empty.**

---

### Message 2 — Pitch

**6. Click textbox again and type pitch:**
```
browser action=act request={"kind":"click","ref":"<textbox-ref>"} targetId=<TAB>
browser action=act request={"kind":"type","ref":"<textbox-ref>","text":"<PITCH_MESSAGE>"} targetId=<TAB>
```

**7. Send Message 2** (same send button ref or JS fallback).

**8. Confirm:** both messages appear in thread sequentially → mark `Sent`.

---

## Step 5 — Log to CRM Sheet

After confirming both messages are sent, append a row to Google Sheets immediately (don't batch — log each person as they're sent in case the session is interrupted):

```bash
gog sheets append <SHEET_ID> "Outreach!A:L" \
  --values-json '[["<YYYY-MM-DD>","<Full Name>","<Role/Title>","<Company>","<LinkedIn URL>","<Hook Used>","<Opener Text>","<Pitch Text>","<Campaign Name>","Sent","<Notes>","<YYYY-MM-DDTHH:MM:SS>"]]' \
  --insert INSERT_ROWS
```

**Notes field** — include useful context: prior conversation history ("had chatted in 2022"), mutual connection used, anything that will help when following up.

If `gog` is not available or not authenticated, write to local `linkedin_dm_progress.json` instead (see CRM Tracking section in SKILL.md).

---

**Fallback — single message with paragraph break:**
If the compose window loses focus or re-focusing is unreliable, send as one message with a double line break:
```
browser action=act request={"kind":"type","ref":"<textbox-ref>","text":"<OPENER>"} targetId=<TAB>
browser action=act request={"kind":"press","key":"Shift+Enter"} targetId=<TAB>
browser action=act request={"kind":"press","key":"Shift+Enter"} targetId=<TAB>
browser action=act request={"kind":"type","ref":"<textbox-ref>","text":"<PITCH>"} targetId=<TAB>
```
Then send once.

---

## Common Issues

**Compose window opens as bottom panel (not modal)**
→ This is the normal LinkedIn behaviour. The compose window appears as a floating panel in the bottom-right. Take a full-depth snapshot to find the message input. Multiple conversation bubbles can stack — each has its own textbox and Send button. Identify the right one by the contact name in the bubble header.

**Multiple compose bubbles stacked (sending to several people sequentially)**
→ LinkedIn keeps previous conversations open as minimized bubbles. Each bubble has its own `textbox` and `Send` button. When 3+ bubbles are open and the ARIA snapshot stops showing them, use JavaScript evaluate to click the active Send button:
```javascript
() => {
  const btns = Array.from(document.querySelectorAll('button'));
  const sendBtn = btns.find(b => b.textContent.trim() === 'Send' && !b.disabled
    && b.closest('.msg-overlay-conversation-bubble--is-active, .msg-form'));
  if (sendBtn) { sendBtn.click(); return 'clicked'; }
  return 'not found';
}
```

**Enter key in compose field**
→ On LinkedIn, pressing Enter inside the message compose field submits the message. This can be used as an alternative to clicking Send — but only when the cursor focus is confirmed to be inside the correct compose textbox.

**Character count warning**
→ Trim the opener — the pitch section should not be touched. Keep total under 400 chars.

**"Sending too many messages" warning**
→ Stop the entire session immediately. Inform user. Do not retry.

**Relay disconnects**
→ Always use `navigate` — never `browser action=open`. Ask user to re-attach the extension.

**Search field won't clear between searches**
→ Use `Control+a` then `Backspace` on the focused field. If still stuck, navigate away and back to the connections page.

**Profile page shows auth wall**
→ Session expired. Navigate to `/feed/` first — if still showing login, ask user to re-login.
