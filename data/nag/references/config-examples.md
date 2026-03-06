# Nag Config Examples

## Daily habit with tone-based messages

```json
{
  "reminders": [
    {
      "id": "morning-vitamins",
      "label": "morning vitamins",
      "cronFirst": "0 8 * * *",
      "nagAfter": "09:00",
      "confirmPatterns": ["taken", "done", "took them", "did it"],
      "tone": "friendly but persistent, get dramatic after 3 nags",
      "messages": {
        "first": "Morning vitamins!"
      }
    }
  ]
}
```

## Workout reminder with hardcoded messages

```json
{
  "id": "daily-workout",
  "label": "workout",
  "cronFirst": "0 10 * * *",
  "nagAfter": "14:00",
  "confirmPatterns": ["worked out", "lifted", "trained", "exercised", "ran"],
  "tone": "coach energy",
  "messages": {
    "first": "Workout today?",
    "nag": "Have you worked out yet today?",
    "escalate": "The iron isn't going to lift itself"
  }
}
```

## Weekly reminder (specific days)

```json
{
  "id": "grocery-list",
  "label": "weekly grocery list",
  "cronFirst": "0 9 * * 0",
  "nagAfter": "11:00",
  "days": ["sunday"],
  "confirmPatterns": ["ordered", "list done", "groceries ordered"],
  "tone": "matter-of-fact"
}
```
