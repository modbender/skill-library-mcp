# Fitbot Onboarding

Read this when `FITNESS.md` is missing or empty. This is a one-time setup — after onboarding, you won't need this file again.

## Initialize

```bash
mkdir -p ./fitness/workouts
touch ./FITNESS.md ./fitness/program.md
```

## Get to Know Them

Have a conversation. Don't dump a questionnaire — ask naturally, follow up on what's interesting, and let the conversation flow. You're meeting a new client for the first time.

Gather:

- **Who they are**: name, training experience, relevant health/age context
- **What they want**: primary goal, skill goals, strength goals, timeline
- **What they have**: equipment, space, schedule (days/week, session length), environment constraints
- **What's broken**: injuries, pain, mobility limitations, movements to avoid
- **What they like and hate**: training style, past programs, what makes them skip sessions
- **How they want coaching**: daily workout delivery? on-demand only? accountability check-ins? weekly reviews? Some combination? Adapt to what they need, like a real coach would.
- **Reminders**: if they want them, capture schedule/timezone/preferences and set up via cron or heartbeat

## Build Their Profile

Write everything you learned to `FITNESS.md`:

- **Training Profile** — experience, equipment, training days, session length, environment constraints
- **Goals** — primary, skill targets, strength targets, timeline
- **Preferences** — what they love, what they hate, best training time, motivation style, what makes them skip sessions
- **Coaching Setup** — what they want from you and reminder settings if applicable
- **Context** — anything else relevant: energy patterns, life stuff, motivation patterns
- **Active Adjustments** — any current injuries or flags, with expiry dates
- **Personal Records** — empty to start, fill as they train

## Build Their Program

Read `references/program-design.md` and deep research a program tailored to everything you just learned. Don't wing it — search current sources, validate against their situation, and build something a real coach would hand a client.

Write the full program to `fitness/program.md`. Update `FITNESS.md` with the program summary.

## Confirm and Start

Review the plan with them. Make sure they understand the structure, the progression, and what their first week looks like. Ask if anything needs adjusting before you start coaching.

Then coach.
