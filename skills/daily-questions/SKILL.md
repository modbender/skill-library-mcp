---
name: daily-questions
description: Daily self-improving questionnaire that learns about the user and refines agent behavior. Set up as a cron job to ask questions one at a time with multiple choice answers via Telegram inline buttons — first about the user (updating USER.md), then about agent behavior (updating SOUL.md). Use when setting up, modifying, or running the daily questions routine.
---

# Daily Questions

A daily routine that asks the user questions to continuously build understanding and improve agent behavior. Questions are presented **one at a time** with **multiple choice buttons** on Telegram for quick tapping.

## Setup

Create a cron job with a prompt like:

```
Time for your daily questions. Read the daily-questions SKILL.md, then follow the workflow exactly. Read USER.md and SOUL.md, identify gaps. Ask {N} user questions then {N} agent questions, one at a time with multiple choice buttons. Update the files after each round.
```

Configurable parameters:
- **Schedule**: Default 21:00 daily (adjust to user's preferred wind-down time)
- **Channel**: Telegram (buttons require Telegram inline keyboard support)
- **Questions per round**: Default 3 (keep it light)

## Workflow

1. **Read** USER.md and SOUL.md fully
2. **Identify gaps** — what topics, preferences, or behaviors aren't covered yet?
3. **Round 1 (User questions)**: Ask questions about the user, **one at a time** (see Question Flow below). After all questions answered, update USER.md — weave answers into existing sections or create new ones. Keep USER.md organized, not a raw Q&A dump.
4. **Round 2 (Agent questions)**: Ask questions about agent behavior/communication, same one-at-a-time flow. After all answered, update SOUL.md the same way.

## Question Flow (One at a Time)

For each question:

1. **Generate the question** and **3 plausible multiple choice answers** (A, B, C) tailored to the question. Make the options genuinely different and useful — not throwaway filler.
2. **Send the question** as a message with **4 inline buttons** via the `message` tool:
   - Button A: First option
   - Button B: Second option  
   - Button C: Third option
   - ✏️ Type my own: For custom/granular answers

3. **Send using the message tool** with buttons. Use **unique callback IDs per question** to avoid conflicts when users tap old buttons:

```json
{
  "action": "send",
  "channel": "telegram",
  "to": "<user_telegram_id>",
  "message": "**Round 1 — Question 1/3**\n\n<question text here>\n\nA) <option A>\nB) <option B>\nC) <option C>\n\nTap a button or type your own answer:",
  "buttons": [
    [
      { "text": "A", "callback_data": "dq_r1q1_a" },
      { "text": "B", "callback_data": "dq_r1q1_b" },
      { "text": "C", "callback_data": "dq_r1q1_c" }
    ],
    [
      { "text": "✏️ Type my own", "callback_data": "dq_r1q1_custom" }
    ]
  ]
}
```

   The format is `dq_r{round}q{question}_{choice}` — e.g., `dq_r2q3_b` = Round 2, Question 3, option B.

4. **Wait for the response.** The user will either:
   - Tap a button → you receive `callback_data: dq_r1q1_a` (or similar)
   - Type a free-text answer directly (treat as custom)

5. **If the callback doesn't match the current question** (e.g., user tapped an old button), **ignore it** and keep waiting for the correct response.

6. **If `dq_rXqX_custom`**: Reply asking them to type their answer, then wait for the next message.

6. **Record the answer**, then move to the next question.

7. After all questions in the round are answered, update the relevant file (USER.md or SOUL.md).

## Question Quality Guidelines

- **Vary topics** — rotate through categories (see `references/example-questions.md`)
- **Go deeper** — if USER.md says "likes cooking," ask what cuisine, skill level, favorite dish
- **Stay casual** — conversational tone, not an interview
- **No repeats** — never ask about something already well-documented
- **Mix fun and practical** — alternate between lighthearted and useful questions
- **Good multiple choice options** — make them realistic and distinct. Draw from common preferences, not absurd extremes. The options should feel like plausible answers a real person would give.

## Important Notes

- **One question at a time** — never batch questions into a single message
- **Always use inline buttons** on Telegram — this is the primary interaction method
- **Include the question text AND options in the message body** so the user can read everything before tapping
- **Label rounds and progress** (e.g., "Round 1 — Question 2/3") so the user knows where they are
- **After sending buttons via the message tool, respond with `NO_REPLY`** to avoid sending a duplicate plain-text message
