---
name: TestFlight
slug: testflight
version: 1.0.0
homepage: https://clawic.com/skills/testflight
description: Distribute iOS and macOS beta builds with TestFlight, tester management, and CI/CD automation.
metadata: {"clawdbot":{"emoji":"🛫","requires":{"bins":[]},"os":["darwin"]}}
---

## When to Use

User needs to distribute beta builds via TestFlight. Agent handles App Store Connect setup, tester groups, build uploads, and CI/CD integration.

## Quick Reference

| Topic | File |
|-------|------|
| CI/CD automation | `ci-cd.md` |

## Core Rules

### 1. App Store Connect Setup First
Before uploading:
- Bundle ID registered in Developer Portal
- App created in App Store Connect
- App-specific password or API key configured

### 2. Build Requirements
Every TestFlight build needs:
- Unique build number (CFBundleVersion) - increment ALWAYS
- Valid provisioning profile (App Store distribution)
- No missing compliance declarations

### 3. Tester Group Strategy

| Group | Purpose | Limit |
|-------|---------|-------|
| Internal | Team members with App Store Connect access | 100 |
| External | Beta testers, requires review | 10,000 |

Internal builds available immediately. External requires Apple review (24-48h first time).

### 4. Upload Methods

| Method | Best For |
|--------|----------|
| Xcode | Manual, one-off uploads |
| `xcrun altool` | Scripts, CI without fastlane |
| Fastlane | Full automation, multiple apps |
| Xcode Cloud | Apple-native CI/CD |
| Transporter | GUI for non-developers |

### 5. Build Expiration
TestFlight builds expire after 90 days. Plan releases accordingly.

## TestFlight Traps

- **Build number not incremented** - rejected immediately, must bump and rebuild
- **Missing export compliance** - stuck in "Processing" until answered in App Store Connect
- **External testers on first build** - requires full beta review, use internal first
- **Expired provisioning profile** - upload fails silently, check before archiving
- **App-specific password in CI** - use App Store Connect API key instead (more secure, no 2FA issues)

## CI/CD Quick Setup

### App Store Connect API Key (Recommended)

1. App Store Connect > Users > Keys > App Store Connect API
2. Generate key with "App Manager" role
3. Download `.p8` file (only shown ONCE)
4. Note: Issuer ID, Key ID

### Fastlane Upload

```bash
# In Fastfile
lane :beta do
  build_app(scheme: "MyApp")
  upload_to_testflight(
    api_key_path: "fastlane/api_key.json",
    skip_waiting_for_build_processing: true
  )
end
```

### xcrun altool (No Fastlane)

```bash
xcrun altool --upload-app \
  --type ios \
  --file "MyApp.ipa" \
  --apiKey "KEY_ID" \
  --apiIssuer "ISSUER_ID"
```

## Security & Privacy

**Data that leaves your machine:**
- IPA/app binary uploaded to Apple servers
- Build metadata (version, bundle ID, team)

**Data that stays local:**
- API keys and certificates (keep in Keychain)
- Source code (not uploaded)

**This skill does NOT:**
- Store Apple credentials in plain text
- Share builds outside Apple's infrastructure

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `ios` — iOS development patterns
- `xcode` — Xcode workflows
- `flutter` — cross-platform builds

## Feedback

- If useful: `clawhub star testflight`
- Stay updated: `clawhub sync`
