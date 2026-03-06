# Form Patterns Reference

Advanced patterns and edge cases for the questions-form skill.

## Timeout Handling

If more than 10 minutes pass between sending the form and receiving a Submit callback, the form may be stale.

On the next user interaction:
- If it is a `form:` callback, process it normally (form is still active)
- If it is unrelated, ask: "You have an incomplete form from earlier. Would you like to continue or start over?"

## Form Cancellation

Always include a Cancel button alongside Submit:

```json
[
  [{ "text": "\u2713 Submit All Answers", "callback_data": "form:submit" }],
  [{ "text": "\u2717 Cancel", "callback_data": "form:cancel" }]
]
```

On `form:cancel`: discard `form_state`, inform the user, and return to normal conversation.

## Dependent Questions

When question B depends on question A's answer:

1. Send all non-dependent questions as the initial form
2. When A is answered and its value triggers B, send B as a new message with buttons
3. Add the new question to `form_state` and update the submit validation

Example:
- Q1: "Platform?" → `[Web] [Mobile]`
- If user picks "Mobile": send Q1a: "iOS or Android?" → `[iOS] [Android] [Both]`
- Submit now requires both Q1 and Q1a to be answered

## Large Option Sets (>6 options)

Split into rows of 2-3 buttons each. Always keep "Other" on its own final row.

Example with 7 options:

```json
"buttons": [
  [
    { "text": "React", "callback_data": "form:fw:react" },
    { "text": "Vue", "callback_data": "form:fw:vue" },
    { "text": "Angular", "callback_data": "form:fw:angular" }
  ],
  [
    { "text": "Svelte", "callback_data": "form:fw:svelte" },
    { "text": "Next.js", "callback_data": "form:fw:next" },
    { "text": "Nuxt", "callback_data": "form:fw:nuxt" }
  ],
  [
    { "text": "Remix", "callback_data": "form:fw:remix" }
  ],
  [
    { "text": "Other (type your answer)", "callback_data": "form:fw:other" }
  ]
]
```

## Multi-Select Questions

For questions where the user can select multiple options, use a toggle pattern:

- `callback_data` format: `form:<qid>:toggle:<value>`
- Agent maintains a Set for that question in `form_state`
- Each click adds or removes the value from the set
- Acknowledge each toggle:
  - Added: `"Added **React** to frameworks (selected: React, Vue)"`
  - Removed: `"Removed **React** from frameworks (selected: Vue)"`

Include a "Done selecting" button to finalize the multi-select question:

```json
[
  [
    { "text": "React", "callback_data": "form:fw:toggle:react" },
    { "text": "Vue", "callback_data": "form:fw:toggle:vue" }
  ],
  [
    { "text": "Angular", "callback_data": "form:fw:toggle:angular" },
    { "text": "Svelte", "callback_data": "form:fw:toggle:svelte" }
  ],
  [
    { "text": "\u2713 Done selecting", "callback_data": "form:fw:done" },
    { "text": "Other (type your answer)", "callback_data": "form:fw:other" }
  ]
]
```

## Free-Text Disambiguation

When `awaiting_freetext` is set and the user sends a message:

- If the message starts with `form:` (i.e., it's a button callback), process it as a button click. **Keep `awaiting_freetext` active** — the user will still need to provide their text later.
- If the message is plain text, treat it as the free-text answer for the pending question.

This prevents confusion when a user clicks another question's button while the agent expects free text input.

## Resuming Interrupted Forms

If the conversation is interrupted (e.g., agent restart, session reset):

- The form state is lost (it lives in conversation context, not persistent storage)
- If the user sends a `form:` callback that the agent has no context for, respond: "It looks like you're responding to a previous form that I no longer have context for. Let me re-send the questions."
- Re-send the entire form from scratch

## Partial Submission

If a user clicks Submit with only some questions answered:

- List the unanswered questions by name/number
- Do **not** re-send the form — the existing button messages still work
- The user can click the remaining buttons and tap Submit again

Example response:
`"You still need to answer: **2. Timeline** and **3. Budget**. Tap the buttons above, then Submit again."`

## Complete Example: 3-Question Form

### Questions:
1. Project type (Web App / Mobile / API / Other)
2. Timeline (This week / This month / No rush / Other)
3. Budget (< $1k / $1k-5k / $5k-10k / > $10k / Other)

### Messages sent (5 total):

**Message 1** (header):
```
"**I have a few questions before we proceed.**
Please answer each one by tapping a button, then tap Submit when done."
```

**Message 2** (Q1):
```
text: "**1. What type of project?**"
buttons: [[Web App, Mobile, API], [Other (type your answer)]]
```

**Message 3** (Q2):
```
text: "**2. What is your timeline?**"
buttons: [[This week, This month, No rush], [Other (type your answer)]]
```

**Message 4** (Q3):
```
text: "**3. Budget range?**"
buttons: [[< $1k, $1k-5k], [$5k-10k, > $10k], [Other (type your answer)]]
```

**Message 5** (submit):
```
text: "**When you've answered all questions above, tap Submit.**"
buttons: [[\u2713 Submit All Answers], [\u2717 Cancel]]
```

### Callback handling sequence:

1. User taps "Mobile" on Q1 → `callback_data: form:type:mobile`
   → Agent: `"Got it -- Project type: **Mobile**"`

2. User taps "Other" on Q2 → `callback_data: form:timeline:other`
   → Agent: `"Type your answer for: What is your timeline?"`
   → User types: `"End of March"`
   → Agent: `"Got it -- Timeline: **End of March**"`

3. User taps "$1k-5k" on Q3 → `callback_data: form:budget:1k_5k`
   → Agent: `"Got it -- Budget: **$1k-5k**"`

4. User taps Submit → `callback_data: form:submit`
   → All answered. Agent proceeds with:
   ```
   { type: "mobile", timeline: "End of March", budget: "1k_5k" }
   ```
