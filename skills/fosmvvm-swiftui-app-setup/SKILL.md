---
name: fosmvvm-swiftui-app-setup
description: Set up the @main App struct for FOSMVVM SwiftUI apps. Configures MVVMEnvironment, deployment URLs, and test infrastructure.
homepage: https://github.com/foscomputerservices/FOSUtilities
metadata: {"clawdbot": {"emoji": "🚀", "os": ["darwin"]}}
---

# FOSMVVM SwiftUI App Setup

Generate the main App struct for a SwiftUI application using FOSMVVM architecture.

## Conceptual Foundation

> For full architecture context, see [FOSMVVMArchitecture.md](../../docs/FOSMVVMArchitecture.md) | [OpenClaw reference]({baseDir}/references/FOSMVVMArchitecture.md)

The **App struct** is the entry point of a SwiftUI application. In FOSMVVM, it has three core responsibilities:

```
┌─────────────────────────────────────────────────────────────┐
│                      @main App Struct                        │
├─────────────────────────────────────────────────────────────┤
│  1. MVVMEnvironment Setup                                   │
│     - Bundles (app + localization resources)                │
│     - Deployment URLs (production, staging, debug)          │
│                                                              │
│  2. Environment Injection                                   │
│     - .environment(mvvmEnv) on WindowGroup                  │
│     - Custom environment values                             │
│                                                              │
│  3. Test Infrastructure (DEBUG only)                        │
│     - .testHost { } modifier for UI testing                 │
│     - registerTestingViews() for individual view testing    │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. MVVMEnvironment

The `MVVMEnvironment` provides FOSMVVM infrastructure to all views:

```swift
private var mvvmEnv: MVVMEnvironment {
    MVVMEnvironment(
        appBundle: Bundle.main,
        resourceBundles: [
            MyAppViewModelsResourceAccess.localizationBundle,
            SharedResourceAccess.localizationBundle
        ],
        deploymentURLs: [
            .production: .init(serverBaseURL: URL(string: "https://api.example.com")!),
            .debug: .init(serverBaseURL: URL(string: "http://localhost:8080")!)
        ]
    )
}
```

**Key configuration:**
- `appBundle` - Usually `Bundle.main` (the app bundle)
- `resourceBundles` - Array of localization bundles from your modules
- `deploymentURLs` - URLs for each deployment environment

**Resource Bundle Accessors:**

Each module that contains localization resources should provide a bundle accessor:

```swift
// In your ViewModels module (e.g., MyAppViewModels/ResourceAccess.swift)
public enum MyAppViewModelsResourceAccess {
    public static var localizationBundle: Bundle { Bundle.module }
}
```

This pattern:
- Uses `Bundle.module` which SPM automatically provides for each module
- Provides a clean public API for accessing the module's resources
- Keeps bundle access centralized in one place per module

### 2. Environment Injection

The `MVVMEnvironment` is injected at the WindowGroup level:

```swift
var body: some Scene {
    WindowGroup {
        MyView()
    }
    .environment(mvvmEnv)  // ← Makes FOSMVVM infrastructure available
}
```

This makes the environment available to all views in the hierarchy.

### 3. Test Infrastructure

The test infrastructure enables UI testing with specific configurations:

**`.testHost { }` modifier:**
```swift
var body: some Scene {
    WindowGroup {
        ZStack {
            LandingPageView()
        }
        #if DEBUG
        .testHost { testConfiguration, testView in
            // Handle specific test configurations...

            default:
                testView
                    .onAppear {
                        underTest = ProcessInfo.processInfo.arguments.count > 1
                    }
        }
        #endif
    }
}
```

**Key points:**
- **Apply to the top-level view** in WindowGroup (the outermost view in your hierarchy)
- This ensures the modifier wraps the entire view hierarchy to intercept test configurations
- Always include the `default:` case
- The default case detects test mode via process arguments
- Sets `@State private var underTest = false` flag
- Optional: Add specific test configurations for advanced scenarios

**`registerTestingViews()` function:**
```swift
#if DEBUG
private extension MyApp {
    @MainActor func registerTestingViews() {
        mvvmEnv.registerTestView(LandingPageView.self)
        mvvmEnv.registerTestView(SettingsView.self)
        // ... register all ViewModelViews for individual testing
    }
}
#endif
```

**Key points:**
- Extension on the **App struct** (not MVVMEnvironment)
- Called from `init()`
- Registers every ViewModelView for isolated testing
- DEBUG only

## When to Use This Skill

- Starting a new FOSMVVM SwiftUI application
- Migrating an existing SwiftUI app to FOSMVVM
- Setting up the App struct with proper FOSMVVM infrastructure
- Configuring test infrastructure for UI testing

## What This Skill Generates

| Component | Location | Purpose |
|-----------|----------|---------|
| Main App struct | `Sources/App/{AppName}.swift` | Entry point with MVVMEnvironment setup |
| MVVMEnvironment configuration | Computed property in App struct | Bundles and deployment URLs |
| Test infrastructure | DEBUG blocks in App struct | UI testing support |

## Project Structure Configuration

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{AppName}` | Your app name | `MyApp`, `AccelApp` |
| `{AppTarget}` | Main app target | `App` |
| `{ResourceBundles}` | Module names with localization | `MyAppViewModels`, `SharedResources` |

## How to Use This Skill

**Invocation:**
/fosmvvm-swiftui-app-setup

**Prerequisites:**
- App name understood from conversation context
- Deployment URLs discussed or documented
- Resource bundles identified (modules with localization)
- Test support requirements clarified

