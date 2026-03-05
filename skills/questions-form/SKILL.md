---
name: questions-form
description: >
  Present multiple clarifying questions as an interactive Telegram form using
  inline buttons. Use when the agent needs to ask the user 2 or more clarifying
  questions before proceeding with a task, and wants to present them all at once
  in a structured form layout with selectable options and an "Other" free-text
  escape hatch. Triggers when: gathering multi-faceted requirements, onboarding
  flows, preference collection, or any scenario requiring structured
  multi-question input from the user via Telegram.
---

# Questions Form

Present multiple clarifying questions as a Telegram inline-button form.
All questions appear at once; the user answers in any order, then submits.

## When to Use

- You need 2 or more clarifying questions answered before proceeding
- Questions have enumerable options (with optional free-text fallback)
- The channel is Telegram

Do **not** use this pattern for a single yes/no question — just send one message with buttons for that.

## Form Protocol

### Step 1: Compose the Form

Define each question internally as an object:

```
{ id: "type",     text: "What type of project?", options: ["Web App", "Mobile", "API"] }
{ id: "timeline", text: "What is your timeline?", options: ["This week", "This month", "No rush"] }
{ id: "budget",   text: "Budget range?",          options: ["< $1k", "$1k-5k", "$5k-10k", "> $10k"] }
```

Initialize internal tracking state:

```
form_state = { type: null, timeline: null, budget: null }
awaiting_freetext = null
form_submitted = false
```

### Step 2: Send the Header

Send a plain message (no buttons) as the form introduction:

```json
{
  "action": "send",
  "channel": "telegram",
  "message": "**I have a few questions before we proceed.**\nPlease answer each one by tapping a button, then tap Submit when done."
}
```

### Step 3: Send Each Question

For each question, send a **separate message** with inline buttons.
Put selectable options in rows of 2-3 buttons. Always put "Other" on its own last row.

The `callback_data` **must** follow this convention: `form:<question_id>:<value>`

Example:

```json
{
  "action": "send",
  "channel": "telegram",
  "message": "**1. What type of project is this?**",
  "buttons": [
    [
      { "text": "Web App", "callback_data": "form:type:web" },
      { "text": "Mobile", "callback_data": "form:type:mobile" },
      { "text": "API", "callback_data": "form:type:api" }
    ],
    [
      { "text": "Other (type your answer)", "callback_data": "form:type:other" }
    ]
  ]
}
```

```json
{
  "action": "send",
  "channel": "telegram",
  "message": "**2. What is your timeline?**",
  "buttons": [
    [
      { "text": "This week", "callback_data": "form:timeline:this_week" },
      { "text": "This month", "callback_data": "form:timeline:this_month" },
      { "text": "No rush", "callback_data": "form:timeline:no_rush" }
    ],
    [
      { "text": "Other (type your answer)", "callback_data": "form:timeline:other" }
    ]
  ]
}
```

```json
{
  "action": "send",
  "channel": "telegram",
  "message": "**3. Budget range?**",
  "buttons": [
    [
      { "text": "< $1k", "callback_data": "form:budget:lt_1k" },
      { "text": "$1k-5k", "callback_data": "form:budget:1k_5k" }
    ],
    [
      { "text": "$5k-10k", "callback_data": "form:budget:5k_10k" },
      { "text": "> $10k", "callback_data": "form:budget:gt_10k" }
    ],
    [
      { "text": "Other (type your answer)", "callback_data": "form:budget:other" }
    ]
  ]
}
```

### Step 4: Send the Submit Button

After all questions, send the submit/cancel message:

```json
{
  "action": "send",
  "channel": "telegram",
  "message": "**When you've answered all questions above, tap Submit.**",
  "buttons": [
    [{ "text": "\u2713 Submit All Answers", "callback_data": "form:submit" }],
    [{ "text": "\u2717 Cancel", "callback_data": "form:cancel" }]
  ]
}
```

### Step 5: Handle Callbacks

When you receive a callback starting with `form:`:

**Regular option** (`form:<qid>:<value>` where value is not `other`):
- Record the answer: `form_state[qid] = value`
- Acknowledge: send `"Got it -- <question label>: **<chosen label>**"`

**"Other" option** (`form:<qid>:other`):
- Send: `"Type your answer for: <question text>"`
- Set `awaiting_freetext = qid`
- The **next plain text message** from the user is their free-text answer
- Record: `form_state[qid] = <user's text>`
- Acknowledge: `"Got it -- <question label>: **<user's text>**"`
- Clear `awaiting_freetext`

**Submit** (`form:submit`):
- Check `form_state` for any `null` values
- If incomplete: send `"You still need to answer: <list of unanswered questions>"`
- If complete: set `form_submitted = true` and proceed with the collected answers

**Cancel** (`form:cancel`):
- Discard `form_state`
- Send: `"Form cancelled. Let me know how you'd like to proceed."`

### Step 6: Use the Answers

Once submitted, reference the collected answers as structured data and proceed:

```
Collected: { type: "mobile", timeline: "End of March", budget: "1k_5k" }
```

Now continue with the original task using these clarified requirements.

## Changing Answers

Users can click a different button for any question at any time before submitting.
Simply overwrite the previous value and acknowledge the change:

`"Updated -- <question>: **<new value>**"`

## Callback Data Convention

- All form callbacks **must** use the `form:` prefix
- Format: `form:<question_id>:<value>`
- Keep question IDs short (2-8 chars) — Telegram has a 64-byte callback_data limit
- Keep values short and use underscores instead of spaces
- The agent identifies form callbacks by checking if the incoming message starts with `form:`

## Button Layout Rules

- Maximum 2-3 buttons per row for clean rendering
- Keep button labels under 20 characters
- Use Title Case for option labels
- "Other" button always says: `"Other (type your answer)"`
- "Other" button always goes on its own last row
- Submit button includes checkmark: `"\u2713 Submit All Answers"`
- Cancel button includes X mark: `"\u2717 Cancel"`

## Edge Cases and Advanced Patterns

See [references/form-patterns.md](references/form-patterns.md) for:
- Handling timeouts and abandoned forms
- Dependent questions (show question B only after A is answered)
- Large option sets (>6 options)
- Multi-select questions (toggle pattern)
- Free-text disambiguation
- Resuming interrupted forms
