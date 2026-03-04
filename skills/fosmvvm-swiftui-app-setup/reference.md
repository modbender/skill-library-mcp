# FOSMVVM SwiftUI App Setup - Reference Templates

Complete file templates for setting up a FOSMVVM SwiftUI application.

> **Conceptual context:** See [SKILL.md](SKILL.md) for when and why to use this skill.
> **Architecture context:** See [FOSMVVMArchitecture.md](../../docs/FOSMVVMArchitecture.md) for full FOSMVVM understanding.

## Placeholders

| Placeholder | Replace With | Example |
|-------------|--------------|---------|
| `{AppName}` | Your app name (without "App" suffix) | `MyApp`, `Accel` |
| `{AppTarget}` | Main app target name | `App` |
| `{ResourceBundle1}`, `{ResourceBundle2}` | Module names containing localization | `MyAppViewModels`, `SharedResources` |
| `{ProductionURL}` | Production server URL | `https://api.example.com` |
| `{DebugURL}` | Debug/local server URL | `http://localhost:8080` |

---

# Template 1: Basic App Setup (No Test Infrastructure)

For simple apps that don't need UI testing support.

**Location:** `Sources/{AppTarget}/{AppName}App.swift`

```swift
// {AppName}App.swift
//
// Copyright (c) 2026 Your Organization. All rights reserved.
// License: Your License

import {ResourceBundle1}
import FOSFoundation
import FOSMVVM
import SwiftUI

/// Entry point for the application
@main
struct {AppName}App: App {
    var body: some Scene {
        WindowGroup {
            LandingPageView()
        }
        .environment(mvvmEnv)
    }
}

private extension {AppName}App {
    var mvvmEnv: MVVMEnvironment {
        MVVMEnvironment(
            appBundle: Bundle.main,
            resourceBundles: [
                {ResourceBundle1}ResourceAccess.localizationBundle
                // Add additional resource bundles here
            ],
            deploymentURLs: [
                .production: .init(serverBaseURL: URL(string: "{ProductionURL}")!),
                .debug: .init(serverBaseURL: URL(string: "{DebugURL}")!)
            ]
        )
    }
}
```

---

# Template 2: Full App Setup (With Test Infrastructure)

For apps that need comprehensive UI testing support.

**Location:** `Sources/{AppTarget}/{AppName}App.swift`

```swift
// {AppName}App.swift
//
// Copyright (c) 2026 Your Organization. All rights reserved.
// License: Your License

import {ResourceBundle1}
import FOSFoundation
import FOSMVVM
import SwiftUI

// Deployment Notes:
//
// For release builds, the deployment environment is configured via Info.plist:
//
//  1. The CI pipeline sets the FOS_DEPLOYMENT build setting (e.g., "staging" or "production")
//  2. Info.plist contains: FOS-DEPLOYMENT = $(FOS_DEPLOYMENT)
//  3. FOSUtilities reads this value at runtime via Bundle.main.infoDictionary
//
// Expected CI configuration:
//   - Develop branch => deployment: staging
//   - Main branch => deployment: production
//
// The FOSMVVM.Deployment.current property automatically detects the deployment from Info.plist.
// No manual override or #if blocks are needed - detection is automatic.
//
// For local development, you can override via Xcode scheme:
//   Edit Scheme → Run → Arguments → Environment Variables → FOS-DEPLOYMENT = staging

/// Entry point for the application
@main
struct {AppName}App: App {
    #if DEBUG
    @State private var underTest = false
    #endif

    var body: some Scene {
        WindowGroup {
            ZStack {
                LandingPageView()
            }
            #if DEBUG
            .testHost { testConfiguration, testView in
                // Handle specific test configurations if needed
                // switch try? testConfiguration.fromJSON() as MyTestConfiguration {
                // case .specificScenario(let data):
                //     testView.environment(MyState.stub(data: data))
                //         .onAppear { underTest = true }
                //
                // default:
                //     testView.onAppear {
                //         underTest = ProcessInfo.processInfo.arguments.count > 1
                //     }
                // }

                // Default case - always needed
                default:
                    testView
                        .onAppear {
                            // Right now there's no other way to detect if the app is under test.
                            // This is only debug code, so we can
                            // proceed for now.
                            underTest = ProcessInfo.processInfo.arguments.count > 1
                        }
            }
            #endif
        }
        .environment(mvvmEnv)
    }

    init() {
        #if DEBUG
        registerTestingViews()
        #endif
    }
}

private extension {AppName}App {
    var mvvmEnv: MVVMEnvironment {
        MVVMEnvironment(
            appBundle: Bundle.main,
            resourceBundles: [
                {ResourceBundle1}ResourceAccess.localizationBundle
                // Add additional resource bundles here
            ],
            deploymentURLs: [
                .production: .init(serverBaseURL: URL(string: "{ProductionURL}")!),
                .debug: .init(serverBaseURL: URL(string: "{DebugURL}")!)
            ]
        )
    }
}

#if DEBUG
private extension {AppName}App {
    // Every ViewModelView is listed here to enable individualized
    // testing of each view
    @MainActor func registerTestingViews() {
        // Landing Page
        mvvmEnv.registerTestView(LandingPageView.self)

        // Add all your ViewModelViews here
        // Example:
        // mvvmEnv.registerTestView(SettingsView.self)
        // mvvmEnv.registerTestView(DashboardView.self)
    }
}
#endif
```

