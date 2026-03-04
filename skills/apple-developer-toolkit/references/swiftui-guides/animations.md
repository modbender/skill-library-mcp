---
description: "Animation fundamentals, transitions, keyframes, phase animators, and the Animatable protocol"
---
# SwiftUI Animations Reference

Comprehensive guide to SwiftUI animations: basics, transitions, keyframes, phase animators, and custom Animatable conformance.

## Core Concepts

State changes trigger view updates. SwiftUI provides mechanisms to animate these changes.

**Animation Process:**
1. State change triggers view tree re-evaluation
2. SwiftUI compares new tree to current render tree
3. Animatable properties are identified and interpolated (~60 fps)

**Key Characteristics:**
- Animations are additive and cancelable
- Always start from current render tree state
- Blend smoothly when interrupted

---

## Implicit Animations

Use `.animation(_:value:)` to animate when a specific value changes.

```swift
// GOOD - uses value parameter
Rectangle()
    .frame(width: isExpanded ? 200 : 100, height: 50)
    .animation(.spring, value: isExpanded)
    .onTapGesture { isExpanded.toggle() }

// BAD - deprecated, animates all changes unexpectedly
Rectangle()
    .frame(width: isExpanded ? 200 : 100, height: 50)
    .animation(.spring)  // Deprecated!
```

---

## Explicit Animations

Use `withAnimation` for event-driven state changes.

```swift
// GOOD - explicit animation
Button("Toggle") {
    withAnimation(.spring) {
        isExpanded.toggle()
    }
}
```

**When to use which:**
- **Implicit**: Animations tied to specific value changes, precise view tree scope
- **Explicit**: Event-driven animations (button taps, gestures)

---

## Animation Placement

Place animation modifiers after the properties they should animate.

```swift
// GOOD - animation after properties
Rectangle()
    .frame(width: isExpanded ? 200 : 100, height: 50)
    .foregroundStyle(isExpanded ? .blue : .red)
    .animation(.default, value: isExpanded)  // Animates both

// BAD - animation before properties
Rectangle()
    .animation(.default, value: isExpanded)  // Too early!
    .frame(width: isExpanded ? 200 : 100, height: 50)
```

---

## Selective Animation

```swift
// GOOD - selective animation
Rectangle()
    .frame(width: isExpanded ? 200 : 100, height: 50)
    .animation(.spring, value: isExpanded)  // Animate size
    .foregroundStyle(isExpanded ? .blue : .red)
    .animation(nil, value: isExpanded)  // Don't animate color

// iOS 17+ scoped animation
Rectangle()
    .foregroundStyle(isExpanded ? .blue : .red)  // Not animated
    .animation(.spring) {
        $0.frame(width: isExpanded ? 200 : 100, height: 50)  // Animated
    }
```

---

## Timing Curves

| Curve | Use Case |
|-------|----------|
| `.spring` | Interactive elements, most UI |
| `.easeInOut` | Appearance changes |
| `.bouncy` | Playful feedback (iOS 17+) |
| `.linear` | Progress indicators only |

```swift
.animation(.default.speed(2.0), value: flag)  // 2x faster
.animation(.default.delay(0.5), value: flag)  // Delayed start
.animation(.default.repeatCount(3, autoreverses: true), value: flag)
```

---

## Animation Performance

### Prefer Transforms Over Layout

```swift
// GOOD - GPU accelerated transforms
Rectangle()
    .frame(width: 100, height: 100)
    .scaleEffect(isActive ? 1.5 : 1.0)  // Fast
    .offset(x: isActive ? 50 : 0)        // Fast
    .rotationEffect(.degrees(isActive ? 45 : 0))  // Fast

// BAD - layout changes are expensive
Rectangle()
    .frame(width: isActive ? 150 : 100, height: isActive ? 150 : 100)  // Expensive
```

### Narrow Animation Scope

```swift
// GOOD - animation scoped to specific subview
VStack {
    HeaderView()  // Not affected
    ExpandableContent(isExpanded: isExpanded)
        .animation(.spring, value: isExpanded)  // Only this
    FooterView()  // Not affected
}
```

### Avoid Animation in Hot Paths

```swift
// GOOD - gate by threshold
.onPreferenceChange(ScrollOffsetKey.self) { offset in
    let shouldShow = offset.y < -50
    if shouldShow != showTitle {
        withAnimation(.easeOut(duration: 0.2)) {
            showTitle = shouldShow
        }
    }
}
```

---

## Disabling Animations

```swift
// GOOD - disable with transaction
Text("Count: \(count)")
    .transaction { $0.animation = nil }

// GOOD - disable from parent context
DataView()
    .transaction { $0.disablesAnimations = true }
```

---

## Transitions

Transitions animate views being inserted or removed from the render tree.

### Critical: Transitions Require Animation Context

