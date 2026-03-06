---
description: "Implementation rules for haptics"
---
# Haptics

HAPTIC FEEDBACK:
- UIImpactFeedbackGenerator(style: .medium).impactOccurred() for simple taps
- UINotificationFeedbackGenerator().notificationOccurred(.success/.warning/.error) for outcomes
- UISelectionFeedbackGenerator().selectionChanged() for selection changes
- CoreHaptics for custom patterns: CHHapticEngine + CHHapticEvent
- Always check CHHapticEngine.capabilitiesForHardware().supportsHaptics
- Prepare generator before use: generator.prepare() for lower latency
