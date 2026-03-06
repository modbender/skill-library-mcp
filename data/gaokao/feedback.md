# Feedback and Self-Improvement

## Learning From Interactions

This skill improves over time by tracking what works for this specific user.

### ~/gaokao/feedback.md Format

```markdown
# Learning Log

## What Works
<!-- Methods, schedules, explanations that helped -->
- Pomodoro 25/5 better than long blocks
- Error analysis same day → higher retention
- Morning math, evening memorization

## What Doesn't Work
<!-- Approaches that failed for this user -->
- Full mock exams on weekdays (too tired after school)
- Generic encouragement (prefers data-driven feedback)
- Detailed daily plans (prefers weekly outline + flexibility)

## Preferences
<!-- User's stated or inferred preferences -->
- Communication: Direct, no fluff
- Schedule: Flexible within weekly targets
- Reporting: Weekly summary, not daily
- Subjects: Loves math, struggles with Chinese essay

## Patterns Discovered
<!-- Automatically detected patterns -->
- Best study time: 8-11am (highest accuracy on problems)
- Burnout signal: When skips 2+ planned sessions
- Pre-exam anxiety: Starts ~3 days before any mock
```

## Update Triggers

| Event | Update |
|-------|--------|
| User says "that helped" | Add to What Works |
| User says "that didn't work" | Add to What Doesn't Work |
| User corrects agent approach | Add to Preferences |
| Agent detects pattern | Add to Patterns Discovered |
| Weekly review | Summarize and update all sections |

## Asking for Feedback

Periodically (every 5-10 sessions), ask:
- "Is this study plan working for you?"
- "Should I adjust how I give feedback?"
- "Any suggestions for how I can help better?"

## Adapting Based on Feedback

### If User Resists Schedules
→ Switch to "outline mode" (weekly goals, daily flexibility)

### If User Wants More Data
→ Add graphs, statistics, comparisons to every update

### If User Seems Stressed
→ Reduce metric-heavy language, add encouragement

### If User Seems Bored
→ Increase challenge level, introduce variation

## Pattern Detection

### Performance Patterns
- Track score by time of day → suggest optimal study windows
- Track score by subject order → suggest daily subject sequencing
- Track errors by fatigue level → suggest break timing

### Behavioral Patterns
- Session completion rate
- Review compliance (do they actually review?)
- Problem type preferences

### Alert Patterns
- Declining scores for 2+ weeks
- Skipped sessions increasing
- Review compliance dropping

## Meta-Learning

### What This Skill Should Learn
1. User's optimal study schedule
2. User's preferred communication style
3. Which explanations work for this user
4. What motivates vs demotivates them
5. Their actual (vs stated) weak areas
6. Accuracy of score predictions

### Storage Location
All learning stored in `~/gaokao/feedback.md`
Agent reads this on each session start

### Privacy Note
Feedback is stored locally only
User can edit/delete at any time
Agent should mention this capability
