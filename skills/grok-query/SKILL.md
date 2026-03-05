---
name: grok-query
description: "Query Grok AI (grok.com) for real-time information via browser automation. Requires: OpenClaw browser enabled, user pre-logged-in to grok.com, and a Grok account (free tier works)."
license: MIT
metadata:
  openclaw:
    emoji: "🧠"
---

# Grok - External Knowledge Query

Use Grok AI to fetch real-time information, latest news, and external knowledge that may not be in your training data.

## Prerequisites

Before using this skill, ensure the following:

1. **OpenClaw browser enabled** — verify with:
   ```bash
   openclaw browser status
   ```
2. **Logged in to grok.com** — the user must have already logged in to grok.com in the OpenClaw browser. This skill cannot handle login flows automatically.
3. **Grok account** — a free-tier Grok account is sufficient for basic queries; SuperGrok is not required.

## When to Use This Skill

Activate when the user:
- Needs real-time information (news, events, product status)
- Wants reasoning and synthesis beyond what `web_search` can provide
- Needs multi-turn conversational research
- Asks to verify uncertain knowledge against up-to-date sources

## Workflow

### Step 1: Open Grok (or Reuse Existing Tab)

```bash
# Check if grok.com is already open
openclaw browser tabs
```

If a grok.com tab already exists, directly switch to it:

```bash
openclaw browser focus <existing-grok-tab-id>
```

If not, open a new tab:

```bash
openclaw browser open https://grok.com
```

Both return a target id — keep this for all subsequent calls.

### Step 2: Snapshot & Check Page State

```bash
openclaw browser snapshot
```

After taking a snapshot, check for **two things** before proceeding:

1. **Popups / banners blocking the page** (see Step 2a)
2. **The input box** (see Step 2b)

### Step 2a: Handle Popups and Banners

Common obstructions:
- "Upgrade to SuperGrok" banner
- Login prompts
- Cookie consent dialogs

If you see any popup or banner in the snapshot:

```bash
# Find the close/dismiss button ref from snapshot, then click it
openclaw browser click <close-button-ref>

# Verify it's gone
openclaw browser snapshot
```

Or try pressing Escape to dismiss overlays:

```bash
openclaw browser press Escape
```

### Step 2b: Locate the Input Box

The Grok input box is a `contenteditable` div (ProseMirror editor) at the **bottom** of the page. In snapshot output, look for a `paragraph` element with placeholder text such as "How can I help you today?" (or its localized equivalent).

If you can't find the input box:

```bash
# Scroll the input box into view (if you know its ref)
openclaw browser scrollintoview <ref>

# Or re-snapshot to check
openclaw browser snapshot
```

### Step 3: Type Question

```bash
openclaw browser type <input-ref> "What is the latest news about AI?"
```

### Step 4: Click Send Button

**Important**: Grok uses Enter for newline, NOT for sending. You must click the send button (the circular ⬆ icon button to the right of the input box).

```bash
# After typing, snapshot to find the send button ref
openclaw browser snapshot

# Click the send button — look for the "Submit" button near the input box
openclaw browser click <send-button-ref>
```

> **Do NOT use** `press Enter` or `--submit` — they only insert a newline in Grok's input box.

### Step 5: Wait for Response and Capture

While Grok is generating, a **"Stop response"** button replaces the voice button next to the input box. When it disappears, the response is complete. A **"Regenerate"** button appearing confirms completion.

**Important**: Do NOT use `wait --text-gone` or `wait --fn` with long timeouts — the browser tool call has a timeout limit and will fail before the wait finishes. Use short waits + snapshot polling instead.

**Poll until response is complete:**

```bash
# 1. Wait 10 seconds
openclaw browser wait --time 10000

# 2. Snapshot and check for completion
openclaw browser snapshot
# Look for "Regenerate" button → response is done
# If "Stop response" button is still visible → still generating, repeat from step 1
```