---

# Template 3: App with Custom Environment Values

For apps that inject additional environment values beyond MVVMEnvironment.

**Location:** `Sources/{AppTarget}/{AppName}App.swift`

```swift
// {AppName}App.swift
//
// Copyright (c) 2026 Your Organization. All rights reserved.
// License: Your License

import {ResourceBundle1}
import FOSFoundation
import FOSMVVM
import SwiftUI

/// Entry point for the application
@main
struct {AppName}App: App {
    @Environment(\.scenePhase) var scenePhase
    @State private var appState: AppState

    #if DEBUG
    @State private var underTest = false
    #endif

    var body: some Scene {
        WindowGroup {
            ZStack {
                LandingPageView()
            }
            #if DEBUG
            .testHost { testConfiguration, testView in
                default:
                    testView
                        .onAppear {
                            underTest = ProcessInfo.processInfo.arguments.count > 1
                        }
            }
            #endif
        }
        .onChange(of: scenePhase) {
            switch scenePhase {
            case .background:
                appState.appEnteredBackground()
            case .inactive:
                break
            case .active:
                appState.appEnteredForeground()
            @unknown default:
                break
            }
        }
        .environment(mvvmEnv)
        .environment(appState)
        .environment(\.colorScheme, .dark)  // Example: Force dark mode
    }

    init() {
        self.appState = AppState()

        #if DEBUG
        registerTestingViews()
        #endif
    }
}

private extension {AppName}App {
    var mvvmEnv: MVVMEnvironment {
        MVVMEnvironment(
            appBundle: Bundle.main,
            resourceBundles: [
                {ResourceBundle1}ResourceAccess.localizationBundle
            ],
            deploymentURLs: [
                .production: .init(serverBaseURL: URL(string: "{ProductionURL}")!),
                .debug: .init(serverBaseURL: URL(string: "{DebugURL}")!)
            ]
        )
    }
}

#if DEBUG
private extension {AppName}App {
    @MainActor func registerTestingViews() {
        mvvmEnv.registerTestView(LandingPageView.self)
    }
}
#endif
```

---

# Template 4: App with Multiple Deployment Environments

For apps that need staging, QA, and production environments.

**Location:** `Sources/{AppTarget}/{AppName}App.swift`

```swift
// {AppName}App.swift
//
// Copyright (c) 2026 Your Organization. All rights reserved.
// License: Your License

import {ResourceBundle1}
import FOSFoundation
import FOSMVVM
import SwiftUI

/// Entry point for the application
@main
struct {AppName}App: App {
    var body: some Scene {
        WindowGroup {
            LandingPageView()
        }
        .environment(mvvmEnv)
    }
}

private extension {AppName}App {
    var mvvmEnv: MVVMEnvironment {
        MVVMEnvironment(
            appBundle: Bundle.main,
            resourceBundles: [
                {ResourceBundle1}ResourceAccess.localizationBundle
            ],
            deploymentURLs: [
                .production: .init(serverBaseURL: URL(string: "https://api.example.com")!),
                .custom("staging"): .init(serverBaseURL: URL(string: "https://staging.api.example.com")!),
                .custom("qa"): .init(serverBaseURL: URL(string: "https://qa.api.example.com")!),
                .debug: .init(serverBaseURL: URL(string: "http://localhost:8080")!)
            ]
        )
    }
}
```

