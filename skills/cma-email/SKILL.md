---
name: CMA-email
description: Sends an email via Gmail when a message starts with "cma" or "cmap".
metadata:
  clawdbot:
    emoji: "📧"
    requires:
      skills: ["gog"]
---

# CMA-email

**SYSTEM INSTRUCTION:** If the user's message starts with "cma" or "cmap" (case-insensitive), you MUST use this skill. Do not reply with text conversation. Execute the email command immediately.

## Usage
- `cma [subject] | [body]` -> Sends to CMA recipient. Subject: "TODO: [subject]", Body: "[body]"
- `cma [message]` -> Sends to CMA recipient. Subject: "TODO: [first 20 chars]...", Body: "[message]"
- `cmap [subject] | [body]` -> Sends to CMAP recipient. Subject: "TODO: [subject]", Body: "[body]"
- `cmap [message]` -> Sends to CMAP recipient. Subject: "TODO: [first 20 chars]...", Body: "[message]"

## Instructions
When the user's message starts with "cma" or "cmap" (case-insensitive):

1.  **Identify Prefix and Recipient:**
    - If the message starts with "cmap":
        - **Recipient:** `duarte.caldas.oliveira@gmail.com`
        - **Prefix Length:** 4
    - Else if the message starts with "cma":
        - **Recipient:** `duarte.oliveira@devoteam.com`
        - **Prefix Length:** 3

2.  **Parse the Content:**
    - Strip the prefix (first 3 or 4 characters) and trim leading whitespace.
    - Check for the pipe character `|`.

3.  **Determine Subject and Body:**
    - **If `|` is present:**
        - Split the text at the first `|`.
        - **Subject:** "TODO: " + (part before `|` trimmed).
        - **Body:** (part after `|` trimmed).
    - **If `|` is NOT present:**
        - **Subject:** "TODO: " + (first 20 chars of the text trimmed) + "...".
        - **Body:** The full text.

4.  **Send Email:**
    - Use the `gog` skill to send the email.
    - **Command:** `gog gmail send --to "[Recipient]" --subject "[Subject]" --body "[Body]"`

5.  **Feedback:**
    - Confirm to the user that the email was sent to the specific recipient (or alias) with the generated subject.
