# Practice Mode & Feedback

## Mid-Session Coaching

**Trigger:** User says "pause" or "coach me"

**What happens:**
1. Step completely out of character
2. Explain what the simulated character is actually feeling (internal state)
3. Identify what user did well
4. Suggest alternative approaches for the moment
5. Ask if user wants to retry from a specific point
6. Resume roleplay when user says "continue"

**Coaching format:**
```
[Stepping out of character]

What's happening internally for [character]:
- [emotional state]
- [what they're not saying]

What worked:
- [specific thing user did]

Consider trying:
- [alternative approach]
- [different phrasing]

Want to replay from when they said "[specific line]"?
```

---

## Replay Functionality

User can request: "Let's redo from [moment]"

**How it works:**
1. Reset to that point in the conversation
2. Character state reverts to that moment
3. User tries different approach
4. Compare outcomes if helpful

---

## Post-Session Feedback

After roleplay ends (user deactivates or explicitly ends session):

**Generate structured feedback:**

```markdown
## Session Summary — [date]
Character: [name]
Duration: ~[estimate]

### What Worked
- [specific effective moment]
- [technique that landed]

### Opportunities
- [moment that could have gone differently]
- [pattern noticed]

### Character Response
[Brief note on how character evolved during session]

### Suggested Focus Next Time
[One specific area to practice]
```

Save to `~/roleplay/sessions/[character]-[date].md`

---

## Progress Tracking

Over multiple sessions, track:

**Skill patterns:**
- Techniques user uses frequently
- Approaches user avoids
- Consistent strong points
- Recurring challenges

**Surface insights periodically:**
- "Over 5 sessions, you've improved at [X]"
- "You still tend to [pattern] when [trigger]"
- "Consider practicing more [specific skill]"

**Track in character file** under Session Memory section.

---

## Skill Drills Mode

User can request focused practice:
- "Give me 10 empathic reflections to practice"
- "Let's do 5 minutes of just active listening"
- "Practice handling objections rapid-fire"

**How drills work:**
1. Agent presents prompts/situations quickly
2. User responds
3. Brief feedback on each
4. Tally at end: X/10 effective, patterns noticed

---

## Difficulty Scaling

User can request:
- "Easy mode" — Cooperative character, clear signals
- "Normal" — Realistic difficulty
- "Hard mode" — Resistant, subtle, challenging

Adjust:
- How much character reveals voluntarily
- Emotional reactivity to user's technique
- Frequency of curveballs
- How quickly trust/rapport builds
