---
description: "Implementation rules for live activities"
---
# Live Activities

LIVE ACTIVITIES (ActivityKit + Dynamic Island):
FRAMEWORK: import ActivityKit

SETUP:
- Requires separate extension target (kind: "live_activity" in plan extensions array)
- NSSupportsLiveActivities: YES is auto-configured on the main app target in project.yml
- AppGroup entitlements are auto-configured for data sharing between app and extension

ATTRIBUTES (define in Shared/ directory so both app and extension compile it):
struct DeliveryAttributes: ActivityAttributes {
    public struct ContentState: Codable, Hashable {
        var status: String       // Mutable: changes during the activity
        var progress: Double
    }
    var orderID: String          // Static: set at start, cannot change
}

STARTING AN ACTIVITY (in app):
let attributes = DeliveryAttributes(orderID: "123")
let initialState = DeliveryAttributes.ContentState(status: "Preparing", progress: 0.0)
let content = ActivityContent(state: initialState, staleDate: nil)
let activity = try Activity.request(attributes: attributes, content: content)

UPDATING AN ACTIVITY:
let updatedState = DeliveryAttributes.ContentState(status: "On the way", progress: 0.6)
let updatedContent = ActivityContent(state: updatedState, staleDate: nil)
await activity.update(updatedContent)

ENDING AN ACTIVITY:
await activity.end(nil, dismissalPolicy: .immediate)

LOCK SCREEN / DYNAMIC ISLAND UI (in extension):
struct DeliveryLiveActivityView: View {
    let context: ActivityViewContext<DeliveryAttributes>
    var body: some View {
        HStack { Text(context.state.status); ProgressView(value: context.state.progress) }
    }
}

struct DeliveryWidget: Widget {
    var body: some WidgetConfiguration {
        ActivityConfiguration(for: DeliveryAttributes.self) { context in
            DeliveryLiveActivityView(context: context)                  // Lock Screen
        } dynamicIsland: { context in
            DynamicIsland {
                DynamicIslandExpandedRegion(.leading) { Text(context.state.status) }
                DynamicIslandExpandedRegion(.trailing) { ProgressView(value: context.state.progress) }
            } compactLeading: {
                Image(systemName: "bicycle")
            } compactTrailing: {
                Text("\(Int(context.state.progress * 100))%")
            } minimal: {
                ProgressView(value: context.state.progress)
            }
        }
    }
}

MANDATORY FILES (every live activity extension MUST have ALL of these):
1. {Name}Bundle.swift — @main WidgetBundle entry point. Without this, the extension has no entry point → linker error "undefined symbol: _main" → CodeSign failure.
2. LiveActivityWidget.swift — Widget struct with ActivityConfiguration(for: Attributes.self) for Lock Screen and Dynamic Island UI.
3. (Optional) Intents.swift — AppIntents for interactive buttons (complete, skip, etc.).

SHARED TYPES (CRITICAL):
- ActivityAttributes struct MUST be defined in Shared/ directory (NOT in main app's Models/). Both the main app and the live activity extension compile Shared/, so the type is visible to both. Defining it only in the main app causes "Cannot find type in scope" in the extension.

SWIFT 6 CONCURRENCY:
- AppIntent static properties MUST use "static let" (not "static var"). Mutable global state violates Swift 6 concurrency rules.
- LiveActivityService (if @MainActor) → all ViewModels calling it must also be @MainActor.

PUSH-TO-START: Use APNs with activity-update payload to start activities remotely (advanced, requires server).