---

# Template 5: Complete Example with Advanced Features

A comprehensive example showing all features together.

**Location:** `Sources/App/MyApp.swift`

```swift
// MyApp.swift
//
// Copyright (c) 2026 Your Organization. All rights reserved.
// License: Your License

import FOSFoundation
import FOSMVVM
import MyAppViewModels
import MyAppViews
import SharedViewModels
import SharedViews
import SwiftUI
import ViewModels

/// Entry point for the application
@main
struct MyApp: App {
    #if DEBUG
    @State private var underTest = false
    #endif
    @Environment(\.scenePhase) var scenePhase
    @State private var appState: MyAppState

    var body: some Scene {
        WindowGroup {
            LandingPageView.bind(
                appState: .init(
                    bindingState: appState.bindingState.modelBindingState
                    // Add other appState properties as needed
                )
            )
            #if DEBUG
            .testHost { testConfiguration, testView in
                switch try? testConfiguration.fromJSON() as TestConfiguration {
                case .scenario1(let data):
                    testView.environment(
                        MyAppState.stub(data: data)
                    )
                    .onAppear {
                        underTest = true
                    }

                case .scenario2(let data):
                    testView.environment(
                        MyAppState.stub(data: data)
                    )
                    .onAppear {
                        underTest = true
                    }

                default:
                    testView
                        .onAppear {
                            underTest = ProcessInfo.processInfo.arguments.count > 1
                        }
                }
            }
            #endif
            .preferredColorScheme(ColorScheme.dark)
            .onAppear {
                loadAppState()
            }
        }
        .onChange(of: scenePhase) {
            switch scenePhase {
            case .background:
                appState.appEnteredBackground()
            case .inactive:
                break
            case .active:
                appState.appEnteredForeground()
            @unknown default:
                break
            }
        }
        .environment(\.colorScheme, .dark)
        .environment(appState)
        .environment(mvvmEnv)
    }

    init() {
        self.appState = MyAppState()

        #if DEBUG
        registerTestingViews()
        #endif
    }

    private func loadAppState() {
        appState.restoreState()
    }
}

private extension MyApp {
    var mvvmEnv: MVVMEnvironment {
        let env = MVVMEnvironment(
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

        #if DEBUG
        env.registerTestingViews()
        #endif

        return env
    }
}

#if DEBUG
private extension MyApp {
    // Every ViewModelView is listed here to enable individualized
    // testing of each view
    @MainActor func registerTestingViews() {
        // Landing Page
        mvvmEnv.registerTestView(LandingPageView.self)

        // Dashboard
        mvvmEnv.registerTestView(DashboardView.self)
        mvvmEnv.registerTestView(CardView.self)

        // Settings
        mvvmEnv.registerTestView(SettingsView.self)
        mvvmEnv.registerTestView(ProfileView.self)
    }
}
#endif
```

---

# Quick Reference: Key Components

## MVVMEnvironment Parameters

```swift
MVVMEnvironment(
    appBundle: Bundle,           // Usually Bundle.main
    resourceBundles: [Bundle],   // Localization bundles from modules
    deploymentURLs: [Deployment: DeploymentURLs]  // URLs per environment
)
```

## Deployment Types

| Deployment | When to Use | Example |
|------------|-------------|---------|
| `.production` | Production environment | Live server |
| `.debug` | Local development | `http://localhost:8080` |
| `.custom("name")` | Custom environments | Staging, QA, etc. |

## Test Infrastructure Components

| Component | Type | Purpose |
|-----------|------|---------|
| `@State private var underTest` | Property | Flag for test mode |
| `.testHost { }` | Modifier | Test configuration handler |
| `registerTestingViews()` | Method | Register views for testing |
| `mvvmEnv.registerTestView()` | Method | Register individual view |