Repeat the wait-then-snapshot cycle until you see completion indicators or **5 minutes** have elapsed:
- **Done**: "Regenerate", "Read aloud", "Copy" buttons appear
- **Still generating**: "Stop response" button is present, or content is still growing
- **Timeout**: If 5 minutes pass with no completion, stop polling and inform the user that the Grok response timed out

**Note on localized UI**: Button text depends on Grok UI language:
- English: "Stop response" / "Regenerate"
- Chinese: "停止模型响应" / "Regenerate"

### Handling Image Responses

If the snapshot contains `img` elements in the response area (e.g. from Grok's Imagine feature), extract the image URL:

```bash
openclaw browser evaluate --fn "(el) => el.src" --ref <img-ref>
```

## Multi-turn Conversation

Stay in the same tab to maintain conversation context. Grok understands follow-up questions that reference earlier messages.

```bash
# 1. Make sure you're on the correct tab
openclaw browser focus <target-id>

# 2. Snapshot to find the input box (placeholder changes to "Ask anything" in follow-ups)
openclaw browser snapshot

# 3. Type your follow-up question
openclaw browser type <input-ref> "What about tomorrow?"

# 4. Snapshot to find the "Submit" button and click it
openclaw browser snapshot
openclaw browser click <send-button-ref>

# 5. Wait and poll for completion (repeat until "Regenerate" appears)
openclaw browser wait --time 10000
openclaw browser snapshot
```

> **Note**: The input box and submit button refs change between turns — always snapshot to get fresh refs before typing or clicking.

## Error Handling

| Problem | Solution |
|---|---|
| Popup / banner blocking | `snapshot`, find close button ref, `click` it; or `press Escape` |
| Input box not found | `press Escape`, re-`snapshot`; or `scrollintoview` |
| Login required | Ask user to log in to grok.com manually, then `openclaw browser navigate https://grok.com` |
| Page not loading | `openclaw browser navigate https://grok.com` or re-open |
| Response incomplete | Increase wait time, take multiple snapshots to confirm |
| Clicked wrong element | Re-`snapshot` to get fresh refs |
| "Unknown ref" error | The ref is stale — page has changed since last snapshot. Run a new `snapshot` and use refs from that result. Never reuse refs from a previous snapshot. |
| Free tier quota exceeded | Inform user their Grok quota is used up; wait for reset or upgrade to SuperGrok |
| CAPTCHA / human verification | Cannot be automated; ask user to complete it manually, then retry |
| "Something went wrong" mid-response | Re-send the question or reload the page and try again |
| "Continue generating" button | Click the button to resume generation, then continue polling |
| Session expired / redirected to login | Ask user to re-login in the browser, then reload grok.com |
| Multiple grok.com tabs open | Use `tabs` to list all, pick the correct one by URL or title |
| DeepSearch UI differs | Completion indicator may differ; poll snapshot and look for source count or result summary instead of "Regenerate" |
| Accidentally opened model selector | `press Escape` to close the dropdown, then re-`snapshot` |
| Tab closed or browser killed mid-response | Start over: `openclaw browser open https://grok.com` and re-send the question |

## Common Use Cases

- **Quick fact check**: "What is the capital of France?"
- **Latest news**: "What are the top tech news today?"
- **Real-time info**: "What's the current status of [event]?"
- **Complex research**: Break into multiple queries in the same session

## Tips

- **Session persistence**: Stay in the same tab for multi-turn conversations
- **Must click send**: Grok's Enter key is newline, always click the ⬆ send button to submit
- **Long responses**: May need to scroll down and take additional snapshots
- **Pre-login**: User should be logged in to grok.com beforehand for best results
- **Screenshot**: Use `openclaw browser screenshot` if you need visual confirmation

## Alternative: Direct Web Search

For simpler queries, consider using `web_search` tool first (faster, no browser needed).

Use Grok when you need:
- Reasoning and synthesis
- Multi-step analysis
- Conversational follow-up
- Complex explanations
