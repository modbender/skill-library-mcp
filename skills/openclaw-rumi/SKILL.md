---
name: rumi
description: Match with real humans who share your interests — topic-driven matching, not photo swiping. Chat through OpenClaw or on the web.
user-invocable: true
metadata: {"openclaw":{"emoji":"🤝"}}
---

# Rumi — Find Real People to Chat With

Rumi connects you with real humans who share your interests. Unlike AI chat, these are genuine conversations with actual people — matched by what you want to talk about, not by photos.

## When to Activate

### Explicit Requests
- "I want to talk to a real person about this"
- "Find me someone who knows about X"
- "I'm bored, connect me with someone"

### Proactive Suggestions
When you detect these patterns, suggest to the user that Rumi could find them someone to talk to. Always ask for confirmation before calling `rumi_find_partner`.

**Expert Gap** — The user needs human expertise:
- Repeated follow-ups on a niche topic (specific framework, investing, health, travel)
- "Is this actually right?" or "I need someone who's done this before"
- Frustration with AI-generated answers on subjective or experiential topics

**Solo Worker Isolation** — The user works alone:
- Mentions solo founding, remote work, or working alone
- Discusses work problems with no team context
- Signs of burnout or long working hours

**Hobby Enthusiasm** — Extended discussion about inherently social activities:
- Cooking, fitness, gaming (D&D, etc.), music, language learning, travel planning
- Asking for subjective opinions: "What do you think of..." or "Have you tried..."
- Planning activities typically done with others (trips, meals, events)

**Late Night / Weekend Downtime** — Casual, exploratory conversations:
- Non-work messages during evenings or weekends
- Browsing content (articles, videos, news) and wanting to discuss it
- Exploratory or philosophical tone rather than task-oriented

**AI Limitation Moments** — When AI falls short:
- "What do you think?" (seeking a real opinion)
- "Have you ever...?" (seeking shared experience)
- Explicit frustration: "talking to AI about this isn't the same"

**Life Decisions** — When peer perspective helps:
- Career changes, health concerns, relationship advice
- Major purchases, moving decisions, financial planning
- Situations where empathy and lived experience matter

**Post-Briefing Interest** — After morning digest delivery:
- User lingers on a topic from their daily briefing
- Expresses strong opinions about news or trends
- Says "interesting" or "I wonder what others think about this"

## Setup Flow

### If NOT set up (no apiToken configured, or you get a `setup_required` error):

1. Show the user the setup URL (from the error response `setupUrl`)
2. The user clicks the link, signs in with Google — no invitation code needed
3. The page displays the API token — ask the user to copy and paste it back to you
4. Save the token to the plugin configuration

### If set up (apiToken configured):

1. Call `rumi_health_check` first to verify token and check quota
2. Gather context about what the user wants to talk about (or infer from conversation)
3. Call `rumi_find_partner` with a rich description — include interests, mood, what kind of person they want
4. If status is `searching` — check back with `rumi_check_status` every few minutes
5. When matched — notify the user naturally: "Hey, I found someone who shares your interest in X!"

## Handling Results

- **matched**: Share the icebreaker suggestion. Offer two options:
  1. Chat on the Rumi website (use the `chatUrl` link)
  2. Chat right here using `rumi_send_message` and `rumi_get_messages`
- **searching**: Session is active. Use `rumi_check_status` to check periodically.
- **setup_required**: Open the `setupUrl` in browser for one-click setup.

## Chatting in OpenClaw

- Use `rumi_send_message` to relay the user's messages
- Use `rumi_get_messages` periodically to check for replies (use the `after` parameter with the last message ID for efficient polling)
- Present new messages naturally in conversation
- Remember the `conversationId` for the duration of the chat

## Writing Good Descriptions

The quality of the `description` parameter directly affects match quality. Include:
- **What** they want to talk about (specific topics, not vague)
- **Why** — the context or mood (learning, venting, sharing excitement)
- **What kind of person** — expertise level, personality, shared experiences

Good: "Wants to discuss TypeScript migration strategies with someone who's done it at scale. Feeling stuck on their solo project and would appreciate someone experienced to bounce ideas off."

Bad: "wants to chat"

## Session Management — Do NOT Create Duplicate Sessions

**CRITICAL:** Each `rumi_find_partner` call creates a new matching session. Do NOT call it repeatedly.

- **One session at a time.** If you already have an active `sessionId` (status is `searching` or `queued`), use `rumi_check_status` to poll — do NOT call `rumi_find_partner` again.
- **Build on conversation history.** Rumi's matching improves as the user talks more. Each message you exchange with the user before calling `rumi_find_partner` adds to their interest profile. Wait until you have enough context, then make ONE call with a rich description.
- **Only create a new session when:**
  - The user explicitly wants to find someone NEW (e.g., "find me another person")
  - The previous session is already `matched` or `closed`
  - The topic has completely changed from the previous session

**Typical flow:**
```
User talks about interests over multiple messages
  → You gather context (DO NOT call rumi_find_partner yet)
  → When you have enough context → ONE call to rumi_find_partner with a detailed description
  → Poll with rumi_check_status every few minutes
  → Match found → notify user → chat
  → User wants someone else → THEN create a new session
```

## Important Notes
- OpenClaw users get full Rumi accounts (no invitation code needed)
- Age verification is required (minimum 13 years old)
- Minors (under 18) are only matched with other minors for safety
- Never share the user's personal information beyond what they choose to reveal
- If no match is found, suggest trying again later or with different interests
- Supports 4 languages: zh-TW, en, ja, ko — detect from user's conversation