**Important:** The `.testHost { }` modifier must be applied to the **top-level view** in your WindowGroup (the outermost view in the hierarchy). This ensures it wraps the entire view hierarchy and can properly intercept test configurations. Commonly this is a ZStack, VStack, or your root navigation view.

## Resource Bundle Accessors

Each module that contains localization resources should provide a bundle accessor:

```swift
// In your ViewModels module (e.g., MyAppViewModels/ResourceAccess.swift)
public enum MyAppViewModelsResourceAccess {
    public static var localizationBundle: Bundle { Bundle.module }
}
```

Then use it in the App's `resourceBundles` array:

```swift
resourceBundles: [
    MyAppViewModelsResourceAccess.localizationBundle,
    SharedResourceAccess.localizationBundle
]
```

## Common Customizations

### Additional Resource Bundles

```swift
resourceBundles: [
    Module1ResourceAccess.localizationBundle,
    Module2ResourceAccess.localizationBundle,
    Module3ResourceAccess.localizationBundle
]
```

### Multiple Deployment URLs

```swift
deploymentURLs: [
    .production: .init(serverBaseURL: URL(string: "https://api.example.com")!),
    .custom("staging"): .init(serverBaseURL: URL(string: "https://staging.api.example.com")!),
    .custom("qa"): .init(serverBaseURL: URL(string: "https://qa.api.example.com")!),
    .debug: .init(serverBaseURL: URL(string: "http://localhost:8080")!)
]
```

### Group Test View Registration

```swift
@MainActor func registerTestingViews() {
    // Landing
    mvvmEnv.registerTestView(LandingPageView.self)

    // Dashboard
    mvvmEnv.registerTestView(DashboardView.self)
    mvvmEnv.registerTestView(DashboardCardView.self)
    mvvmEnv.registerTestView(DashboardHeaderView.self)

    // Settings
    mvvmEnv.registerTestView(SettingsView.self)
    mvvmEnv.registerTestView(SettingsRowView.self)
}
```

---

# Checklists

## Basic App Setup:
- [ ] `@main` attribute on App struct
- [ ] `var body: some Scene` with WindowGroup
- [ ] Computed `var mvvmEnv: MVVMEnvironment`
- [ ] `.environment(mvvmEnv)` on WindowGroup
- [ ] `appBundle: Bundle.main` configured
- [ ] Resource bundles array populated
- [ ] Deployment URLs configured

## With Test Infrastructure:
- [ ] `@State private var underTest = false` in DEBUG
- [ ] `.testHost { }` modifier on main view
- [ ] Default case with `underTest` detection
- [ ] `init()` method created
- [ ] `registerTestingViews()` extension created
- [ ] `registerTestingViews()` called from `init()`
- [ ] All ViewModelViews registered

## Deployment Configuration:
- [ ] Info.plist contains `FOS-DEPLOYMENT = $(FOS_DEPLOYMENT)`
- [ ] CI pipeline sets `FOS_DEPLOYMENT` build setting
- [ ] Develop branch → staging
- [ ] Main branch → production
- [ ] Local development override documented

---

# Common Patterns

## Pattern 1: Initialize in App.init()

Custom initialization logic goes in `init()`:

```swift
init() {
    // Custom setup
    UserDefaults.standard.set(versionString, forKey: "app-version")

    // Initialize state
    self.appState = MyAppState()

    #if DEBUG
    registerTestingViews()
    #endif
}
```

## Pattern 2: Scene Phase Handling

React to app lifecycle events:

```swift
.onChange(of: scenePhase) {
    switch scenePhase {
    case .background:
        appState.appEnteredBackground()
        Task {
            await performBackgroundTasks()
        }
    case .active:
        appState.appEnteredForeground()
    case .inactive:
        break
    @unknown default:
        break
    }
}
```

## Pattern 3: Conditional Environment Configuration

Customize MVVMEnvironment based on build configuration:

```swift
var mvvmEnv: MVVMEnvironment {
    let env = MVVMEnvironment(
        appBundle: Bundle.main,
        resourceBundles: [...],
        deploymentURLs: [...]
    )

    #if DEBUG
    env.registerTestingViews()
    #endif

    return env
}
```
