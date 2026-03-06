# Modern SwiftUI API Replacements

Prefer modern APIs when the deployment target allows. This catalog covers legacy patterns and their replacements, plus new APIs by iOS version.

## Contents

### Legacy → Modern Migration Tables
- [Navigation](#navigation)
- [Appearance](#appearance)
- [State & Data](#state--data)
- [Events & Lifecycle](#events--lifecycle)
- [Lists & Collections](#lists--collections)
- [Tabs (iOS 18+)](#tabs-ios-18)
- [Layout & Sizing](#layout--sizing)
- [Sheets & Presentation](#sheets--presentation)

### New APIs by Version
- [iOS 17 New APIs](#ios-17-new-apis) - @Observable, ScrollView, Animation, Inspector, Sensory Feedback, Container Relative Frame, onChange initial, Shape Improvements
- [iOS 18 New APIs](#ios-18-new-apis) - @Entry, @Previewable, Tab API, Mesh Gradients, Zoom Transitions, SF Symbol Animations, Custom Container Views, Controls
- [iOS 26 New APIs](#ios-26-new-apis) - Liquid Glass, WebView, Rich Text, Glass Button, Toolbar Spacer, TabView Minimize, Navigation Subtitles, Label Icon Width, Scene Padding, @Animatable, 3D Charts, openURL In-App, Drag Container

### Guidelines
- [Migration Priority](#migration-priority)
- [Availability Patterns](#availability-patterns)

## Navigation

| Legacy | Modern | Notes |
|--------|--------|-------|
| `NavigationView` | `NavigationStack` | Value-based, type-safe navigation |
| `NavigationLink(destination:)` | `NavigationLink(value:)` + `navigationDestination(for:)` | Decouple link from destination |
| `navigationBarTitle(_:)` | `navigationTitle(_:)` | Unified API |
| `navigationBarItems(leading:trailing:)` | `toolbar { ToolbarItem(placement:) }` | Consistent placement |
| `navigationBarHidden(_:)` | `toolbar(.hidden, for: .navigationBar)` | iOS 16+ |
| `.isDetailLink(false)` | Not needed | NavigationStack handles automatically |

## Appearance

| Legacy | Modern | Notes |
|--------|--------|-------|
| `foregroundColor(_:)` | `foregroundStyle(_:)` | Supports gradients, materials |
| `accentColor(_:)` | `tint(_:)` | Per-view accent color |
| `cornerRadius(_:)` | `.clipShape(.rect(cornerRadius:))` | More flexible, selective corners |
| `background(Color.x)` | `background { }` or `.background(.x, in:)` | Shape-aware backgrounds |
| `overlay(Circle())` | `overlay { Circle() }` | ViewBuilder syntax |

## State & Data

| Legacy | Modern | Notes |
|--------|--------|-------|
| `@StateObject` | `@State` with `@Observable` | Simpler, no wrapper needed |
| `@ObservedObject` | Direct reference to `@Observable` | Automatic tracking |
| `@EnvironmentObject` | `@Environment(MyType.self)` | Type-safe environment |
| `@Published` | Not needed with `@Observable` | Automatic property tracking |
| `Image("name")` | `Image(.name)` | Type-safe asset references |

## Events & Lifecycle

| Legacy | Modern | Notes |
|--------|--------|-------|
| `onChange(of:) { value in }` | `onChange(of:) { old, new in }` or `onChange(of:) { }` | Two or zero params (iOS 17+) |
| `onAppear { Task { } }` | `.task { }` | Auto-cancellation on disappear |
| `onReceive(publisher)` | `.task` or `.onChange` | When lifecycle-safe |
| `onTapGesture { }` | `Button` | Unless need tap location/count |

## Lists & Collections

| Legacy | Modern | Notes |
|--------|--------|-------|
| Manual pull-to-refresh | `.refreshable { }` | Native refresh control |
| `EditButton()` standalone | `.toolbar { EditButton() }` | Toolbar placement |
| `id: \.self` for value types | Prefer `Identifiable` | Better performance |

## Tabs (iOS 18+)

| Legacy | Modern | Notes |
|--------|--------|-------|
| `TabView { }.tabItem { }` | `TabView { Tab("", systemImage:) { } }` | New Tab API |
| Manual sidebar | `TabViewStyle.sidebarAdaptable` | Adaptive sidebar on iPad |

## Layout & Sizing

| Legacy | Modern | Notes |
|--------|--------|-------|
| `UIScreen.main.bounds` | `GeometryReader` or layout APIs | Avoid hard-coded sizes |
| `GeometryReader` for sizing | `containerRelativeFrame()` | iOS 17+, cleaner |
| `frame(width:height:)` fixed | `frame(minWidth:maxWidth:)` | Flexible sizing |

## Sheets & Presentation

| Legacy | Modern | Notes |
|--------|--------|-------|
| `.sheet(isPresented:)` | `.sheet(item:)` | When driven by model |
| Custom sheet sizing | `presentationDetents([.medium, .large])` | Native detents |
| Dismiss via binding | `@Environment(\.dismiss)` | Cleaner dismiss action |

---

## iOS 17 New APIs

### @Observable Macro
Replaces `ObservableObject` with simpler syntax:
```swift
// iOS 17+
@Observable
class UserModel {
    var name = ""      // Automatically tracked
    var age = 0
}

struct ContentView: View {
    @State private var user = UserModel()  // Use @State, not @StateObject
    var body: some View {
        TextField("Name", text: $user.name)
    }
}
```

### Scroll View Enhancements
```swift
ScrollView {
    content
}
.scrollTargetBehavior(.paging)           // Paging behavior
.scrollPosition(id: $selectedID)          // Programmatic scroll
.scrollTransition { content, phase in     // Scroll-based transitions
    content.opacity(phase.isIdentity ? 1 : 0.5)
}
.defaultScrollAnchor(.bottom)             // Start at bottom
.scrollIndicatorsFlash(trigger: items)    // Flash indicators
```

### Animation Improvements
```swift
// New spring animations
withAnimation(.bouncy) { }
withAnimation(.snappy) { }

// Phase animator for multi-step animations
PhaseAnimator([0, 1, 2]) { phase in
    Circle()
        .scaleEffect(phase == 1 ? 1.5 : 1)
}

// Keyframe animations
KeyframeAnimator(initialValue: AnimationValues()) { value in
    Circle()
        .scaleEffect(value.scale)
        .offset(value.offset)
} keyframes: { _ in
    KeyframeTrack(\.scale) {
        SpringKeyframe(1.5, duration: 0.3)
        SpringKeyframe(1.0, duration: 0.3)
    }
}

// Animation completion
withAnimation(.default) {
    isExpanded.toggle()
} completion: {
    // Animation finished
}
```

### Inspector Modifier
```swift
NavigationStack {
    ContentView()
        .inspector(isPresented: $showInspector) {
            InspectorView()
        }
}
```

### Sensory Feedback
```swift
Button("Tap") { }
    .sensoryFeedback(.impact, trigger: tapCount)

// Conditional feedback
Button("Submit") { }
    .sensoryFeedback(.success, trigger: submitCount) { old, new in
        new > old  // Only when count increases
    }
```

### Container Relative Frame
```swift
Image("photo")
    .containerRelativeFrame(.horizontal) { size, axis in
        size * 0.8  // 80% of container width
    }
```

### onChange with Initial Value
```swift
.onChange(of: searchText, initial: true) { oldValue, newValue in
    // Fires immediately with initial value
}
```

### Shape Improvements
```swift
// Selective corner rounding
RoundedRectangle(cornerRadii: .init(topLeading: 20, bottomTrailing: 20))

// Combined fill and stroke
Circle()
    .stroke(.red, lineWidth: 2)
    .fill(.blue)
```

---

## iOS 18 New APIs

### @Entry Macro for Environment
```swift
// Simplified custom environment values
extension EnvironmentValues {
    @Entry var myCustomValue: String = "default"
}

// Usage
.environment(\.myCustomValue, "custom")
@Environment(\.myCustomValue) var value
```

### @Previewable Macro
```swift
#Preview {
    @Previewable @State var count = 0
    Button("Count: \(count)") { count += 1 }
}
```

### Tab API
```swift
TabView {
    Tab("Home", systemImage: "house") {
        HomeView()
    }
    Tab("Search", systemImage: "magnifyingglass", role: .search) {
        SearchView()
    }
}
.tabViewStyle(.sidebarAdaptable)  // Sidebar on iPad
```

### Mesh Gradients
```swift
MeshGradient(
    width: 3, height: 3,
    points: [
        [0, 0], [0.5, 0], [1, 0],
        [0, 0.5], [0.5, 0.5], [1, 0.5],
        [0, 1], [0.5, 1], [1, 1]
    ],
    colors: [
        .red, .orange, .yellow,
        .green, .blue, .purple,
        .pink, .cyan, .mint
    ]
)
```

### Zoom Navigation Transition
```swift
NavigationLink(value: item) {
    ItemRow(item: item)
}
.matchedTransitionSource(id: item.id, in: namespace)

// Destination
DetailView(item: item)
    .navigationTransition(.zoom(sourceID: item.id, in: namespace))
```

### SF Symbol Animations
```swift
Image(systemName: "checkmark.circle")
    .symbolEffect(.bounce, value: isComplete)
    .symbolEffect(.rotate, value: isLoading)
```

### Custom Container Views
```swift
struct CardStack<Content: View>: View {
    @ViewBuilder var content: Content

    var body: some View {
        ForEach(subviews: content) { subview in
            subview
                .padding()
                .background(.ultraThinMaterial)
        }
    }
}
```

### Controls for Lock Screen / Control Center
```swift
struct MyControl: ControlWidget {
    var body: some ControlWidgetConfiguration {
        StaticControlConfiguration(kind: "MyControl") {
            ControlWidgetButton(action: MyIntent()) {
                Label("Toggle", systemImage: "lightbulb")
            }
        }
    }
}
```

---

## iOS 26 New APIs

### Liquid Glass Design
Automatic with Xcode 26 build. Opt out if needed:
```swift
// Disable Liquid Glass for transition period
.preferredGlassEffect(.disabled)
```

### WebView (Native)
```swift
import WebKit

struct BrowserView: View {
    @State private var page = WebPage()

    var body: some View {
        WebView(page)
            .onAppear {
                page.load(URLRequest(url: URL(string: "https://apple.com")!))
            }
    }
}
```

### Rich Text Editing with AttributedString
```swift
struct RichTextEditor: View {
    @State private var text = AttributedString("Hello")

    var body: some View {
        TextEditor(text: $text)
            .toolbar {
                Button("Bold") {
                    text.font = .boldSystemFont(ofSize: 17)
                }
            }
    }
}
```

### Glass Button Style
```swift
Button("Action") { }
    .buttonStyle(.glass)
```

### Toolbar Spacer
```swift
.toolbar {
    ToolbarItem(placement: .primaryAction) {
        Button("Save") { }
    }
    ToolbarSpacer(.fixed)
    ToolbarItem(placement: .primaryAction) {
        Button("Share") { }
    }
}
```

### TabView Minimize on Scroll
```swift
TabView {
    Tab("Home", systemImage: "house") {
        ScrollView {
            // Content
        }
    }
}
.tabBarMinimizeBehavior(.automatic)
```

### Navigation Subtitles
```swift
.navigationTitle("Documents")
.navigationSubtitle("23 items")
```

### Label Icon Fixed Width
```swift
Label("Settings", systemImage: "gear")
    .labelIconFixedWidth()
```

### Scene Padding
```swift
VStack {
    content
}
.scenePadding()  // Automatic padding for scene context
```

### @Animatable Macro
```swift
@Animatable
struct PulsingCircle: View {
    var scale: Double

    var body: some View {
        Circle()
            .scaleEffect(scale)
    }
}
```

### 3D Charts
```swift
Chart3D {
    ForEach(data) { item in
        BarMark3D(
            x: .value("X", item.x),
            y: .value("Y", item.y),
            z: .value("Z", item.z)
        )
    }
}
```

### openURL In-App Browser
```swift
@Environment(\.openURL) var openURL

Button("Open Link") {
    openURL(url, prefersInApp: true)  // Opens in-app browser
}
```

### Drag Container
```swift
List(selection: $selection) {
    ForEach(items) { item in
        ItemRow(item: item)
    }
}
.dragContainer(for: selection) { items in
    // Return drag preview
}
```

---

## Migration Priority

1. **High:** NavigationView → NavigationStack (architecture impact)
2. **High:** ObservableObject → @Observable (iOS 17+)
3. **High:** TabView tabItem → Tab API (iOS 18+)
4. **Medium:** foregroundColor → foregroundStyle
5. **Medium:** onChange single-param → two-param
6. **Medium:** @EnvironmentObject → @Environment
7. **Low:** cornerRadius → clipShape (visual only)

## Availability Patterns

```swift
// Feature check
if #available(iOS 17, *) {
    ContentView()
        .containerRelativeFrame(.horizontal)
} else {
    GeometryReader { geo in
        ContentView()
            .frame(width: geo.size.width * 0.8)
    }
}

// View modifier extension for compatibility
extension View {
    @ViewBuilder
    func iOS17ContainerFrame() -> some View {
        if #available(iOS 17, *) {
            self.containerRelativeFrame(.horizontal)
        } else {
            self
        }
    }
}
```

Sources: [Hacking with Swift - iOS 17](https://www.hackingwithswift.com/articles/260/whats-new-in-swiftui-for-ios-17), [Hacking with Swift - iOS 18](https://www.hackingwithswift.com/articles/270/whats-new-in-swiftui-for-ios-18), [Hacking with Swift - iOS 26](https://www.hackingwithswift.com/articles/278/whats-new-in-swiftui-for-ios-26), [Swift with Majid - WWDC25](https://swiftwithmajid.com/2025/06/10/what-is-new-in-swiftui-after-wwdc25/)
