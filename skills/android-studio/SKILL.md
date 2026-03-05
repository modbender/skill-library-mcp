---
name: Android Studio
slug: android-studio
version: 1.0.0
homepage: https://clawic.com/skills/android-studio
description: Master Android Studio IDE with debugging, profiling, refactoring, and productivity shortcuts.
metadata: {"clawdbot":{"emoji":"🤖","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
changelog: Initial release with IDE workflows, debugging, profiling, and shortcuts.
---

## Setup

On first use, read `setup.md` for integration guidelines.

## When to Use

User works with Android Studio IDE. Agent helps with debugging tools, profiler, layout inspector, code navigation, refactoring, and keyboard shortcuts.

## Architecture

Memory at `~/android-studio/`. See `memory-template.md` for structure.

```
~/android-studio/
├── memory.md      # Preferences and project context
└── shortcuts.md   # Custom shortcuts learned
```

## Quick Reference

| Topic | File |
|-------|------|
| Setup process | `setup.md` |
| Memory template | `memory-template.md` |
| Shortcuts | `shortcuts.md` |
| Debugging | `debugging.md` |

## Core Rules

### 1. Check IDE Version First
Before suggesting features, confirm Android Studio version. Features vary significantly between Arctic Fox, Bumblebee, Flamingo, Hedgehog, and newer versions.

### 2. Platform-Aware Shortcuts
| Action | macOS | Windows/Linux |
|--------|-------|---------------|
| Search Everywhere | Double Shift | Double Shift |
| Find Action | Cmd+Shift+A | Ctrl+Shift+A |
| Recent Files | Cmd+E | Ctrl+E |
| Navigate to Class | Cmd+O | Ctrl+N |
| Navigate to File | Cmd+Shift+O | Ctrl+Shift+N |
| Refactor This | Ctrl+T | Ctrl+Alt+Shift+T |
| Run | Ctrl+R | Shift+F10 |
| Debug | Ctrl+D | Shift+F9 |

### 3. Use IDE Tools Over Manual Inspection
- Layout Inspector over print debugging for UI issues
- Profiler over manual timing for performance
- Database Inspector over manual queries
- Network Inspector over logging requests

### 4. Leverage Code Generation
- Live Templates for boilerplate (type abbreviation + Tab)
- File Templates for new components
- Generate menu (Cmd/Alt+N) for constructors, getters, overrides

### 5. Debugging Strategy
1. Breakpoints with conditions for targeted debugging
2. Evaluate Expression (Alt+F8) for runtime inspection
3. Watches for tracking variables across frames
4. Frame inspection to navigate call stack

## Debugging Traps

- Setting breakpoints in hot loops → freezes IDE. Use conditional breakpoints.
- Debugging release builds → missing symbols. Debug with debug variant.
- Ignoring Logcat filters → drowning in logs. Filter by app package or tag.
- Not using "Attach Debugger" → missing app startup. Attach to running process.

## Profiling Traps

- Profiling debug builds → misleading performance. Profile release builds.
- CPU Profiler without filtering → overwhelming data. Focus on specific methods.
- Memory Profiler heap dumps during GC → skewed results. Trigger GC first.
- Ignoring Network Profiler → missing slow API calls. Always check network timing.

## Essential IDE Features

### Layout Inspector
- Inspect live view hierarchy in running app
- 3D mode for seeing layer depth
- Attribute inspection for debugging constraints
- Works with Compose and View system

### Database Inspector
- Query Room databases in real-time
- Edit values directly for testing
- Export data for analysis
- Requires API 26+ on device

### Network Inspector
- Inspect OkHttp/Retrofit requests without code changes
- View request/response bodies
- Timeline for identifying slow calls
- Requires enabling in manifest for release

### App Inspection
- Combined view of Database, Network, Background Tasks
- WorkManager task monitoring
- Background task scheduling inspection

### Profiler Tools
| Tool | Use Case |
|------|----------|
| CPU Profiler | Method timing, thread analysis |
| Memory Profiler | Leaks, allocation tracking |
| Energy Profiler | Battery usage patterns |
| Network Profiler | Request timing, payload size |

## Refactoring Shortcuts

| Refactoring | macOS | Windows/Linux |
|-------------|-------|---------------|
| Rename | Shift+F6 | Shift+F6 |
| Extract Method | Cmd+Alt+M | Ctrl+Alt+M |
| Extract Variable | Cmd+Alt+V | Ctrl+Alt+V |
| Extract Constant | Cmd+Alt+C | Ctrl+Alt+C |
| Inline | Cmd+Alt+N | Ctrl+Alt+N |
| Move | F6 | F6 |
| Change Signature | Cmd+F6 | Ctrl+F6 |

## Build Configuration

### Gradle Sync Issues
- File → Invalidate Caches / Restart for persistent issues
- Delete `.gradle` and `.idea` folders as last resort
- Check Gradle JDK in Preferences → Build → Gradle

### Build Variants
- Select variant in Build Variants panel
- Debug vs Release affects debugging capabilities
- Product flavors for different app configurations

### SDK Manager
- Tools → SDK Manager for Android SDK updates
- Install platform tools matching target devices
- Keep build tools updated for latest features

## Emulator Tips

- Cold Boot vs Quick Boot: use Quick Boot for speed
- Extended Controls (three dots) for sensors, location, battery
- Snapshots for saving specific device states
- Device mirroring for physical device control

## Plugin Recommendations

| Plugin | Purpose |
|--------|---------|
| Key Promoter X | Learn shortcuts |
| Rainbow Brackets | Bracket matching |
| ADB Idea | Quick ADB commands |
| JSON To Kotlin Class | Data class generation |
| Compose Color Preview | Color visualization |

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `android` — Android development patterns
- `kotlin` — Kotlin language features
- `java` — Java language patterns

## Feedback

- If useful: `clawhub star android-studio`
- Stay updated: `clawhub sync`
