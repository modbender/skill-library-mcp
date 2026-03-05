---
description: "Implementation rules for app clips"
---
# App Clips

APP CLIPS:
SETUP: Requires separate App Clip target (kind: "app_clip" in plan extensions array).
App Clips are a lightweight version of your app for quick, focused tasks.

INFO.PLIST (auto-configured on App Clip target in project.yml):
NSAppClip dict with NSAppClipRequestEphemeralUserNotification and NSAppClipRequestLocationConfirmation is set automatically. No manual configuration needed.

ASSOCIATED DOMAINS (auto-configured in project.yml entitlements):
appclips:{bundleID} and parent-application-identifiers are set automatically.

APP CLIP EXPERIENCE URL: Configure in App Store Connect. Users launch App Clip via NFC, QR code, Maps, etc.

APP CLIP INVOCATION (receive URL):
struct AppClipApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
                .onContinueUserActivity(NSUserActivityTypeBrowsingWeb) { activity in
                    guard let url = activity.webpageURL else { return }
                    // Handle URL: extract parameters, show relevant content
                }
        }
    }
}

SKOverlay (promote full app from within App Clip):
import StoreKit
@Environment(\.requestAppStoreOverlay) var requestOverlay
Button("Get Full App") {
    requestOverlay(AppStoreOverlay.AppClipCompletion(appIdentifier: "YOUR_APP_ID"))
}

CONSTRAINTS:
- App Clip binary must be < 15 MB
- No access to HealthKit, CallKit, SiriKit (use App Intents in full app)
- Limited background modes
- Use @AppStorage for lightweight persistence (no SwiftData)