```swift
// GOOD - animation outside conditional
VStack {
    Button("Toggle") { showDetail.toggle() }
    if showDetail {
        DetailView()
            .transition(.slide)
    }
}
.animation(.spring, value: showDetail)

// BAD - animation inside conditional (removed with view!)
if showDetail {
    DetailView()
        .transition(.slide)
        .animation(.spring, value: showDetail)  // Won't work on removal!
}
```

### Built-in Transitions

| Transition | Effect |
|------------|--------|
| `.opacity` | Fade in/out (default) |
| `.scale` | Scale up/down |
| `.slide` | Slide from leading edge |
| `.move(edge:)` | Move from specific edge |
| `.offset(x:y:)` | Move by offset amount |

### Combining Transitions

```swift
.transition(.slide.combined(with: .opacity))
```

### Asymmetric Transitions

```swift
// GOOD - different animations for insert/remove
if showCard {
    CardView()
        .transition(
            .asymmetric(
                insertion: .scale.combined(with: .opacity),
                removal: .move(edge: .bottom).combined(with: .opacity)
            )
        )
}
```

### Custom Transitions (iOS 17+)

```swift
struct BlurTransition: Transition {
    var radius: CGFloat

    func body(content: Content, phase: TransitionPhase) -> some View {
        content
            .blur(radius: phase.isIdentity ? 0 : radius)
            .opacity(phase.isIdentity ? 1 : 0)
    }
}
```

---

## The Animatable Protocol

Enables custom property interpolation during animations.

```swift
struct ShakeModifier: ViewModifier, Animatable {
    var shakeCount: Double

    var animatableData: Double {
        get { shakeCount }
        set { shakeCount = newValue }
    }

    func body(content: Content) -> some View {
        content.offset(x: sin(shakeCount * .pi * 2) * 10)
    }
}
```

### Multiple Properties with AnimatablePair

```swift
struct ComplexModifier: ViewModifier, Animatable {
    var scale: CGFloat
    var rotation: Double

    var animatableData: AnimatablePair<CGFloat, Double> {
        get { AnimatablePair(scale, rotation) }
        set {
            scale = newValue.first
            rotation = newValue.second
        }
    }

    func body(content: Content) -> some View {
        content
            .scaleEffect(scale)
            .rotationEffect(.degrees(rotation))
    }
}
```

---

## Transactions

The underlying mechanism for all animations in SwiftUI.

```swift
// withAnimation is shorthand for withTransaction
var transaction = Transaction(animation: .default)
withTransaction(transaction) { flag.toggle() }
```

**Implicit animations override explicit animations** (later in view tree wins).

---

## Phase Animations (iOS 17+)

Cycle through discrete phases automatically.

```swift
// Triggered phase animation
Button("Shake") { trigger += 1 }
    .phaseAnimator(
        [0.0, -10.0, 10.0, -5.0, 5.0, 0.0],
        trigger: trigger
    ) { content, offset in
        content.offset(x: offset)
    }
```

### Enum Phases (Recommended)

```swift
enum BouncePhase: CaseIterable {
    case initial, up, down, settle

    var scale: CGFloat {
        switch self {
        case .initial: 1.0
        case .up: 1.2
        case .down: 0.9
        case .settle: 1.0
        }
    }
}

Circle()
    .phaseAnimator(BouncePhase.allCases, trigger: trigger) { content, phase in
        content.scaleEffect(phase.scale)
    }
```

---

## Keyframe Animations (iOS 17+)

Precise timing control with exact values at specific times.

```swift
Button("Bounce") { trigger += 1 }
    .keyframeAnimator(
        initialValue: AnimationValues(),
        trigger: trigger
    ) { content, value in
        content
            .scaleEffect(value.scale)
            .offset(y: value.verticalOffset)
    } keyframes: { _ in
        KeyframeTrack(\.scale) {
            SpringKeyframe(1.2, duration: 0.15)
            SpringKeyframe(0.9, duration: 0.1)
            SpringKeyframe(1.0, duration: 0.15)
        }
        KeyframeTrack(\.verticalOffset) {
            LinearKeyframe(-20, duration: 0.15)
            LinearKeyframe(0, duration: 0.25)
        }
    }

struct AnimationValues {
    var scale: CGFloat = 1.0
    var verticalOffset: CGFloat = 0
}
```

| Keyframe Type | Behavior |
|---------------|----------|
| `CubicKeyframe` | Smooth interpolation |
| `LinearKeyframe` | Straight-line interpolation |
| `SpringKeyframe` | Spring physics |
| `MoveKeyframe` | Instant jump (no interpolation) |

---

## Animation Completion (iOS 17+)

```swift
Button("Animate") {
    withAnimation(.spring) {
        isExpanded.toggle()
    } completion: {
        showNextStep = true
    }
}
```
