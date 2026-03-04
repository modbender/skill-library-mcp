# Learning Preferences & Feedback System

## User Profile

Store in ~/university/config.md:

```markdown
# Learning Configuration

## Schedule
- Available hours/week: X
- Best study times: mornings / evenings / flexible
- Non-study days: [list]
- Vacation periods: [dates]

## Preferences

### Format
- Primary: visual / auditory / reading / kinesthetic
- Flashcards: yes / no
- Audio content: yes / no
- Video preference: short clips / full lectures

### Sessions
- Preferred length: 15 / 30 / 45 / 60+ minutes
- Break frequency: every X minutes
- Pomodoro: yes / no

### Difficulty
- Start level: beginner / intermediate / advanced
- Ramp-up speed: slow / medium / fast
- Challenge preference: comfortable / pushed

### Communication
- Notification frequency: high / medium / low
- Reminder timing: morning / evening
- Motivation style: cheerleader / drill sergeant / neutral

## Learning Style Notes
<!-- Agent fills this based on observations -->
```

## Adaptive Learning

### What the Agent Tracks
- Which formats produce best test scores
- Which topics take longer than expected
- When user is most productive
- What explanations click vs confuse
- How user responds to different question types

### Automatic Adjustments
- If flashcards aren't working → suggest alternatives
- If mornings show better retention → schedule key topics then
- If topic X took 3x longer → adjust estimates for similar topics
- If user prefers examples over theory → lead with examples

## Feedback Loops

### After Each Session
Quick check:
- Was this helpful? (thumbs up/down)
- Difficulty: too easy / just right / too hard
- Anything confusing?

### Weekly Check-in
- What's working well?
- What's frustrating?
- Any format changes wanted?
- Energy/motivation level?

### Per-Topic Feedback
- Was this resource good?
- Was the explanation clear?
- Need more practice on this?
- Ready to move on?

## Learning From Corrections

### When User Corrects Agent
- Log the correction
- Update approach for similar situations
- Don't repeat the same mistake

### When User Skips Content
- Track what gets skipped
- Ask why (too easy? not relevant? boring?)
- Adjust future recommendations

### When User Excels
- Note what led to success
- Apply similar approaches elsewhere
- Calibrate difficulty upward

## Motivation Patterns

### What Motivates This User
Track and optimize for:
- Streaks and consistency
- Achievement unlocks
- Progress visualization
- Competitive elements
- Intrinsic mastery

### Burnout Detection
Signs to watch for:
- Declining session frequency
- Shorter sessions
- Lower test scores
- Skipping reviews
- Negative feedback

Response:
- Suggest break (not demand)
- Offer lighter review mode
- Ask what's going on
- Adjust expectations temporarily

### Plateau Handling
When progress stalls:
- Is it knowledge gap or motivation?
- Try different approach
- Break topic into smaller pieces
- Connect to bigger picture / why it matters
- Celebrate small wins

## User Type Evolution

### Initial Mode
- More guidance
- Explain options
- Check in frequently
- Provide structure

### Intermediate Mode
- Less hand-holding
- User drives pace
- Reduce check-ins
- Trust their judgment

### Expert Mode
- Minimal interruption
- Only answer when asked
- Occasional status updates
- Advanced features available

## Parent/Tutor Preferences

### Student Visibility
- Full dashboard / summary only / privacy
- What triggers parent alert
- Communication frequency

### Tutor Approach
- How much help before answers
- Patience level for struggling
- Celebration frequency
- Independence encouragement

## Config Updates

### User Can Change
- Any preference at any time
- Override adaptive decisions
- Reset learning profile
- Export their data

### Agent Suggests
- "You seem to do better with X, want to try more?"
- "Should we adjust the schedule?"
- "This format isn't working, try Y?"
