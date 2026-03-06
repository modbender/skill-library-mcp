# Siri Shortcuts

## Naming for Voice Activation

**Rules:**
- 2-3 words ideal
- No punctuation or special characters
- Phonetically distinct (avoid rhymes with other shortcuts)
- Easy to remember and pronounce
- Test by saying it aloud before saving

**Good Names:**
- "Morning Routine", "Work Mode", "Quick Note"
- "Start Workout", "Call Mom", "Night Mode"

**Bad Names:**
- "My Super Awesome Morning Routine v2" (too long)
- "Do the thing" (too vague, easy to mis-trigger)
- "Test 1" (meaningless)

---

## Triggering Shortcuts

**By Voice:**
- "Hey Siri, [exact shortcut name]"
- Works on iPhone, iPad, Mac, HomePod, Apple Watch

**Alternative Methods:**
- Spotlight search (type shortcut name)
- Shortcuts app directly
- Home Screen widget
- Back Tap (Settings > Accessibility > Touch > Back Tap)
- Lock Screen widget (iOS 16+)

---

## User Input in Shortcuts

**Ask for Input:**
- Add "Ask for Input" action
- Siri will speak the prompt and wait for response
- Supports text, number, URL, date, time

**Dictation:**
- "Dictate Text" action captures voice as text
- Useful for notes, messages, quick captures

**Choose from Menu:**
- Present options for user to select
- Works via voice with numbered options

---

## Variables and Parameters

**App Intents (iOS 16+):**
- Pass parameters directly via voice
- "Hey Siri, log 8 hours of sleep" (if shortcut accepts number)
- Requires developer implementation of App Intents

**Classic Shortcuts:**
- Can't pass voice parameters directly
- Use "Ask for Input" as workaround
- Store variables between runs with Data Jar or files

---

## Error Handling

**Use If/Otherwise blocks:**
```
If [Input] has any value
  → Process input
Otherwise
  → Show notification "No input provided"
```

**iOS 18 Change:**
- Blank text fields now return empty string, not "nothing"
- Update conditions: check "is empty" instead of "has no value"

**Test Edge Cases:**
- What if user says nothing?
- What if Siri misunderstands?
- What if dependent app isn't installed?

---

## Output and Feedback

**Show Result:**
- Displays text/result on screen
- Siri reads it aloud

**Speak Text:**
- Explicitly speak custom message
- Useful for hands-free confirmation

**Show Notification:**
- Silent banner notification
- Doesn't interrupt flow

**Best Practice:**
- Confirm completion: "Done" or "Added [item]"
- Report failures: "Couldn't connect to [service]"

---

## Running on Other Devices

**HomePod:**
- Shortcuts run on HomePod if they don't require display
- Actions requiring screen fail silently
- Test on HomePod before relying on it

**Apple Watch:**
- Subset of actions available
- Complications can trigger shortcuts
- Keep watch shortcuts simple

**Mac:**
- Full Shortcuts app on macOS Monterey+
- Can trigger via Siri, menu bar, keyboard shortcut

---

## Automation Triggers

| Trigger | Example |
|---------|---------|
| Time of Day | 7 AM weekdays |
| Location | Arriving at work |
| CarPlay | Connecting to car |
| App Opens | When opening Camera |
| Email/Message | From specific sender |
| Workout | Starting/ending workout |
| NFC Tag | Tapping tag with phone |
| Alarm | After dismissing alarm |

**Note:** Some triggers require confirmation, some run automatically.
Settings > Shortcuts > Automation > [your automation] > Ask Before Running

---

## Debugging Tips

1. **Run manually first** - Test shortcut by tapping before trying voice
2. **Check action order** - Actions execute top to bottom
3. **Use Quick Look** - Add "Quick Look" action to inspect variables mid-flow
4. **Simplify** - If complex shortcut fails, break into smaller parts
5. **Check permissions** - Some actions need explicit permissions per shortcut

---

## Common Patterns

**Morning Routine:**
1. Get weather forecast
2. Read calendar events
3. Start podcast/music
4. Set device modes (Do Not Disturb off)

**Quick Capture:**
1. Dictate text
2. Add to Notes/Reminders
3. Confirm completion

**Smart Home Scene:**
1. Set multiple HomeKit scenes
2. Open specific app
3. Start music