**Workflow integration:**
This skill is used when setting up a new FOSMVVM SwiftUI application or adding FOSMVVM infrastructure to an existing app. The skill references conversation context automatically—no file paths or Q&A needed.

## Pattern Implementation

This skill references conversation context to determine App struct configuration:

### Configuration Detection

From conversation context, the skill identifies:
- **App name** (from project discussion or existing code)
- **Deployment environments** (production, staging, debug URLs)
- **Resource bundles** (modules containing localization YAML files)
- **Test infrastructure** (whether UI testing support needed)

### MVVMEnvironment Setup

Based on project structure:
- **App bundle** (typically Bundle.main)
- **Resource bundle accessors** (from identified modules)
- **Deployment URLs** (for each environment)
- **Current version** (from shared module)

### Test Infrastructure Planning

If test support needed:
- **Test detection** (process arguments check)
- **Test host modifier** (wrapping top-level view)
- **View registration** (all ViewModelViews for testing)

### File Generation

1. Main App struct with @main attribute
2. MVVMEnvironment computed property
3. WindowGroup with environment injection
4. Test infrastructure (if requested, DEBUG-only)
5. registerTestingViews() extension (if test support)

### Context Sources

Skill references information from:
- **Prior conversation**: App requirements, deployment environments discussed
- **Project structure**: From codebase analysis of module organization
- **Existing patterns**: From other FOSMVVM apps if context available

## Key Patterns

### MVVMEnvironment as Computed Property

The `MVVMEnvironment` is a computed property, not a stored property:

```swift
private var mvvmEnv: MVVMEnvironment {
    MVVMEnvironment(
        appBundle: Bundle.main,
        resourceBundles: [...],
        deploymentURLs: [...]
    )
}
```

**Why computed?**
- Keeps initialization logic separate
- Can be customized in DEBUG vs RELEASE
- Clear dependency on bundles and URLs

### Test Detection Pattern

The default test detection uses process arguments:

```swift
@State private var underTest = false

// In .testHost default case:
testView
    .onAppear {
        // Right now there's no other way to detect if the app is under test.
        // This is only debug code, so we can proceed for now.
        underTest = ProcessInfo.processInfo.arguments.count > 1
    }
```

**Why this approach?**
- Simple and reliable for DEBUG builds
- No additional dependencies
- Process arguments are set by test runner

### Register All ViewModelViews

Every ViewModelView should be registered for testing:

```swift
@MainActor func registerTestingViews() {
    // Landing Page
    mvvmEnv.registerTestView(LandingPageView.self)

    // Settings
    mvvmEnv.registerTestView(SettingsView.self)
    mvvmEnv.registerTestView(ProfileView.self)

    // Dashboard
    mvvmEnv.registerTestView(DashboardView.self)
    mvvmEnv.registerTestView(CardView.self)
}
```

**Organization tips:**
- Group by feature/screen with comments
- Alphabetical order within groups
- One view per line for easy scanning

## Common Customizations

### Multiple Environment Values

You can inject multiple environment values:

```swift
var body: some Scene {
    WindowGroup {
        MyView()
    }
    .environment(mvvmEnv)
    .environment(appState)
    .environment(\.colorScheme, .dark)
    .environment(\.customValue, myCustomValue)
}
```

### Conditional Test Registration

You can conditionally register views based on build configuration:

```swift
#if DEBUG
@MainActor func registerTestingViews() {
    mvvmEnv.registerTestView(LandingPageView.self)

    #if INCLUDE_ADMIN_FEATURES
    mvvmEnv.registerTestView(AdminPanelView.self)
    #endif
}
#endif
```

### Advanced Test Configurations

You can add specific test configurations in `.testHost`:

```swift
.testHost { testConfiguration, testView in
    switch try? testConfiguration.fromJSON() as MyTestConfiguration {
    case .specificScenario(let data):
        testView.environment(MyState.stub(data: data))
            .onAppear { underTest = true }

    default:
        testView
            .onAppear {
                underTest = ProcessInfo.processInfo.arguments.count > 1
            }
    }
}
```

## File Templates

See [reference.md](reference.md) for complete file templates.

## Naming Conventions

| Concept | Convention | Example |
|---------|------------|---------|
| App struct | `{Name}App` | `MyApp`, `AccelApp` |
| Main file | `{Name}App.swift` | `MyApp.swift` |
| MVVMEnvironment property | `mvvmEnv` | Always `mvvmEnv` |
| Test flag | `underTest` | Always `underTest` |

## Deployment Configuration

FOSMVVM supports deployment detection via Info.plist:

```
CI Pipeline Sets:
   FOS_DEPLOYMENT build setting (e.g., "staging" or "production")
        ↓
Info.plist Contains:
   FOS-DEPLOYMENT = $(FOS_DEPLOYMENT)
        ↓
Runtime Detection:
   FOSMVVM.Deployment.current reads from Bundle.main.infoDictionary
```

**Local development override:**
- Edit Scheme → Run → Arguments → Environment Variables
- Add: `FOS-DEPLOYMENT = staging`

## See Also

- [Architecture Patterns](../shared/architecture-patterns.md) - Mental models and patterns
- [FOSMVVMArchitecture.md](../../docs/FOSMVVMArchitecture.md) - Full FOSMVVM architecture
- [fosmvvm-viewmodel-generator](../fosmvvm-viewmodel-generator/SKILL.md) - For creating ViewModels
- [reference.md](reference.md) - Complete file templates

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-23 | Initial skill for SwiftUI app setup |
| 1.1 | 2026-01-24 | Update to context-aware approach (remove file-parsing/Q&A). Skill references conversation context instead of asking questions or accepting file paths. |
