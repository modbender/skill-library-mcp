# Apple Developer Toolkit

All-in-one Apple developer skill: documentation search, WWDC videos, App Store Connect management, and autonomous iOS app builder.

## Install

```bash
brew tap Abdullah4AI/tap
brew install appstore swiftship
```

Or via npx:

```bash
npx skills add Abdullah4AI/apple-developer-toolkit
```

ClawHub:

```bash
clawhub install apple-developer-toolkit
```

## What's Inside

### 1. Documentation Search

Search Apple Developer Documentation and 1,267 WWDC sessions (2014-2025) locally indexed.

```bash
node cli.js search "NavigationStack"
node cli.js symbols "UIView"
node cli.js doc "/documentation/swiftui/navigationstack"
node cli.js overview "SwiftUI"
node cli.js samples "SwiftUI"
node cli.js wwdc-search "concurrency"
node cli.js wwdc-year 2025
node cli.js wwdc-topic "swiftui-ui-frameworks"
```

### 2. App Store Connect (`appstore`)

80+ commands covering the entire App Store Connect API.

```bash
appstore auth login --name "MyApp" --key-id "KEY_ID" --issuer-id "ISSUER_ID" --private-key /path/to/AuthKey.p8
```

#### Apps & Versions
```bash
appstore apps                                    # List all apps
appstore versions --app "APP_ID"                 # List versions
appstore app-info --app "APP_ID"                 # App metadata
appstore localizations --app "APP_ID"            # Localization metadata
appstore screenshots upload --app "APP_ID" ...   # Upload screenshots
```

#### TestFlight & Builds
```bash
appstore builds upload --app "APP_ID" --ipa "app.ipa" --wait
appstore publish testflight --app "APP_ID" --ipa "app.ipa" --group "Beta" --wait
appstore testflight groups --app "APP_ID"
appstore feedback --app "APP_ID"
appstore crashes --app "APP_ID"
```

#### App Store Submission
```bash
appstore publish appstore --app "APP_ID" --ipa "app.ipa" --submit --confirm --wait
appstore submit --app "APP_ID"
appstore validate --app "APP_ID" --version-id "VER_ID" --strict
appstore review --app "APP_ID"
```

#### Signing & Certificates
```bash
appstore certificates list
appstore profiles list
appstore bundle-ids list
appstore signing create --app "APP_ID"
```

#### Monetization
```bash
appstore subscriptions list --app "APP_ID"
appstore iap list --app "APP_ID"
appstore offer-codes create --subscription "SUB_ID"
appstore pricing schedule get --app "APP_ID"
```

#### Analytics & Finance
```bash
appstore analytics sales --vendor "VENDOR" --type SALES --subtype SUMMARY --frequency DAILY --date "2024-01-20"
appstore finance reports --vendor "VENDOR"
appstore reviews --app "APP_ID" --output table
appstore insights weekly --app "APP_ID"
```

#### Automation
```bash
appstore xcode-cloud run --app "APP_ID" --workflow "CI" --branch "main" --wait
appstore notarization submit --file ./MyApp.zip --wait
appstore webhooks list
appstore workflow run --file .appstore/workflow.json
appstore migrate from-fastlane --app "APP_ID"
```

#### Full Command List

| Category | Commands |
|----------|----------|
| Getting Started | auth, doctor, init, docs |
| Apps | apps, app-setup, app-tags, app-info, app-infos, versions, localizations, screenshots, video-previews |
| TestFlight | testflight, builds, build-bundles, pre-release-versions, build-localizations, beta-app-localizations, sandbox |
| Review & Release | review, reviews, submit, validate, publish |
| Signing | signing, bundle-ids, certificates, profiles, merchant-ids, pass-type-ids, notarization |
| Monetization | iap, subscriptions, offer-codes, win-back-offers, promoted-purchases, app-events, pricing, pre-orders |
| Analytics | analytics, insights, finance, performance, feedback, crashes |
| Automation | xcode-cloud, webhooks, notify, migrate, workflow, metadata, diff |
| Team | account, users, actors, devices |
| Other | categories, age-rating, accessibility, encryption, eula, agreements, app-clips, game-center, background-assets, product-pages, routing-coverage, nominations, marketplace, alternative-distribution, android-ios-mapping |

### 3. iOS App Builder (`swiftship`)

Build complete iOS apps from natural language descriptions. Powered by AI code generation.

```bash
swiftship                        # Interactive mode - describe your app
swiftship chat                   # Chat mode for editing existing apps
swiftship setup                  # Install prerequisites (Xcode, XcodeGen)
swiftship fix                    # Auto-fix build errors
swiftship run                    # Build and launch in simulator
swiftship open                   # Open project in Xcode
swiftship info                   # Show project status
swiftship usage                  # Token usage and cost
swiftship --model opus           # Use a specific model
```

#### How It Works

```
describe → analyze → plan → build → fix → run
```

1. **Analyze** - Extracts app name, features, core flow from your description
2. **Plan** - Produces file-level build plan with data models, navigation, and design system
3. **Build** - Generates Swift source files, project.yml, and asset catalog
4. **Fix** - Compiles and auto-repairs until build succeeds
5. **Run** - Boots iOS Simulator and launches the app

#### Interactive Commands

| Command | Description |
|---------|-------------|
| `/run` | Build and launch in simulator |
| `/fix` | Auto-fix compilation errors |
| `/open` | Open project in Xcode |
| `/model [name]` | Switch model (sonnet, opus, haiku) |
| `/info` | Show project info |
| `/usage` | Token usage and cost |

## Reference Files

This skill includes 50+ reference files for AI agents:

| Reference | Content |
|-----------|---------|
| `references/app-store-connect.md` | Complete App Store Connect CLI reference |
| `references/ios-rules/` | 38 iOS development rules |
| `references/swiftui-guides/` | 12 SwiftUI best practice guides |
| `references/ios-app-builder-prompts.md` | System prompts for app building |

### iOS Rules (38)

accessibility, app_clips, app_review, apple_translation, biometrics, camera, charts, color_contrast, components, dark_mode, design-system, feedback_states, file-structure, forbidden-patterns, foundation_models, gestures, haptics, healthkit, live_activities, localization, maps, mvvm-architecture, navigation-patterns, notification_service, notifications, safari_extension, share_extension, siri_intents, spacing_layout, speech, storage-patterns, swift-conventions, timers, typography, view-composition, view_complexity, website_links, widgets

### SwiftUI Guides (12)

animations, forms-and-input, layout, liquid-glass, list-patterns, media, modern-apis, navigation, performance, scroll-patterns, state-management, text-formatting

## Requirements

- **Node.js** v18+ (documentation search)
- **Xcode** (iOS app building)
- **Homebrew** (binary installation)

## License

MIT
