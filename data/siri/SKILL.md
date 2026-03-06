---
name: Siri
description: Control devices, run automations, and help users get more from Siri with HomeKit, Shortcuts, and voice command guidance.
---

## Activation & Setup

**Trigger methods:**
- Hold Side/Home button
- "Hey Siri" (always-listening)
- "Siri" alone (iOS 17+)

**Hey Siri not working?** Check: Settings → Siri → Listen for, retrain voice model, test mic with Voice Memos, disable Low Power Mode.

## Command Patterns

**Structure:** Action + Target + Details
- "Call Mom on speaker"
- "Set a timer for 12 minutes"
- "Remind me to buy milk when I get home"

**Discovery:** "What can I say?" or "What can you do with [App]?"

**Corrections:** Say "Change that to..." after Siri transcribes wrong.

## Smart Home (HomeKit)

**Device naming:** Short, distinct, no special characters. "Kitchen light" not "Philips Hue A19 Kitchen #2".

**Room-aware commands:**
- "Turn off the lights" (current room on HomePod)
- "Turn off the bedroom lights" (specific room)
- "Turn off downstairs" (zone)

**Scenes:** Name for voice: "Good morning", "Movie time", "I'm leaving". Trigger with "Hey Siri, [scene name]".

**Schedules:** "Turn on porch light at sunset", "Lock doors at 10 PM".

**Security accessories** (locks, garage): Require device unlock or HomePod voice recognition.

## Shortcuts Integration

**Naming for voice:**
- Short (2-3 words ideal)
- Unique (avoid similar sounds)
- No punctuation
- Test pronunciation

**Triggering:** Just say the shortcut name. Works on iPhone, HomePod, Apple Watch, CarPlay.

**User input:** Use "Ask for Input" action—Siri will speak the prompt and wait.

**Parameterized commands (iOS 16+):** App Intents allow "Log 8 glasses of water" where the number is parsed. Requires developer implementation.

**Feedback:** End shortcuts with "Show Result" for spoken response or "Show Notification" for silent confirmation.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Siri doesn't hear me | Check mic, remove case, disable Bluetooth audio |
| Wrong transcription | Speak slower, reduce background noise, check language setting |
| "I can't do that" | Feature not supported or app not Siri-enabled |
| HomeKit device not responding | Check Home app, verify device online, restart Home hub |
| Shortcut won't run by voice | Rename shorter, check Siri toggle in shortcut settings |

## Power Tips

- **CarPlay:** Siri is hands-free default—just start talking after beep
- **AirPods:** Squeeze stem or say "Siri" (if enabled)
- **Type to Siri:** Settings → Accessibility → Siri → Type to Siri
- **Announce notifications:** HomePod/AirPods can read incoming messages
- **Intercom:** "Hey Siri, intercom I'm home" broadcasts to all HomePods

---

## When to Load More

| Situation | Reference |
|-----------|-----------|
| Full command list by category | `commands.md` |
| HomeKit setup, scenes, zones, troubleshooting | `homekit.md` |
| Building Shortcuts, triggers, automation | `shortcuts.md` |
| SiriKit, App Intents, developer integration | `development.md` |
