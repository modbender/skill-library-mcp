---
description: "Implementation rules for widgets"
---
# Widgets

WIDGETS (WidgetKit):
FRAMEWORK: import WidgetKit

SETUP:
- Requires separate widget extension target (kind: "widget" in plan extensions array)
- Use AppGroup for data sharing between app and widget (auto-configured in project.yml)
- Widget code goes in Targets/{WidgetName}/ directory

TIMELINE ENTRY (data for a single widget render):
struct MyEntry: TimelineEntry {
    let date: Date
    let title: String
    let value: Double
}

TIMELINE PROVIDER (supplies entries to the system):
struct MyProvider: TimelineProvider {
    func placeholder(in context: Context) -> MyEntry {
        MyEntry(date: .now, title: "Placeholder", value: 0)
    }
    func getSnapshot(in context: Context, completion: @escaping (MyEntry) -> Void) {
        completion(MyEntry(date: .now, title: "Snapshot", value: 42))
    }
    func getTimeline(in context: Context, completion: @escaping (Timeline<MyEntry>) -> Void) {
        let entry = MyEntry(date: .now, title: "Current", value: 42)
        let timeline = Timeline(entries: [entry], policy: .after(.now.addingTimeInterval(3600)))
        completion(timeline)
    }
}

WIDGET VIEW:
struct MyWidgetView: View {
    var entry: MyProvider.Entry
    @Environment(\.widgetFamily) var family
    var body: some View {
        switch family {
        case .systemSmall:
            VStack { Text(entry.title).font(.headline); Text("\(Int(entry.value))").font(.largeTitle) }
        case .systemMedium:
            HStack { VStack(alignment: .leading) { Text(entry.title); Text("\(Int(entry.value))").font(.title) }; Spacer() }
        default:
            Text(entry.title)
        }
    }
}

WIDGET DEFINITION:
struct MyWidget: Widget {
    let kind: String = "MyWidget"
    var body: some WidgetConfiguration {
        StaticConfiguration(kind: kind, provider: MyProvider()) { entry in
            MyWidgetView(entry: entry)
                .containerBackground(.fill.tertiary, for: .widget)  // REQUIRED iOS 17+
        }
        .configurationDisplayName("My Widget")
        .description("Shows current status")
        .supportedFamilies([.systemSmall, .systemMedium])
    }
}

WIDGET BUNDLE (when multiple widgets exist):
@main
struct MyWidgetBundle: WidgetBundle {
    var body: some Widget {
        MyWidget()
        AnotherWidget()
    }
}

MANDATORY FILES (every widget extension MUST have ALL of these):
1. {Name}Bundle.swift — @main WidgetBundle entry point. Without this, the extension has no entry point → linker error "undefined symbol: _main" → CodeSign failure.
2. Provider.swift — TimelineProvider implementation.
3. WidgetView.swift — The widget's SwiftUI view.
4. (Optional) Intent.swift — AppIntent for interactive widgets (tap-to-complete, etc.).

CRITICAL RULES:
- .containerBackground(.fill.tertiary, for: .widget) is REQUIRED on the widget view in iOS 17+. Without it, the widget renders with no background.
- The @main entry point is MANDATORY. Use @main on WidgetBundle (multiple widgets) or Widget (single widget). An extension target with NO @main will fail to link.
- Shared data types between app and widget go in the Shared/ directory at the project root (both targets compile it). NEVER define shared types only in the main app's Models/ — the widget extension cannot see them.
- Widget views must be self-contained — they cannot use @StateObject, @ObservedObject, or network calls. All data comes through the TimelineEntry.
- Use .supportedFamilies() to declare which sizes the widget supports.
- AppIntent static properties MUST use "static let" (not "static var") for Swift 6 concurrency safety. Using "static var" causes "not concurrency-safe because it is nonisolated global shared mutable state" error.
