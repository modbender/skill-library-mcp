# Reminders Priority Levels

Apple Reminders uses integer priority values matching the iCalendar standard.

## Priority mapping

| Level | Value | Display |
|---|---|---|
| None | `0` | No priority indicator |
| High | `1` | `!!!` — red exclamation marks |
| Medium | `5` | `!!` — orange exclamation marks |
| Low | `9` | `!` — yellow exclamation mark |

## Natural language mapping

| User says | Priority value |
|---|---|
| "high priority", "urgent", "important", "ASAP" | `1` |
| "medium priority", "normal priority" | `5` |
| "low priority", "not urgent", "whenever" | `9` |
| (nothing specified) | `0` (none) |

## Notes

- Values 1-4 are all treated as "high" by Reminders.app
- Values 5-8 are all treated as "medium"
- Value 9 is treated as "low"
- The skill uses the canonical values (1, 5, 9) for clarity
