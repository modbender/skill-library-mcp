# SiriKit & App Intents Development

## Framework Evolution

**SiriKit (iOS 10+):**
- Intent Definition Files (.intentdefinition)
- Limited to predefined domains
- Requires Intents extension

**App Intents (iOS 16+):**
- Swift-only, code-first approach
- Custom actions with parameters
- Automatic Shortcuts/Spotlight integration
- No extension required

**Migration Path:**
- New apps: Use App Intents directly
- Existing apps: Can wrap old intents with App Intents for consistency

---

## App Intents Basics

```swift
import AppIntents

struct LogSleepIntent: AppIntent {
    static var title: LocalizedStringResource = "Log Sleep"
    static var description = IntentDescription("Records hours of sleep")
    
    @Parameter(title: "Hours")
    var hours: Double
    
    func perform() async throws -> some IntentResult & ProvidesDialog {
        // Save sleep data
        return .result(dialog: "Logged \(hours) hours of sleep")
    }
}
```

**Key Points:**
- Return type must be `some IntentResult & ...` (never primitives)
- `@Parameter` for voice-capturable values
- `perform()` is async, can call APIs
- Registration is automatic (no manual setup)

---

## Supported Domains (Classic SiriKit)

| Domain | Example Intents |
|--------|-----------------|
| Messages | Send, Search messages |
| VoIP Calling | Start call, Answer call |
| Payments | Send payment, Request payment |
| Workouts | Start, End, Pause workout |
| Lists & Notes | Create note, Add to list |
| Visual Codes | Show QR code |
| Photos | Search photos |
| Ride Booking | Request ride, Get status |
| Car Commands | Lock, Unlock, Get status |
| Media | Play media, Add to library |

---

## NSUserActivity Donations

For Spotlight and Siri Suggestions (non-intent based):

```swift
let activity = NSUserActivity(activityType: "com.app.viewRecipe")
activity.title = "Chicken Curry Recipe"
activity.isEligibleForSearch = true
activity.isEligibleForPrediction = true
activity.suggestedInvocationPhrase = "Show curry recipe"
activity.persistentIdentifier = "recipe-123"
activity.becomeCurrent()
```

**Donation Flow:**
1. User performs action in app
2. Create NSUserActivity with relevant metadata
3. Call `becomeCurrent()` to donate
4. iOS learns patterns, suggests in Spotlight/Siri

**Deleting Donations:**
```swift
NSUserActivity.deleteSavedUserActivities(
    withPersistentIdentifiers: ["recipe-123"]
)
```

---

## App Shortcuts (Automatic)

```swift
struct MyAppShortcuts: AppShortcutsProvider {
    static var appShortcuts: [AppShortcut] {
        AppShortcut(
            intent: LogSleepIntent(),
            phrases: [
                "Log sleep in \(.applicationName)",
                "Record \(\.$hours) hours of sleep in \(.applicationName)"
            ],
            shortTitle: "Log Sleep",
            systemImageName: "bed.double"
        )
    }
}
```

**Benefits:**
- Available immediately on install
- Appears in Shortcuts app automatically
- No user setup required

---

## Testing & Debugging

**Simulator:**
- Siri available in simulator (iOS 14+)
- Test intent handling with "Test in Siri" button in Xcode

**Device Testing:**
- Real voice recognition only on device
- Test with actual voice commands
- Check Console.app for intent logs

**Common Issues:**
- Intent not appearing: Check Info.plist IntentsSupported
- Parameters not captured: Verify @Parameter types match expected
- Shortcut not in app: Ensure AppShortcutsProvider is registered

---

## Certification Requirements

**Required Behaviors:**
- Handle gracefully when permissions denied
- Don't request capabilities app doesn't use
- Provide meaningful responses (not just "Done")
- Handle edge cases (empty input, network failure)

**Common Rejections:**
- Requesting SiriKit permissions without clear use case
- Silent failures (no user feedback)
- Blocking UI during intent processing

---

## Extension Architecture

**For Classic SiriKit:**
```
Main App
└── Intents Extension (handles background)
└── IntentsUI Extension (custom UI, optional)
```

**For App Intents:**
```
Main App (all code lives here)
└── AppIntent structs auto-registered
```

**Sharing Data:**
- App Groups for UserDefaults/files
- Core Data with shared container
- Keychain for sensitive data

---

## Voice Recognition Tips

**Slot Values:**
- Define synonyms: "7", "seven", "VII" → 7
- Handle common mishearings
- Use `@Parameter(default:)` for optional values

**Phrasing:**
- Register multiple phrases for same intent
- Include app name: "in \(.applicationName)"
- Test pronunciation of custom terms

---

## Accessibility Considerations

**Type to Siri:**
- Works with all intents automatically
- No special handling needed

**VoiceOver:**
- Siri responses read automatically
- Custom UI should support VoiceOver

**Switch Control:**
- Siri provides alternative input method
- Ensure intents work without touch
